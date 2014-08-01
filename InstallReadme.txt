To use this project, please install the following programs from the LILI Install folder:
(even if you are running 64-bit Windows, Please use 32-bit versions of these programs)

The CSLU Toolkit as described in TalkingAvatarReadme.
	run cslu206
	--select all c source code options and any languages you would like to use
	-use the "bsync.tcl" in the LSSRobotWin32 repository and copy and paste it over C:\Program Files\CSLU\Toolkit\2.0\script\bsync_1.0\bsync.tcl
	-run the "baldi sync" application to get the face window and the TTS window
		-if no short cut is found go to C:\Program Files\CSLU\Toolkit\2.0\apps and set the baldiSync.tcl file's
			default program to wish80.exe (C:\Program Files\CSLU\Tcl80\bin)
		-should be able to double click baldiSync.tcl to run
	-right click on the face and go to preferences
		-change face to desired face (Lily)
		-change emotions as needed (ie .1 happy) -> keep neutral at max to avoid highly distorted faces
		-click save when satisfied
	-click into the TTS window where text would be entered in to make it possible for the code to simulate keystrokes into there

Microsoft Speech SDK 11:
	first, run dotNetFx40_Full_Setup
	run SpeechPlatformRuntime
	run MicrosoftSpeechPlatformSDK
	run MSSpeech_SR_en-US_TELE

OpenNI 2.1 
NITE 2.2 (install OpenNI first)
OpenCV 2.4.9
Python 2.7 
	-pyserial, numpy, matplotlib

If there are errors dealing with "clr" module, unzip Python for .NET into the working directory along with a copy of the python.exe from the Python27 folder after installing python 2.7

Canopy and Visual Studios are optional editors

FTDI-A12 Drivers (if cannot connect to the iRobotCreate)
	instructions found inside the FTDI folder
e1649fwu drivers (if the monitor does not plug-and-play)


All other related code can be found in the following repositories:
(Visual Studio Projects)
https://github.com/deadtomgc/nitepy
https://github.com/clguerrero93/lilivoicecommand
https://github.com/deadtomgc/fakeinput
