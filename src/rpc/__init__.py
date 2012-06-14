import re

import webapp2

from rpc.component import componentManager
from rpc.repo import RepoManager
RepoManager()

import json

class Request(webapp2.RequestHandler):
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
