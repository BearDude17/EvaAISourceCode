import json
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.models import Sequential, save_model, load_model
from tensorflow.keras.layers import Dense, Embedding, Bidirectional, LSTM, GRU
from tensorflow.keras.optimizers import Adam
from tensorflow import convert_to_tensor
from re import compile
from numpy import array
from os.path import isfile
from Tasks import EvaTasks


def isQuestion(command: str) -> bool:
    r = "((what|when|where|which|who|whom|whose|why|how)|(can|could|shall|should|will|would|may|might|must|" \
        "am|is|are|was|were|been|have|has|had|do|does|did|done))[A-Za-z ]*"

    x = compile(r)
    m = x.match(command)

    if m is None:
        return False

    print("The Question in '", command, "' --->", m.group())
    return True


class Analyzer(object):

    def __init__(self):

        self.replies = dict()
        self.classes = list()
        self.corpus = Tokenizer(oov_token="<blank>")
        self.sequneces = list()
        self.model = Sequential()
        self.maxlength = 0

        self.prepareData()
        if not isfile("Analyzer.h5"):
            x, y = self.prepareTrainingData()

            self.trainModel(x, y)
        else:
            self.model = load_model("Analyzer.h5")

    def prepareData(self):
        dataset = json.loads(open("replyiesDataset.json").read())["Dataset"]
        data = list()
        words = list()

        for d in dataset:
            self.replies[d["tag"]] = d["reply"]
            self.classes.append(d["tag"])
            words.extend(d["pattern"])
            data.append((d["pattern"], d["tag"]))

        print(words)

        self.corpus.fit_on_texts(words)

        print(self.corpus.word_index)

        sequances = [(self.corpus.texts_to_sequences(seqs), seqClass) for seqs, seqClass in data]
        sequances.append(([[1, ]], "Error"))

        lengths = list()

        for seq in sequances:
            print(seq)
            lengths.append(max([len(x) for x in seq[0]]))

        self.maxlength = max(lengths)

        for seq in sequances:
            self.sequneces.append((array(pad_sequences(seq[0], self.maxlength, value=1)), seq[1]))

    def prepareTrainingData(self) -> tuple:
        data, labels = list(), list()

        for seq in self.sequneces:
            for s in seq[0]:
                data.append(s)
                labels.append(self.classes.index(seq[1]))

        data = convert_to_tensor(data)
        labels = convert_to_tensor(labels)
        return data, labels

    def trainModel(self, data, labels):

        print(len(self.replies))

        self.model = Sequential([
            Embedding(len(self.corpus.word_index), 10000, input_length=len(data[0])),
            GRU(512, return_sequences=True),
            Bidirectional(LSTM(256)),
            Dense(len(self.replies), "softmax")
        ])

        loss = SparseCategoricalCrossentropy()
        optimizer = Adam(learning_rate=0.001)

        self.model.compile(optimizer, loss, metrics=['accuracy'])
        self.model.summary()

        self.model.fit(data, labels, epochs=30, verbose=2)

        save_model(self.model, "Analyzer.h5")

    def isSearchCommand(self, command) -> bool:
        if "what is " in command:
            return True
        elif "what do you know about" in command:
            return True
        elif "search for" in command:
            return True
        elif "search about" in command:
            return True
        elif "I want to know about" in command:
            return True
        elif "Tell me about" in command:
            return True
        elif "short version" in command:
            return True
        elif "long version" in command:
            return True

        return False

    def Analyze(self, message: str) -> tuple:

        if isQuestion(message) and "you" not in message:
            return EvaTasks.AnswerQuestion, ["I found that ", "", "After too much searching i found that", ""
                , "the answer is ", ""]

        x = self.corpus.texts_to_sequences([message])
        x = pad_sequences(x, self.maxlength, truncating='post', value=1)
        print(x)
        out = list(self.model.predict(x)[0])

        accuracy = max(out)

        out = out.index(accuracy)

        out = self.classes[out]
        print("Category: ", out, " ", accuracy * 100)

        if accuracy * 100 < 70:
            if self.isSearchCommand(message):
                return EvaTasks.Search, self.replies["Search"]

            return EvaTasks.Error, self.replies["Error"]
        else:
            if self.isSearchCommand(message):
                return EvaTasks.Search, self.replies["Search"]
            else:
                return EvaTasks[out], self.replies[out]
