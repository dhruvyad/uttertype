import audiomath as am
from openai import OpenAI
from pynput import keyboard
import asyncio


class AudioTranscriber:
    def __init__(self):
        self.recorder = None
        self.event_loop = asyncio.get_event_loop()
        self.transcriptions = asyncio.Queue()
        self.client = OpenAI()

    def start_recording(self):
        """Start recording audio from the microphone."""
        # Start a new recording in the background, do not block
        self.recorder = am.Recorder(30, filename="audio.wav")
        self.recorder.Start()

    def stop_recording(self):
        """Stop the recording and save to a file."""
        if self.recorder:
            self.recorder.Stop()

    def fn_hold(self, key):
        if hasattr(key, "vk") and key.vk == 63:  # Adjust vk according to your keyboard
            if self.recorder:  # hold ended
                self.stop_recording()
                self.transcribe_audio(open("audio.wav", "rb"))
                self.recorder = None
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
