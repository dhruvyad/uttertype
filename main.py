import threading
from transcriber import AudioTranscriber

if __name__ == "__main__":
    transcriber = AudioTranscriber()
    t = threading.Thread(target=transcriber.listen_for_keypress)
    t.start()