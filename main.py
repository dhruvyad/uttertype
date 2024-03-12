import librosa
import asyncio
from transcriber import AudioTranscriber
from table_interface import ConsoleTable
from dotenv import load_dotenv
from pynput import keyboard


async def main():
    load_dotenv()
    transcriber = AudioTranscriber()
    console_table = ConsoleTable()
    keyboard_writer = keyboard.Controller()
    transcriber.listen_for_keypress()
    with console_table as table:
        async for transcription in transcriber.get_transcriptions():
            keyboard_writer.type(transcription)
            console_table.insert(
                transcription,
                round(0.0001 * librosa.get_duration(path="audio.wav"), 6),
            )


if __name__ == "__main__":
    asyncio.run(main())
