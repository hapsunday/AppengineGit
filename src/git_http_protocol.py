from dulwich.web import HTTPGitApplication
from dulwich.server import Backend

from gae_backend import Repo

import re

class AppengineBackend(Backend):
	@classmethod
	def open_repository(cls, path):
		regex = re.compile('/([A-Za-z0-9]+).git')
		results = regex.findall(path)
		name = results[0]
		return Repo(name)

app = HTTPGitApplication(AppengineBackend)