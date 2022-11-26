import Tasks
from Analyzer import Analyzer
from VoskEars import Ears
from Mouth import Mouth
from CommandApplier import CommandApplier
from os import environ
from time import sleep

environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

isRunning = True
isListening = False

ears = Ears()
analyzer = Analyzer()
applier = CommandApplier()
mouth = Mouth()

while isRunning:

    haveText,text = ears.getCommand()

#    haveText, text = True, "eva, What time is it"

    if text == "the":
        continue

    if "eva" in text:
        isListening = True

    if haveText and text and isListening:
        print("You : ",text)
        command,replies = analyzer.Analyze(text)

        isListening,reply = applier.applyCommand(command,text,replies)
        mouth.say(reply)
        if command is Tasks.EvaTasks.Close:
            sleep(5)
            isRunning = False
        elif command is Tasks.EvaTasks.Retrain:
            analyzer = Analyzer()
            mouth.say("Done training and ready again")
