# Master Control for the Lily Robot
# 20 June 2014

import iRobotCreate
import time
import IPC
import Queue

q = Queue.Queue()
quit = 0
wave = ""
readyTT=False

# Checks if phrasesToSay.py is ready to accept another input phrase
def checkReady():
    global readyTT
    ready = sp.line.strip()
    if ready=="ready":
        readyTT=True

def KinectQueue():
    q.put(km.line.strip())

# Search for gesture
def GestureResponse():
    global readyTT
    if readyTT==False:
        return
    wave = q.get()
    if wave == "rightWave":
        waveRight()
    if wave == "leftWave":
        waveLeft()
    if wave == "quit":
        Exit()

# Execute response to registered gesture
def waveRight():
    global readyTT
    print "Right Wave Received."
    readyTT = False
    sp.write("right\n")
    print "Moving one meter."
    r.moveTo(r.x,r.y+1,r.theta)
    
def waveLeft():
    global readyTT
    print "Left Wave Received."
    readyTT = False
    sp.write("left\n")
    print "Moving one meter."
    r.moveTo(r.x,r.y-1,r.theta)
      
# Close connection
def Exit():
    global readyTT
    global quit
    print "Lily is going to sleep."
    readyTT = False
    sp.write("bye\n")
    quit = 1
    time.sleep(4)
    r.delete()  


# How to search for a gesture
km = IPC.process(False, 'KinectMonitor.py')
km.setOnReadLine(KinectQueue)

# Lily's voice control
sp = IPC.process(False, 'phrasesToSay.py')
sp.setOnReadLine(checkReady)

# Initial 
IPC.InitSync()

# Connect to the create
r = iRobotCreate.iRobotCreate(0, 5, "COM4")
time.sleep(1)

sp.tryReadLine()
readyTT = False
print "Lily is awake."
sp.write("hello\n")

while readyTT == False:
    sp.tryReadLine()
readyTT = False
print "Lily is ready!"
sp.write("query\n")

while quit == 0:
    km.tryReadLine()
    sp.tryReadLine()
    if not q.empty():
        GestureResponse()
    IPC.Sync()