from IPC import *
from nitepy import *
import threading
import thread
import sys




lock = threading.Lock()
lock.acquire()
rightWave=False
leftWave =False
follow = False
stopfollow = False
pauseSkel = False
userOfInt=0
quits = False
e = threading.Event()
lock.release()
track = lib.Tracker_new()

curSkeletonPersonIDs = {} #dictionary where a skeletonID is paired with a personID
oldSkeletonPersonIDs = {} #old version of curSkeletonPersonIDs dictionary
personIDAttempts = {} #dictionary where a skeletonID is paired with the number of attempts made to identify the person

gestGivenPID = -1 #personID of the user who provided a gesture

lib.loop(track)

readyCount = 0 #so face identification is run every NUM_LOOPS times
NUM_LOOPS = 10 #number of loops before each attempted facial recognition
MAX_GUESSES = 10 #maximum number of guesses the face identifier is allowed before a person is considered unrecognized

def detect_motion():
    global rightWave
    global leftWave
    global follow
    global stopfollow
    global userOfInt
    global quits
    global track
    global gestGivenPID
    user = 0
    lstage = ["none"] #array of states for left wave.  Each stage is for one person.
    rstage = ["none"] #array of states for right wave.
    follstage = ["none"] #array of states for follow.
    stopfollstage = ["none"] #array of states for  stop follow.
    quitstage = ["none"]  #array of states for quit.
    while True:
        e.wait()   #pauses thread if main thread flag is cleared
        lock.acquire()
        lib.loop(track)  #grab a new 3D frame
        lock.release()
        for user in range(0,lib.getUsersCount(track)):
            if len(lstage)<=user:
                lstage.append("none") #there is an additional user, we need more state variables
                rstage.append("none")
                follstage.append("none")
                quitstage.append("none")
                stopfollstage.append("none")
            if lstage[user]=="none":  #nothing has happened yet, check if the arm is in a position of interest
                if lib.getUserSkeletonL_HandX(track,user)-lib.getUserSkeletonL_ElbowX(track,user)>100:
                    if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonL_ElbowY(track,user)>0:
                        lstage[user] = "ready"
            if lstage[user]=="ready":#we hit one point of interest, move to the next if the arm has met the new POI
                if lib.getUserSkeletonL_ElbowX(track,user)-lib.getUserSkeletonL_HandX(track,user)>100:
                    if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonL_ElbowY(track,user)>0:
                        lstage[user] = "none"
                        lock.acquire()
                        leftWave = True
                        gestGivenPID = curSkeletonPersonIDs[lib.getUserID(track, user)]
                        sys.stderr.write("got left wave from user "+str(user) +"\n")
                        lock.release()
            if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonL_ElbowY(track,user)<0:
                lstage[user] = "none"#we hit a point that is un acceptable for this gesture, cancel it
                
            if rstage[user]=="none":#nothing has happened yet, check if the arm is in a position of interest
                if lib.getUserSkeletonR_HandX(track,user)-lib.getUserSkeletonR_ElbowX(track,user)<-100:
                    if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonR_ElbowY(track,user)>0:
                        rstage[user] = "ready"
            if rstage[user]=="ready":#we hit one point of interest, move to the next if the arm has met the new POI
                if lib.getUserSkeletonR_ElbowX(track,user)-lib.getUserSkeletonR_HandX(track,user)<-100:
                    if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonR_ElbowY(track,user)>0:
                        rstage[user] = "none"
                        lock.acquire()
                        rightWave = True
                        gestGivenPID = curSkeletonPersonIDs[lib.getUserID(track, user)]
                        sys.stderr.write("got right wave from user "+str(user)+"\n")
                        lock.release()
            if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonR_ElbowY(track,user)<0:
                rstage[user] = "none"#we hit a point that is un acceptable for this gesture, cancel it
                
            if follstage[user]=="none":#nothing has happened yet, check if the arm is in a position of interest
                if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonR_HandZ(track,user))<100:
                    if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonL_ShZ(track,user))>300:
                        follstage[user] = "ext"
            if follstage[user]=="ext":#we hit one point of interest, move to the next if the arm has met the new POI
                if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonR_HandZ(track,user))<100:
                    if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonL_ShZ(track,user))<150:
                        follstage[user]="none"
                        lock.acquire()
                        userOfInt = user
                        follow = True
                        sys.stderr.write("got follow from user "+str(user)+"\n")
                        lock.release()
            if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonR_HandZ(track,user))>100:
                follstage[user]="none" #invalid for the follow gesture
            if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonTorsoY(track,user)<0:
                follstage[user]="none"#invalid for the follow gesture
            if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonTorsoY(track,user)<0:
                follstage[user]="none"#invalid for the follow gesture

            if stopfollstage[user]=="none":#nothing has happened yet, check if the arm is in a position of interest
                if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonR_HandZ(track,user))<100:
                    if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonL_ShZ(track,user))<150:
                        stopfollstage[user] = "close"
            if stopfollstage[user]=="close":#we hit one point of interest, move to the next if the arm has met the new POI
                if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonR_HandZ(track,user))<100:
                    if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonL_ShZ(track,user))>300:
                        stopfollstage[user]="none"
                        lock.acquire()
                        userOfInt = lib.getUserID(track,user)
                        stopfollow = True
                        sys.stderr.write("got stop follow from user "+str(user)+"\n")
                        lock.release()
            if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonR_HandZ(track,user))>100:
                stopfollstage[user]="none"#invalid for the stop follow gesture
            if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonTorsoY(track,user)<0:
                stopfollstage[user]="none"#invalid for the stop follow gesture
            if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonTorsoY(track,user)<0:
                stopfollstage[user]="none"#invalid for the stop follow gesture
                    
            if quitstage[user]=="none":#nothing has happened yet, check if the arm is in a position of interest
                if lib.getUserSkeletonR_HandX(track,user)-lib.getUserSkeletonNeckX(track,user)<-50:
                    quitstage[user]="scut"
            if quitstage[user]=="scut":#we hit one point of interest, move to the next if the arm has met the new POI
                if lib.getUserSkeletonR_HandX(track,user)-lib.getUserSkeletonNeckX(track,user)>50:
                    quitstage[user]="none"
                    lock.acquire()
                    quits = True
                    gestGivenPID = curSkeletonPersonIDs[lib.getUserID(track, user)]
                    sys.stderr.write("goodbye "+str(user)+"\n")
                    lock.release()
            if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonNeckY(track,user)<0:
                quitstage[user]="none"#invalid for the quit gesture
            if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonHeadY(track,user)>0:
                quitstage[user]="none"#invalid for the quit gesture
        

def facialActions():
    global curSkeletonPersonIDs
    global oldSkeletonPersonIDs
    global personIDAttempts
    
    while True:
        e.wait()   #pauses thread if main thread flag is cleared
        lock.acquire()
        lib.takeSnapShot(track)
        lib.detectPeople(track)
        lock.release()
        
        tempSkelIDs = []
        
        lock.acquire()
        for user in range(0, lib.getUsersCount(track)):
            curSkeletonPersonIDs[lib.getUserID(track, user)] = lib.getUserPersonID(track, user) #for each user, match skeletonID to personID
            if not lib.getUserID(track, user) in personIDAttempts.keys():
                personIDAttempts[lib.getUserID(track, user)] = 0
            tempSkelIDs.append(lib.getUserID(track, user))
            
        for key in curSkeletonPersonIDs:       #for every skeletonID that has been created
            if not key in tempSkelIDs:     #check if it is still on screen
                curSkeletonPersonIDs[key] = -1 #skeleton is no longer on screen
        
        deleteKeys = []
        #check for any changes in the personIDs that correspond to the skeletonIDs
        for key in curSkeletonPersonIDs.keys():
            if key in oldSkeletonPersonIDs.keys(): #check skeletonIDs that were previously on screen
                if (not (curSkeletonPersonIDs[key] == oldSkeletonPersonIDs[key])) and (personIDAttempts[key] < MAX_GUESSES): #if the personID changed for a given skeletonID
                    if curSkeletonPersonIDs[key] >= 0 and oldSkeletonPersonIDs[key] < 0:
                        #person is now recognized
                        p.write("face recognized " + str(key) + " " + str(curSkeletonPersonIDs[key]) + " " + str(time.time()) + "\n")
                        sys.stderr.write("recognized skeleton: " + str(key) + " as person: " + str(curSkeletonPersonIDs[key]) + "\n")
                    elif curSkeletonPersonIDs[key] < 0 and oldSkeletonPersonIDs[key] >= 0:
                        #recognized person has left the frame
                        p.write("face lost " + str(key) + " " + str(oldSkeletonPersonIDs[key]) + " " + str(time.time()) + "\n")
                        sys.stderr.write("person: " + str(oldSkeletonPersonIDs[key]) + " has left vision as skeleton: " + str(key) + "\n")
                        deleteKeys.append(key)
                    elif curSkeletonPersonIDs[key] < 0 and oldSkeletonPersonIDs[key] < 0: #for different negative numbers showing up (any negative number is a failure to recognize
                        personIDAttempts[key] = personIDAttempts[key] + 1
                elif personIDAttempts[key] < MAX_GUESSES:
                    personIDAttempts[key] = personIDAttempts[key] + 1  #attempt failed to identify user
                elif personIDAttempts[key] == MAX_GUESSES:
                    #person was failed to be recognized
                    p.write("face unrecognized " + str(time.time()) + "\n")
                    sys.stderr.write(" user is unrecognizable\n")
                    personIDAttempts[key] = personIDAttempts[key] + 1
            else:
                personIDAttempts[key] = personIDAttempts[key] + 1
                if curSkeletonPersonIDs[key] >= 0:
                    #if face is recognized in one try (user comes on and is immediately recognized
                    p.write("face recognized " + str(key) + " " + str(curSkeletonPersonIDs[key]) + " " + str(time.time()) + "\n")
                    sys.stderr.write("recognized skeleton: " + str(key) + " as person: " + str(curSkeletonPersonIDs[key]) + "\n")
        for key in deleteKeys:
            del curSkeletonPersonIDs[key]  #removes from dictionary any skeletons that have left the field of vision
        oldSkeletonPersonIDs = dict(curSkeletonPersonIDs)
        lock.release()
       
        time.sleep(.5)
                
                                
def handleLine():
    global userOfInt
    global follow
    global stopfollow
    if p.line == "follow\n":
        if lib.getUsersCount(track)>0:
            lock.acquire()
            userOfInt = lib.getUserID(track,0)
            follow = True
            sys.stderr.write("got follow from userID "+str(userOfInt)+"\n")
            lock.release()
        else:
            sys.stderr.write("no users\n")
    elif p.line == "follow stop\n":
        stopfollow = True
        sys.stderr.write("got stop follow\n")
    elif p.line == "sleep\n":
        e.clear()  #pauses the other threads until ready for them to start again
    elif p.line == "wake\n":
        e.set()    #allows other threads to continue
    else:
        sys.stderr.write("handle line " + p.line)

thread.start_new_thread(detect_motion,())
thread.start_new_thread(facialActions, ())

sys.stderr.write("starting KM process\n")

p = process(True,"KM")
p.setOnReadLine(handleLine)
InitSync()
e.set()
while True:
    p.tryReadLine()
    lock.acquire()
    if stopfollow:
        p.write("follow stop "+str(time.time()) + "\n")
        follow = False
        stopfollow = False
    if quits:
        p.write("quit " + str(gestGivenPID) + " " + str(time.time()) + "\n") #if person is unknown, master control/speaking program will handle
        gestGivenPID = -1 #reset it to an unknown person
        exit()
    if follow:
        #sys.stderr.write(str(track) + " " + str(userOfInt) + "\n")
        user = -1
        index = 0
        while index<lib.getUsersCount(track): #find index of userOfInt which is a UserID. (user is an index)
            #sys.stderr.write("in while loop\n")
            if lib.getUserID(track,index)==userOfInt:
                user = index
            index = index + 1
        if user>=0: #we found the user
            if lib.isUserTracked(track, user):
                #sys.stderr.write("is following\n")
                p.write("follow "+str(lib.getUserSkeletonTorsoZ(track,user)/1000)+" "+str(lib.getUserSkeletonTorsoX(track,user)/1000)+" " + str(time.time()) + "\n")
            else:#they aren't tracked
                stopfollow = True
        else:#they're not here
            stopfollow = True
    if rightWave:
        rightWave=False
        p.write("rightWave " + str(gestGivenPID) + " " + str(time.time()) + "\n") #if person is unknown, master control/speaking program will handle
        gestGivenPID = -1 #reset it to an unknown person
    if leftWave:
        leftWave=False
        p.write("leftWave " + str(gestGivenPID) + " " + str(time.time()) + "\n") #if person is unknown, master control/speaking program will handle
        gestGivenPID = -1 #reset it to an unknown person
    lock.release()
    
    Sync()
