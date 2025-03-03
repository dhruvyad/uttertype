import os
import io
from typing import List, Tuple, Optional
import pyaudio
import wave
from openai import OpenAI
import asyncio
from threading import Thread, Event
import webrtcvad
from uttertype.utils import transcription_concat
import tempfile
from textwrap import dedent
from google import genai
from google.genai import types

FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 16000  # Sample rate
CHUNK_DURATION_MS = 30  # Frame duration in milliseconds
CHUNK = int(RATE * CHUNK_DURATION_MS / 1000)
# Minimum duration of speech to send to API between gaps of silence (hard-coded to 10 seconds)
MIN_TRANSCRIPTION_SIZE_MS = 10000


class AudioTranscriber:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.recording_finished = Event()  # Threading event to end recording
        self.recording_finished.set()  # Initialize as finished
        self.frames = []
        self.audio_duration = 0
        self.rolling_transcriptions: List[Tuple[int, str]] = []  # (idx, transcription)
        self.rolling_requests: List[Thread] = []  # list of pending requests
        self.event_loop = asyncio.get_event_loop()
        self.vad = webrtcvad.Vad(1)  # Voice Activity Detector, mode can be 0 to 3
        self.transcriptions = asyncio.Queue()

    def start_recording(self):
        """Start recording audio from the microphone."""

        # Start a new recording in the background, do not block
        def _record():
            self.recording_finished = Event()
            stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )
            intermediate_trancriptions_idx = 0
            while (
                not self.recording_finished.is_set()
            ):  # Keep recording until interrupted
                data = stream.read(CHUNK)
                self.audio_duration += CHUNK_DURATION_MS
                is_speech = self.vad.is_speech(data, RATE)
                current_audio_duration = len(self.frames) * CHUNK_DURATION_MS
                if (
                    not is_speech
                    and current_audio_duration >= MIN_TRANSCRIPTION_SIZE_MS
                ):  # silence
                    rolling_request = Thread(
                        target=self._intermediate_transcription,
                        args=(
                            intermediate_trancriptions_idx,
                            self._frames_to_wav(),
                        ),
                    )
                    self.frames = []
                    self.rolling_requests.append(rolling_request)
                    rolling_request.start()
                    intermediate_trancriptions_idx += 1
                self.frames.append(data)

        # start recording in a new non-blocking thread
        Thread(target=_record).start()

    def stop_recording(self):
        """Stop the recording and reset variables"""
        self.recording_finished.set()
        self._finish_transcription()
        self.frames = []
        self.audio_duration = 0
        self.rolling_requests = []
        self.rolling_transcriptions = []

    def _intermediate_transcription(self, idx, audio):
        intermediate_transcription = self.transcribe_audio(audio)
        self.rolling_transcriptions.append((idx, intermediate_transcription))

    def _finish_transcription(self):
        for request in self.rolling_requests:  # Wait for all of the rolling requests
            request.join()

        # Process the final transcription chunk
        final_transcription_chunk = self.transcribe_audio(
            self._frames_to_wav()
        )

        # Sort by idx
        sorted_transcription_chunks = sorted(self.rolling_transcriptions, key=lambda x: x[0])

        # Get only the transcription texts
        transcriptions = [t[1] for t in sorted_transcription_chunks] + [final_transcription_chunk]

        # Put final combined result in finished queue
        self.event_loop.call_soon_threadsafe(
            self.transcriptions.put_nowait,
            (transcription_concat(transcriptions), self.audio_duration),
        )

    def _frames_to_wav(self):
        buffer = io.BytesIO()
        buffer.name = "tmp.wav"
        wf = wave.open(buffer, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(self.frames))
        wf.close()
        return buffer

    def transcribe_audio(self, audio: io.BytesIO) -> str:
        raise NotImplementedError("Please use a subclass of AudioTranscriber")

    async def get_transcriptions(self):
        """
        Asynchronously get transcriptions from the queue.
        Returns (transcription string, audio duration in ms).
        """
        while True:
            transcription = await self.transcriptions.get()
            yield transcription
            self.transcriptions.task_done()


class WhisperAPITranscriber(AudioTranscriber):
    def __init__(self, base_url, model_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model_name = model_name
        self.client = OpenAI(base_url=base_url)

    @staticmethod
    def create(*args, **kwargs):
        base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        model_name = os.getenv('OPENAI_MODEL_NAME', 'whisper-1')

        return WhisperAPITranscriber(base_url, model_name)

    def transcribe_audio(self, audio: io.BytesIO) -> str:
        try:
            transcription = self.client.audio.transcriptions.create(
                model=self.model_name,
                file=audio,
                response_format="text",
                language="en",
                prompt="The following is normal speech or technical speech from an engineer.",
            )
            return transcription
        except Exception as e:
            print(f"Encountered Error: {e}")
            return ""


class WhisperLocalMLXTranscriber(AudioTranscriber):
    def __init__(self, model_type="distil-medium.en", *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from lightning_whisper_mlx import LightningWhisperMLX
            self.model = LightningWhisperMLX(model_type)
        except ImportError:
            raise ImportError(
                "lightning-whisper-mlx not found. Install with: uv sync --extra mlx"
            )
    
    @staticmethod
    def create(*args, **kwargs):
        model_type = os.getenv('MLX_MODEL_NAME', 'distil-medium.en')
        return WhisperLocalMLXTranscriber(model_type=model_type)

    def transcribe_audio(self, audio: io.BytesIO) -> str:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                tmpfile.write(audio.getvalue())
                transcription = self.model.transcribe(tmpfile.name)["text"]
                os.unlink(tmpfile.name)
            return transcription
        except Exception as e:
            print(f"Encountered Error: {e}")
            return ""


class GeminiTranscriber(AudioTranscriber):
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 use_vertex: bool = False,
                 project: Optional[str] = None, 
                 location: str = "us-central1",
                 model: str = "gemini-2.0-flash",
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if use_vertex:
            if not project:
                raise ValueError("Project ID is required for Vertex AI")
            self.client = genai.Client(
                vertexai=True,
                project=project,
                location=location
            )
        else:
            if not api_key:
                raise ValueError("API key is required for Gemini API")
            self.client = genai.Client(api_key=api_key)
        
        self.model_name = model
        self.prompt = dedent("""\
        Audio Transcription Guidelines

        Your task is to transcribe the provided audio accurately. Whether the audio contains normal speech or technical content with varied speeds, please adhere to the following guidelines:

        1. Transcribe exactly what is spoken, preserving the original meaning and content.

        2. Assume English is spoken, unless it is clear another language is spoken.

        3. Numbers should be numerical and not written as words.

        4. For special characters that are spoken by name (such as "underscore," "dash," "period"), convert them to their corresponding symbols (_, -, .) when contextually appropriate, such as in:
          - Email addresses
          - Website URLs
          - File names
          - Programming code
          - Mathematical expressions

        5. Maintain proper punctuation, capitalization, and paragraph breaks to enhance readability.

        6. For technical content, preserve technical terms, acronyms, and specialized vocabulary exactly as spoken.

        7. Remove any ums and uhs. Connect their thought so that it is fluid.

        8. The user may have self-edited while speaking. If the user corrects themselves (usually via some interjection like "I meant" or "no, no"), edit the transcription to reflect their intended meaning rather than including the correction process itself.

        <EXAMPLE>
        User Said: "The art of doing science and engineering. I mean just science."
        Expected Transcription: "The art of doing science."
        </EXAMPLE>

        Below will follow the audio.
        """)

    @staticmethod
    def create(*args, **kwargs):
        use_vertex = os.getenv('GEMINI_USE_VERTEX', 'false').lower() in ('true', 'yes', '1', 't')
        project = os.getenv('GEMINI_PROJECT_ID')
        api_key = os.getenv('GEMINI_API_KEY')
        model = os.getenv('GEMINI_MODEL_NAME', 'gemini-2.0-flash')
        location = os.getenv('GEMINI_LOCATION', 'us-central1')
        
        return GeminiTranscriber(
            api_key=api_key,
            use_vertex=use_vertex,
            project=project,
            location=location,
            model=model
        )
    
    def transcribe_audio(self, audio: io.BytesIO) -> str:
        try:
            # Get the audio bytes directly from the BytesIO object
            audio_bytes = audio.getvalue()
            
            # Send to Gemini API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    self.prompt,
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type='audio/wav',
                    ),
                ]
            )

            # Extract transcription from response
            transcription = response.text.strip()
            return transcription
            
        except Exception as e:
            print(f"Gemini Transcription Error: {e}")
            return ""
