import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import ctypes
lib=ctypes.CDLL('pywrap')

lib.lidarScan.restype = ctypes.c_long

plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111)
line1, = ax.plot([], [], 'r-') # Returns a tuple of line objects, thus the comma

ax.set_ylim([0,5000])
ax.set_xlim([-5000,5000])

while 1:
    n = lib.lidarScan(1,0,0)
    data = np.zeros((1,n))
    for i in range(0,n):
        data[0][i]=lib.lidarScan(0,i,0)
    th = np.arange(n)*240.0/n-120+90
    x=data*np.cos(th*3.1415/180)
    y=data*np.sin(th*3.1415/180)
    line1.set_data(x,y)
    fig.canvas.draw()