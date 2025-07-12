import asyncio
import os
from pynput import keyboard
from transcriber import WhisperAPITranscriber
from table_interface import ConsoleTable
from key_listener import create_keylistener
from dotenv import load_dotenv
from utils import manual_type


async def main():
    load_dotenv()

    transcriber = WhisperAPITranscriber.create()
    # Set initial language from environment variable if provided
    initial_language = os.getenv('UTTERTYPE_LANGUAGE', 'en')
    transcriber.set_language(initial_language)
    
    hotkey = create_keylistener(transcriber)

    keyboard.Listener(on_press=hotkey.press, on_release=hotkey.release).start()
    console_table = ConsoleTable()
    
    # Get language configuration for display
    primary_lang = os.getenv('UTTERTYPE_LANGUAGE', 'en')
    secondary_lang = os.getenv('UTTERTYPE_SECOND_LANGUAGE', 'ru')
    primary_key = os.getenv('UTTERTYPE_RECORD_HOTKEYS', '<ctrl>+<alt>+v')
    secondary_key = os.getenv('UTTERTYPE_RECORD_HOTKEYS_SECOND_LANGUAGE', '<ctrl>+<alt>+r')
    
    print(f"UtterType started with dual language support")
    print(f"Primary language ({primary_lang.upper()}): {primary_key}")
    print(f"Secondary language ({secondary_lang.upper()}): {secondary_key}")
    print("Hold the respective hotkey to record in the corresponding language")
    
    with console_table:
        async for transcription, audio_duration_ms in transcriber.get_transcriptions():
            current_lang = transcriber.get_language().upper()
            print(f"[{current_lang}] Transcribed: {transcription.strip()}")
            manual_type(transcription.strip())
            console_table.insert(
                f"[{current_lang}] {transcription}",
                round(0.0001 * audio_duration_ms / 1000, 6),
            )


if __name__ == "__main__":
    asyncio.run(main())
