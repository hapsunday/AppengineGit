from git_http_protocol import GitRequest
import rpc
import webapp2

class Web(webapp2.RequestHandler):
	def get(self):
		self.response.out.write("Under Development")

p = webapp2.WSGIApplication(
				[
					('/([A-Za-z0-9]+).git(/.*)', GitRequest),
					('/rpc/([A-Za-z\.]+)', rpc.Request),
					('/.*', Web),
				],
				debug=True,
		)
