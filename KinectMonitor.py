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
    lstage = "none"
    rstage = "none"
    while True:
        lib.loop(track)
        if lib.getUsersCount(track)>0:#for user in range(0,1):#lib.getUsersCount(track)):
            if lstage=="none":
                if lib.getUserSkeletonL_HandX(track,user)-lib.getUserSkeletonL_ElbowX(track,user)>100:
                    if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonL_ElbowY(track,user)>0:
                        lstage = "ready"
            if lstage=="ready":
                if lib.getUserSkeletonL_ElbowX(track,user)-lib.getUserSkeletonL_HandX(track,user)>100:
                    if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonL_ElbowY(track,user)>0:
                        lstage = "none"
                        lock.acquire()
                        leftWave = True
                        sys.stderr.write("got left wave\n")
                        lock.release()
            if lib.getUserSkeletonL_HandY(track,user)-lib.getUserSkeletonL_ElbowY(track,user)<0:
                lstage = "none"
                
            if rstage=="none":
                if lib.getUserSkeletonR_HandX(track,user)-lib.getUserSkeletonR_ElbowX(track,user)<-100:
                    if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonR_ElbowY(track,user)>0:
                        rstage = "ready"
            if rstage=="ready":
                if lib.getUserSkeletonR_ElbowX(track,user)-lib.getUserSkeletonR_HandX(track,user)<-100:
                    if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonR_ElbowY(track,user)>0:
                        rstage = "none"
                        lock.acquire()
                        rightWave = True
                        sys.stderr.write("got right wave\n")
                        lock.release()
            if lib.getUserSkeletonR_HandY(track,user)-lib.getUserSkeletonR_ElbowY(track,user)<0:
                rstage = "none"


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
        p.write("rightWave\n")
    if leftWave:
        leftWave=False
        p.write("leftWave\n")
    lock.release()
    Sync()
