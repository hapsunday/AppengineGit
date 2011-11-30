import re

import webapp2

from rpc.component import componentManager
from rpc.auth import AuthManager
AuthManager()
from rpc.repo import RepoManager
RepoManager()

import json

class Request(webapp2.RequestHandler):
	def get(self, filereq=None):
		if filereq == 'index.html':
			self.response.headers['Content-Type'] = 'text/html'
			self.response.out.write("""
				<!DOCTYPE html>
				<html>
					<head>
						<title>Git RPC interface</title>
						<style type="text/css">
							label {
								display:block;
							}
						</style>
						<script type="text/javascript" src="/rpc/rpc.js"></script>
					</head>
					<body>
						<p>Use a javascript console to send messages to the server</p>
						<pre id="response"></pre>
					</body>
				</html>
			""")
		elif filereq == 'rpc.js':
			f = open('rpc/rpc.js', 'r')
			self.response.headers['Content-Type'] = 'text/javascript'
			self.response.out.write(f.read())
			f.close()
		else:
			self.error(404)
	
	def post(self, method=None):
		#make sure there is a method
		if method==None:
			self.error(404)

		#parse arguments
		regex = re.compile('([A-Za-z0-9]+)=([A-Za-z0-9]+)\&?')
		args = {}
		for arg in regex.findall(self.request.body):
			args[arg[0]] = arg[1]

		response = componentManager.call(method, args)
		self.response.out.write( json.dumps( response ) )
