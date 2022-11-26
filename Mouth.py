from torch.package import PackageImporter
from nltk.tokenize import word_tokenize
from num2words import num2words
from sounddevice import play


def toValidStr(string: str) -> str:
    x = word_tokenize(string)

    s = ""
    for i in x:
        if i.isnumeric():
            s += num2words(int(i)) + ' '
        else:
            s += i + ' '

    return s


class Mouth(object):
    def __init__(self):
        self.speaker = "en_0"
        self.rate = 24000  # 4000,24000,48000
        self.model = PackageImporter("Mouth.pt").load_pickle("tts_models", "model")

    #        self.model.to("cuda")

    def say(self, reply: str):
        print("Eva: ", reply)
        if isinstance(reply, list):
            for i in reply:
                try:
                    i = toValidStr(i)
                    x = self.model.apply_tts(i, speaker=self.speaker, sample_rate=self.rate).numpy()
                    play(x, self.rate, blocking=True)
                except Exception:
                    print("Can't Say This", str(reply))
        else:
            try:
                reply = toValidStr(reply)
                x = self.model.apply_tts(reply, speaker=self.speaker, sample_rate=self.rate).numpy()
                play(x, self.rate)
            except Exception as e:
                print("Can't Say This", str(reply), "\n", e)
