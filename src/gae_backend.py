#python imports
import os
#dulwich inports
from dulwich.repo import (
	SYMREF,
	BaseRepo,
	RefsContainer as BaseRefsContainer,
)
from dulwich.object_store import PackBasedObjectStore
from dulwich.pack import (
	Pack as DulwichPack,
	PackIndex as DulwichPackIndex,
	PackData as DulwichPackData,
#	ThinPackData,
#	write_pack_data,
	iter_sha1,
	write_pack_header,
	write_pack_object,
	compute_file_sha,
	PackIndexer,
	PackStreamCopier,
)
from dulwich.objects import (
	ShaFile,
	sha_to_hex,
	hex_to_sha,
)
from dulwich.errors import (
    MissingCommitError,
    NoIndexPresent,
    NotBlobError,
    NotCommitError,
    NotGitRepository,
    NotTreeError,
    NotTagError,
    PackedRefsException,
    CommitError,
    RefFormatError,
    ChecksumMismatch
   )
#appengine imports
from google.appengine.ext import (
	db,
	blobstore,
)
from google.appengine.api import files
#python imports
from StringIO import StringIO
import logging

#baseRepo
class Repositories(db.Model):
	pass

class NamedFiles(db.Model):
	repository = db.ReferenceProperty(Repositories)
	filename = db.StringProperty()
	contents = db.TextProperty()

class Repo(BaseRepo):
	"""
		Class for repositories on google appengine
		:param RepoName: String, open the repo with name String
	"""
	def __init__(self, RepoName):
		repo = Repositories.get_by_key_name(RepoName)
		if repo:
			self.REPO_NAME = RepoName
			self.REPO = Repositories.get_by_key_name(self.REPO_NAME)
			self.Bare = True
			object_store = ObjectStore(self.REPO)
			refs_container = RefsContainer(self.REPO)
			BaseRepo.__init__(self, object_store, refs_container)
		else:
			raise NotGitRepository(RepoName)
	
	def get_named_file(self, fname):
		"""
			get a file from the database keyed by path
			the table is set out similar to a key value table
			:param fname: the key of a key value pair
		"""

		obj = db.Query(NamedFiles)
		obj.filter('repository =', self.REPO)
		obj.filter('filename =', fname)

		if obj.count(1): #exists
			f = obj.get()
			return StringIO(f.contents)
		else:
			return None

	def _put_named_file(self, fname, contents):
		"""
			save a file in the datastore containing contents and keyed by path
			the table is set out similar to a key value table
			:param fname: the key
			:param contents: the value corresponding to key
		"""
		obj = db.Query(NamedFiles)
		obj.filter('repository =', self.REPO)
		obj.filter('filename =', fname)

		if obj.count(1): #exists
			f = obj.get()
			f.contents = contents
			f.put()
		else:
			NamedFiles(
				repository = self.REPO,
				filename = fname,
				contents = contents,
			).put()

	def head(self):
		"""
			return the sha pointed at head
			:return: string hex encoded sha
		"""
		HEAD = self.refs['HEAD']
		return HEAD

	def open_index(self):
		"""
			this is a bare repo which doesn't have an index
			an index is used in a working repo to keep a record of changes to files,
			thus saving git having to scan all the files for changes at commit time
			I'm assuming the index is updated when running git add
			
			as this is a server, it does not have a working tree and hence does not have an index
		"""
		raise NoIndexPresent()
	
	@classmethod
	def init_bare(cls, RepoName):
		"""
			creates a new repository with name RepoName
			:param RepoName: the name of the new repo
			:return: a AppengineRepo class object
		"""
		Repositories(
			key_name = RepoName,
		).put()
		repo = cls(RepoName)
		repo.refs.set_symbolic_ref("HEAD", "refs/heads/master")
		repo._init_files(bare=True)
		return repo
		

#object/pack store
#objects reference the blob, not the other way round
class PackStore(db.Model):
	repository = db.ReferenceProperty(Repositories)
	sha1 = db.StringListProperty()
	data = blobstore.BlobReferenceProperty()
	size = db.IntegerProperty()
	checksum = db.BlobProperty()

class PackStoreIndex(db.Model):
	"""
		This is needed, pack indexes are stored in a separate file. This table is that separate file
		The indexes appear to be a cache (of sorts) as the index data can be created from the pack data
	"""
	packref = db.ReferenceProperty(PackStore)
	sha = db.StringProperty() #@TODO: should be a binary property, the sha is not hex encoded
	offset = db.IntegerProperty()
	crc32 = db.IntegerProperty()

class ObjectStore(PackBasedObjectStore):
	""" object store interface """
	def __init__(self, Repo):
		"""
			specifies which repository the object store should use
			:param REPO_NAME: the name of the repository object_store should access
		"""
		self.REPO = Repo
		super(ObjectStore, self).__init__()
	
	#def alternatives(self):
	
	#def contains_packed(self, sha):
	
	def _load_packs(self):
		q = db.Query(PackStore)
		q.filter('repository =', self.REPO)
		ret = []
		for p in q:
			ret.append( Pack(p) )
		return ret
	
	def _pack_cache_stale(self):
		if self._pack_cache != None:
			return True
		else:
			return False
	
	#def _add_known_pack(self, pack):
	
	#def packs(self):
	
	def _iter_loose_objects(self):
		"""
			Iterate over the SHAs of all loose objects.
			we don't have loose objects so return an empty iter
		"""
		return [].__iter__()
		

	def _get_loose_object(self, sha):
		"""
			return the object with given sha.
			we don't have loose objects so always None
		"""
		return None

	def _remove_loose_object(self, sha):
		"""this shouldn't be called"""
		raise NotImplementedError(self._remove_loose_object)
	
	def pack_loose_objects(self):
		logging.error('attempting to pack loose objects')
		super(ObjectStore, self).pack_loose_objects()
	
	#def __iter__(self):
	
	#def contains_loose(self, sha):

	def get_raw(self, name):
		return super(ObjectStore, self).get_raw(name)

	#def add_object(self, object):
		#implemented in BaseObjectStore
	
	#def add_objects(self, objects):
	
	def add_pack(self):
		raise NotImplementedError(self.add_pack)
	
	def _complete_thin_pack(self, f, path, copier, indexer):
		"taken from dulwich.object_store.DiskObjectStore._complete_thin_pack"
		"""Move a specific file containing a pack into the pack directory.

		:note: The file should be on the same file system as the
			packs directory.

		:param f: Open file object for the pack.
		:param path: Path to the pack file.
		:param copier: A PackStreamCopier to use for writing pack data.
		:param indexer: A PackIndexer for indexing the pack.
		"""

	
	def add_thin_pack(self, read_all, read_some):
		f = StringIO()
		indexer = PackIndexer(f, resolve_ext_ref=self.get_raw)
		copier = PackStreamCopier(read_all, read_some, f, delta_iter=indexer)
		copier.verify()
		pack_store = PackStore(repository=self.REPO)
		final_pack = Pack.from_thinpack(pack_store, f, indexer, resolve_ext_ref=self.get_raw)
		self._add_known_pack(final_pack)
	
#	def add_thin_pack(self):
#		"""
#			A pack is a single file containing multiple objects
#			A pack contains a list of references to objects inside the pack
#			this is done to save parsing through the entire file to find all the objects
#			
#			The difference between a pack and thin pack is thin packs contain references
#			to objects which may not be stored in the pack, rather git must refer to the repository
#			which contains the referenced object as either a loose object or a pack
#			
#			DiskObjectStore, which I used as a reference for this function creates a full pack.
#			Here I extract all the objects and store them as loose objects in the datastore, similar to
#			how memory object store works
#		"""
#		fileContents = StringIO("")
#		def newcommit():
#			try:
#				#write the new pack
#				logging.error('starting the write')
#				#creating a copy of fileContents is done to move the file pointer back to the beginning
#				fileContents.seek(0,2)
#				tempstring = StringIO(fileContents.getvalue())
#				ThinPack = ThinPackData(self.get_raw, filename=None, file=tempstring, size=fileContents.tell())
#				store = PackStore(repository = self.REPO)
#				store.size = fileContents.tell()
#				store.save()
#				p = Pack.Create(store, ThinPack)
#			except:
#				import traceback
#				traceback.print_exc()
#				raise CommitError
#			return p
#		return fileContents, newcommit
	

class Pack(DulwichPack):
	"""
		What I want this class to do
			- return a dulwich.pack.Pack object from a blobstore key
			- generate a new pack dulwich.pack.Pack from a ThinPackData
	"""
	@classmethod
	def from_thinpack(cls, pack_store, f, indexer, resolve_ext_ref):
		entries = list(indexer)

		# Update the header with the new number of objects.
		f.seek(0)
		write_pack_header(f, len(entries) + len(indexer.ext_refs()))

		# Rescan the rest of the pack, computing the SHA with the new header.
		new_sha = compute_file_sha(f, end_ofs=-20)

		# Complete the pack.
		for ext_sha in indexer.ext_refs():
			assert len(ext_sha) == 20
			type_num, data = resolve_ext_ref(ext_sha)
			offset = f.tell()
			crc32 = write_pack_object(f, type_num, data, sha=new_sha)
			entries.append((ext_sha, offset, crc32))
		pack_sha = new_sha.digest()
		f.write(pack_sha)
		#f.close()
		
		#write the pack
		blob_name = files.blobstore.create(mime_type='application/octet-stream')
		with files.open(blob_name, 'a') as blob:
			blob.write(f.getvalue())
		files.finalize(blob_name)
		
		#store pack info
		pack_store.data = files.blobstore.get_blob_key(blob_name)
		#pack_store.sha1 = [entries.name]
		pack_store.size = f.tell()
		pack_store.checksum = sha_to_hex(pack_sha)
		pack_store.save()

		# Write the index.
		pack_indexes = [pack_store]
		for (name, offset, entry_checksum) in entries:
			idx = PackStoreIndex(
					packref = pack_store,
					sha = sha_to_hex(name),
					offset = offset,
					crc32 = entry_checksum
				)
			pack_store.sha1.append( sha_to_hex(name) )
			pack_indexes.append(idx)
		db.save(pack_indexes)

		# Add the pack to the store and return it.
		final_pack = Pack(pack_store)
		final_pack.check_length_and_checksum()
		return final_pack
	
	""" this was commented out for committing """
	def __init__(self, pack_store):
		super(Pack, self).__init__("")
		if pack_store != "": #This is to ensure Pack.FromObjects will work
			self.pack_store = pack_store
			blob_reader = blobstore.BlobReader(self.pack_store.data)
			self._data_load = lambda: PackData(filename=None, file=blob_reader, size=self.pack_store.size)
			self._idx_load = lambda: PackIndex(self.pack_store) #@TODO: I need to store the checksum somewhere


class PackData(DulwichPackData):
	pass

class PackIndex(DulwichPackIndex):
	"""Pack index that is stored entirely in memory."""
	@classmethod
	def create(cls, pack_store, pack_data):
		for sha, offset, crc32 in pack_data.iterentries():
			sha = sha_to_hex(sha)
			pack_store.sha1.append(sha)
			PackStoreIndex(
				packref = pack_store,
				sha = sha,
				offset = offset,
				crc32 = crc32,
			).save()
		t_checksum = pack_data.get_stored_checksum()
		pack_store.checksum=t_checksum
		pack_store.save()
		return cls(pack_store)
	
	def __init__(self, pack_store, pack_checksum=None):
		"""Create a new MemoryPackIndex.

		:param entries: Sequence of name, idx, crc32 (sorted)
		:param pack_checksum: Optional pack checksum
		"""
		self._by_sha = {}
		self._entries = []
		q = db.Query(PackStoreIndex)
		q.filter('packref =', pack_store)
		for obj in q:
			sha = hex_to_sha(obj.sha)
			self._by_sha[sha] = obj.offset
			self._entries.append( [sha, obj.offset, obj.crc32] )
		self._pack_checksum = hex_to_sha(pack_store.checksum)

	def get_pack_checksum(self):
		#@todo: this returns a blob type, should return a str type
		return self._pack_checksum

	def __len__(self):
		return len(self._entries)

	def object_index(self, sha):
		return self._by_sha[sha]

	def _itersha(self):
		return iter(self._by_sha)

	def iterentries(self):
		return iter(self._entries)
	
	def check(self):
		"""Check that the stored checksum matches the actual checksum."""
		logging.error("gae_backend.py -> PackIndex.Check()")
		return
		# taken from Pack.FilePackIndex
		#actual = self.calculate_checksum()
		#stored = self.get_stored_checksum()
		#if actual != stored:
		#	raise ChecksumMismatch(stored, actual)

#RefsContainer
class References(db.Model):
	repository = db.ReferenceProperty(Repositories)
	ref = db.StringProperty()
	pointer = db.StringProperty() #this can be an sha1 or a link to another ref

class RefsContainer(BaseRefsContainer):
	def __init__(self, Repo):
		self.REPO = Repo

	def set_symbolic_ref(self, name, other):
		"""
			refs usually point at objects,
			however it is possible for a ref to point at another ref
			an example is HEAD
			
			:name string: the name of the ref
			:other string: the target of this ref (what the reference points at).
		"""
		References(
			repository = self.REPO,
			ref=name,
			pointer=SYMREF+other,
		).put()
	
	def get_packed_refs(self):
		"""
			refs stores inside a pack
		"""
		return {}
	
	def _query(self, ref=None):
		q = db.Query(References)
		if ref != None:
			q.filter('ref =', ref)
		q.filter('repository =', self.REPO)
		return q
	
	def allkeys(self):
		keys = []
		q = db.Query(References)
		q.filter('repository =', self.REPO)
		for k in q:
			s = str(k.ref)
			keys.append(s)
		return keys
	
	def read_loose_ref(self, name):
		"""
			returns the target of a reference
			this function does not follow symbolic refs
			:name string: the name of the reference
		"""
		refs = self._query(name)
		if refs.count(1):
			tref = refs.get()
			tpointer = tref.pointer
			output = "%s" % str(tpointer)
			return output
		else:
			return None


	

	
	def set_if_equals(self, name, old_ref, new_ref):
		"""if old_ref is none we continue
		if refs[name]== old_ref we continue
		else we false"""
		realReference = self._follow(name)
		if old_ref == None or realReference[1] == old_ref:
			query = self._query(name)
			ref = query.get()
			if ref == None:
				ref = References(
					repository = self.REPO,
					ref = name,
				)
			ref.pointer = new_ref
			ref.put()
			return True
		else:
			return False
	
	def add_if_new(self, name, new):
		""" add a reference if it doesn't exist """
		if self._query(name).get() == None:
			References(
				repository = self.REPO,
				ref = name,
				pointer = new,
			).put()
		
	def remove_if_equals(self, name, old_ref):
		""" remove a reference """
		ref = self._query(name).get()
		if ref == None:
			return False
		if old_ref == None or ref.pointer == old_ref:
			ref.delete()
			return True
		else:
			return False
		
