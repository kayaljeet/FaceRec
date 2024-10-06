# Face Recognition Application

In this project, socket programming is used to establish client-server connections to stream video inputs from multiple clients to a server device. The server then performs facial recognition on the received frames, obtaining the registered face images from an S3 bucket. Once a face is matched with a registered face, details such as the identified person’s name, client device name, and time of entry are stored in a JSON file, avoiding multiple spammed entries for a person by maintaining a buffer of 120 seconds for each individual. A Flask application running simultaneously displays the log entries on a web page as they get updated, allowing the viewer to sort through them as well. The server also displays the incoming video streams in imshow windows with a colored bounding box around the faces, showing details such as their name, with the color being either red or green depending on whether the individual is authorized or restricted.

## S3 Bucket Structure

```
Authorised/
    ├── person1.jpeg
    ├── person2.jpeg
    └── ...
Restricted/
    ├── person1.jpeg
    ├── person2.jpeg
```

## Contents

### 1) Client

- **client.py**: Socket program that sends a video stream and device name to the server.
- **config.txt**: Contains the host, port (of the server), and device name (client device).
- **requirements.txt**: Lists the required Python packages.

### 2) Server

- **static/css**
  - **style.css**: Stylesheet for the web application.
  
- **templates**
  - **error_page.html**: HTML page to display error messages.
  - **index.html**: HTML page to display entry logs.

- **app.py**: Flask application that reads logs from a JSON file, displays them on a webpage, and provides an option to filter through them.
- **exec.sh**: Script for running `main.py`.
- **exec_app.sh**: Script for running the Flask application.
- **main.py**: Socket program that connects to clients, receives video streams and device names, performs facial recognition, obtains registered faces from an S3 bucket, and stores the results in a JSON file along with a timestamp and device name.

### 3) Service

- **ScriptService.service**: Service script for managing the application.
