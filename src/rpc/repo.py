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
			repos.append({
				'name': item.key().name(),
			})
		return repos
	
	@remote
	def create(self, name):
		"""
		create a new repo
		
		:param name: the name to give the new repo
		:type name: string
		"""
		repo = Repo.init_bare(name)
		return {
			'errorno':0,
			'error':'successfully created %s' % name,
		}
	
	@remote
	def delete(self, name):
		"""
		delete an existing repo
		:param name: the name of the repo to delete
		:type name: string
		:return: an integer representing the result of the operation
		"""
		from google.appengine.ext import db
		from gae_backend import (
			Repositories,
			NamedFiles,
			PackStore,
			PackStoreIndex,
			References,
		)
		name_repo = Repositories.get_by_key_name(name)
		#clear named files
		query = db.Query(NamedFiles)
		query.filter('repository =', name_repo)
		db.delete(query)
		#clear packstore and packstore indexes
		stores = db.Query(PackStore)
		stores.filter('repository =', name_repo)
		for s in stores:
			query = db.Query(PackStoreIndex)
			query.filter('packref =', s)
			db.delete(query)
		db.delete(stores)
		#clear references
		query = db.Query(References)
		query.filter('repository =', name_repo)
		db.delete(query)
		#remove repository
		db.delete(name_repo)
		
		