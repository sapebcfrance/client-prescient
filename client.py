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


# rtsp://admin:sapebc@192.168.3.194:554//h264Preview_01_main

rpiName = socket.gethostname()

with open("ips.txt", "r") as readFile:
	readFileData = readFile.read()

sys.stdout = open("logs.txt", "a")


cameraIPs = [x for x in readFileData.split("\n") if x != ""]
videoStreams = [VideoStream(src=y).start() for y in cameraIPs]


await asyncio.sleep(2.0)


async def cam0():
	uri = "wss://prescient.cfapps.eu10.hana.ondemand.com/ws/0"
	async with websockets.connect(uri, max_size=2**30, close_timeout=30) as websocket:
		while True:
			frame = videoStreams[0].read()
			await websocket.send(np.frombuffer(cv2.imencode(".jpg", frame)[1], dtype=np.uint8).tobytes())
			print("CAM 0 SENT")
			greeting = await websocket.recv()
			print(f"< {greeting}")


async def cam1():
	uri = "wss://prescient.cfapps.eu10.hana.ondemand.com/ws/1"
	async with websockets.connect(uri, max_size=2**30, close_timeout=30) as websocket:
		while True:
			frame = videoStreams[1].read()
			await websocket.send(np.frombuffer(cv2.imencode(".jpg", frame)[1], dtype=np.uint8).tobytes())
			print("CAM 1 SENT")
			greeting = await websocket.recv()
			print(f"< {greeting}")


async def cam2():
	uri = "wss://prescient.cfapps.eu10.hana.ondemand.com/ws/2"
	async with websockets.connect(uri, max_size=2**30, close_timeout=30) as websocket:
		while True:
			frame = videoStreams[2].read()
			await websocket.send(np.frombuffer(cv2.imencode(".jpg", frame)[1], dtype=np.uint8).tobytes())
			print("CAM 2 SENT")
			greeting = await websocket.recv()
			print(f"< {greeting}")


loop = asyncio.get_event_loop()
cors = asyncio.wait([cam0(), cam1(), cam2()])
loop.run_until_complete(cors)
