"""
This file, written by Rohan Kapur
and Tanay Singhal, is the main Python
server where REST requests are made
from the frontend to process and respond
with a determinstic output.
"""

import json
import time
import BaseHTTPServer

HOST_NAME = 'localhost'
PORT_NUMBER = 8000

class RESTHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_HEAD(s):
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.end_headers()
	def do_GET(s):
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.end_headers()
		s.wfile.write("This is where the car driving Machine Learning and processing takes place (via POST requests).")
	def do_POST(s):
		content_len = int(s.headers.getheader('content-length', 0))
		post_body = s.rfile.read(content_len)
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
		s.wfile.write(json.dumps({}))

server_class = BaseHTTPServer.HTTPServer
httpd = server_class((HOST_NAME, PORT_NUMBER), RESTHandler)
httpd.serve_forever()