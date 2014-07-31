import time
import sys
import ctypes
import IPC
lib=ctypes.CDLL('FakeInputWin')

#FakeInputWin simulates input into the BaldiSync window

             
#should be a valid key code
def speak(key):
    
    if(key in phrases):
        lib.typeInBaldi(phrases[key]) #pass the phrase for BaldiSync to say
        time.sleep(delay[key]) #sleeps so that a new phrase isn't started before the other is finished
        p.write('ready\n')  #tell master controller that it is ready for another phrase
              
#should be a valid key code, speaks the name after the phrase   
def speakName(key, name):
    
    if key in phrases:
        lib.typeInBaldi(phrases[key] + " " + name)
        time.sleep(.3 + delay[key])
        p.write('ready\n')

#method for adding a new key-phrase pair witha given delay
def addPhrase(key, phrase, d):
    phrases[key] = phrase
    delay[key] = d
    
#add a new name
def addPerson(name):
    names.append(name)

def onLineRead():
    message = p.line.strip().split()
    if message[0] in phrases and message[0] in delay:
        if len(message) > 1:
            if int(message[1]) < len(names):  #means a valid person ID was passed as well as a key
                p.write('not yet\n')  #tell master controller that a phrase is still being spoken
                speakName(message[0], names[int(message[1])])
            else: #person ID was invalid for phrasesToSay
                p.write('not yet\n')
                speak(message[0]) 
        else:  #no person ID given
            p.write('not yet\n')
            speak(message[0])
    
#keys for phrases and delay should all match
    
#set of initial phrases                
phrases = {"right": "I am moving to your right"}
phrases["left"] = "I am moving to your left"
phrases["hello"] = "Hello there"
phrases["query"] = "What would you like me to do"
phrases["bye"] = "Good bye"
phrases["follow"] = "I am following you now"
phrases["stopFollow"] = "I am no longer following you"
phrases["lost"] = "I can not see you"
phrases["unrecognized"] = "I am sorry. I do not know you"
phrases["turnAround"] = "I am turning"

#set of initial delays
delay = {"right": 3}
delay["left"] = 3
delay["hello"] = 3
delay["query"] = 3
delay["bye"] = 2
delay["follow"] = 3
delay["stopFollow"] = 3.3
delay["lost"] = 2.5
delay["unrecognized"] = 4
delay["turnAround"] = 3

#set of initial names
names = ["Daniel", "Chris", "Cassie"]

#initial setup for interprocess communication
p = IPC.process(True, "phrasesToSay")
p.setOnReadLine(onLineRead)
IPC.InitSync()

#tell master controller that it is ready to speak
p.write('ready\n')

#main loop to run and communicate with master controller
while True:
    p.tryReadLine()
    IPC.Sync()
