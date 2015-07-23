"""
This file, written by Rohan Kapur
and Tanay Singhal, is the main Python
server where REST requests are made
from the frontend to process and respond
with a determinstic output.
"""

import BaseHTTPServer
import json

HOST_NAME = 'localhost'
PORT_NUMBER = 8000

class RESTHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
	def do_GET(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write("This is where the car driving Machine Learning and processing takes place (via POST requests).")
	def do_POST(self):
		content_len = int(self.headers.getheader('content-length', 0))
		post_body = self.rfile.read(content_len)
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(json.dumps({}))

server_class = BaseHTTPServer.HTTPServer
httpd = server_class((HOST_NAME, PORT_NUMBER), RESTHandler)
httpd.serve_forever()