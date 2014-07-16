from IPC import *
import sys
import clr

sys.path.append("C:\Users\Vader\Documents\Smart Spaces Robot\LSSRobotWin32")

clr.AddReference('LiliVoiceCommand')
import SpeechRecognitionApp as sra

commands = ['Lily', 'rightWave', 'leftWave', 'follow', 'stop', 'quit']

vm = process(True, 'VoiceMonitor.py')

re = sra.Program()
engine = re.buildRecognizer()
re.runRecognizer(engine)
while re.Listening == True:
    index = re.grabCommand()
    if not index == -1:
        if index == 5:
            re.stopListening(engine)
        vm.write(str(commands[index])+'\n')