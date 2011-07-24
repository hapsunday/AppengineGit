from google.appengine.ext import webapp
from rpc.component import componentManager
from rpc.auth import AuthManager
AuthManager()
from rpc.repo import RepoManager
RepoManager()
from django.utils import simplejson as json

class Request(webapp.RequestHandler):
	def get(self, path=None):
		"""
		@todo: remove the contents of this function and return a 404
		the contents of this function make it easier to send post requests and need to be removed
		"""
		self.response.headers['Content-Type'] = 'text/html'
		self.response.out.write("""
			<form action="/" method="POST">
				<label style="display:block;">Method: <input type="text" name="method" value="auth.login"/></label>
				<label style="display:block;">Args: <input type="text" name="args" style="width:500px;" value='{"username":"myname","password":"mypass"}'/></label>
				<label style="display:block;"><input type="submit" name="submit" value="submit"/></label>
			</form>
		""")
	
	def post(self, path=None):
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
		response = componentManager.call(method, args)
		self.response.out.write( json.dumps( response ) )
