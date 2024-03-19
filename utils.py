import sys
import time
import pyperclip
import pyautogui
from typing import List
from pynput import keyboard

keyboard_writer = keyboard.Controller()

def clipboard_type(text):
    """
    Instead of typing each key, just copy to clipboard and paste
    Probably won't work for some fields that don't accept pasting
    """
    original_clipboard_content = pyperclip.paste()
    pyperclip.copy(text)
    print("Pasting:", text)
    pyautogui.hotkey('command' if sys.platform == 'darwin' else 'ctrl', 'v')
    pyperclip.copy(original_clipboard_content)

def manual_type(text: str, delay: float = 0.0042):
    """
    Type each key manually with delay to prevent overwhelming the target
    Copied from keyboard.Controller.type() to add delay
    """
    for i, character in enumerate(text):
        key = keyboard._CONTROL_CODES.get(character, character)
        try:
            keyboard_writer.press(key)
            keyboard_writer.release(key)
            time.sleep(delay)
        except (ValueError, keyboard_writer.InvalidKeyException):
            raise keyboard_writer.InvalidCharacterException(i, character)

def transcription_concat(transcriptions: List[str]) -> str:
    return " ".join([_t.strip() for _t in transcriptions])  # Simple concat for now

