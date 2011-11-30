from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2

from git_http_protocol import GitRequest
import rpc

from gae_backend import Repo
from gae_backend import Repositories

import logging

class derp(webapp2.RequestHandler):
	def get(self):
		self.response.out.write("hello world")

p = webapp2.WSGIApplication(
				[
					('/([A-Za-z0-9]+).git(/.*)', GitRequest),
					('/favicon.ico', derp),
					('/rpc/([A-Za-z\.]+)', rpc.Request),
				],
				debug=True,
		)
