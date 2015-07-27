"""
This file, written by Rohan Kapur
and Tanay Singhal, is the main Python
server where REST requests are made
from the frontend to process and respond
with a determinstic output.
"""

from multiprocessing import Process
import BaseHTTPServer
import json
import learning

HOST_NAME = 'localhost'
PORT_NUMBER = 8000

# API Routes
SEND_DRIVING_DATA_ROUTE = '/sendDrivingData'
GET_DRIVING_DATA_ROUTE = '/getDrivingData'

# Driving Control Types
DRIVING_CONTROL_TYPE_MOTION = 'motion'
DRIVING_CONTROL_TYPE_STEERING = 'steering'

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-Type", "text/html")
		self.end_headers()
	def do_GET(self):
		self.send_response(200)
		self.send_header("Content-Type", "text/html")
		self.end_headers()
		self.wfile.write("This is where the car driving Machine Learning and processing takes place (via POST requests).")
	def do_POST(self):
		body = json.loads(self.rfile.read(int(self.headers.getheader('Content-Length', 0))))
		path = self.path
		response = learningServer.handleRequest(path, body)
		responseData = response['data']
		error = response['error']
		if error:
			self.send_response(400)
		else:
			self.send_response(200)
		self.send_header("Content-Type", "application/json")
		self.end_headers()
		self.wfile.write(json.dumps(responseData))

class LearningServer():
	def __init__(self):
		self.motionHandler = learning.MotionHandler()
		self.steeringHandler = learning.SteeringHandler()
	def handleRequest(self, path, body):
		response = {}
		error = False
		types = body['types']
		if path == SEND_DRIVING_DATA_ROUTE:
			if DRIVING_CONTROL_TYPE_MOTION in types:
				self.motionHandler.receivedNewMotionData(body['data'])
			if DRIVING_CONTROL_TYPE_STEERING in types:
				self.steeringHandler.receivedNewSteeringData(body['data'])
		elif path == GET_DRIVING_DATA_ROUTE:
			if DRIVING_CONTROL_TYPE_MOTION in types:
				response.update(self.motionHandler.suggestedMotionResponseFromData(body['data']))
			if DRIVING_CONTROL_TYPE_STEERING in types:
				response.update(self.steeringHandler.suggestedSteeringResponseFromData(body['data']))
		return {'data': response, 'error': error}

if __name__ == "__main__":
	learningServer = LearningServer()

server_class = BaseHTTPServer.HTTPServer
httpd = server_class((HOST_NAME, PORT_NUMBER), RequestHandler)
httpd.serve_forever()
