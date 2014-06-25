import ctypes
lib=ctypes.CDLL('nitepy')

track = lib.Tracker_new()
lib.getUserSkeletonHeadX.restype = ctypes.c_float
lib.getUserSkeletonHeadY.restype = ctypes.c_float
lib.getUserSkeletonHeadZ.restype = ctypes.c_float

lib.getUserSkeletonNeckX.restype = ctypes.c_float
lib.getUserSkeletonNeckY.restype = ctypes.c_float
lib.getUserSkeletonNeckZ.restype = ctypes.c_float

lib.getUserSkeletonL_ShX.restype = ctypes.c_float
lib.getUserSkeletonL_ShY.restype = ctypes.c_float
lib.getUserSkeletonL_ShZ.restype = ctypes.c_float

lib.getUserSkeletonR_ShX.restype = ctypes.c_float
lib.getUserSkeletonR_ShY.restype = ctypes.c_float
lib.getUserSkeletonR_ShZ.restype = ctypes.c_float

lib.getUserSkeletonL_ElbowX.restype = ctypes.c_float
lib.getUserSkeletonL_ElbowY.restype = ctypes.c_float
lib.getUserSkeletonL_ElbowZ.restype = ctypes.c_float

lib.getUserSkeletonR_ElbowX.restype = ctypes.c_float
lib.getUserSkeletonR_ElbowY.restype = ctypes.c_float
lib.getUserSkeletonR_ElbowZ.restype = ctypes.c_float

lib.getUserSkeletonL_HandX.restype = ctypes.c_float
lib.getUserSkeletonL_HandY.restype = ctypes.c_float
lib.getUserSkeletonL_HandZ.restype = ctypes.c_float

lib.getUserSkeletonR_HandX.restype = ctypes.c_float
lib.getUserSkeletonR_HandY.restype = ctypes.c_float
lib.getUserSkeletonR_HandZ.restype = ctypes.c_float

lib.getUserSkeletonTorsoX.restype = ctypes.c_float
lib.getUserSkeletonTorsoY.restype = ctypes.c_float
lib.getUserSkeletonTorsoZ.restype = ctypes.c_float

lib.getUserSkeletonL_HipX.restype = ctypes.c_float
lib.getUserSkeletonL_HipY.restype = ctypes.c_float
lib.getUserSkeletonL_HipZ.restype = ctypes.c_float

lib.getUserSkeletonR_HipX.restype = ctypes.c_float
lib.getUserSkeletonR_HipY.restype = ctypes.c_float
lib.getUserSkeletonR_HipZ.restype = ctypes.c_float

lib.getUserSkeletonL_KneeX.restype = ctypes.c_float
lib.getUserSkeletonL_KneeY.restype = ctypes.c_float
lib.getUserSkeletonL_KneeZ.restype = ctypes.c_float

lib.getUserSkeletonR_KneeX.restype = ctypes.c_float
lib.getUserSkeletonR_KneeY.restype = ctypes.c_float
lib.getUserSkeletonR_KneeZ.restype = ctypes.c_float

lib.getUserSkeletonL_FootX.restype = ctypes.c_float
lib.getUserSkeletonL_FootY.restype = ctypes.c_float
lib.getUserSkeletonL_FootZ.restype = ctypes.c_float

lib.getUserSkeletonR_FootX.restype = ctypes.c_float
lib.getUserSkeletonR_FootY.restype = ctypes.c_float
lib.getUserSkeletonR_FootZ.restype = ctypes.c_float
