import pyautogui
import audiomath as am
from openai import OpenAI
import speech_recognition as sr
from pynput import keyboard


class AudioTranscriber:
    def __init__(self):
        self.recorder = None
        self.client = OpenAI()

    def start_recording(self):
        """Start recording audio from the microphone."""
        # Start a new recording in the background, do not block
        self.recorder = am.Recorder(30, filename="audio.wav")
        self.recorder.Start()
        print("Recording started...")

    def stop_recording(self):
        """Stop the recording and save to a file."""
        if self.recorder:
            self.recorder.Stop()
            print("Recording stopped.")

    def fn_hold(self, key):
        if hasattr(key, "vk") and key.vk == 63:  # Adjust vk according to your keyboard
            if self.recorder:  # hold ended
                self.stop_recording()
                transcription = self.transcribe_audio(open("audio.wav", "rb")).strip()
                pyautogui.write(transcription)
                self.recorder = None
            else:  # hold started
                self.start_recording()

    def transcribe_audio(self, audio) -> str:
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
            response_format="text",
            language="en",
            prompt="The following is normal speech or technical speech from an engineer.",
        )
        return transcription

    def listen_for_keypress(self):
        with keyboard.Listener(
            on_release=self.fn_hold,
        ) as listener:
            listener.join()

