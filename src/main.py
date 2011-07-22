from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp

from git_http_protocol import GitRequest
import rpc

from gae_backend import Repo
from gae_backend import Repositories

import logging

class req(webapp.RequestHandler):
	def get(self, path):
		name = self.request.get('name', False)
		populate = self.request.get('populate', False)

		logging.error(name)
		logging.error(populate)

		if not name:
			return {"error":"no reponame provided"}
		repo = Repo.init_bare(name)

		if populate:
			from dulwich.objects import Blob
			blob = Blob.from_string("#include <iostream>\nusing namespace std;\n\nint main(){\nreturn 0;\n}\n")
			blob2 = Blob.from_string("#!/usr/bin/env python\n\nprint \"Hello World\"\n")

		from dulwich.objects import Tree
		tree = Tree()
		if populate:
			tree.add('main.cpp', 644, blob.id)
			tree.add('HelloWorld.py', 755, blob2.id)

		from dulwich.objects import Commit, parse_timezone
		from time import time
		commit = Commit()
		commit.tree = tree.id	#is the tree.id the sha1 of the files contained in tree
		author = "New Project Wizard <wizard@host>"
		commit.author = commit.committer = author
		commit.commit_time = commit.author_time = int(time())
		tz = parse_timezone('+1000')[0]
		commit.commit_timezone = commit.author_timezone = tz
		commit.encoding = "UTF-8"
		commit.message = "New Project."

		object_store = repo.object_store
		#loop through all files
		if populate:
			object_store.add_object(blob)
			object_store.add_object(blob2)
		#then add the tree
		object_store.add_object(tree)
		#then add the commit
		object_store.add_object(commit)

		repo.refs['refs/heads/master'] = commit.id

		return {"success":"%s.git created" % name}

def main():
	run_wsgi_app(
			webapp.WSGIApplication(
				[
					('/([A-Za-z0-9]*).git(/.*)', GitRequest),
					('/favicon.ico', webapp.RequestHandler),
					('/(.*)', rpc.Request),
				],
				debug=True,
			)
	)

if __name__ == "__main__":
	main()
