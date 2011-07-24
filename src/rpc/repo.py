from rpc.component import Component, remote
from gae_backend import Repo

class RepoManager(Component):
	def __init__(self):
		Component.__init__(self, "repo")
	
	@remote
	def list(self):
		"""
		lists all the repos hosted on the server
		"""
		from google.appengine.ext import db
		from gae_backend import Repositories
		repos = []
		for item in db.Query(Repositories):
			repos.append( item.key().name() )
		return repos
	
	@remote
	def create(self, name):
		"""
		create a new repo
		
		:param name: the name to give the new repo
		:type name: string
		"""
		repo = Repo.init_bare(name)
	
		from dulwich.objects import Tree
		tree = Tree()
		
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

		#then add the tree
		object_store.add_object(tree)
		#then add the commit
		object_store.add_object(commit)
		
		repo.refs['refs/heads/master'] = commit.id
		
		return {"success":"%s.git created" % name}