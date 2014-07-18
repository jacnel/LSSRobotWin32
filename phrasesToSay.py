import time
import sys
import ctypes
import IPC
lib=ctypes.CDLL('FakeInputWin')
             
#message passed to this should be the correct key code


def speak(key):
    
    if(key in phrases):
        lib.typeInBaldi(phrases[key])
        time.sleep(delay[key])
        p.write('ready\n')       
    
def speakName(key, name):
    
    if key in phrases:
        lib.typeInBaldi(phrases[key] + " " + name)
        time.sleep(.3 + delay[key])
        p.write('ready\n')

def addPhrase(key, phrase, d):
    phrases[key] = phrase
    delay[key] = d
    

def onLineRead():
    message = p.line.strip().split()
    if message[0] in phrases:
        if len(message) > 1:
            #if message[1].isDigit():
            if int(message[1]) < len(names):
                p.write('not yet\n')
                speakName(message[0], names[int(message[1])])
            else:
                p.write('not yet\n')
                speak(message[0])
            #else:
            #    p.write('not yet\n')
            #    speak(message[0])
        else:
            p.write('not yet\n')
            speak(message[0])
                
phrases = {"right": "I am moving to your right"}
phrases["left"] = "I am moving to your left"
phrases["hello"] = "Hello there"
phrases["query"] = "What would you like me to do"
phrases["bye"] = "Good bye"
phrases["follow"] = "I am following you now"
phrases["stopFollow"] = "I am no longer following you"
phrases["lost"] = "I can not see you"

delay = {"right": 3}
delay["left"] = 3
delay["hello"] = 3
delay["query"] = 3
delay["bye"] = 2
delay["follow"] = 3
delay["stopFollow"] = 3.3
delay["lost"] = 2.5

names = ["Daniel", "Chris"]

p = IPC.process(True, "phrasesToSay")
p.setOnReadLine(onLineRead)
IPC.InitSync()

p.write('ready\n')

while True:
    p.tryReadLine()
    IPC.Sync()
