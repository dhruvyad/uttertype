import io
from typing import List, Tuple
import pyaudio
import wave
from openai import OpenAI
from pynput import keyboard
import asyncio
from threading import Thread, Event
import webrtcvad
from utils import transcription_concat

# TODO: put these in a toml file
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 16000  # Sample rate
CHUNK_DURATION_MS = 30  # Frame duration in milliseconds
CHUNK = int(RATE * CHUNK_DURATION_MS / 1000)
MIN_TRANSCRIPTION_SIZE = (
    1500  # Minimum duration of speech to send to API in case of silence
)


class AudioTranscriber:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.recording_finished = Event()  # Threading event to end recording
        self.recording_finished.set()  # Initialize as finished
        self.frames = []
        self.rolling_transcriptions: List[Tuple[int, str]] = []  # (idx, transcription)
        self.rolling_requests: List[Thread] = []  # list of pending requests
        self.event_loop = asyncio.get_event_loop()
        self.vad = webrtcvad.Vad(1)  # Voice Activity Detector, mode can be 0 to 3
        self.transcriptions = asyncio.Queue()
        self.client = OpenAI()

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
                is_speech = self.vad.is_speech(data, RATE)
                current_audio_duration = len(self.frames) * CHUNK_DURATION_MS
                print(
                    is_speech,
                    f"{(current_audio_duration / MIN_TRANSCRIPTION_SIZE) * 100}%",
                )
                if (
                    not is_speech and current_audio_duration >= MIN_TRANSCRIPTION_SIZE
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

    def _intermediate_transcription(self, idx, audio):
        intermediate_transcription = self.transcribe_audio(audio)
        self.rolling_transcriptions.append((idx, intermediate_transcription))

    def stop_recording(self):
        """Stop the recording and save to a file."""
        self.recording_finished.set()
        self.frames = []
        self.rolling_requests = []
        self.rolling_transcriptions = []

    def _finish_transcription(self):
        self.recording_finished.set()  # Stop before sending final request to avoid race
        transcription = self.transcribe_audio(
            self._frames_to_wav()
        )  # Last transcription
        for request in self.rolling_requests:  # Wait for rolling requests
            request.join()
        self.rolling_transcriptions.append(
            (len(self.rolling_transcriptions), transcription)
        )
        sorted(self.rolling_transcriptions, key=lambda x: x[0])  # Sort by idx
        transcriptions = [
            t[1] for t in self.rolling_transcriptions
        ]  # Get ordered transcriptions
        self.event_loop.call_soon_threadsafe(  # Put final combined result in finished queue
            self.transcriptions.put_nowait,
            transcription_concat(transcriptions),
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

    def fn_hold(self, key):
        if hasattr(key, "vk") and key.vk == 63:  # Adjust vk according to your keyboard
            if not self.recording_finished.is_set():  # hold ended
                self._finish_transcription()
                self.stop_recording()
            else:  # hold started
                self.start_recording()

    def transcribe_audio(self, audio: io.BytesIO) -> str:
        try:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text",
                language="en",
                prompt="The following is normal speech or technical speech from an engineer.",
            )
            return transcription
        except Exception as e:
            print(f"Encountered Error: {e}")
            return ""

    async def get_transcriptions(self):
        while True:
            item = await self.transcriptions.get()
            yield item
            self.transcriptions.task_done()

    def listen_for_keypress(self):
        keyboard.Listener(
            on_release=self.fn_hold,
        ).start()
