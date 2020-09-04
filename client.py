from videostream import VideoStream
import sys
import socket
import time
import struct
import gzip
import imutils
import cv2
import numpy as np

import asyncio
import websockets


class Pack:
	def __init__(self):
		self.content = []

	def add(self, frame):
		self.content.append(frame)

	def generate(self):
		data = b""

		for frame in self.content:
			fby = cv2.imencode(".png", frame)[1].tostring()
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
			if len(data[i:i+8]) == 0:
				break

			lenframe = struct.unpack("l", data[i:i+8])[0]  # struct L length
			print(lenframe)
			frames.append(cv2.imdecode(np.fromstring(data[i+8:i+8+lenframe], np.uint8), cv2.IMREAD_COLOR))
			i += 8 + lenframe

		return frames


# rtsp://admin:sapebc@192.168.3.194:554//h264Preview_01_main

rpiName = socket.gethostname()

with open("ips.txt", "r") as readFile:
	readFileData = readFile.read()

logs = open("logs.txt", "a")
sys.stdout = logs
sys.stderr = logs


cameraIPs = [x for x in readFileData.split("\n") if x != ""]
videoStreams = [VideoStream(src=y).start() for y in cameraIPs]

# Si resolution plus basse ajouter , resolution=(320, 240)
# vs = VideoStream(usePiCamera=True).start()

time.sleep(2.0)

async def flux():
    uri = "wss://prescient2.cfapps.eu10.hana.ondemand.com/ws"
    async with websockets.connect(uri) as websocket:
        while True:
        
            pack = Pack()
            for vs in videoStreams:
                pack.add(vs.read())
        
            await websocket.send(pack.generate())
            print("Pack sent !")

            greeting = await websocket.recv()
            print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(flux())
