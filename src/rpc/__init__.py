from google.appengine.ext import webapp
from rpc import component
from rpc import auth
auth.Auth()
from django.utils import simplejson as json

class Request(webapp.RequestHandler):
	def get(self, path):
		self.response.headers['Content-Type'] = 'text/html'
		self.response.out.write("""
			<form action="/" method="POST">
				<label style="display:block;">Method: <input type="text" name="method" value="auth.login"/></label>
				<label style="display:block;">Args: <input type="text" name="args" style="width:500px;" value='{"username":"myname","password":"mypass"}'/></label>
				<label style="display:block;"><input type="submit" name="submit" value="submit"/></label>
			</form>
		""")
	
	def post(self, path):
		method = self.request.get('method', False)
		s_args = self.request.get('args', False)
		if method == False or s_args == False:
			self.error(404)
		"@todo: there must be a better way to convert unicode to utf-8, especially for the dict"
		ENCODING = 'utf-8'
		method = method.encode(ENCODING)
		args = {}
		for key, val in json.loads(s_args).iteritems():
			if type(key) == type(u''):
				key = key.encode(ENCODING)
			if type(val) == type(u''):
				val = val.encode(ENCODING)
			args[key] = val
		return component.registry.call(method, args)
