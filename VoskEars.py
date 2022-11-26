from vosk import Model, KaldiRecognizer
from pyaudio import PyAudio, paInt16


class Ears(object):

    def __init__(self):
        self.recognizer = KaldiRecognizer(Model(r"EarsModel"), 16000)
        self.mic = PyAudio().open(format=paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192, )
        self.mic.start_stream()

    def getCommand(self):
        data = self.mic.read(4096, False)
        if self.recognizer.AcceptWaveform(data):
            text = self.recognizer.Result()
            return True, text[14:-3]
        else:
            return False, "Nothing to read..."
