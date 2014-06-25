import subprocess
import time
import sys
from threading  import Thread
from Queue import Queue, Empty
refreshRate = 5 #Hz
warn = False
def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

class process:
    
    def __init__(self,usestd,var):
        self.usestd=usestd
        if usestd==False:
            self.p = subprocess.Popen(['python',var],-1,None,subprocess.PIPE,subprocess.PIPE)
        self.q = Queue()
        if usestd==True:
            self.t = Thread(target=enqueue_output, args=(sys.stdin, self.q))
        else:
            self.t = Thread(target=enqueue_output, args=(self.p.stdout, self.q))
        self.t.daemon = True # thread dies with the program
        self.t.start()
        self.line = ""
        
    def setOnReadLine(self,onReadLine):
        self.onRead = onReadLine
    def tryReadLine(self):
        try: self.line = self.q.get_nowait() # or q.get(timeout=.1)
        except Empty:
            if warn:
                sys.stderr.write('no output yet\n')
        else:
            self.onRead()
    def write(self,data):
        if self.usestd==False:
            self.p.stdin.write(data)
            self.p.stdin.flush()
        else:
            sys.stdout.write(data)
            sys.stdout.flush()

def InitSync():
    global oldTime
    oldTime=time.time()
def Sync():
    global oldTime
    curTime = time.time()
    if curTime-oldTime<1.0/refreshRate:
        time.sleep(1.0/refreshRate - (curTime-oldTime))
    else:
        if warn:
            sys.stderr.write("tester Falling behind!!!\n")
    oldTime=time.time()
