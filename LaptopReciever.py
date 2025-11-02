import socket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Connect to Raspberry Pi
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('172.20.10.2', 5005))

# Create figure with 3D visualization
fig = plt.figure(figsize=(12, 10))

# 3D orientation view
ax1 = fig.add_subplot(2, 2, 1, projection='3d')
ax1.set_title('3D Orientation', fontsize=14, fontweight='bold')
ax1.set_xlim([-1.5, 1.5])
ax1.set_ylim([-1.5, 1.5])
ax1.set_zlim([-1.5, 1.5])
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')

# Pitch gauge
ax2 = fig.add_subplot(2, 2, 2)
ax2.set_title('Pitch', fontsize=14, fontweight='bold')
ax2.set_xlim([0, 1])
ax2.set_ylim([-90, 90])
ax2.set_xticks([])
pitch_bar = ax2.barh([0], [0], height=20, color='blue')
ax2.axhline(y=0, color='red', linestyle='--', linewidth=2)
ax2.set_ylabel('Degrees')

# Roll gauge
ax3 = fig.add_subplot(2, 2, 3)
ax3.set_title('Roll', fontsize=14, fontweight='bold')
ax3.set_xlim([0, 1])
ax3.set_ylim([-90, 90])
ax3.set_xticks([])
roll_bar = ax3.barh([0], [0], height=20, color='green')
ax3.axhline(y=0, color='red', linestyle='--', linewidth=2)
ax3.set_ylabel('Degrees')

# Text display
ax4 = fig.add_subplot(2, 2, 4)
ax4.axis('off')
text_display = ax4.text(0.5, 0.5, '', fontsize=16, ha='center', va='center',
                        family='monospace', transform=ax4.transAxes)

plt.tight_layout()

def rotation_matrix(pitch, roll):
    #Create rotation matrix from pitch, roll
    pitch_rad = np.radians(pitch)
    roll_rad = np.radians(roll)
    
    # Rotation matrix
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(roll_rad), -np.sin(roll_rad)],
                   [0, np.sin(roll_rad), np.cos(roll_rad)]])
    
    Ry = np.array([[np.cos(pitch_rad), 0, np.sin(pitch_rad)],
                   [0, 1, 0],
                   [-np.sin(pitch_rad), 0, np.cos(pitch_rad)]])
    
    return Ry @ Rx

def update(frame):
    try:
        data = s.recv(1024).decode().strip()
        if data:
            pitch, roll = map(float, data.split(','))
            
            # Clear 3D plot
            ax1.cla()
            ax1.set_xlim([-1.5, 1.5])
            ax1.set_ylim([-1.5, 1.5])
            ax1.set_zlim([-1.5, 1.5])
            ax1.set_xlabel('X')
            ax1.set_ylabel('Y')
            ax1.set_zlabel('Z')
            ax1.set_title('3D Orientation', fontsize=14, fontweight='bold')
            
            # Create board representation
            R = rotation_matrix(pitch, roll)
            
            # Define board corners (rectangular board)
            board_corners = np.array([
                [-1, -0.6, 0], [1, -0.6, 0], [1, 0.6, 0], [-1, 0.6, 0], [-1, -0.6, 0]
            ])
            
            # Rotate board
            rotated_corners = (R @ board_corners.T).T
            
            # Draw board
            ax1.plot(rotated_corners[:, 0], rotated_corners[:, 1], rotated_corners[:, 2], 
                    'b-', linewidth=3)
            ax1.plot([rotated_corners[0, 0], rotated_corners[2, 0]], 
                    [rotated_corners[0, 1], rotated_corners[2, 1]], 
                    [rotated_corners[0, 2], rotated_corners[2, 2]], 'b--', alpha=0.3)
            ax1.plot([rotated_corners[1, 0], rotated_corners[3, 0]], 
                    [rotated_corners[1, 1], rotated_corners[3, 1]], 
                    [rotated_corners[1, 2], rotated_corners[3, 2]], 'b--', alpha=0.3)
            
            # Draw axes
            axis_length = 1.2
            axes = np.array([[axis_length, 0, 0], [0, axis_length, 0], [0, 0, axis_length]])
            rotated_axes = (R @ axes.T).T
            
            colors = ['r', 'g', 'b']
            labels = ['X', 'Y', 'Z']
            for i in range(3):
                ax1.quiver(0, 0, 0, rotated_axes[i, 0], rotated_axes[i, 1], rotated_axes[i, 2],
                          color=colors[i], arrow_length_ratio=0.15, linewidth=2, label=labels[i])
            
            ax1.legend()
            
            # Update pitch bar
            pitch_bar[0].set_width(0.5)
            pitch_bar[0].set_y(pitch)
            pitch_bar[0].set_height(abs(pitch))
            pitch_bar[0].set_color('blue' if pitch >= 0 else 'orange')
            
            # Update roll bar
            roll_bar[0].set_width(0.5)
            roll_bar[0].set_y(roll)
            roll_bar[0].set_height(abs(roll))
            roll_bar[0].set_color('green' if roll >= 0 else 'purple')
            
            # Update text display
            text_display.set_text(f'Pitch: {pitch:6.2f}°\nRoll:  {roll:6.2f}°')
            
    except Exception as e:
        print(f"Error: {e}")
    
    return []

ani = FuncAnimation(fig, update, interval=50, blit=False)
plt.show()
