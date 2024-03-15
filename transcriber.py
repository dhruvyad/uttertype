import io
import pyaudio
import wave
from openai import OpenAI
from pynput import keyboard
import asyncio
from threading import Thread

# TODO: put these in a toml file
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 16000  # Sample rate
CHUNK = 64  # Frames per buffer

class AudioTranscriber:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.event_loop = asyncio.get_event_loop()
        self.transcriptions = asyncio.Queue()
        self.client = OpenAI()

    def start_recording(self):
        """Start recording audio from the microphone."""
        # Start a new recording in the background, do not block
        def _record():
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK
            )
            while self.stream:  # Keep recording until interrupted
                data = self.stream.read(CHUNK)
                self.frames.append(data)
        # start recording in a new non-blocking thread
        Thread(target=_record).start()

    def stop_recording(self):
        """Stop the recording and save to a file."""
        self.stream = None
        self.frames = []

    def _frames_to_wav(self):
        buffer = io.BytesIO()
        buffer.name = "tmp.wav"
        wf = wave.open(buffer, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        return buffer

    def fn_hold(self, key):
        if hasattr(key, "vk") and key.vk == 63:  # Adjust vk according to your keyboard
            if self.stream:  # hold ended
                self.transcribe_audio(self._frames_to_wav())
                self.stop_recording()
            else:  # hold started
                self.start_recording()

    def transcribe_audio(self, audio) -> str:
        try:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text",
                language="en",
                prompt="The following is normal speech or technical speech from an engineer.",
            )
            self.event_loop.call_soon_threadsafe(
                self.transcriptions.put_nowait, transcription
            )
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

