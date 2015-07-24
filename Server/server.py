"""
This file, written by Rohan Kapur
and Tanay Singhal, is the main Python
server where REST requests are made
from the frontend to process and respond
with a determinstic output.
"""

import learning
import BaseHTTPServer
import json

HOST_NAME = 'localhost'
PORT_NUMBER = 8000

# API Routes
SEND_DRIVING_DATA_ROUTE = '/sendDrivingData'
GET_DRIVING_DATA_ROUTE = '/getDrivingData'
WIPE_HISTORY_ROUTE = '/wipeHistory'

# Driving Control Types
DRIVING_CONTROL_TYPE_MOTION = 'motion'

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
		if not hasattr(self, 'learningServer'):
			self.learningServer = LearningServer()
		body = json.loads(self.rfile.read(int(self.headers.getheader('Content-Length', 0))))
		path = self.path
		response = self.learningServer.handleRequest(path, body)
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
	def handleRequest(self, path, body):
		response = {}
		error = False
		if path == SEND_DRIVING_DATA_ROUTE:
			if body['type'] == DRIVING_CONTROL_TYPE_MOTION:
				self.motionHandler.receivedNewMotionData(body['data'])
		elif path == GET_DRIVING_DATA_ROUTE:
			if body['type'] == DRIVING_CONTROL_TYPE_MOTION:
				response = self.motionHandler.suggestedMotionResponseFromData(body['data'])
		elif path == WIPE_HISTORY_ROUTE:
			if body['type'] == DRIVING_CONTROL_TYPE_MOTION:
				self.motionHandler.wipe()
		return {'data': response, 'error': error}

server_class = BaseHTTPServer.HTTPServer
httpd = server_class((HOST_NAME, PORT_NUMBER), RequestHandler)
httpd.serve_forever()