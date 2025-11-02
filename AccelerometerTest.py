# Raspberry Pi Sender (send_data.py)
import smbus2  # needed for communicating over i2c in the pi
import socket  # creates the TCP server to communicate with the laptop
import time
import math

bus = smbus2.SMBus(1)  # initilizes the i2c bus with the normal bus address
# run "i2cdetect -y 1" to find it
BMA250_I2C_ADDR = 0x18  # default address of the accelerometer
BMA250_REG_DATA_X_LSB = 0x02

s = socket.socket(socket.AF_INET,
                  socket.SOCK_STREAM)  # creates a new socket to communicate and it is ipv4 and TCP (more reliable than UDP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address if the address is still in use
s.bind(('0.0.0.0',
        5005))  # binds to address and port, 0.0.0.0 means listen to all interfaces and both client and server have to connect to 5005
s.listen(1)  # the server waits for one connection

print("Waiting for connection with the laptop client")
conn, addr = s.accept()  # pauses code until connection, once the server connects conn becomes the new socket and addr is the ip address

while True:
    # reads data at the address and it reads 6 bytes of data
    data = bus.read_i2c_block_data(BMA250_I2C_ADDR, BMA250_REG_DATA_X_LSB, 6)
    # converts data into integer values
    x_raw = ((data[1] << 8) | data[0]) >> 4
    y_raw = ((data[3] << 8) | data[2]) >> 4
    z_raw = ((data[5] << 8) | data[4]) >> 4
    
    # Handle signed values (12-bit two's complement)
    if x_raw > 2047:
        x_raw -= 4096
    if y_raw > 2047:
        y_raw -= 4096
    if z_raw > 2047:
        z_raw -= 4096
    
    # Convert to g values with a +-2g
    x_g = x_raw * 2.0 / 2048
    y_g = y_raw * 2.0 / 2048
    z_g = z_raw * 2.0 / 2048
    
    # Calculate pitch and roll in degrees
    pitch = math.atan2(x_g, math.sqrt(y_g**2 + z_g**2)) * 180 / math.pi
    roll = math.atan2(y_g, math.sqrt(x_g**2 + z_g**2)) * 180 / math.pi
    
    # sends pitch roll to the client encoded in UTF-8
    conn.send(f"{pitch:.2f},{roll:.2f}\n".encode())
    time.sleep(0.05)
