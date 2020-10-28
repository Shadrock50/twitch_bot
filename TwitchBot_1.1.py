import socket
import pyautogui
import threading
import time
import re
from gtts import gTTS
from playsound import playsound
import winsound
import os

####Think about recombining threads. Run slower, less CPU usage####

SERVER = "irc.twitch.tv"
PORT = 6667
OAuth = ""
USER = ""
CHANNEL = ""
OWNER = ""
message = ""
user = ""
language = 'en'
bitAmount = '0'
#commands required to make a correct irc connection to twitch
irc = socket.socket()
irc.connect((SERVER, PORT))
irc.send((  "PASS " + OAuth + "\n" +
            "NICK " + USER + "\n" + 
            "JOIN #" + CHANNEL + "\n").encode())

#Controls all commands that play sound (No video)
#create play TTS function - Done
def soundControl():

    def playTTS(messageTemp):
        testObj = gTTS(text=messageTemp, lang=language, slow=False)
        testObj.save("texttospeech.mp3")
        playsound("texttospeech.mp3")
        os.remove("texttospeech.mp3")

    global message
    global user
    rickRollLimiter = False
    file1 = open('bannedWordList.txt', 'r')
    #file2 = open('vipList.txt', 'r')
    bannedWords = file1.readlines()
    #vip = file2.readlines()

    #Runs so long as the script runs
    while True:
        #finds the !welcome in an incoming message, splits it into pieces to send a message
        if "!welcome" in message.lower():
            try:
                newMessage = message.split(" " , 1)
                messageTemp = "PRIVMSG #" + CHANNEL + " :" + "Welcome " + str(newMessage[1]) + "! We hope you have fun here!"
                message = ""
                user = ""
                irc.send((messageTemp + "\n").encode())
                playsound('celebrate.mp3')
            except Exception:
                pass

        #plays a simple sound
        elif "!cringe" in message.lower():
            message = ""
            user = ""
            playsound('cringe.wav')

        #Splits the incoming message and plays a sound file, generates a TTS sound file and plays it afterwards
        elif "!rebuke" in message.lower():
            try: 
                newMessage = message.split(" " , 1)
                messageTemp = newMessage[1]
                message = ""
                user = ""
                testObj = gTTS(text=messageTemp, lang=language, slow=False)
                testObj.save("texttospeech.mp3")
                playsound("rebuke.wav")
                playsound("texttospeech.mp3")
                os.remove("texttospeech.mp3")
            except Exception:
                pass

        #plays a simple sound
        elif "!vandito" in message.lower():
            message = ""
            user = ""
            playsound('El_vandito.wav')

        #Change theultimatetroll to you selection. Remember to update hints.
        #Plays a sound, but limited to only play once per running of the code 
        elif "!theultimatetroll" in message.lower():
            message = ""
            user = ""
            if rickRollLimiter == False:
                rickRollLimiter = True
                playsound("rickroll.mp3")
            else:
                pass

        #reads a text file to check for any banned words.
        #If no banned words are found, generates TTS sound file and plays. 
        #Talk restricted to vip users only

        #FIX BUG#
        elif "!talk" in message.lower() and len(message) <= 500:
            badWordCount = 0
            #vipUser = False
            try: 
                newMessage = message.split(" " , 1)
                messageTemp = newMessage[1]
                message = ""
                user = ""
            except Exception:
                pass

            # for i in bannedWords:
            #    testWord = i.rstrip("\n")
            #    if testWord in messageTemp.lower():
            #        badWordCount = badWordCount + 1

            # for i in vip:
            #     testWord = i.rstrip("\n")
            #     if testWord in message.lower():
            #         vipUser = True

            # if badWordCount > 0: #and vipUser != False:
            #    pass
            # else:
            playTTS(messageTemp)
            #vipUser = False

        #plays a simple sound file
        elif "!david" in message.lower():
            message = ""
            user = ""
            playsound("david.wav")

        #Test for restricting !talk to cheering.
        elif (re.search(r'cheer[0-9]+', message.lower())) is not None:
            
            try: 
                cheerMessage = re.match(r'cheer[0-9]+', message.lower())
                bitAmount = str(cheerMessage.group())[5:]
                print(bitAmount)

                newMessage = message.split(" " , 1)
                messageTemp = newMessage[1]
                message = ""
                user = ""

                badWordCount = 0
                for i in bannedWords:
                    testWord = i.rstrip("\n")
                    if testWord in message.lower():
                        badWordCount = badWordCount + 1

                if badWordCount > 0:
                    pass
                else:
                    playTTS(messageTemp)
            except Exception:
                pass


        #if nothing found in message, pass and continue the loop. 
        else:
            pass
    

#thread that controls elements with timing based mechanics
def timer():
    global message
    global user

    #timing variables
    seconds = int(900)
    hintSeconds = 0

    while True:

        #one timer needs to count up, the other down. 
        seconds = seconds - 1
        hintSeconds = hintSeconds + 1
        #hintCounter determines how long before getting a new hint
        hintCounter = hintSeconds/1800

        #sends a message everytime seconds == 0, resets clock
        if seconds == 0:
            messageTemp = "PRIVMSG #" + CHANNEL + " :" + "Five Dollar Federation is a gaming group all about finding great gaming experiences for under $5. We play one game a month and then talk about it. Join our discord for more info! https://discord.gg/RtTNpwy"
            irc.send((messageTemp + "\n").encode())
            seconds = 900

        #sleeps this thread for one second to create the timer.   
        time.sleep(1)

        ####YOUR HINTS GO HERE####
        #hint system gives different messages dependant on when the command is used relevant to when the program was launched. 
        if "!hint" in message.lower():
            if hintSeconds > 0 and hintCounter < 1:
                messageTemp = "PRIVMSG #" + CHANNEL + " :" + "***PUT HINT 1 HERE MATT***"
                irc.send((messageTemp + "\n").encode())
                message = ""
                user = ""

            elif hintCounter >= 1 and hintCounter <= 2:
                messageTemp = "PRIVMSG #" + CHANNEL + " :" + "***PUT HINT 2 HERE MATT***"
                irc.send((messageTemp + "\n").encode())
                message = ""
                user = ""

            elif hintCounter >= 2:
                messageTemp = "PRIVMSG #" + CHANNEL + " :" + "***PUT HINT 3 HERE MATT***"
                irc.send((messageTemp + "\n").encode())
                message = ""
                user = ""

#thread that controls all text message sending
def textControl():
    global message
    global user
    global listenCount 
    listenCount = 0
    global cowardCount 
    cowardCount = 0
    global headshotCount 
    headshotCount = 0

    def headShotSwitcher(x):
        return {
            1: "st",
            2: "nd",
            3: "rd"
        }.get(x, "th")

    while True:
        if "!commands" in message.lower():
            messageTemp = "PRIVMSG #" + CHANNEL + " :" + "This bot has many sick commands. They are: !listen, !welcome, !deals, !hint, !talk, !david, !vandito, !rebuke, !cringe, !coward and !headshot."
            message = ""
            user = ""
            irc.send((messageTemp + "\n").encode())

        elif "!listen" in message.lower():
            listenCount = listenCount + 1
            messageTemp = "PRIVMSG #" + CHANNEL + " :" + "The streamer has overused listen " + str(listenCount) + " times."
            message = ""
            user = ""
            irc.send((messageTemp + "\n").encode())

        elif "!coward" in message.lower():
            cowardCount = cowardCount + 1
            messageTemp = "PRIVMSG #" + CHANNEL + " :" + "The F$F Streamer has been a coward " + str(cowardCount) + " times this stream. Stop it!"
            message = ""
            user = ""
            irc.send((messageTemp + "\n").encode())

        elif "!headshot" in message.lower():
            #use switch statement later - switch = st,nd,rd,th. Run faster - Done
            prefVar = ""
            try:
                newNumber = message.split(" " , 1)
                if newNumber[1].isnumeric() and int(newNumber[1]) > 1:
                    headshotCount = headshotCount + int(newNumber[1])
                else:
                    headshotCount = headshotCount + 1 
            except Exception:
                headshotCount = headshotCount + 1 

            prefVar = headShotSwitcher(headshotCount)

            messageTemp = "PRIVMSG #" + CHANNEL + " :" + "Wicked!! That was your " + str(headshotCount) + prefVar + " sick headshot!"

            message = ""
            user = ""
            irc.send((messageTemp + "\n").encode())

        elif "!deals" in message.lower():
            message = ""
            user = ""
            messageTemp = "PRIVMSG #" + CHANNEL + " :" + "See the deals that will make you scream: https://docs.google.com/spreadsheets/d/15AYri9jK8R4VmkX7ZN4K7pmPztP7EMGq8yeh_zKVhZQ/edit?usp=sharing"
            irc.send((messageTemp + "\n").encode())
        
        else:
            pass
    

        
#thread that controls connecting to twitch and pulling messages from Twitch API
def twitch():
    #sends initial irc call, and decodes initial messages
    def joinchat():
        Loading = True
        while Loading:
            readbuffer_join = irc.recv(1024)
            readbuffer_join = readbuffer_join.decode()
            for line in readbuffer_join.split("\n")[0:-1]:
                print(line)
                Loading = loadingComplete(line)
    #reads for end of connection message and alerts the user of connection. 
    def loadingComplete(line):
        if ("End of /NAMES list" in line):
            print("Bot has joined " + CHANNEL + "'s Channel!")
            sendMessage(irc, "This is a test bot. Because Matt is a heathen.")
            return False
        else:
            return True

    #sends any message that is needed in this thread
    def sendMessage(irc, message):
        messageTemp = "PRIVMSG #" + CHANNEL + " :" + message
        irc.send((messageTemp + "\n").encode())

    #pulls the user from the decoded irc.recv
    #setter for the user variable
    def getUser(line):
        global user
        try:
            separate = line.split(":", 2)
            user = separate[1].split("!" , 1)[0]
        except:
            user = ""

        return user

    #pulls the message from the decode irc.recv
    #setter for the message variable.
    def getMessage(line):
        global message
        try:
            message = (line.split(":",2))[2]
        except:
            message = ""
        
        return message

    #checks whether the user is twitch or a user.
    def CheckUser(line):
        if "PRIVMSG" in line:
            return False
        else:
            return True

    joinchat()

    #checks if the message coming in is from twitch
    #if from titch, sends a pong message to twitch to stay connected
    #if from a user, print the message and use setters for later loops. 
    while True:
        try:
            readbuffer = irc.recv(1024).decode()
        except:
            readbuffer = ""
        for line in readbuffer.split("\r\n"):
            if line == "":
                continue
            elif "PING" in line and CheckUser(line):
                msg = "PONG tmi.twitch.tv\r\n".encode()
                irc.send(msg)
                continue
            else:
                user = getUser(line)
                message = getMessage(line)
                print(user + ": " + message)

#main function starts the threads and their loops
if __name__ == '__main__':
    t1 = threading.Thread(target = twitch)
    t1.start()
    t2 = threading.Thread(target = textControl)
    t2.start()
    t3 = threading.Thread(target = timer)
    t3.start()
    t4 = threading.Thread(target = soundControl)
    t4.start()
        
