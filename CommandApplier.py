import os

from Tasks import EvaTasks
from random import randint
from wikipedia import summary
from nltk.tokenize import sent_tokenize, word_tokenize
from os.path import isfile
import pywhatkit as whkit
from pickle import dump, load
from tkinter import Tk, simpledialog, Label, StringVar, OptionMenu, Button
import datetime as dt


def getInput(title: str, message: str, type=None):
    window = Tk()
    window.withdraw()

    if type == "float":
        result = simpledialog.askfloat(title, message)
    elif type == "int":
        result = simpledialog.askinteger(title, message)
    else:
        result = simpledialog.askstring(title, message)

    return result


def getFromMultiple(title: str, message: str, options: list) -> int:
    x = [i for i in options]
    x.insert(0, "None")

    window = Tk()
    window.title(title)

    Label(window, text=message).pack(pady=10, padx=20)
    value = StringVar()
    value.set(str(x[0]))

    OptionMenu(window, value, *x).pack(pady=5)
    Button(window, text="Done", command=window.destroy).pack(pady=10)

    window.mainloop()
    if value.get() == "None":
        return -1

    return options.index(value.get())


class Contact(object):
    def __init__(self, name: str, phone: str):
        self.name = name
        self.phone = phone

    def isEmpty(self) -> bool:
        return not bool(self.phone)


class CommandApplier(object):
    def __init__(self):
        self.subject = ""
        self.file = open('log.txt', 'a')
        self.file.writelines('--------------------Starting Session At: ' + str(dt.datetime.now().strftime('%c')) + "\n")

        self.activeContact = Contact("None", "")
        self.contacts = list()
        self.getContacts()

    def getContacts(self):

        if isfile('Contacts.dat'):
            file = open("Contacts.dat", 'rb')
            self.contacts = load(file)
            file.close()

    def saveContact(self, contact: Contact):

        if contact.name in [x.name for x in self.contacts]:
            raise Exception(contact.name + " already inserted")

        self.contacts.append(contact)

        file = open("Contacts.dat", 'wb')
        dump(self.contacts, file)
        file.close()

    def getSubject(self, command: str):
        self.subject = command.replace("what is ", "")
        self.subject = self.subject.replace("what do you know about ", "")
        self.subject = self.subject.replace("search about ", "")
        self.subject = self.subject.replace("search for ", "")
        self.subject = self.subject.replace("i want to know about ", "")
        self.subject = self.subject.replace("tell me about", "")
        self.subject = self.subject.replace("give me a short version about ", "")
        self.subject = self.subject.replace("short version about ", "")
        self.subject = self.subject.replace("long version about ", "")
        self.subject = self.subject.replace("give me a long version about ", "")
        self.subject = self.subject.replace("eva ", "")

    #        self.subject = self.subject.replace("evangeline", "")

    def applyCommand(self, commandCategory: EvaTasks, command: str, replies: list):

        self.file.writelines("You: " + str(command) + "\n")

        reply = replies[randint(0, len(replies) - 1)]

        if commandCategory is EvaTasks.Awake:
            self.file.writelines('Eva: ' + str(reply) + "\n")
            return True, reply
        elif commandCategory is EvaTasks.Name:
            self.file.writelines('Eva: ' + str(reply) + "\n")
            return True, reply
        elif commandCategory is EvaTasks.Error:
            self.file.writelines('Eva: ' + str(reply) + "\n")
            return True, reply
        elif commandCategory is EvaTasks.Bye:
            self.file.writelines('Eva: ' + str(reply) + "\n")
            self.subject = ""
            return False, reply
        elif commandCategory is EvaTasks.Doing:
            self.file.writelines('Eva: ' + str(reply) + "\n")
            return True, reply
        elif commandCategory is EvaTasks.Greeting:
            self.file.writelines('Eva: ' + str(reply) + "\n")
            return True, reply
        elif commandCategory is EvaTasks.Presenting:
            self.file.writelines('Eva: ' + str(reply) + "\n")
            return True, reply
        elif commandCategory is EvaTasks.Time:

            reply = reply.format(x=dt.datetime.now().strftime('%X'))

            reply = reply.replace(':', ' ')

            self.file.writelines('Eva: ' + str(reply) + "\n")
            return True, reply
        elif commandCategory is EvaTasks.Day:
            if "full" in command:
                reply = reply.format(x=dt.datetime.now().strftime("%A %d %B %Y"))
            else:
                reply = reply.format(x=dt.datetime.now().strftime('%A'))

            self.file.writelines('Eva: ' + str(reply) + "\n")
            return True, reply
        elif commandCategory is EvaTasks.Close:
            self.file.writelines('Eva: ' + str(reply) + "\n")
            return False, reply
        elif commandCategory is EvaTasks.Retrain:

            if os.path.isfile("Analyzer.h5"):
                os.remove("Analyzer.h5")
            return False, reply
        elif commandCategory is EvaTasks.Search:
            self.getSubject(command)

            try:
                data = summary(self.subject)
            except:
                self.subject = ""
                self.file.writelines("Eva: I can't find anything about {x}\n".format(x=self.subject))
                return True, "I can't find anything about {x}\n".format(x=self.subject)

            data = sent_tokenize(data)

            try:
                if "short" in command:
                    reply = reply.format(x=data[0])
                    self.file.writelines('Eva: ' + reply + "\n")
                    return True, reply
                elif "long" in command:
                    self.file.writelines('Eva: ' + str(data) + "\n")
                    return True, data
                else:
                    self.file.writelines('Eva: ' + str(data[0:1]) + "\n")
                    return True, data[0:1]
            except:
                print(data)
                self.file.writelines("Sorry,Error Happened\n")
                return True, "Sorry,Can't Store this in log but here is what i found." + str(data[0:1])

        elif commandCategory is EvaTasks.DiscussSubject:

            if not self.subject:
                self.file.writelines("Eva: We have not discussed anything yet\n")
                return True, "We have not discussed anything yet"

            data = summary(self.subject)
            data = sent_tokenize(data)

            try:
                if "short" in command:
                    reply = reply.format(x=data[0])
                    self.file.writelines('Eva: ' + reply + "\n")
                    return True, reply
                elif "long" in command:
                    self.file.writelines('Eva: ' + str(data) + "\n")
                    return True, data
                else:
                    self.file.writelines('Eva: ' + str(data[0:1]) + "\n")
                    return True, data[0:1]
            except:
                self.file.writelines('Eva: ' + "Sorry,Error Happened\n")
                return True, "Sorry,Can't Store this in log but here is what i found." + str(data[0:1])

        elif commandCategory is EvaTasks.SavingContact:
            name = ""
            try:
                name = getInput("Contact Name", "What is this contact's name?\n"
                                                "Make sure it is something pronounceable for me to be able to identify "
                                                "him when you need :)")

                phone = getInput("Contact Number", "What is this contact's number?\n"
                                                   "Make sure it is valid,Ex:+201xxxxxxxxx")

                if not (name and phone):
                    self.file.writelines('Eva: ' "You have not inserted the name and the phone\n")
                    return True, "You have not inserted the name and the phone"

                self.saveContact(Contact(name, phone))

                self.file.writelines('Eva: ' + reply + ". \n " + str(name) + " is Saved\n")
                return True, reply + ". \n " + str(name) + " is Saved"
            except Exception as e:
                self.file.writelines('Eva: ' + "Can't save " + str(name) + ".\n" + str(e) + "\n")

                return True, "Can't save " + str(name) + "\n" + str(e)

        elif commandCategory is EvaTasks.ListContacts:

            contacts = [x.name for x in self.contacts]
            x = getFromMultiple("Your Contacts", "Choose one to make him the active contact for messaging", contacts)

            if x == -1:
                self.file.writelines("Eva: " + "There is no activated contact\n")
                return True, "There is no activated contact"

            self.activeContact = self.contacts[x]

            self.file.writelines('Eva: ' + reply.format(x=contacts[x]) + "\n")
            return True, reply.format(x=contacts[x])

        elif commandCategory is EvaTasks.ActivateContact:
            for contact in self.contacts:
                if contact.name.lower() in command:
                    self.activeContact = contact
                    self.file.writelines('Eva: ' + reply.format(x=contact.name) + "\n")
                    return True, reply.format(x=contact.name)

            command = command.replace("activate", "")
            command = command.replace("get", "")
            command = command.replace("ready to text", "")
            self.file.writelines('Eva: ' + "No contact called " + str(command) + "\n")
            return True, "No contact called " + command

        elif commandCategory is EvaTasks.WhatsUpPersonalMessage:
            if self.activeContact.isEmpty():
                self.file.writelines("Eva: " + "There is no active contact")
                return True, "There is no active contact"

            try:
                message = getInput("Message for " + self.activeContact.name, "Write your what's up message")

                whkit.sendwhatmsg_instantly(self.activeContact.name, message)
                self.file.writelines("Eva: " + reply.format(x=self.activeContact.name))
                return True, reply.format(x=self.activeContact.name)

            except Exception as e:
                self.file.writelines("Eva: " + "Can't send message for " + self.activeContact.name + ".\n" + str(e))
                return True, "Can't send message for " + self.activeContact.name + ".\n" + str(e)

        elif commandCategory is EvaTasks.Google:
            for word in word_tokenize("Google On Google,Search for On Browser, Search for Search on browser for "
                                      "search on google now for "):

                if word.lower() in command:
                    command = command.replace(word, "")

            try:
                whkit.search(command)
                self.file.writelines('Eva: ' + reply + "\n")
                return True, reply
            except Exception as e:
                self.file.writelines('Eva: ' + "Can't google " + command + ".\n" + str(e) + "\n")
                return True, "Can't google " + command + ".\n" + str(e)

        elif commandCategory is EvaTasks.YouTube:
            for word in word_tokenize("Play Youtube Play Video about"):

                if word.lower() in command:
                    command = command.replace(word, "")

            try:
                whkit.playonyt(command)
                self.file.writelines('Eva: ' + reply + "\n")
                return True, reply
            except Exception as e:
                self.file.writelines('Eva: ' + "Can't play " + command + ".\n" + str(e) + "\n")
                return True, "Can't play " + command + ".\n" + str(e)

        elif commandCategory is EvaTasks.AnswerQuestion:
            try:
                command = command.replace("eva", "")
                command = command.replace("evangeline", "")

                data = whkit.info(command)
                return True, data
            except Exception as e:
                self.file.writelines("Eva: " + "Can't answer " + command + ".\n" + str(e))
                return True, "Can't answer " + command + ".\n" + str(e)
