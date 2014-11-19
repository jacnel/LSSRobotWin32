import subprocess
import time
import sys
from threading  import Thread
from Queue import Queue, Empty
refreshRate = 5 #Hz
warn = False #set to True if you want warning messages to display
def enqueue_output(out, queue): #puts output stream data onto a queue
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

class process: #create one of these to do IPC
    
    def __init__(self,usestd,var): #set usestd to true if you want to communicate through std in and out (this should be a child process in this case)
        self.usestd=usestd
        if usestd==False:
            self.p = subprocess.Popen(['python',var],-1,None,subprocess.PIPE,subprocess.PIPE) #spawns child process
        self.q = Queue()
        if usestd==True:
            self.t = Thread(target=enqueue_output, args=(sys.stdin, self.q))#start looking for input and be ready to send output
        else:
            self.t = Thread(target=enqueue_output, args=(self.p.stdout, self.q))#start looking for input and be ready to send output
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
    def write(self,data): #data should always end with a new line ("\n")
        if self.usestd==False:
            try:
                self.p.stdin.write(data)
                self.p.stdin.flush()
            except Exception:
                sys.stderr.write('error writing to process\n')
        else:
            try:
                sys.stdout.write(data)
                sys.stdout.flush()
            except Exception:
                sys.stderr.write('error writing to process\n')

#sets up initial time to sync from
def InitSync():
    global oldTime
    oldTime=time.time()
#makes sure process is not running at a higher rate than the refresh rate
def Sync():
    global oldTime
    curTime = time.time()
    if curTime-oldTime<1.0/refreshRate: #if process is keeping up
        #sys.stderr.write("sleeping for "+str(1.0/refreshRate - (curTime-oldTime))+"\n")
        time.sleep(1.0/refreshRate - (curTime-oldTime))
    else: #if process is falling behind
        if warn:
            sys.stderr.write("Falling behind!!!\n")
    oldTime=time.time()
