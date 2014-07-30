Setting up Talking Avatar

-http://www.cslu.ogi.edu/toolkit/download/index.html
		--link for downloading applications
		--you will need to fill out the registration form
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