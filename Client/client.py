import socket
import cv2
import pickle
import struct
import time

config_file = "config.txt"
config = {}
with open(config_file, "r") as file:
    for line in file:
        key, value = line.strip().split("=")
        config[key] = value

host = config.get('host')
port = int(config.get('port'))
camera_name = config.get('camera_name')

if host is None or port is None or camera_name is None:
    raise ValueError("Configuration values missing in config.txt")

def send_frame(ClientSocket, camera_name):
    vid = cv2.VideoCapture(0)
    while vid.isOpened():
        ret, frame = vid.read()
        if not ret:
            break
        frame = cv2.resize(frame, (320, 240))

        cv2.imshow('Sending Frame - ' + camera_name, frame)
        cv2.waitKey(1)  # Wait for a short time to update the display

        data = pickle.dumps((camera_name, frame))
        message = struct.pack("Q", len(data)) + data
        try:
            ClientSocket.sendall(message)
        except (socket.error, BrokenPipeError) as e:
            print(f"Connection to the server lost. Attempting to reconnect...")
            time.sleep(5)  # Wait for a few seconds before attempting to reconnect
            try:
                ClientSocket.connect((host, port))
                print(f"Reconnected to the server.")
            except socket.error as e:
                print(f"Error reconnecting to the server: {str(e)}")
                exit(1)

    vid.release()
    cv2.destroyAllWindows()

    cv2.destroyWindow('Sending Frame - ' + camera_name)
    ClientSocket.close()
ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

send_frame(ClientSocket, camera_name)
ClientSocket.close()
