import motor.motor_tornado
import multiprocessing as mp
import pickle
import pymongo
import json

import env


class Backend():
	def __init__(self):
		pass

	def initialize(self):
		pass


	# user functions -----
	async def user_query(self, page, page_size):
		raise NotImplementedError()

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
	async def user_query(self, page, page_size):
		self._lock.acquire()
		self.load()

		# sort users by date_created in descending order
		self._db['users'].sort(key=lambda w: w['date_created'], reverse=True)

		# return the specified page of users
		users = self._db['users'][(page * page_size):((page + 1) * page_size)]

		self._lock.release()

		return users

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
	async def dataset_query(self, user_id, page, page_size):
		self._lock.acquire()
		self.load()

		# get the datasets from a user id
		if user_id == 'admin':
			datasets = self._db['datasets']
		else:
			datasets = [d for d in self._db['datasets'] if d['user_id'] == user_id]

		# sort datasets by date_created in descending order
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
	async def workflow_query(self, user_id, page, page_size):
		self._lock.acquire()
		self.load()

		# get the workflows from a user id
		if user_id == 'admin':
			workflows = self._db['workflows']
		else:
			workflows = [d for d in self._db['workflows'] if d['user_id'] == user_id]

		# sort workflows by date_created in descending order
		workflows.sort(key=lambda w: w['date_created'], reverse=True)

		# return the specified page of workflows
		workflows = workflows[(page * page_size) : ((page + 1) * page_size)]

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



	# ----------------
	# Output functions
	# ----------------
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
						self._db['workflows'][i]['n_attempts'] -= 1
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
		self._db = self._client[env.MONGODB_DB]


	# ----------------
	# User functions
	# ----------------
	async def user_query(self, page, page_size):
		return await self._db.users \
			.find() \
			.sort('date_created', pymongo.DESCENDING) \
			.skip(page * page_size) \
			.to_list(length=page_size)

	async def user_create(self, user):
		# get username
		username = user['username']

		# check if the username already exists
		found = await self._db.users.find_one({'username': username})
		
		# if user is found, raise an error
		if found:
				raise IndexError('User already exists')

		# if user is not found, insert the new user
		return await self._db.users.insert_one(user)

	async def user_get(self, username):
		return await self._db.users.find_one({ 'username': username })

	async def user_update(self, id, user):
		return await self._db.users.replace_one({ '_id': id }, user)

	async def user_delete(self, id):
		return await self._db.users.delete_one({ '_id': id })



	# ----------------
	# Dataset functions
	# ----------------
	async def dataset_query(self, user_id, page, page_size):
		# if admin retrieves all; otherwise only created by user_id
		query = {} if user_id == 'admin' else {'user_id': user_id}
		return await self._db.datasets \
			.find(query) \
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
	async def workflow_query(self, user_id, page, page_size):
		# if admin retrieves all; otherwise only created by user_id
		query = {} if user_id == 'admin' else {'user_id': user_id}
		return await self._db.workflows \
			.find(query) \
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
	# Output functions
	# ----------------
	async def output_delete(self, id, attempt):

		# find the workflow with the specified ID
		workflow = await self._db.workflows.find_one({'_id': id})
		if not workflow:
			raise IndexError('Workflow not found')

		# find the attempt within the workflow
		attempts = workflow.get('attempts', [])
		n_attempts = len(attempts)
		found = False
		for a in attempts:
			if str(a['id']) == attempt:
				attempts.remove(a)
				found = True
				break

		if not found:
				raise IndexError('Output was not found')

		# update the workflow with the modified attempts list
		result = await self._db.workflows.update_one(
			{'_id': id},
			{'$set': {'attempts': attempts, 'n_attempts': n_attempts-1}}
		)

		if result.matched_count == 0:
			raise IndexError('Failed to delete the output')



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




# /*
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 	FILE META
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#		Class that save meta data into a file
# ----------------------------------------------------------------------------------------
# */

class FileMeta():

	def __init__(self, file):
		self._lock = mp.Lock()
		self._file = file
		self.initialize()

	def initialize(self, error_not_found=False):
		# Load database from JSON file if it exists, otherwise initialize empty data
		try:
			self.load()
		except FileNotFoundError:
			self._meta = {}
			self.save()

	def load(self):
		with open(self._file, 'r') as file:
			self._meta = json.load(file)

	def save(self):
		with open(self._file, 'w') as file:
			json.dump(self._meta, file, indent=4)  # Indent for readability

	# add meta info into meta file
	async def create(self, meta):
		self._lock.acquire()
		try:
			self.load()
			self._meta = meta
			self.save()
		finally:
				self._lock.release()

