
#This file contains the setup to use the methods from the nitepy.dll.
#The methods must have their return types set using ctypes otherwise the values returned
#from nitepy.dll will be unreadable and cause errors.
#Any file that wants to utilize the skeleton data needs to import this file or a file that
#has already imported this file.
#After importing this file, the methods can be used in the normal way they would be called
#(ie. lib.getUserSkeletonHeadX(Tracker, int)

import ctypes
lib=ctypes.CDLL('pywrap')

lib.lidarScan.restype = ctypes.c_long

while 1:
    n = lib.lidarScan(1,0,0)
    print n
    for i in range(0,n/100):
        print lib.lidarScan(0,i*100,0)
    print ""