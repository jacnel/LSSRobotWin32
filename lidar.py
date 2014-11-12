
import ctypes
lidar=ctypes.CDLL('lidar')

lidar.lidarScan.restype = ctypes.c_long


