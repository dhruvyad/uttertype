import threading
from transcriber import AudioTranscriber
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    transcriber = AudioTranscriber()
    t = threading.Thread(target=transcriber.listen_for_keypress)
    t.start()