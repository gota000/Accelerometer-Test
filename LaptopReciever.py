import socket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.0.143 ', 5005)) 

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
line, = ax.plot([], [], 'o', markersize=10)
ax.set_ylim(0,1)

def update(frame):
    data = s.recv(1024).decode().strip()
    if data:
        x_raw, y_raw, z_raw = map(int, data.split(','))
        x_g = x_raw * 2.0 / 2048
        y_g = y_raw * 2.0 / 2048
        angle = math.atan2(y_g, x_g)
        magnitude = math.sqrt(x_g**2 + y_g**2)
        line.set_data([angle], [magnitude])
    return line,

ani = FuncAnimation(fig, update, interval=100)
plt.show()
