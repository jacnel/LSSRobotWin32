
import ctypes
lib=ctypes.CDLL('pywrap')

lib.lidarScan.restype = ctypes.c_long


