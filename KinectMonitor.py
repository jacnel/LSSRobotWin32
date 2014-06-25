from IPC import *
from nitepy import *
import threading
import thread
import sys

lock = threading.Lock()
lock.acquire()
rightWave=False
leftWave =False
lock.release()


def detect_motion():
    global rightWave
    global leftWave
    track = lib.Tracker_new()
    user = 0
    lstage = ["none"]
    rstage = ["none"]
    while True:
        lib.loop(track)
        for user in range(0,lib.getUsersCount(track)):
            if len(lstage)<=user:
                lstage.append("none")
                rstage.append("none")
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


def handleLine():
    sys.stderr.write(p.line)

thread.start_new_thread(detect_motion,())

p = process(True,"")
p.setOnReadLine(handleLine)
InitSync()
while True:
    p.tryReadLine()
    lock.acquire()
    if rightWave:
        rightWave=False
        p.write("rightWave " + str(time.time()) + "\n")
    if leftWave:
        leftWave=False
        p.write("leftWave " + str(time.time()) + "\n")
    lock.release()
    Sync()
