from rpc.component import Component, remote

class Auth(Component):
	def __init__(self):
		Component.__init__(self, "auth")
	
	@remote
	def login(self, username, password):
		import logging
		logging.error(username)
		logging.error(password)
	
	def addUser(self, username):
		import logging
		logging.error(username)
	
	@remote
	def changePassword(self, username, new_password):
		import logging
		logging.error(username)
		logging.error(new_password)