import speech_recognition as sr


class SREars(object):

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def getCommand(self):

        try:
            with sr.Microphone() as mic:
                print("listening...")
                voice = self.recognizer.listen(mic)
                command = self.recognizer.recognize_sphinx(voice)

                return True, command
        except:
            return False, ""
