import webapp2

from dulwich.server import DEFAULT_HANDLERS, Backend
from dulwich.protocol import ReceivableProtocol

from gae_backend import Repo
from gae_backend import Repositories

import logging

class AppengineBackend(Backend):
	def open_repository(self, name):
		return Repo(name)

class GitRequest(webapp2.RequestHandler):
	"""
		@todo: check to see how much of the service request I can move to a separate function
	"""
	REPO = Repo
	def get(self, repo, path):
		"""
			Responds to the dumb git protocol
			to my knowledge the dumb git protocol only uses GET requests
			however we need to tell git that the smart protocol is available
		"""
		if path == '/info/refs':
			service = self.request.get('service', None)
			handler_cls = DEFAULT_HANDLERS.get(service, None)
			if handler_cls:
				self.response.headers['Content-Type'] = str('application/x-%s-advertisement' % service)
				#@todo: set headers to prevent page caching
				proto = ReceivableProtocol(self.request.body_file.read, self.response.out.write)
				handler = handler_cls(AppengineBackend(), [repo], proto, stateless_rpc=True, advertise_refs=True)
				handler.proto.write_pkt_line('# service=%s\n' % service)
				logging.info('# service=%s\n' % service)
				handler.proto.write_pkt_line(None)
				handler.handle()

			else:
				self.response.out.write('Unsupported service %s' % service)
				return
		else:
			self.response.out.write("This page responds to git dumb prototcol requests")
			raise NotImplementedError("the git (dumb) http protocol not implemented yet")
			
	
	def post(self, repo, path):
		"""
			Responds to the smart git protocol
		"""
		service = path.lstrip('/')
		handler_cls = DEFAULT_HANDLERS.get(service, None)
		if handler_cls:
			self.response.headers['Content-Type'] = 'application/x-%s-advertisement' % service
			#@todo: set headers to prevent page caching
			proto = ReceivableProtocol(self.request.body_file.read, self.response.out.write)
			handler = handler_cls(AppengineBackend(), [repo], proto, stateless_rpc=True)
			handler.handle()
		else:
			self.response.out.write('Unsupported service %s' % service)
			return


