# Master Control for the LILI Robot
# 20 June 2014

import iRobotCreate
import time
import IPC
import Queue
import string

# qGest is a Queue which holds commands for gestures sent from the Kinect monitor
#    these commands are pulled off the queue when all processes are ready
qGest = Queue.Queue()

# Queue to hold the follow commands to follow the user
qFollow = Queue.Queue()

#The program will continue to wait for commands to be received until quit = True
quit = False

#The robot will run a response to the gesture recorded in this variable.
gest = ""

#When readyTT is False, the TTS program is busy and we must wait.
# When readyTT is True, the TTS program can receive commands.
readyTT=False

#holds the time of completion of the most recent movement
lastMoveTime = time.time()

state = "waiting"

def follow():
    global state
    global readyTT
    global lastMoveTime
    if not state == "following":
        print "Following."
        readyTT = False
        sp.write("follow\n")
    state = "following"
    line = qFollow.get()
    list = string.split(line)
    if list[1] == "stop":
        print "Stopping."
        readyTT = False
        r.setvel(0,0)
        sp.write("stopFollow\n")
        state = "waiting"
        lastMoveTime = time.time()
        return
    a = float(list[1])
    b = float(list[2])
#    ts = float(list[3])
    #if ts < lastMoveTime:
    #    return
    distF = 2 #distance behind person
    
    if not a == 0:
        c = a - (distF/(1+(b/a)**2))**.5
        d = b - (b/a)*((distF/(1+(b/a)**2))**.5)
    else:
        c = 0 
        d = b - 1 
    
    r.goToGoal(c,d)
    lastMoveTime = time.time()

# Checks if phrasesToSay.py is ready to accept another input phrase
def checkReady():
    global readyTT
    #reads the output from the TTS program
    ready = sp.line.strip()
    if ready=="ready":
        readyTT=True

def KinectQueue():
    line = km.line.strip()
    if line[:line.find(' ')] == "follow":
        qFollow.put(line)
    else:
    #Gestures received from the Kinect Monitor will be added to the queue
        qGest.put(line)

def VocalQueue():
    global state
    line = vm.line.strip()
    if line == "follow":
        km.write('follow\n')
    if line == "stop":
        km.write('follow stop\n')
    else:
    #Gestures received from the Voice Monitor will be added to the queue
        qGest.put(line + ' ' + str(time.time()) + '\n')

# Search for gesture
def GestureResponse():
    global readyTT
    # if the TTS is busy, exit this loop
    if readyTT==False:
        return
    # when TTS is ready, pull the next gesture off of the queue
    line = qGest.get() #line should be "command timeStamp"
    gest = line[:line.find(' ')] #holds "command"
    timeStamp = float(line[line.find(' ')+1:]) #holds float version of timeStamp
    #exit if message was received during the last movement
    if not gest == 'Lily':
        if timeStamp < lastMoveTime or not state == "waiting":
            return
    if gest == "Lily":
        print "Yes?"
    if gest == "rightWave":
        waveRight()
    if gest == "leftWave":
        waveLeft()
    if gest == "quit":
        Exit()

# Execute response to registered gesture
def waveRight():
    global readyTT
    global lastMoveTime
    print "Right Wave Received."
    readyTT = False
    sp.write("right\n")
    print "Moving one meter to the right."
    r.moveTo(r.x,r.y+1,r.theta)
    lastMoveTime = time.time() #update lastMoveTime
    print "DONE"
    
def waveLeft():
    global readyTT
    global lastMoveTime
    print "Left Wave Received."
    readyTT = False
    sp.write("left\n")
    print "Moving one meter to the left."
    r.moveTo(r.x,r.y-1,r.theta)
    lastMoveTime = time.time() #update lastMoveTime
    print "DONE"
    
# Close connection
def Exit():
    global readyTT
    global quit
    print "Lily is going to sleep."
    readyTT = False
    sp.write("bye\n")
    quit = True
    time.sleep(4)
    r.delete()  


# How to search for a gesture
    #open communication to the kinect monitor
km = IPC.process(False, 'KinectMonitor.py')
    #when input from the kinect monitor is received,
        # add the input to the queue
km.setOnReadLine(KinectQueue)

# Lily's voice control
    #open communication to phrasesToSay
sp = IPC.process(False, 'phrasesToSay.py')
    #when input is received from phrasesToSay,
        #check if the TTS program is ready to receive input
sp.setOnReadLine(checkReady)

# Open Speech Recognition Control
vm = IPC.process(False, 'VoiceMonitor.py')
vm.setOnReadLine(VocalQueue)

# Initialize synchronization
IPC.InitSync()

# Open a serial connection to the create
r = iRobotCreate.iRobotCreate(0, 5, "COM4")
time.sleep(1)

# Execute start-up commands
# request input from the TTS
sp.tryReadLine()
readyTT = False
print "Lily is awake."
# command TTS
sp.write("hello\n")

#wait for the TTS to be ready
while readyTT == False:
    sp.tryReadLine()
readyTT = False
print "Lily is ready!"
#command TTS
sp.write("query\n")

#Waiting state: search for gestures from the kinect monitor
while quit == False: # The user has not asked to quit.
    vm.tryReadLine()  # receive input from the voice monitor
    km.tryReadLine()  # receive input from the kinect monitor
    sp.tryReadLine()  # receive input from the TTS
    
    if not qFollow.empty():
        follow()
    else:
        if state == "following":
            print "Stopping."
            readyTT = False
            r.setvel(0,0)
            sp.write("lost\n")
            state = "waiting"
            lastMoveTime = time.time()
            
# if there are items on the queue, try to respond
    if not qGest.empty():  
        GestureResponse()
    IPC.Sync()