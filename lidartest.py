import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import ctypes
lib=ctypes.CDLL('lidar')

lib.lidarScan.restype = ctypes.c_long

# plt.ion()

# fig = plt.figure()
# ax = fig.add_subplot(111)
# line1, = ax.plot([], [], 'r.') # Returns a tuple of line objects, thus the comma

# ax.set_ylim([-5000,5000])
# ax.set_xlim([-5000,5000])
count = 0
while 1:
    n = lib.lidarScan(1,0,0)
    if n<0:
        print "negative"
        continue
    data = np.zeros(n)
    for i in range(0,n):
        data[i]=lib.lidarScan(0,i,0)
    th = np.arange(n)*240.0/n-120
    x=np.multiply(data,np.cos(th*3.1415/180))
    y=np.multiply(data,np.sin(th*3.1415/180))
    print x[n/2]
    print count
    count = count +1
    # line1.set_data(x,y)
    # fig.canvas.draw()
    time.sleep(0.1)