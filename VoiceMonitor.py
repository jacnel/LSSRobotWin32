import IPC
import sys
import clr

sys.path.append("C:\Users\vader\Documents\lssrobotwin32")

clr.AddReference('LiliVoiceCommand')
import SpeechRecognitionApp as sra

commands = ['Lily', 'rightWave', 'leftWave', 'follow', 'stop', 'quit'] #gesture commands
recoged = ['Lily', 'Move right', 'Move left', 'Follow me', 'Stop', 'Goodbye'] #recognized phrases

vm = IPC.process(True, 'VoiceMonitor.py')

re = sra.Program()
engine = re.buildRecognizer() #create Speech Recognition Engine

re.runRecognizer(engine) #start listening

while re.Listening == True: #while listening
   index = re.grabCommand()  #access recognized command
   if not index == -1:
       if index == 5: #index 5 is a quit command
           re.stopListening(engine)
       vm.write(str(commands[index])+'\n')
       sys.stderr.write("Recognized Phrase "+str(recoged[index]) +"\n")