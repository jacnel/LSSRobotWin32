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

curSkeletonPersonIDs = {-1:-1} #dictionary where a skeletonID is paired with a personID
oldSkeletonPersonIDs = {-1:-1} #old version of dictionary

lib.loop(track)

readyCount = 0 #so face identification is run every NUM_LOOPS times
NUM_LOOPS = 10 #number of loops before each attempted facial recognition

def detect_motion():
    global rightWave
    global leftWave
    global follow
    global stopfollow
    global userOfInt
    global quits
    global track
    user = 0
    lstage = ["none"]
    rstage = ["none"]
    follstage = ["none"]
    stopfollstage = ["none"]
    quitstage = ["none"]
    while True:
        lock.acquire()
        lib.loop(track)
        lock.release()
        for user in range(0,lib.getUsersCount(track)):
            if len(lstage)<=user:
                lstage.append("none")
                rstage.append("none")
                follstage.append("none")
                quitstage.append("none")
                stopfollstage.append("none")
            if lstage[user]=="none":
                if lib.getUserSkeletonL_HandX(track,user)-lib.getUserSkeletonL_ElbowX(track,user)>100:
                    if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonL_ElbowY(track,user)>0:
                        lstage[user] = "ready"
            if lstage[user]=="ready":
                if lib.getUserSkeletonL_ElbowX(track,user)-lib.getUserSkeletonL_HandX(track,user)>100:
                    if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonL_ElbowY(track,user)>0:
                        lstage[user] = "none"
                        lock.acquire()
                        leftWave = True
                        sys.stderr.write("got left wave from user "+str(user) +"\n")
                        lock.release()
            if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonL_ElbowY(track,user)<0:
                lstage[user] = "none"
                
            if rstage[user]=="none":
                if lib.getUserSkeletonR_HandX(track,user)-lib.getUserSkeletonR_ElbowX(track,user)<-100:
                    if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonR_ElbowY(track,user)>0:
                        rstage[user] = "ready"
            if rstage[user]=="ready":
                if lib.getUserSkeletonR_ElbowX(track,user)-lib.getUserSkeletonR_HandX(track,user)<-100:
                    if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonR_ElbowY(track,user)>0:
                        rstage[user] = "none"
                        lock.acquire()
                        rightWave = True
                        sys.stderr.write("got right wave from user "+str(user)+"\n")
                        lock.release()
            if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonR_ElbowY(track,user)<0:
                rstage[user] = "none"
            if follstage[user]=="none":
                if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonR_HandZ(track,user))<100:
                    if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonL_ShZ(track,user))>300:
                        follstage[user] = "ext"
            if follstage[user]=="ext":
                if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonR_HandZ(track,user))<100:
                    if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonL_ShZ(track,user))<150:
                        follstage[user]="none"
                        lock.acquire()
                        userOfInt = user
                        follow = True
                        sys.stderr.write("got follow from user "+str(user)+"\n")
                        lock.release()
            if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonR_HandZ(track,user))>100:
                follstage[user]="none"
            if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonTorsoY(track,user)<0:
                follstage[user]="none"
            if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonTorsoY(track,user)<0:
                follstage[user]="none"

            if stopfollstage[user]=="none":
                if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonR_HandZ(track,user))<100:
                    if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonL_ShZ(track,user))<150:
                        stopfollstage[user] = "close"
            if stopfollstage[user]=="close":
                if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonR_HandZ(track,user))<100:
                    if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonL_ShZ(track,user))>300:
                        stopfollstage[user]="none"
                        lock.acquire()
                        userOfInt = lib.getUserID(track,user)
                        stopfollow = True
                        sys.stderr.write("got stop follow from user "+str(user)+"\n")
                        lock.release()
            if abs(lib.getUserSkeletonL_HandZ(track,user)-lib.getUserSkeletonR_HandZ(track,user))>100:
                stopfollstage[user]="none"
            if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonTorsoY(track,user)<0:
                stopfollstage[user]="none"
            if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonTorsoY(track,user)<0:
                stopfollstage[user]="none"
                    
            if quitstage[user]=="none":
                if lib.getUserSkeletonR_HandX(track,user)-lib.getUserSkeletonNeckX(track,user)<-50:
                    quitstage[user]="scut"
            if quitstage[user]=="scut":
                if lib.getUserSkeletonR_HandX(track,user)-lib.getUserSkeletonNeckX(track,user)>50:
                    quitstage[user]="none"
                    lock.acquire()
                    quits = True
                    sys.stderr.write("goodbye "+str(user)+"\n")
                    lock.release()
            if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonNeckY(track,user)<0:
                quitstage[user]="none"
            if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonHeadY(track,user)>0:
                quitstage[user]="none"
        

def facialActions():
    global curSkeletonPersonIDs
    global oldSkeletonPersonIDs
    #SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_IDLE)
    #sys.stderr.write("set priority idle\n")
    while True:
        lock.acquire()
        lib.takeSnapShot(track)
        #lock.release()
        #
        #lock.acquire()
        lib.detectPeople(track)
        lock.release()
        
        tempSkelIDs = []
        
        lock.acquire()
        for user in range(0, lib.getUsersCount(track)):
            curSkeletonPersonIDs[lib.getUserID(track, user)] = lib.getUserPersonID(track, user) #for each user, match skeletonID to personID
            tempSkelIDs.append(lib.getUserID(track, user))
            
        for key in curSkeletonPersonIDs:       #for every skeletonID that has been created
            if not key in tempSkelIDs:     #check if it is still on screen
                curSkeletonPersonIDs[key] = -1 #skeleton is no longer on screen
        
        #check for any changes in the personIDs that correspond to the skeletonIDs
        for key in curSkeletonPersonIDs:
            if key in oldSkeletonPersonIDs: #check skeletonIDs that were previously on screen
                if not curSkeletonPersonIDs[key] == oldSkeletonPersonIDs[key]: #if the personID changed for a given skeletonID
                    if curSkeletonPersonIDs[key] >= 0 and oldSkeletonPersonIDs[key] < 0:
                        #person is now recognized
                        p.write("face recognized " + str(key) + " " + str(curSkeletonPersonIDs[key]) + " " + str(time.time()) + "\n")
                        sys.stderr.write("recognized skeleton: " + str(key) + " as person: " + str(curSkeletonPersonIDs[key]) + "\n")
                    elif curSkeletonPersonIDs[key] < 0 and oldSkeletonPersonIDs[key] >= 0:
                        #recognized person has left the frame
                        p.write("face lost " + str(key) + " " + str(oldSkeletonPersonIDs[key]) + " " + str(time.time()) + "\n")
                        sys.stderr.write("person: " + str(oldSkeletonPersonIDs[key]) + " has left vision as skeleton: " + str(key) + "\n")
            else:
                if curSkeletonPersonIDs[key] >= 0:
                    #if face is recognized in one try
                    p.write("face recognized " + str(key) + " " + str(curSkeletonPersonIDs[key]) + " " + str(time.time()) + "\n")
                    sys.stderr.write("recognized skeleton: " + str(key) + " as person: " + str(curSkeletonPersonIDs[key]) + "\n")
        oldSkeletonPersonIDs = dict(curSkeletonPersonIDs)
        lock.release()
       
        time.sleep(1)
                
                                
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
    else:
        sys.stderr.write("handle line " + p.line)

thread.start_new_thread(detect_motion,())
thread.start_new_thread(facialActions, ())

sys.stderr.write("starting KM process\n")

p = process(True,"KM")
p.setOnReadLine(handleLine)
InitSync()
while True:
    p.tryReadLine()
    lock.acquire()
    if stopfollow:
        p.write("follow stop "+str(time.time()) + "\n")
        follow = False
        stopfollow = False
    if quits:
        p.write("quit " + str(time.time()) + "\n")
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
        p.write("rightWave " + str(time.time()) + "\n")
    if leftWave:
        leftWave=False
        p.write("leftWave " + str(time.time()) + "\n")
    lock.release()
    e.set()
    e.clear()
    Sync()
