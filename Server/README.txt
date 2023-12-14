Face Recognition Application:

In this project, using socket programming, a client-server connections are established, to stream video inputs from multiple clients to a server device, that then performs a facial recognition on the frames recieved, obtaining the registered faces’ images from a S3 bucket. Once the face is matched with a registered face, it then store details such as the identified person’s name, client device name, and time of entry into a json file, and avoiding multiple spammed entries on a person by keeping a buffer of 120s for each individual. A flask application that is running simultaneously, displays the log entries on a web page as the get updated, and allow the viewer to sort through them as well. The server also displays the incoming video streams in imshow windows with a coloured bounding box around the faces, with details such as their name and colour being either red or green, depending on whether the individual is authorised or restricted.

S3 bucket structure:

Authorised/person1.jpeg
Authorised/person2.jpeg
….
Restricted/person1.jpeg
Restricted/person2.jpeg


Contents:

1) Client:
	a) client.py:
		Socket program that sends a video stream and device name to Server
	b) config.txt:
		Stating the host, port (of server) and device name (client device)
	c) requirements.txt
2) Server:
	a) static/css
		i) style.css
	b) templates
		i) error_page.html
		ii) index.html:
			html page to display entry logs 
	c) app.py:
		Flask application to read logs from a json file, display them on a webpage and availing a option to filter through them
	d) exec.sh:
		for main.py
	e) exec_app.sh
	 f) main.py:
		Socket program to connect to clients and recieve video streams and device names, and perform facial recognition, obtaining the registered faces from a S3 bucket, and store the result in a json file along with a timestamp and device name
		
3) service:
	a) ScriptService.service

