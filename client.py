from videostream import VideoStream
import sys
import socket
import requests
import time
import struct
import gzip
import imutils
import cv2
import numpy as np


class Pack:
	def __init__(self):
		self.content = []

	def add(self, frame):
		self.content.append(cv2.resize(frame, (720, 480)))

	def generate(self):
		data = b""

		for frame in self.content:
			fby = cv2.imencode(".jpg", frame)[1].tostring()
			lencompf = struct.pack("l", len(fby))

			data += lencompf + fby

		data = gzip.compress(data)
		print("TOTAL : " + str(len(data)))
		return data

	@staticmethod
	def retrieve(data):
		frames = []
		i = 0

		data = gzip.decompress(data)
		lendata = len(data)

		while i <= lendata:
			if len(data[i:i+4]) == 0:
				break

			lenframe = struct.unpack("l", data[i:i+4])[0]  # struct L length
			frames.append(cv2.imdecode(np.fromstring(data[i+4:i+4+lenframe], np.uint8), cv2.IMREAD_COLOR))
			i += 4 + lenframe

		return frames


# rtsp://admin:sapebc@192.168.3.194:554//h264Preview_01_main

rpiName = socket.gethostname()

with open("ips.txt", "r") as readFile:
	readFileData = readFile.read()

logs = open(logs.txt, "a")
sys.stdout = logs
sys.stderr = logs


cameraIPs = [x for x in readFileData.split("\n") if x != ""]
videoStreams = [VideoStream(src=y).start() for y in cameraIPs]

# Si resolution plus basse ajouter , resolution=(320, 240)
# vs = VideoStream(usePiCamera=True).start()

time.sleep(2.0)

with requests.session() as session:
	while True:
		pack = Pack()

		for vs in videoStreams:
			pack.add(vs.read())

		session.post("https://prescient.cfapps.eu10.hana.ondemand.com/pack", data=pack.generate())
		
		time.sleep(0.25)
