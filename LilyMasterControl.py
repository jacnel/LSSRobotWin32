# Master Control for the LILI Robot
# 28 June 2014

import iRobotCreate
import time
import IPC
import Queue
import string
import sys
import numpy as np

# qGest is a Queue which holds commands for gestures sent from the Kinect monitor
#    these commands are pulled off the queue when all processes are ready
qGest = Queue.Queue()

# Queue to hold the follow commands to follow the user
qFollow = Queue.Queue()

#Queue to hold the commands regarding face recognition
qFace = Queue.Queue()

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
voiceFollow = False #true if the follow command was received by voice and should follow regardless of recognition

#holds dictionary of recognized skeletonIDs and their personID
skeletonPersonIDs = {-1:-1}

#handles values from the qFollow queue
def follow():
    global state
    global readyTT
    global lastMoveTime
    global qFollow
    global voiceFollow
    line = qFollow.get()
    list = string.split(line)
    if not state == "following": #LILI just started following user
        print "Following."
        readyTT = False
        mess = "follow "
        if len(list) > 4: #"follow xCoord yCoord skeletonID timeStamp"
            if int(list[3]) in skeletonPersonIDs.keys() and skeletonPersonIDs[int(list[3])] >= 0:    #handles if a name was given also, unrecognized means don't follow
                mess = mess + str(skeletonPersonIDs[list[3]])
            else:
                readyTT = True #exits because should not follow
                return
        elif not voiceFollow: #"follow xCoord yCoord timeStamp" and follow was not started by voice command
            readyTT = True #exits because should not follow
            return
        mess = mess + "\n"
        sp.write(mess) #will speak a name if valid user gave gesture, will speak without a name if follow came from voice command
    state = "following"
    
    if list[1] == "stop": #LILI received a stop command or has lost track of the user
        print "Stopping."
        readyTT = False
        r.setvel(0,0) #stop robot motion
        mess = "stopFollow "
        if len(list) > 3: #"follow stop idNum timeStamp"
            try:
                int(list[2])
                mess = mess + list[2]
            except ValueError:
                mess = mess
        mess = mess + "\n"
        sp.write(mess)
        state = "waiting"
        voiceFollow = False
        lastMoveTime = time.time()
        return
    a = float(list[1]) #x coordinate of user relative to LILI
    b = float(list[2]) #y coordinate of user relative to LILI

    distF = 1.5 #distance behind person
    
    #find the point 1.5 meters behind the user on a straight line between the user and the robot
    if not a == 0:
        c = a - (distF/(1+(b/a)**2))**.5
        d = b - (b/a)*((distF/(1+(b/a)**2))**.5)
    else: #user is directly in front of LILI
        c = 0 
        d = b - distF 
    
    #stop moving if bump sensor is being pressed, does not stop following
    if not r.isbumped():
        r.goToGoal(c,d)
    else:
        r.setvel(0, 0)
    lastMoveTime = time.time()
    

# Checks if phrasesToSay.py is ready to accept another input phrase
def checkReady():
    global readyTT
    #reads the output from the TTS program
    ready = sp.line.strip()
    if ready=="ready": 
        readyTT=True #TTS program is ready to speak again

#adds command from KinectMonitor onto appropriate queue
def KinectQueue():
    line = km.line.strip()
    if line[:line.find(' ')] == "follow": #all information regarding following starts with the word "follow"
        qFollow.put(line)
    elif line[:line.find(' ')] == "face": #all information regarding faces start with the word "face"
        qFace.put(line)
    else:
    #Gestures received from the Kinect Monitor will be added to the queue
        qGest.put(line)

#adds command from VoiceMonitor onto appropriate queue
def VocalQueue():
    global state
    global voiceFollow
    line = vm.line.strip()
    #follow information must be writeen to KinectMonitor so that it will start sending information about user location
    if line == "follow":
        voiceFollow = True #if follow started by voice command, LILI can follow unknown users. This allows for that functionality
        km.write('follow\n')
    if line == "stop":
        km.write('follow stop\n')
    else:
    #Gestures received from the Voice Monitor will be added to the queue
        qGest.put(line + ' ' + str(time.time()))

# Search for gesture
#should have at least one item on qGest before calling this method
def GestureResponse():
    global readyTT
    # if the TTS is busy, exit this loop
    if readyTT==False:
        return
    # when TTS is ready, pull the next gesture off of the queue
    line = qGest.get() #line should be "command timeStamp" or "command personID timeStamp"
    
    parts = line.split() #splits on whitespace by default
    
    gest = parts[0] #gesture command is the first word
    timeStamp = 0.0
    pID = -1
    if len(parts) > 2: #line given was "command personID timeStamp"
        pID = int(parts[1])
        timeStamp = float(parts[2])
    else:             #line given was "command timeStamp"
        timeStamp = float(parts[1])
        pID = -3 #not a number that might be passed from KinectMonitor (those are either -2 or -1)
    
    #exit if message was received during the last movement or is not in a waiting state
    #otherwise execute the correct command response
    if not gest == 'Lily':
        if timeStamp < lastMoveTime or not state == "waiting": #gesture received during another gesture execution
            return
    if gest == "Lily": 
        print "Yes?"
    if gest == "rightWave":
        waveRight(pID)
    if gest == "leftWave":
        waveLeft(pID)
    if gest == "quit":
        Exit(pID)
    if gest == "turnAround":
        turnAround()


#should have at least one item on qFace queue before calling this method
def faceResponse():
    global readyTT
    parts = qFace.get().split() #should be of the form "face [recognized|lost] skeletonID personID timeStamp"
    if parts[1] == "recognized":
        #new recognized user
        
        skeletonPersonIDs[int(parts[2])] = int(parts[3]) #add new user to dictionary
        readyTT = False
        sp.write("hello " + parts[3] + "\n")
        
    elif parts[1] == "lost":
        #recognized user has left
        
        del skeletonPersonIDs[int(parts[2])] #remove user that has been lost
        readyTT = False
        sp.write("bye " + parts[3] + "\n")
        
    elif parts[1] == "unrecognized":
        #user has been marked as unkown and no more attempts will be made to recognize them
        readyTT = False
        sp.write("unrecognized\n")
    else:
        sys.stderr.write("invalid input " + parts[1] + "\n")
        
        

# Execute response to registered gesture
#personID should be an integer representing the ID number for the person's face
def waveRight(personID):
    global readyTT
    global lastMoveTime
    print "Right Wave Received."
    readyTT = False
    #check to see if person who gave wave is known
    if personID == -3:
        sp.write("right\n")
    elif personID >= 0:
        sp.write("right " + str(personID) + "\n")
    else:
        readyTT = True
        return #gesture came from KinectMonitor and user is unrecognized should not execute command
    print "Moving one meter to the right."
    if not r.isbumped():
        km.write("sleep\n")  #stop the kinect monitor actions while movement is happening
        r.moveTo(r.x,r.y+1,r.theta) #is a blocking method call
    r.setvel(0,0) #make sure robot has stopped
    km.write("wake\n")   #start kinect monitor again
    lastMoveTime = time.time() #update lastMoveTime
    print "DONE\n"

#personID should be an integer representing the ID number for the person's face    
def waveLeft(personID):
    global readyTT
    global lastMoveTime
    print "Left Wave Received."
    readyTT = False
    #check to see if person who gave wave is known
    if personID == -3:
        sp.write("left\n")
    elif personID >= 0:
        sp.write("left " + str(personID) + "\n")
    else:
        readyTT = True
        return #gesture came from KinectMonitor and user is unrecognized should not execute command
    print "Moving one meter to the left."
    if not r.isbumped():
        km.write("sleep\n")  #stop the kinect monitor actions while movement is happening
        r.moveTo(r.x,r.y-1,r.theta) #is a blocking method call
    r.setvel(0,0)
    km.write("wake\n")   #start kinect monitor again
    lastMoveTime = time.time() #update lastMoveTime
    print "DONE\n"
    
# Close connection
#personID should be an integer representing the ID number for the person's face
def Exit(personID):
    global readyTT
    global quit
    print "Lily is going to sleep."
    readyTT = False
    #check to see if person who gave command is known
    if personID == -3:
        sp.write("bye\n")
    elif personID >= 0:
        sp.write("bye " + str(personID) + "\n")
    else:
        readyTT = True
        return #gesture came from KinectMonitor and user is unrecognized should not execute command
    quit = True
    time.sleep(5) #to allow all subprocesses to close
    r.delete()  

#turns LILI 180 degrees to face the other direction
def turnAround():
    global readyTT
    global lastMoveTime
    print "Turn around received"
    readyTT = False
    if not r.isbumped():
        km.write("sleep\n")
        r.rotate(np.pi) #rotate 180 degrees
    r.setvel(0,0)
    km.write("wake\n")
    lastMoveTime = time.time()
    

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
r = iRobotCreate.iRobotCreate(0, 5, "COM3")
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

#start VoiceMonitor listening
vm.write("start\n")

#Waiting state: search for gestures from the kinect monitor
while quit == False: # The user has not asked to quit.
    vm.tryReadLine()  # receive input from the voice monitor
    km.tryReadLine()  # receive input from the kinect monitor
    sp.tryReadLine()  # receive input from the TTS
    
    if not qFollow.empty(): #if there is a command in the qFollow queue
        follow()
    else:
        #stop following if the KinectMonitor stops sending values
        if state == "following":
            km.write('follow stop\n')
            
# if there are items on the queue, try to respond
    if not qGest.empty():  
        GestureResponse()
    if not qFace.empty():
        faceResponse()
    IPC.Sync()
