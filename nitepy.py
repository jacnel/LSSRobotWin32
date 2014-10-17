
#This file contains the setup to use the methods from the nitepy.dll.
#The methods must have their return types set using ctypes otherwise the values returned
#from nitepy.dll will be unreadable and cause errors.
#Any file that wants to utilize the skeleton data needs to import this file or a file that
#has already imported this file.
#After importing this file, the methods can be used in the normal way they would be called
#(ie. lib.getUserSkeletonHeadX(Tracker, int)

import ctypes
lib=ctypes.CDLL('nitepy')

lib.getUserSkeletonHeadConf.restype = ctypes.c_float
lib.getUserSkeletonHeadX.restype = ctypes.c_float
lib.getUserSkeletonHeadY.restype = ctypes.c_float
lib.getUserSkeletonHeadZ.restype = ctypes.c_float

lib.getUserSkeletonNeckConf.restype = ctypes.c_float
lib.getUserSkeletonNeckX.restype = ctypes.c_float
lib.getUserSkeletonNeckY.restype = ctypes.c_float
lib.getUserSkeletonNeckZ.restype = ctypes.c_float

lib.getUserSkeletonL_ShConf.restype = ctypes.c_float
lib.getUserSkeletonL_ShX.restype = ctypes.c_float
lib.getUserSkeletonL_ShY.restype = ctypes.c_float
lib.getUserSkeletonL_ShZ.restype = ctypes.c_float

lib.getUserSkeletonR_ShConf.restype = ctypes.c_float
lib.getUserSkeletonR_ShX.restype = ctypes.c_float
lib.getUserSkeletonR_ShY.restype = ctypes.c_float
lib.getUserSkeletonR_ShZ.restype = ctypes.c_float

lib.getUserSkeletonL_ElbowConf.restype = ctypes.c_float
lib.getUserSkeletonL_ElbowX.restype = ctypes.c_float
lib.getUserSkeletonL_ElbowY.restype = ctypes.c_float
lib.getUserSkeletonL_ElbowZ.restype = ctypes.c_float

lib.getUserSkeletonR_ElbowConf.restype = ctypes.c_float
lib.getUserSkeletonR_ElbowX.restype = ctypes.c_float
lib.getUserSkeletonR_ElbowY.restype = ctypes.c_float
lib.getUserSkeletonR_ElbowZ.restype = ctypes.c_float

lib.getUserSkeletonL_HandConf.restype = ctypes.c_float
lib.getUserSkeletonL_HandX.restype = ctypes.c_float
lib.getUserSkeletonL_HandY.restype = ctypes.c_float
lib.getUserSkeletonL_HandZ.restype = ctypes.c_float

lib.getUserSkeletonR_HandConf.restype = ctypes.c_float
lib.getUserSkeletonR_HandX.restype = ctypes.c_float
lib.getUserSkeletonR_HandY.restype = ctypes.c_float
lib.getUserSkeletonR_HandZ.restype = ctypes.c_float

lib.getUserSkeletonTorsoConf.restype = ctypes.c_float
lib.getUserSkeletonTorsoX.restype = ctypes.c_float
lib.getUserSkeletonTorsoY.restype = ctypes.c_float
lib.getUserSkeletonTorsoZ.restype = ctypes.c_float

lib.getUserSkeletonL_HipConf.restype = ctypes.c_float
lib.getUserSkeletonL_HipX.restype = ctypes.c_float
lib.getUserSkeletonL_HipY.restype = ctypes.c_float
lib.getUserSkeletonL_HipZ.restype = ctypes.c_float

lib.getUserSkeletonR_HipConf.restype = ctypes.c_float
lib.getUserSkeletonR_HipX.restype = ctypes.c_float
lib.getUserSkeletonR_HipY.restype = ctypes.c_float
lib.getUserSkeletonR_HipZ.restype = ctypes.c_float

lib.getUserSkeletonL_KneeConf.restype = ctypes.c_float
lib.getUserSkeletonL_KneeX.restype = ctypes.c_float
lib.getUserSkeletonL_KneeY.restype = ctypes.c_float
lib.getUserSkeletonL_KneeZ.restype = ctypes.c_float

lib.getUserSkeletonR_KneeConf.restype = ctypes.c_float
lib.getUserSkeletonR_KneeX.restype = ctypes.c_float
lib.getUserSkeletonR_KneeY.restype = ctypes.c_float
lib.getUserSkeletonR_KneeZ.restype = ctypes.c_float


lib.getUserSkeletonL_FootConf.restype = ctypes.c_float
lib.getUserSkeletonL_FootX.restype = ctypes.c_float
lib.getUserSkeletonL_FootY.restype = ctypes.c_float
lib.getUserSkeletonL_FootZ.restype = ctypes.c_float


lib.getUserSkeletonR_FootConf.restype = ctypes.c_float
lib.getUserSkeletonR_FootX.restype = ctypes.c_float
lib.getUserSkeletonR_FootY.restype = ctypes.c_float
lib.getUserSkeletonR_FootZ.restype = ctypes.c_float
