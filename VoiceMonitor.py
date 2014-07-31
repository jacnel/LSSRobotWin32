import IPC
import sys
import clr

sys.path.append("C:\Users\vader\Documents\lssrobotwin32")

clr.AddReference('LiliVoiceCommand')
import SpeechRecognitionApp as sra

commands = ['Lily', 'rightWave', 'leftWave', 'follow', 'stop', 'quit'] #gesture commands
recoged = ['Lily', 'Move right', 'Move left', 'Follow me', 'Stop', 'Goodbye'] #recognized phrases

vm = IPC.process(True, 'VoiceMonitor.py')

started = False #changes once it gets start command from master controller
Lily = False #user must say Lily before giving a command

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
   if index == 0:
       Lily = True
   elif Lily == True:
       if not index == -1: #-1 means queue is empty
            if index == 5: #index 5 is a quit command
                re.stopListening(engine)
            vm.write(str(commands[index])+'\n')
            sys.stderr.write("Recognized Phrase "+str(recoged[index]) +"\n")
            Lily = False