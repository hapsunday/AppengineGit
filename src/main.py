import rpc
import webapp2

class Web(webapp2.RequestHandler):
	def get(self, filereq=None):
		if filereq == '/index.html' or filereq == '/':
			self.response.headers['Content-Type'] = 'text/html'
			with open("rpc/rpc.html", "r") as f:
				self.response.out.write(f.read())
		else:
			self.error(404)
			

app = webapp2.WSGIApplication(
				[
					('/rpc/([A-Za-z\.]+)', rpc.Request),
					('(/.*)', Web),
				],
				debug=True,
		)
