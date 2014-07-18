import IPC
import sys
import clr

sys.path.append("C:\Users\college\lssrobotwin32")

clr.AddReference('LiliVoiceCommand')
import SpeechRecognitionApp as sra

commands = ['Lily', 'rightWave', 'leftWave', 'follow', 'stop', 'quit']
recoged = ['Lily', 'Move right', 'Move left', 'Follow me', 'Stop', 'Goodbye']

vm = IPC.process(True, 'VoiceMonitor.py')

re = sra.Program()
engine = re.buildRecognizer()

#def receiver():
#    message = vm.line.strip()
#    if message == 'True':
#        readyToListen()
#    if message == 'False':
#        re.stopListening(engine)

re.runRecognizer(engine)

while re.Listening == True:
   index = re.grabCommand()
   if not index == -1:
       if index == 5:
           re.stopListening(engine)
       vm.write(str(commands[index])+'\n')
       sys.stderr.write("Recognized Phrase "+str(recoged[index]) +"\n")
            
#vm.setOnReadLine(receiver)
#IPC.InitSync()

#while True:
#    vm.tryReadLine()
#    IPC.Sync()