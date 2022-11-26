from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model, save_model, Sequential
from tensorflow.keras.layers import Embedding, Dense, Bidirectional, LSTM
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
import numpy as np
from pickle import dump, load
from os.path import isfile


class Replyer(object):

    def __init__(self):
        self.tokenizer = Tokenizer(oov_token="<oov>")
        self.corpus = list()
        self.sentences = list()

        if isfile("Model.h5") and isfile("data.dat"):
            self.model = load_model("Model.h5")
            data = dict(load(open("data.dat",'rb')))
            self.tokenizer = data["Tokenizer"]
            self.corpus = data["Corpus"]
            self.sentences = data["Sequences"]
        else:
            self.updateData()

    def replyTo(self, stringToReply: str):

        result = ""
        last = ""
        z = ""
        while True:
            z = self.getRelativeWord(stringToReply + " " + result)

            if z == last:
                break

            result += z + " "
            last = z

        return result

    def getRelativeWord(self, stringSeq:str):
        max_seq_len = max([len(x) for x in self.sentences])
        seq = self.tokenizer.texts_to_sequences([stringSeq])[0]

        seq = np.array(pad_sequences([seq], maxlen=max_seq_len, padding="pre"))

        y = self.model.predict(seq)

        y = np.argmax(y)

        for word, index in self.corpus.items():
            if index == y:
                return word

        return ""

    def updateData(self):
        file = open("messages.txt", 'r')
        data = file.readlines()
        file.close()

        self.tokenizer.fit_on_texts(data)
        self.corpus = self.tokenizer.word_index

        for line in data:
            tokenList = self.tokenizer.texts_to_sequences([line])[0]

            for i in range(1, len(tokenList)):
                self.sentences.append(tokenList[:i + 1])

        max_seq_len = max([len(x) for x in self.sentences])

        self.sentences = np.array(pad_sequences(self.sentences, maxlen=max_seq_len, padding="pre"))

        features = self.sentences[:, :-1]
        labels = self.sentences[:, -1]

        labels = to_categorical(labels, len(self.corpus) + 1)

        print(features)
        print(labels)

        self.model = Sequential([
            Embedding(len(self.corpus) + 1, 240, input_length=max_seq_len - 1),
            Bidirectional(LSTM(150)),
            Dense(len(self.corpus) + 1, "softmax")
        ])

        optimizer = Adam(learning_rate=0.01)
        loss = CategoricalCrossentropy()

        self.model.compile(optimizer, loss, metrics=["accuracy"])
        self.model.summary()

        print("Corpus : ", self.corpus)
        print("Total Words : ", len(self.corpus) + 1)
        print("Features Length : ", len(features))
        print("Labels Length : ", len(labels))
        print("Features Shape : ", len(features[0]))
        print("Input length : ", max_seq_len)
        print("Features : ", features)
        print("Labels : ", labels)

        self.model.fit(features, labels, epochs=100, verbose=1)

        data = {"Tokenizer": self.tokenizer, "Corpus": self.corpus,
                "Sequences": self.sentences}

        save_model(self.model, "Model.h5")

        dump(data, open("data.dat", 'wb'))
