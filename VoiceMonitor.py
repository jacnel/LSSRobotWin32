import IPC
import sys
import clr
import time

sys.path.append("C:\Users\vader\Documents\lssrobotwin32")

clr.AddReference('LiliVoiceCommand')
import SpeechRecognitionApp as sra

commands = ['Lily', 'rightWave', 'leftWave', 'follow', 'stop', 'turnAround', 'quit'] #gesture commands
recoged = ['Lily', 'Move right', 'Move left', 'Follow me', 'Stop', 'Turn around', 'Goodbye'] #recognized phrases

vm = IPC.process(True, 'VoiceMonitor.py')

started = False #changes once it gets start command from master controller
Lily = False #user must say Lily before giving a command
lilytime = time.time()
timeout = time.time()

re = sra.Program()
engine = re.buildRecognizer() #create Speech Recognition Engine

#for now, only used to receive start command
def onLineRead():
    global started
    message = vm.line.strip()
    if message == "start":
        re.runRecognizer(engine) #start listening
        started = True  #changes to exit first while loop

vm.setOnReadLine(onLineRead)
IPC.InitSync()
#keep checking if it should start listening
while not started:
    vm.tryReadLine()
    IPC.Sync()

while re.Listening == True: #while listening
   index = re.grabCommand()  #access recognized command
   timeout = time.time()
   if index == 0:
       Lily = True
       lilytime = time.time()
   elif Lily == True:
       if not index == -1: #-1 means queue is empty
           if timeout < lilytime + 5:
               if index == 6: #index 6 is a quit command
                    re.stopListening(engine)
               vm.write(str(commands[index])+'\n')
               sys.stderr.write("Recognized Phrase "+str(recoged[index]) +"\n")
               Lily = False
           else:
                Lily = False