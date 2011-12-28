import rpc
import webapp2

class Web(webapp2.RequestHandler):
	def get(self):
		self.response.out.write("Under Development")

app = webapp2.WSGIApplication(
				[
					('/rpc/([A-Za-z\.]+)', rpc.Request),
					('/.*', Web),
				],
				debug=True,
		)
