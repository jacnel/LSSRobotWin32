import time
import sys
import ctypes
import IPC
lib=ctypes.CDLL('FakeInputWin')
             
#message passed to this should be the correct key code


def speak(key):
    #time.sleep(3) #3 second delay
    if(key in phrases):
        lib.typeInBaldi(phrases[key])
        time.sleep(delay[key])
        p.write('ready\n')       
    
def addPhrase(key, phrase, d):
    phrases[key] = phrase
    delay[key] = d
    

def onLineRead():
    message = p.line.strip()
    if message in phrases:
        p.write('not yet\n')
        speak(message)
                
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

p = IPC.process(True, "phrasesToSay")
p.setOnReadLine(onLineRead)
IPC.InitSync()

p.write('ready\n')

while True:
    p.tryReadLine()
    IPC.Sync()
    #read message
    #message = sys.stdin.readline().strip()
    #action
    #if message in phrases:
    #    print 'not yet'
    #    sys.stdout.flush()
    #    speak(message)
    
    #sleep to end of time
    #time.sleep(1)