import asyncio
from pynput import keyboard
from transcriber import WhisperAPITranscriber
from table_interface import ConsoleTable
from key_listener import create_keylistener
from dotenv import load_dotenv
from utils import manual_type


async def main():
    load_dotenv()

    transcriber = WhisperAPITranscriber.create()
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


if __name__ == "__main__":
    asyncio.run(main())
