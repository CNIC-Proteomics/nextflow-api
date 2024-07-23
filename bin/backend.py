import motor.motor_tornado
import multiprocessing as mp
import pickle
import pymongo



class Backend():
	def __init__(self):
		pass

	def initialize(self):
		pass


	# user functions -----
	async def user_create(self, user):
		raise NotImplementedError()

	async def user_get(self, username):
		raise NotImplementedError()

	async def user_update(self, id, user):
		raise NotImplementedError()

	async def user_delete(self, id):
		raise NotImplementedError()

	# dataset functions -----
	async def dataset_query(self, page, page_size):
		raise NotImplementedError()

	async def dataset_create(self, data):
		raise NotImplementedError()

	async def dataset_get(self, id):
		raise NotImplementedError()

	async def dataset_update(self, id, dataset):
		raise NotImplementedError()

	async def dataset_delete(self, id):
		raise NotImplementedError()

	# workflow functions -----
	async def workflow_query(self, page, page_size):
		raise NotImplementedError()

	async def workflow_create(self, workflow):
		raise NotImplementedError()

	async def workflow_get(self, id):
		raise NotImplementedError()

	async def workflow_update(self, id, workflow):
		raise NotImplementedError()

	async def workflow_delete(self, id):
		raise NotImplementedError()
	
	async def output_delete(self, id, attempt):
		raise NotImplementedError()

	# task functions -----
	async def task_query(self, page, page_size):
		raise NotImplementedError()

	async def task_create(self, task):
		raise NotImplementedError()

	async def task_get(self, id):
		raise NotImplementedError()


# /*
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 	FILE BACKEND
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#		Class that saves the dataset, workflows and tasks information into a file
# ----------------------------------------------------------------------------------------
# */

class FileBackend(Backend):

	def __init__(self, url):
		self._lock = mp.Lock()
		self._url = url
		self.initialize()

	def initialize(self, error_not_found=False):
		# load database from pickle file
		try:
			self.load()

		# initialize empty database if pickle file doesn't exist
		except FileNotFoundError:
			self._db = {
				'users': [],
				'datasets': [],
				'workflows': [],
				'outputs': [],
				'tasks': []
			}
			self.save()

	def load(self):
		self._db = pickle.load(open(self._url, 'rb'))

	def save(self):
		pickle.dump(self._db, open(self._url, 'wb'))


	# ----------------
	# User functions
	# ----------------
	async def user_create(self, user):
		self._lock.acquire()
		self.load()
		
		# get username
		username = user['username']

		# check if username already exists
		found = next((True for u in self._db['users'] if u['username'] == username), False)

		# append user to list of users if user was not found
		if not found:			
			self._db['users'].append(user)
			self.save()
		
		self._lock.release()

		# raise error if user was found
		if found:
			raise IndexError('User already exists')

	async def user_get(self, username):
		self._lock.acquire()
		self.load()

		# get user
		user = next((u for u in self._db['users'] if u['username'] == username), None)
		
		self._lock.release()

		# raise error if user wasn't found
		if user == None:
			raise IndexError('User was not found')

		return user

	async def user_update(self, id, user):
		self._lock.acquire()
		self.load()

		# search for user by id and update it
		found = False

		for i, d in enumerate(self._db['users']):
			if d['_id'] == id:
				# update user
				self._db['users'][i] = user
				found = True
				break

		self.save()
		self._lock.release()

		# raise error if user wasn't found
		if not found:
			raise IndexError('User was not found')

	async def user_delete(self, id):
		self._lock.acquire()
		self.load()

		# search for user by id and delete it
		found = False

		for i, d in enumerate(self._db['users']):
			if d['_id'] == id:
				# delete user
				self._db['users'].pop(i)
				found = True
				break

		self.save()
		self._lock.release()

		# raise error if user wasn't found
		if not found:
			raise IndexError('User was not found')


	# ----------------
	# Dataset functions
	# ----------------
	# async def dataset_query(self, page, page_size):
	# 	self._lock.acquire()
	# 	self.load()

	# 	# sort datasets by date_created in descending order
	# 	self._db['datasets'].sort(key=lambda w: w['date_created'], reverse=True)

	# 	# return the specified page of datasets
	# 	datasets = self._db['datasets'][(page * page_size) : ((page + 1) * page_size)]

	# 	self._lock.release()

	# 	return datasets
	async def dataset_query(self, user_id, page, page_size):
		self._lock.acquire()
		self.load()

		# sort datasets by date_created in descending order
		datasets = [d for d in self._db['datasets'] if d['user_id'] == user_id]
		datasets.sort(key=lambda w: w['date_created'], reverse=True)

		# return the specified page of datasets
		datasets = datasets[(page * page_size):((page + 1) * page_size)]

		self._lock.release()

		return datasets


	async def dataset_create(self, dataset):
		self._lock.acquire()
		self.load()

		# append dataset to list of datasets
		self._db['datasets'].append(dataset)

		self.save()
		self._lock.release()

	async def dataset_get(self, id):
		self._lock.acquire()
		self.load()

		# search for dataset by id
		dataset = None

		for d in self._db['datasets']:
			if d['_id'] == id:
				dataset = d
				break

		self._lock.release()

		# return dataset or raise error if dataset wasn't found
		if dataset != None:
			return dataset
		else:
			raise IndexError('Dataset was not found')

	async def dataset_update(self, id, dataset):
		self._lock.acquire()
		self.load()

		# search for dataset by id and update it
		found = False

		for i, d in enumerate(self._db['datasets']):
			if d['_id'] == id:
				# update dataset
				self._db['datasets'][i] = dataset
				found = True
				break

		self.save()
		self._lock.release()

		# raise error if dataset wasn't found
		if not found:
			raise IndexError('Dataset was not found')

	async def dataset_delete(self, id):
		self._lock.acquire()
		self.load()

		# search for dataset by id and delete it
		found = False

		for i, d in enumerate(self._db['datasets']):
			if d['_id'] == id:
				# delete dataset
				self._db['datasets'].pop(i)
				found = True
				break

		self.save()
		self._lock.release()

		# raise error if dataset wasn't found
		if not found:
			raise IndexError('Dataset was not found')


	# ----------------
	# Workflow functions
	# ----------------
	async def workflow_query(self, page, page_size):
		self._lock.acquire()
		self.load()

		# sort workflows by date_created in descending order
		self._db['workflows'].sort(key=lambda w: w['date_created'], reverse=True)

		# return the specified page of workflows
		workflows = self._db['workflows'][(page * page_size) : ((page + 1) * page_size)]

		self._lock.release()

		return workflows

	async def workflow_create(self, workflow):
		self._lock.acquire()
		self.load()

		# append workflow to list of workflows
		self._db['workflows'].append(workflow)

		self.save()
		self._lock.release()

	async def workflow_get(self, id):
		self._lock.acquire()
		self.load()

		# search for workflow by id
		workflow = None

		for w in self._db['workflows']:
			if w['_id'] == id:
				workflow = w
				break

		self._lock.release()

		# return workflow or raise error if workflow wasn't found
		if workflow != None:
			return workflow
		else:
			raise IndexError('Workflow was not found')

	async def workflow_update(self, id, workflow):
		self._lock.acquire()
		self.load()

		# search for workflow by id and update it
		found = False

		for i, w in enumerate(self._db['workflows']):
			if w['_id'] == id:
				# update workflow
				self._db['workflows'][i] = workflow
				found = True
				break

		self.save()
		self._lock.release()

		# raise error if workflow wasn't found
		if not found:
			raise IndexError('Workflow was not found')

	async def workflow_delete(self, id):
		self._lock.acquire()
		self.load()

		# search for workflow by id and delete it
		found = False

		for i, w in enumerate(self._db['workflows']):
			if w['_id'] == id:
				# delete workflow
				self._db['workflows'].pop(i)
				found = True
				break

		self.save()
		self._lock.release()

		# raise error if workflow wasn't found
		if not found:
			raise IndexError('Workflow was not found')

	async def output_delete(self, id, attempt):
		self._lock.acquire()
		self.load()

		# search for workflow by id and delete it
		found = False

		for i, w in enumerate(self._db['workflows']):
			if w['_id'] == id:
				for j, a in enumerate(w['attempts']):
					if str(a['id']) == attempt:
						# delete outpus
						self._db['workflows'][i]['attempts'].pop(j)
						found = True
						break

		self.save()
		self._lock.release()

		# raise error if workflow wasn't found
		if not found:
			raise IndexError('Output was not found')



	# ----------------
	# Task functions
	# ----------------
	async def task_query(self, page, page_size):
		self._lock.acquire()
		self.load()

		# sort tasks by date_created in descending order
		self._db['tasks'].sort(key=lambda t: t['utcTime'], reverse=True)

		# return the specified page of workflows
		tasks = self._db['tasks'][(page * page_size) : ((page + 1) * page_size)]

		self._lock.release()

		return tasks

	async def task_query_pipelines(self):
		self._lock.acquire()
		self.load()

		# extract list of unique pipelines from all 'started' events
		pipelines = [t['metadata']['workflow']['projectName'] for t in self._db['tasks'] if t['event'] == 'started']
		pipelines = list(set(pipelines))

		self._lock.release()

		return pipelines

	async def task_query_pipeline(self, pipeline):
		self._lock.acquire()
		self.load()

		# find all runs of the given pipeline
		run_ids = [t['runId'] for t in self._db['tasks'] if t['event'] == 'started' and t['metadata']['workflow']['projectName'] == pipeline]

		# find all tasks associated with the given runs
		tasks = [t for t in self._db['tasks'] if t['event'] == 'process_completed' and t['runId'] in run_ids]

		self._lock.release()

		return tasks

	async def task_create(self, task):
		self._lock.acquire()
		self.load()

		# append workflow to list of workflows
		self._db['tasks'].append(task)

		self.save()
		self._lock.release()

	async def task_get(self, id):
		self._lock.acquire()
		self.load()

		# search for task by id
		task = None

		for t in self._db['tasks']:
			if t['_id'] == id:
				task = t
				break

		self._lock.release()

		# raise error if task wasn't found
		if task != None:
			return task
		else:
			raise IndexError('Task was not found')




# /*
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 	MONGODB BACKEND
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#		Class that saves the dataset, workflows and tasks information into mongoDB database
# ----------------------------------------------------------------------------------------
# */

class MongoBackend(Backend):
	def __init__(self, url):
		self._url = url
		self.initialize()

	def initialize(self):
		self._client = motor.motor_tornado.MotorClient(self._url)
		self._db = self._client['nextflow_api']

	# ----------------
	# Dataset functions
	# ----------------
	async def dataset_query(self, page, page_size):
		return await self._db.datasets \
			.find() \
			.sort('date_created', pymongo.DESCENDING) \
			.skip(page * page_size) \
			.to_list(length=page_size)

	async def dataset_create(self, dataset):
		return await self._db.datasets.insert_one(dataset)

	async def dataset_get(self, id):
		return await self._db.datasets.find_one({ '_id': id })

	async def dataset_update(self, id, dataset):
		return await self._db.datasets.replace_one({ '_id': id }, dataset)

	async def dataset_delete(self, id):
		return await self._db.datasets.delete_one({ '_id': id })

	# ----------------
	# Workflow functions
	# ----------------
	async def workflow_query(self, page, page_size):
		return await self._db.workflows \
			.find() \
			.sort('date_created', pymongo.DESCENDING) \
			.skip(page * page_size) \
			.to_list(length=page_size)

	async def workflow_create(self, workflow):
		return await self._db.workflows.insert_one(workflow)

	async def workflow_get(self, id):
		return await self._db.workflows.find_one({ '_id': id })

	async def workflow_update(self, id, workflow):
		return await self._db.workflows.replace_one({ '_id': id }, workflow)

	async def workflow_delete(self, id):
		return await self._db.workflows.delete_one({ '_id': id })

	# ----------------
	# Task functions
	# ----------------
	async def task_query(self, page, page_size):
		return await self._db.tasks \
			.find({}, { '_id': 1, 'runName': 1, 'utcTime': 1, 'event': 1 }) \
			.sort('utcTime', pymongo.DESCENDING) \
			.skip(page * page_size) \
			.to_list(length=page_size)

	async def task_query_pipelines(self):
		# find all 'started' events
		tasks = await self._db.tasks \
			.find({ 'event': 'started' }, { 'metadata.workflow.projectName': 1 }) \
			.to_list(length=None)

		# extract list of unique pipelines
		pipelines = [t['metadata']['workflow']['projectName'] for t in tasks]
		pipelines = list(set(pipelines))

		return pipelines

	async def task_query_pipeline(self, pipeline):
		# find all runs of the given pipeline
		runs = await self._db.tasks \
			.find({ 'event': 'started', 'metadata.workflow.projectName': pipeline }, { 'runId': 1 }) \
			.to_list(length=None)

		run_ids = [run['runId'] for run in runs]

		# find all tasks associated with the given runs
		tasks = await self._db.tasks \
			.find({ 'event': 'process_completed', 'runId': { '$in': run_ids } }) \
			.to_list(length=None)

		return tasks

	async def task_create(self, task):
		return await self._db.tasks.insert_one(task)

	async def task_get(self, id):
		return await self._db.tasks.find_one({ '_id': id })
