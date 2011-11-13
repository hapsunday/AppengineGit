from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp

from git_http_protocol import GitRequest
import rpc

from gae_backend import Repo
from gae_backend import Repositories

import logging

def main():
	run_wsgi_app(
			webapp.WSGIApplication(
				[
					('/([A-Za-z0-9]+).git(/.*)', GitRequest),
					('/favicon.ico', webapp.RequestHandler),
					('/rpc/([A-Za-z\.]+)', rpc.Request),
				],
				debug=True,
			)
	)

if __name__ == "__main__":
	main()
