import argparse
import socket
import cv2
import pickle
import struct
from _thread import *
import threading
import os
import face_recognition
import json
from datetime import datetime, timedelta
import boto3

last_entry_times = {}
host = '0.0.0.0'

folders = ["Authorized", "Restricted"]
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
known_face_encodings = []
known_face_names = []

for folder in folders:
    folder_path = os.path.join(os.getcwd(), folder)
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

parser = argparse.ArgumentParser(description="Face Recognition Server")
parser.add_argument("--bucketname", required=True, help="AWS S3 bucket name")
parser.add_argument("--access_key", required=True, help="AWS access key")
parser.add_argument("--secret_password", required=True, help="AWS secret password")
parser.add_argument("--port", type=int, default=8080, help="Port number to listen on")

args = parser.parse_args()

bucketname = args.bucketname
access_key = args.access_key
secret_password = args.secret_password
port = args.port

s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_password)

for folder in folders:
    objects = s3.list_objects(Bucket=bucketname, Prefix=folder)
    for obj in objects.get('Contents', []):
        key = obj['Key']
        filename = os.path.basename(key)
        local_path = os.path.join(os.getcwd(), folder, filename)
        s3.download_file(bucketname, key, local_path)

for folder in folders:
    for filename in os.listdir(folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            known_face_image = face_recognition.load_image_file(os.path.join(folder, filename))
            face_encodings = face_recognition.face_encodings(known_face_image)

            # Check if any face encodings were found in the image
            if face_encodings:
                face_encoding = face_encodings[0]
                known_face_encodings.append(face_encoding)
                known_face_names.append((os.path.splitext(filename)[0], folder))
            else:
                print(f"No face detected in {filename}")



def recognize_faces(frame, camera_name):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    log_entries = []

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.512)
        name = "Unknown"
        folder = None

        if True in matches:
            matched_indices = [i for i, match in enumerate(matches) if match]
            first_match_index = matched_indices[0]
            name, folder = known_face_names[first_match_index]

        if name == "Unknown":
            rectangle_color = (0, 255, 255)  # Yellow rectangle for unknown people
        else:
            rectangle_color = (0, 255, 0) if folder == "Authorized" else (0, 0, 255)  # Green or Red rectangle

        cv2.rectangle(frame, (left, top), (right, bottom), rectangle_color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, rectangle_color, 2)

        log_entry = {
            "Name": name,
            "Category": folder,
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "Camera ID": camera_name
        }
        if name == "Unknown":
            continue  # Skip processing entries for unknown people

            # Get the last entry time for the current person on the current camera
        last_entry_time = last_entry_times.get((name, camera_name))

        # If last entry time exists and at least 1 minute has not passed, skip adding the entry
        if last_entry_time is not None:
            current_time = datetime.now()
            time_since_last_entry = current_time - last_entry_time
            if time_since_last_entry < timedelta(minutes=1):
                continue

        # Update the last entry time for the current person on the current camera
        last_entry_times[(name, camera_name)] = datetime.now()

        log_entry = {
            "Name": name,
            "Category": folder,
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "Camera ID": camera_name
        }
        log_entries.append(log_entry)

    with open("log.json", "a") as log_file:
        for entry in log_entries:
            json.dump(entry, log_file)
            log_file.write("\n")

    return frame

def client_handler(connection):
    global camera_name
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        try:
            while len(data) < payload_size:
                packet = connection.recv(4 * 1024)  # 4K
                if not packet:
                    break
                data += packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += connection.recv(4 * 1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]

            camera_name, frame = pickle.loads(frame_data)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            frame_with_recognition = recognize_faces(frame, camera_name)

            cv2.imshow(camera_name, frame_with_recognition)
            cv2.waitKey(1)

        except Exception as e:
            print(f"Client {camera_name} disconnected - exception {e}")
            cv2.destroyWindow(camera_name)
            break

    connection.close()


def accept_connections(ServerSocket):
   while True:
        Client, address = ServerSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        #start_new_thread(client_handler, (Client, )) #for handling multiple clients
        thread = threading.Thread(target=client_handler(Client))
        print('Total Clients', threading.active_count()-1)
        #client_handler(Client)


def start_server(host, port):
    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))
    print(f'Server is listening on port {port}...')
    ServerSocket.listen()

    while True:
        accept_connections(ServerSocket)


start_server(host, port)
