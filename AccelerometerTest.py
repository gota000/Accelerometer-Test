# Raspberry Pi Sender (send_data.py)
import smbus2  # needed for communicating over i2c in the pi
import socket  # creates the TCP server to communicate with the laptop
import time

bus = smbus2.SMBus(1)  # initilizes the i2c bus with the normal bus address
BMA250_I2C_ADDR = 0x18  # default address of the accelerometer
BMA250_REG_DATA_X_LSB = 0x02

s = socket.socket(socket.AF_INET,
                  socket.SOCK_STREAM)  # creates a new socket to communicate and it is ipv4 and TCP (more reliable than UDP)
s.bind(('0.0.0.0',
        5005))  # binds to address and port, 0.0.0.0 means listen to all interfaces and both client and server have to connect to 5005
s.listen(1)  # the server waits for one connection

conn, addr = s.accept()  # pauses code until connection, once the server connects conn becomes the new socket and addr is the ip address

while True:
    # reads data at the address and it reads 6 bytes of data
    data = bus.read_i2c_block_data(BMA250_I2C_ADDR, BMA250_REG_DATA_X_LSB, 6)
    # converts data into integer values
    x = ((data[1] << 8) | data[0]) >> 4
    y = ((data[3] << 8) | data[2]) >> 4
    z = ((data[5] << 8) | data[4]) >> 4
    # sends these data to the client and is incoded in UTF-8
    conn.send(f"{x},{y},{z}\n".encode())
    time.sleep(0.05)
