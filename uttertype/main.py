from dotenv import load_dotenv
load_dotenv()  # Load environment variables up front

import asyncio
import os
from pynput import keyboard
from uttertype.transcriber import WhisperAPITranscriber, GeminiTranscriber
from uttertype.table_interface import ConsoleTable
from uttertype.key_listener import create_keylistener
from uttertype.utils import manual_type

async def main():
    # Choose transcriber based on environment variable
    transcriber_provider = os.getenv('UTTERTYPE_PROVIDER', 'openai').lower()
    
    if transcriber_provider == 'google':
        transcriber = GeminiTranscriber.create()
    elif transcriber_provider == 'openai':
        transcriber = WhisperAPITranscriber.create()
    else:
        raise ValueError(f'Invalid transcriber provider: {transcriber_provider}')

    hotkey = create_keylistener(transcriber)

    keyboard.Listener(on_press=hotkey.press, on_release=hotkey.release).start()
    console_table = ConsoleTable()
    with console_table:
        async for transcription, audio_duration_ms in transcriber.get_transcriptions():
            manual_type(transcription.strip())
            console_table.insert(
                transcription,
                round(0.0001 * audio_duration_ms / 1000, 6),
            )


def run_app():
    """Entry point for the uttertype application when installed via pip/uv"""
    asyncio.run(main())


if __name__ == "__main__":
    run_app()
