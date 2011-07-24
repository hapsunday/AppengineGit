from rpc.component import Component, remote

class AuthManager(Component):
	def __init__(self):
		Component.__init__(self, "auth")
	
	@remote
	def login(self, username, password):
		import logging
		logging.error("auth.login not implemented")
	
	@remote	
	def addUser(self, username):
		import logging
		logging.error("auth.addUser not implemented")
	
	@remote
	def changePassword(self, username, new_password):
		import logging
		logging.error("auth.changePassword not implemented")