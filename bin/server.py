#!/usr/bin/env python3

import base64
import bson
import json
import multiprocessing as mp
import os
import pandas as pd
import shutil
import socket
import subprocess
import time
import tornado
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import zipfile
import io
import mimetypes
import traceback
# login
import bcrypt
import jwt
import datetime

import backend
import env
# import model as Model
import visualizer as Visualizer
import workflow as Workflow



#-------------------------------------
# Local functions
#-------------------------------------

# 
# Return message
#
def message(status, message):
	return {
		'status': status,
		'message': message
	}

#
# Function to handle and print unhandled exceptions
#
def log_exception(e):
	print('ERROR: %s' % (e), flush=True)
	traceback.print_exc()
	
#
# Retrieves the list of files recursively
#
def list_dir_recursive(path, relpath_start=''):
	files = [os.path.join(dir, f) for (dir, subdirs, filenames) in os.walk(path) for f in filenames]
	files = [os.path.relpath(f, start=relpath_start) for f in files]
	files.sort()

	return files

#
# Convert size to a readable format (bytes to KB, MB, etc.)
#
def get_size_readable(size):
	for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
		if size < 1024:
			return f"{size:.2f}{unit}"
		size /= 1024
	return f"{size:.2f}PB"

#
# Build the file tree from a path
#
def build_tree(path, relpath_start='', key_prefix=''):
	tree = []
	key_counter = 0

	# Check if the parent folder (path) itself is a symbolic link
	parent_is_link = True if os.path.islink(path) else False

	# Get the dir, subdir and files from a given path
	for dirpath, subdirs, filenames in os.walk(path):
		# exclude hidden files, directories, and files starting with "~", "$"
		subdirs[:] = [d for d in subdirs if not d.startswith('.') and not d.startswith('~') and not d.startswith('$')]
		filenames = [f for f in filenames if not f.startswith('.') and not f.startswith('~') and not f.startswith('$')]

		# identify symlinks that point to directories and update subdirs and filenames
		symlink_dirs = [f for f in filenames if os.path.islink(os.path.join(dirpath, f)) and os.path.isdir(os.path.join(dirpath, f))]
		subdirs.extend(symlink_dirs)
		filenames = [f for f in filenames if f not in symlink_dirs]

		# process directories
		for subdir in subdirs:
			key = f"{key_counter}" if key_prefix == '' else f"{key_prefix}-{key_counter}"
			full_subdir_path = os.path.join(dirpath, subdir)
			is_link = os.path.islink(full_subdir_path)
			# Stop scanning more subfolders if the parent folder is a link
			children = [] if parent_is_link else build_tree(full_subdir_path, relpath_start, key)
			tree.append({
				'key': key,
				'data': {
					'name': subdir,
					'size': None,
					'type': 'folder',
					'is_link': is_link
				},
				'children': children
			})
			key_counter += 1

		# process files
		for filename in filenames:
			key = f"{key_counter}" if key_prefix == '' else f"{key_prefix}-{key_counter}"
			relative_dirpath = os.path.relpath(dirpath, start=relpath_start)
			full_file_path = os.path.join(dirpath, filename)
			is_link = os.path.islink(full_file_path)
			file_size = os.path.getsize(full_file_path) if not is_link else 0
			tree.append({
				'key': key,
				'data': {
					'name': filename,
					'path': relative_dirpath,
					'size': get_size_readable(file_size),
					'type': 'file',
					'is_link': is_link
				}
			})
			key_counter += 1

		# Only process the top level of the current directory, not recursively
		break

	# Sort the tree by 'type' (folders first) and 'name'
	tree = sorted(tree, key=lambda x: (x['data']['type'] != 'folder', x['data']['name']))


	return tree

#
# Extract the files/folders from a path. Only retrieve the contents of the current directory
#
def scan_directory(path):

	# Get the meta info if exists
	def _get_meta(full_subdir_path):
		meta = {}
		meta_file = os.path.join(full_subdir_path, 'meta.json')
		if os.path.exists(meta_file):
			with open(meta_file, 'r') as m:
				meta = json.load(m)
		return meta

	tree = []

	try:
		# get the directories and files in the given path (no recursion)
		for dirpath, subdirs, filenames in [(path, next(os.walk(path))[1], next(os.walk(path))[2])]:
			# exclude hidden files, directories, and files starting with "~", "$"
			subdirs = [d for d in subdirs if not d.startswith('.') and not d.startswith('~') and not d.startswith('$')]
			filenames = [f for f in filenames if not f.startswith('.') and not f.startswith('~') and not f.startswith('$')]

			# process directories (only immediate children)
			for subdir in subdirs:
				full_subdir_path = os.path.join(dirpath, subdir)
				is_link = os.path.islink(full_subdir_path)
				# check if we have permission to access this directory
				if os.access(full_subdir_path, os.R_OK):
					meta = _get_meta(full_subdir_path)
					tree.append({
						'key': full_subdir_path,
						'data': {
							'id': subdir,
							'name': meta.get('name') if 'name' in meta else subdir,
							'meta': meta,
							'size': None,
							'type': 'folder',
							'is_link': is_link
						},
						# 'children': []  # No recursive children
					})

			# process files (only immediate children)
			for filename in filenames:
				full_file_path = os.path.join(dirpath, filename)
				# Check if we have permission to access this file
				if os.access(full_file_path, os.R_OK):
					full_file_path = os.path.join(dirpath, filename)
					is_link = os.path.islink(full_file_path)
					file_size = os.path.getsize(full_file_path) if not is_link else 0
					# file_type = mimetypes.guess_type(full_file_path, strict=False)[0]
					file_type = 'file'
					tree.append({
						'key': full_file_path,
						'data': {
							'name': filename,
							'size': get_size_readable(file_size),
							'type': file_type,
							'is_link': is_link
						}
					})

	except Exception as e:
		log_exception(e)

	# sort the tree by 'type' (folders first) and 'name'
	tree = sorted(tree, key=lambda x: (x['data']['type'] != 'folder', x['data']['name']))

	return tree

# 
# Initialize users
#
async def initialize_users(db):
	
	# initialize the admin user
	try:
		user_admin = await create_user(db, env.USER_ADMIN, env.PWD_ADMIN, role='admin')
		print(f'** admin user with ID: {user_admin["_id"]}')
	except Exception as e:
		print(f'** admin user: {e}')

	# initialize the guest user
	try:
		user_guest = await create_user(db, env.USER_GUEST, env.PWD_GUEST)
		print(f'** guest user with ID: {user_guest["_id"]}')
	except Exception as e:
		print(f'** guest user: {e}')



#-------------------------------------
# CORS permissions
#-------------------------------------

# Define your CORSMixin
class CORSMixin:
	def set_default_headers(self):
		origin = self.request.headers.get("Origin")
		if origin in env.CORS_HOSTS:
				self.set_header("Access-Control-Allow-Origin", origin)
		self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type")
		self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, DELETE, PUT")

	def options(self, *args, **kwargs):
		self.set_status(204)
		self.finish()



#-------------------------------------
# CORS and Authorization permissions
#-------------------------------------

# Define your CORSAuthMixin
class CORSAuthMixin(tornado.web.RequestHandler):
	def set_default_headers(self):
			origin = self.request.headers.get("Origin")
			if origin in env.CORS_HOSTS:
					self.set_header("Access-Control-Allow-Origin", origin)
			self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type, Authorization")
			self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, DELETE, PUT")
			self.set_header("Access-Control-Allow-Credentials", "true")

	def options(self, *args, **kwargs):
		self.set_status(204)
		self.finish()

	def write_error(self, status_code, **kwargs):
		self.set_header('Content-Type', 'application/json')
		self.finish({"status": status_code, "message": self._reason})

	def prepare(self):
		# OPTIONS request should not require authorization
		if self.request.method == "OPTIONS":
			return
		if 'Authorization' not in self.request.headers:
			raise tornado.web.HTTPError(401, 'Missing authorization header')		
		token = self.request.headers['Authorization'].split(' ')[-1]
		payload = jwt_decode(token)
		self.current_user = payload


		

#-------------------------------------
# LOGIN Function and Class
#-------------------------------------

#
# Create user
#
async def create_user(db, username, password, role='guest'):

	# encode pwd
	try:
		password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
	except Exception as e:
		raise KeyError('Encoding pwd')

	# create user
	try:
		user = {
			'username': username,
			'password': password_hash,
			'role': role,
			'_id': str(bson.ObjectId()),
			'date_created': int(time.time() * 1000)
		}
	except Exception as e:
		raise KeyError('Creating user')

	# save the user to the database
	try:
		await db.user_create(user)
	except Exception as e:
		raise KeyError(e)

	return user

#
# Check if the user is admin or not
#
async def is_admin(db, user):
		try:
			admin = await db.user_get('admin')
			return user['_id'] == admin['_id']
		except Exception as e:
			return False


#
# Decoded token (JWT)
#
def jwt_decode(token):
	try:
		payload = jwt.decode(token, env.JWT_SECRET, algorithms=[env.JWT_ALGORITHM])
		return payload
	except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
		raise tornado.web.HTTPError(401, 'Invalid token')

#
# Encode token (JWT)
#
def jwt_encode(user):
	payload = {
		'_id': user['_id'],
		'username': user['username'],
		'role': user['role'],
		'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=env.JWT_EXP_DELTA_SECONDS)
	}
	jwt_token = jwt.encode(payload, env.JWT_SECRET, env.JWT_ALGORITHM)
	return jwt_token

#
# Get the role of user
#
def role_required(roles):
	def decorator(method):
		def wrapper(self, *args, **kwargs):
			if len(roles) > 0 and self.current_user['role'] not in roles:
				raise tornado.web.HTTPError(403, 'Forbidden')
			return method(self, *args, **kwargs)
		return wrapper
	return decorator


class LoginHandler(CORSMixin, tornado.web.RequestHandler):

	REQUIRED_KEYS = set([
		'username',
		'password'
	])

	async def post(self):
		db = self.settings['db']

		# make sure request body is valid
		try:
			data = tornado.escape.json_decode(self.request.body)
			missing_keys = self.REQUIRED_KEYS - data.keys()
		except json.JSONDecodeError:
			self.set_status(422)
			self.write(message(422, 'Ill-formatted JSON'))
			return

		if missing_keys:
			self.set_status(400)
			self.write(message(400, 'Missing required field(s): %s' % list(missing_keys)))
			return

		# get data parameters
		# user = {**data}
		username = data['username']
		password = data['password']

		# get user
		try:
			user = await db.user_get(username)
		except Exception as e:
			log_exception(e)
			self.set_status(500)
			self.write(message(500, f'Failed to login user: {str(e)}'))
			return
		
		# create jwt token
		if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
			jwt_token = jwt_encode(user)
			self.set_status(200)
			self.write({'token': jwt_token})
		else:
			self.set_status(401)
			self.write(message(401, 'Invalid username or password'))
			return



class UserCreateHandler(CORSMixin, tornado.web.RequestHandler):

	REQUIRED_KEYS = set([
		'username',
		'password'
	])

	async def post(self):
		db = self.settings['db']

		# make sure request body is valid
		try:
			data = tornado.escape.json_decode(self.request.body)
			missing_keys = self.REQUIRED_KEYS - data.keys()
		except json.JSONDecodeError:
			self.set_status(422)
			self.write(message(422, 'Ill-formatted JSON'))
			return

		if missing_keys:
			self.set_status(400)
			self.write(message(400, 'Missing required field(s): %s' % list(missing_keys)))
			return

		# get data parameters
		# user = {**data}
		username = data['username']
		password = data['password']

		# Check if username already exists
		try:
			user = await db.user_get(username)
			if user:
				self.set_status(409)  # Conflict
				self.write(message(409, 'Username already exists'))
				return
		except Exception as e:
			log_exception(e)
			self.set_status(500)
			self.write(message(500, f'Error checking username: {str(e)}'))
			return

		# create user
		try:
			user = await create_user(db, username, password)
		except Exception as e:
			log_exception(e)
			self.set_status(500)
			self.write(message(500, f'Creating user: {str(e)}'))
			return
	
		self.set_status(201)
		self.set_header('content-type', 'application/json')
		self.write(tornado.escape.json_encode({ '_id': user['_id'] }))


class UserQueryHandler(CORSAuthMixin, tornado.web.RequestHandler):

	@role_required(['admin'])
	async def get(self):
		page = int(self.get_query_argument('page', 0))
		page_size = int(self.get_query_argument('page_size', 100))

		db = self.settings['db']

		# return all users if user is admin
		users = await db.user_query(page, page_size)

		# don't display password field
		users = [{**u, 'password': ''} for u in users]

		self.set_status(200)
		self.set_header('content-type', 'application/json')
		self.write(tornado.escape.json_encode(users))


class UserEditHandler(CORSAuthMixin, tornado.web.RequestHandler):

	REQUIRED_KEYS = set([
		'username',
		'role',
		'password'
	])

	DEFAULTS = {
		'username': '',
		'role': ''
	}

	@role_required([])
	async def get(self, username):
		db = self.settings['db']

		try:
			# get user
			user = await db.user_get(username)

			# don't display password field
			user['password'] = ''

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(user))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to get user \"%s\"' % username))

	@role_required(['admin'])
	async def post(self, username):
		db = self.settings['db']

		# make sure request body is valid
		try:
			data = tornado.escape.json_decode(self.request.body)
			added_keys = data.keys() - self.REQUIRED_KEYS
		except json.JSONDecodeError:
			self.set_status(422)
			self.write(message(422, 'Ill-formatted JSON'))

		if added_keys:
			self.set_status(400)
			self.write(message(400, 'There are more field(s) than allowed: %s' % list(self.REQUIRED_KEYS)))
			return

		try:
			# update user from request body
			user = await db.user_get(username)
			user = {**self.DEFAULTS, **user, **data}

			# get user id
			id = user['_id']

			# encode pwd
			if 'password' in data:
				password_hash = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt())
				user['password'] = password_hash

			# save user
			await db.user_update(id, user)

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode({ '_id': id }))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to update user \"%s\"' % username))

	@role_required(['admin'])
	async def delete(self, username):
		db = self.settings['db']

		try:
			# get user
			user = await db.user_get(username)
			id = user['_id']

			# delete user
			await db.user_delete(id)

			self.set_status(200)
			self.write(message(200, 'User \"%s\" was deleted' % username))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to delete user \"%s\"' % username))


#-------------------------------------
# DATASETS Classes
#-------------------------------------

class DatasetQueryHandler(CORSAuthMixin, tornado.web.RequestHandler):

	@role_required([])
	async def get(self):
		page = int(self.get_query_argument('page', 0))
		page_size = int(self.get_query_argument('page_size', 100))

		db = self.settings['db']

		# return all datasets if user is admin
		if await is_admin(db, self.current_user):
			datasets = await db.dataset_query('admin', page, page_size)
		else:
			datasets = await db.dataset_query(self.current_user['_id'], page, page_size)

		self.set_status(200)
		self.set_header('content-type', 'application/json')
		self.write(tornado.escape.json_encode(datasets))



class DatasetCreateHandler(CORSAuthMixin, tornado.web.RequestHandler):

	REQUIRED_KEYS = set([])

	DEFAULTS = {
		'name': '',
		'author': '',
		'description': '',
		'n_files': 0
	}

	@role_required([])
	def get(self):
		dataset = {**self.DEFAULTS, **{ '_id': '0' }}

		self.set_status(200)
		self.set_header('content-type', 'application/json')
		self.write(tornado.escape.json_encode(dataset))

	@role_required([])
	async def post(self):
		db = self.settings['db']

		# make sure request body is valid
		try:
			data = tornado.escape.json_decode(self.request.body)
			missing_keys = self.REQUIRED_KEYS - data.keys()
		except json.JSONDecodeError:
			self.set_status(422)
			self.write(message(422, 'Ill-formatted JSON'))
			return

		if missing_keys:
			self.set_status(400)
			self.write(message(400, 'Missing required field(s): %s' % list(missing_keys)))
			return

		try:
			# create dataset
			dataset = {**self.DEFAULTS, **data}
			dataset['_id'] = str(bson.ObjectId())

			# append creation timestamp to dataset
			dataset['date_created'] = int(time.time() * 1000)

			# append the current user id
			dataset['user_id'] = self.current_user['_id']

			# save dataset
			await db.dataset_create(dataset)

			# create dataset directory
			dataset_dir = os.path.join(env.DATASETS_DIR, dataset['_id'])
			os.makedirs(dataset_dir)

			# save meta file
			meta = backend.FileMeta(os.path.join(dataset_dir, 'meta.json'))
			await meta.create(dataset)

			self.set_status(201)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode({ '_id': dataset['_id'] }))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to create dataset \"%s\"' % id))




class DatasetEditHandler(CORSAuthMixin, tornado.web.RequestHandler):

	REQUIRED_KEYS = set([])

	DEFAULTS = {
		'name': '',
		'author': '',
		'description': '',
		'n_files': 0
	}

	@role_required([])
	async def get(self, id):
		db = self.settings['db']

		try:
			# get dataset
			dataset = await db.dataset_get(id)

			# append list of input files
			dataset_dir = os.path.join(env.DATASETS_DIR, id)
			if os.path.exists(dataset_dir):
				dataset['files'] = build_tree(dataset_dir, relpath_start=dataset_dir)
			else:
				dataset['files'] = []

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(dataset))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to get dataset \"%s\"' % id))

	@role_required([])
	async def post(self, id):
		db = self.settings['db']

		# make sure request body is valid
		try:
			data = tornado.escape.json_decode(self.request.body)
			missing_keys = self.REQUIRED_KEYS - data.keys()
		except json.JSONDecodeError:
			self.set_status(422)
			self.write(message(422, 'Ill-formatted JSON'))

		if missing_keys:
			self.set_status(400)
			self.write(message(400, 'Missing required field(s): %s' % list(missing_keys)))
			return

		try:
			# update dataset from request body
			dataset = await db.dataset_get(id)
			dataset = {**self.DEFAULTS, **dataset, **data}

			# save dataset
			await db.dataset_update(id, dataset)

			# save meta file
			dataset_dir = os.path.join(env.DATASETS_DIR, dataset['_id'])
			meta = backend.FileMeta(os.path.join(dataset_dir, 'meta.json'))
			await meta.create(dataset)

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode({ '_id': id }))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to update dataset \"%s\"' % id))

	@role_required(['admin'])
	async def delete(self, id):
		db = self.settings['db']

		try:
			# delete dataset
			await db.dataset_delete(id)

			# delete dataset directory
			shutil.rmtree(os.path.join(env.DATASETS_DIR, id), ignore_errors=True)

			self.set_status(200)
			self.write(message(200, 'Dataset \"%s\" was deleted' % id))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to delete dataset \"%s\"' % id))




class DatasetUploadHandler(CORSAuthMixin, tornado.web.RequestHandler):

	@role_required([])
	async def post(self, id, format, parameter):
		db = self.settings['db']

		# make sure request body contains files
		files = self.request.files

		if not files:
			self.set_status(400)
			self.write(message(400, 'No files were uploaded'))
			return

		try:
			# get dataset
			dataset = await db.dataset_get(id)
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Dataset \"%s\" was not found' % id))

		# determine which type of upload to do
		if format == "directory-path":
			try:
				# initialize input directory using the parameter 'directory-path'
				input_dir = os.path.join(env.DATASETS_DIR, id, parameter)
				os.makedirs(input_dir, exist_ok=True)

				# save uploaded files to input directory
				filenames = []

				for f_list in files.values():
					for f_arg in f_list:
						filename, body = f_arg['filename'], f_arg['body']
						# get the filename
						filename = os.path.basename(filename)
						with open(os.path.join(input_dir, filename), 'wb') as f:
							f.write(body)
						filenames.append(filename)

				# increase n_files
				dataset['n_files'] += len(filenames)

				# save dataset
				await db.dataset_update(id, dataset)

				self.set_status(200)
				self.write(message(200, 'File \"%s\" was uploaded for dataset \"%s\" successfully' % (filenames, id)))
			except Exception as e:
				log_exception(e)
				self.set_status(404)
				self.write(message(404, 'Failed to upload the file for dataset \"%s\"' % id))

		# determine which type of upload to do
		elif format == "file-path":
			try:
				# initialize input directory
				input_dir = os.path.join(env.DATASETS_DIR, id)
				os.makedirs(input_dir, exist_ok=True)

				# save uploaded files to input directory
				filenames = []

				for f_list in files.values():
					for f_arg in f_list:
						filename, body = f_arg['filename'], f_arg['body']
						# rename the filename based on 'parameter' query 'file-path'
						filename = parameter + os.path.splitext(os.path.basename(filename))[1]
						with open(os.path.join(input_dir, filename), 'wb') as f:
							f.write(body)
						filenames.append(filename)

				# increase n_files
				dataset['n_files'] += len(filenames)

				# save dataset
				await db.dataset_update(id, dataset)

				self.set_status(200)
				self.write(message(200, 'File \"%s\" was uploaded for dataset \"%s\" successfully' % (filenames, id)))
			except Exception as e:
				log_exception(e)
				self.set_status(404)
				self.write(message(404, 'Failed to upload the file for dataset \"%s\"' % id))

		# determine which type of upload to do
		else:
			self.set_status(404)
			self.write(message(404, 'The \"%s\" value for the query is not correct. Try with ["directory-path","file-path"]' % format))




class DatasetLinkHandler(CORSAuthMixin, tornado.web.RequestHandler):

	REQUIRED_KEYS = set([
		'name',
		'path'
	])

	@role_required([])
	async def post(self, id):
		db = self.settings['db']

		# make sure request body is valid
		try:
			data = tornado.escape.json_decode(self.request.body)
			missing_keys = self.REQUIRED_KEYS - data.keys()
		except json.JSONDecodeError:
			self.set_status(422)
			self.write(message(422, 'Ill-formatted JSON'))
			return

		if missing_keys:
			self.set_status(400)
			self.write(message(400, 'Missing required field(s): %s' % list(missing_keys)))
			return

		try:
			# get dataset
			dataset = await db.dataset_get(id)
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Dataset \"%s\" was not found' % id))

		try:
			# to track data
			link_name = data['name']
			link_path = data['path']

			# initialize input directory
			input_dir = os.path.join(env.DATASETS_DIR, id)
			os.makedirs(input_dir, exist_ok=True)

			# check if link already exists
			link_filename = os.path.join(input_dir, link_name)
			if os.path.exists(link_filename):
				self.set_status(400)
				self.write(message(400, 'Link \"%s\" already exists' % link_filename))
				return

			# create symbolic link
			os.symlink(link_path, link_filename)

			# increase n_files
			dataset['n_files'] += 1

			# save dataset
			await db.dataset_update(id, dataset)

			self.set_status(200)
			self.write(message(200, 'Link to \"%s\" created successfully at \"%s\" successfully' % (link_path, link_filename)))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to craete link for dataset \"%s\"' % id))




class DatasetDeleteHandler(CORSAuthMixin, tornado.web.RequestHandler):

	REQUIRED_KEYS = set([
		'filenames'
	])

	@role_required([])
	async def delete(self, id):
		db = self.settings['db']

		# make sure request body is valid
		try:
			data = tornado.escape.json_decode(self.request.body)
			missing_keys = self.REQUIRED_KEYS - data.keys()
		except json.JSONDecodeError:
			self.set_status(422)
			self.write(message(422, 'Ill-formatted JSON'))
			return

		if missing_keys:
			self.set_status(400)
			self.write(message(400, 'Missing required field(s): %s' % list(missing_keys)))
			return

		try:
			# get dataset
			dataset = await db.dataset_get(id)
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Dataset \"%s\" was not found' % id))

		try:
			# directory where the dataset's files are stored
			input_dir = os.path.join(env.DATASETS_DIR, id)

			# to track deleted files
			filenames = data['filenames']

			for filename in filenames:
				f_path = os.path.join(input_dir, filename)
				# remove the file and decrease the number of files
				if os.path.exists(f_path):
 					# handle symbolic links
					if os.path.islink(f_path):
						os.unlink(f_path)
						dataset['n_files'] = max(0, dataset['n_files'] - 1)  # ensure it doesn't go below 0
					# handle directories
					elif os.path.isdir(f_path):
						fc = sum(len(files) for _, _, files in os.walk(f_path)) # conunt the num files
						shutil.rmtree(f_path, ignore_errors=True)
						dataset['n_files'] -= max(0, dataset['n_files'] - fc) # descrease the num. files that has been deleted. ensure it doesn't go below 0
					# handle regular files
					else:
						os.remove(f_path)
						dataset['n_files'] = max(0, dataset['n_files'] - 1)  # ensure it doesn't go below 0
				else:
					raise KeyError('File \"%s\" does not exists' % (filename))

			# save dataset
			await db.dataset_update(id, dataset)

			self.set_status(200)
			self.write(message(200, 'Files \"%s\" were deleted for dataset \"%s\" successfully' % (','.join(filenames), id)))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to remove the files for dataset \"%s\"' % id))







#-------------------------------------
# WORKFLOW Classes
#-------------------------------------

class WorkflowQueryHandler(CORSAuthMixin, tornado.web.RequestHandler):

	@role_required([])
	async def get(self):
		page = int(self.get_query_argument('page', 0))
		page_size = int(self.get_query_argument('page_size', 100))

		db = self.settings['db']

		# return all workflows if user is admin
		if await is_admin(db, self.current_user):
			workflows = await db.workflow_query('admin', page, page_size)
		else:
			workflows = await db.workflow_query(self.current_user['_id'], page, page_size)

		self.set_status(200)
		self.set_header('content-type', 'application/json')
		self.write(tornado.escape.json_encode(workflows))



class WorkflowCreateHandler(CORSAuthMixin, tornado.web.RequestHandler):

	REQUIRED_KEYS = set([
		'pipeline',
		'revision',
		'profiles'
	])

	DEFAULTS = {
		'name': '',
		'author': '',
		'description': '',
		'revision': 'main',
		'profiles': 'guest',
		'n_attempts': 0,
		'attempts': []
	}

	@role_required([])
	def get(self):
		workflow = {**self.DEFAULTS, **{ '_id': '0' }}

		self.set_status(200)
		self.set_header('content-type', 'application/json')
		self.write(tornado.escape.json_encode(workflow))

	@role_required([])
	async def post(self):
		db = self.settings['db']

		# make sure request body is valid
		try:
			data = tornado.escape.json_decode(self.request.body)
			missing_keys = self.REQUIRED_KEYS - data.keys()
		except json.JSONDecodeError:
			self.set_status(422)
			self.write(message(422, 'Ill-formatted JSON'))
			return

		if missing_keys:
			self.set_status(400)
			self.write(message(400, 'Missing required field(s): %s' % list(missing_keys)))
			return

		try:
			# create workflow
			workflow = {**self.DEFAULTS, **data, **{ 'status': 'nascent' }}
			workflow['_id'] = str(bson.ObjectId())

			# append creation timestamp to workflow
			workflow['date_created'] = int(time.time() * 1000)

			# transform pipeline name to lowercase
			workflow['pipeline'] = workflow['pipeline'].lower() 

			# append the current user id
			workflow['user_id'] = self.current_user['_id']

			# save workflow
			await db.workflow_create(workflow)

			# create workflow directory
			workflow_dir = os.path.join(env.WORKFLOWS_DIR, workflow['_id'])
			os.makedirs(workflow_dir)

			# save meta file
			meta = backend.FileMeta(os.path.join(workflow_dir, 'meta.json'))
			await meta.create(workflow)

			self.set_status(201)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode({ '_id': workflow['_id'] }))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to create workflow \"%s\"' % id))




class WorkflowEditHandler(CORSAuthMixin, tornado.web.RequestHandler):

	REQUIRED_KEYS = set([])

	DEFAULTS = {
		'name': '',
		'author': '',
		'description': '',
		'revision': 'main',
		'profiles': 'guest',
		'n_attempts': 0,
		'attempts': []
	}

	@role_required([])
	async def get(self, id):
		db = self.settings['db']

		try:
			# get workflow
			workflow = await db.workflow_get(id)

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(workflow))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to get workflow \"%s\"' % id))

	@role_required([])
	async def post(self, id):
		db = self.settings['db']

		# make sure request body is valid
		try:
			data = tornado.escape.json_decode(self.request.body)
			missing_keys = self.REQUIRED_KEYS - data.keys()
		except json.JSONDecodeError:
			self.set_status(422)
			self.write(message(422, 'Ill-formatted JSON'))

		if missing_keys:
			self.set_status(400)
			self.write(message(400, 'Missing required field(s): %s' % list(missing_keys)))
			return

		try:
			# update workflow from request body
			workflow = await db.workflow_get(id)
			workflow = {**self.DEFAULTS, **workflow, **data}

			# transform pipeline name to lowercase
			workflow['pipeline'] = workflow['pipeline'].lower() 

			# save workflow
			await db.workflow_update(id, workflow)

			# save meta file
			workflow_dir = os.path.join(env.WORKFLOWS_DIR, workflow['_id'])
			meta = backend.FileMeta(os.path.join(workflow_dir, 'meta.json'))
			await meta.create(workflow)

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode({ '_id': id }))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to update workflow \"%s\"' % id))

	@role_required(['admin'])
	async def delete(self, id):
		db = self.settings['db']

		try:
			# delete workflow
			await db.workflow_delete(id)

			# delete workflow directory
			shutil.rmtree(os.path.join(env.WORKFLOWS_DIR, id), ignore_errors=True)

			self.set_status(200)
			self.write(message(200, 'Workflow \"%s\" was deleted' % id))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to delete workflow \"%s\"' % id))




class WorkflowLaunchHandler(CORSAuthMixin, tornado.web.RequestHandler):

	REQUIRED_KEYS = set([
		'inputs'
	])

	DEFAULTS = {
		'inputs': [],
		'resume': False
	}


	@role_required([])
	async def post(self, id):
		db = self.settings['db']

		# make sure request body is valid
		try:
			data = tornado.escape.json_decode(self.request.body)
			missing_keys = self.REQUIRED_KEYS - data.keys()
		except json.JSONDecodeError:
			self.set_status(422)
			self.write(message(422, 'Ill-formatted JSON'))
			return

		if missing_keys:
			self.set_status(400)
			self.write(message(400, 'Missing required field(s): %s' % list(missing_keys)))
			return

		try:
			# get workflow
			workflow = await db.workflow_get(id)
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to get workflow \"%s\"' % id))
			return

		# make sure workflow is not already running
		if workflow['status'] == 'running':
			self.set_status(400)
			self.write(message(400, 'Workflow \"%s\" is already running' % id))
			return

		try:

			# update workflow from request body
			workflow = await db.workflow_get(id)

			# update data from request body
			data = {**self.DEFAULTS, **data}

			# update workflow status
			workflow['status'] = 'running'
			workflow['n_attempts'] += 1

			# set up the workflow directory
			workflow_dir = os.path.join(env.WORKFLOWS_DIR, id)

			# set up the attempt directory
			attempt_dir = os.path.join(id, str(workflow['n_attempts']))

			# update attempt execution
			attempt = {
				'id': workflow['n_attempts'],
				'description': data['description'],
				'inputs': data['inputs'],
				'date_submitted': int(time.time() * 1000),
				'status': 'running',
				'output_dir': attempt_dir
			}
			workflow['attempts'].append(attempt)

			await db.workflow_update(id, workflow)

			# copy nextflow.config from nextflow configuration folder
			os.makedirs(workflow_dir, exist_ok=True)
			src = os.path.join(env.NXF_CONF, 'nextflow.config')
			dst = os.path.join(workflow_dir, 'nextflow.config')

			if os.path.exists(dst):
				os.remove(dst)   

			if os.path.exists(src):
				shutil.copyfile(src, dst)

			# append additional settings to nextflow.config
			with open(dst, 'a') as f:
				weblog_url = 'http://%s:%d/api/tasks' % (socket.gethostbyname(socket.gethostname()), tornado.options.options.port)
				f.write('weblog { enabled = true\n url = \"%s\" }\n' % (weblog_url))
				f.write('k8s { launchDir = \"%s\" }\n' % (workflow_dir))

			# set up the output directory
			output_dir = os.path.join(env.OUTPUTS_DIR, attempt_dir)
			os.makedirs(output_dir, exist_ok=True)

			# launch workflow as a child process
			p = mp.Process(target=Workflow.launch, args=(db, workflow, attempt, workflow_dir, output_dir, data['resume']))
			p.start()

			self.set_status(200)
			self.write(message(200, 'Workflow \"%s\" was launched' % id))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to launch workflow \"%s\"' % id))



class WorkflowCancelHandler(CORSAuthMixin, tornado.web.RequestHandler):

	@role_required([])
	async def post(self, id):
		db = self.settings['db']

		try:
			# get workflow
			workflow = await db.workflow_get(id)
			workflow = {**{ 'pid': -1 }, **workflow}

			# get last attempt because has to be the running one
			n_attempt = int(workflow['n_attempts'] - 1)

			# cancel workflow
			Workflow.cancel(workflow)

			# update workflow status
			workflow['status'] = 'canceled'
			workflow['attempts'][n_attempt]['status'] = 'canceled'
			workflow['pid'] = -1

			await db.workflow_update(id, workflow)

			self.set_status(200)
			self.write(message(200, 'Workflow \"%s\" was canceled' % id))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to cancel workflow \"%s\"' % id))



class WorkflowLogHandler(CORSAuthMixin, tornado.web.RequestHandler):

	@role_required([])
	async def get(self, id, attempt_id):
		db = self.settings['db']

		try:
			# get workflow
			workflow = await db.workflow_get(id)

			# get atempt
			# convert the attempt to the index of list (minus one)
			n_attempt = int(attempt_id) - 1
			attempt = workflow['attempts'][n_attempt]

			# get append data if it exists
			log_file = os.path.join(env.OUTPUTS_DIR, attempt['output_dir'], '.workflow.log')
			if os.path.exists(log_file):
				f = open(log_file)
				log = ''.join(f.readlines())
				# get the attempt data
				description = attempt['description']
				status = attempt['status']
				date_submitted = attempt['date_submitted']
			else:
				log = ''
				status = ''
				date_submitted = ''

			# construct response data
			data = {
				'_id': id,
				'attempt': attempt_id,
				'description': description,
				'status': status,
				'date_submitted': date_submitted,
				'log': log
			}

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.set_header('cache-control', 'no-store, no-cache, must-revalidate, max-age=0')
			self.write(tornado.escape.json_encode(data))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to fetch log for workflow \"%s\"' % id))




# class WorkflowDownloadHandler(tornado.web.StaticFileHandler):

# 	def parse_url_path(self, id):
# 		# provide output file if path is specified, otherwise output data archive
# 		filename_default = 'outputs-%s-%s.zip' % (id, attempt)
# 		filename = self.get_query_argument('path', filename_default)

# 		self.set_header('content-disposition', 'attachment; filename=\"%s\"' % filename)
# 		return os.path.join(id, filename)




#-------------------------------------
# OUTPUTS Classes
#-------------------------------------

class OutputEditHandler(CORSAuthMixin, tornado.web.RequestHandler):

	@role_required([])
	async def get(self, id, attempt):
		db = self.settings['db']

		try:
			# get workflow
			workflow = await db.workflow_get(id)

			# get output directory from attempt
			output_dir = os.path.join(env.OUTPUTS_DIR, id, attempt)

			if os.path.exists(output_dir):
				outputs = build_tree(output_dir, relpath_start=output_dir)
				# remove hide files
				# outputs = [o for o in outputs if not o['name'].startswith('.')]
			else:
				outputs = []

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(outputs))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to get output attempt from workflow \"%s/%s\"' % (id,attempt)))

	@role_required(['admin'])
	async def delete(self, id, attempt):
		db = self.settings['db']

		try:
			# delete output
			await db.output_delete(id, attempt)

			# get output directory from attempt
			output_dir = os.path.join(env.OUTPUTS_DIR, id, attempt)

			if os.path.exists(output_dir):  
				shutil.rmtree(output_dir, ignore_errors=True)

			self.set_status(200)
			self.write(message(200, 'Output \"%s/%s\" was deleted' % (id,attempt)))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to delete output \"%s/%s\"' % (id,attempt)))



class OutputDownloadHandler(CORSAuthMixin, tornado.web.StaticFileHandler):

	@role_required([])
	def parse_url_path(self, data):
		# get the given parameters
		id = data.split('/')[0]
		filename_default = '/'.join(data.split('/')[1:])

		# provide output file if path is specified, otherwise output data archive
		filename = self.get_query_argument('path', filename_default)

		# set up the output from the attempt directory and filename
		self.set_header('content-disposition', 'attachment; filename=\"%s\"' % filename)
		output = os.path.join(env.OUTPUTS_DIR, id, filename_default)
		return output



class OutputMultipleDownloadHandler(CORSAuthMixin, tornado.web.RequestHandler):

	@role_required([])
	async def post(self, id, attempt):
		db = self.settings['db']

		# make sure request body is valid
		try:
			data = tornado.escape.json_decode(self.request.body)
		except json.JSONDecodeError:
			self.set_status(422)
			self.write(message(422, 'Ill-formatted JSON'))

		try:
			# update workflow from request body
			workflow = await db.workflow_get(id)

			# get output directory from attempt
			output_dir = os.path.join(env.OUTPUTS_DIR, id, attempt)

			# # create zip archive of outputt files
			# zipfile = os.path.join(env.TRACES_DIR, 'traces-%s-%s-%s.zip' % (id, attempt, str(bson.ObjectId())) )
			# # ofiles = [o for o in data]
			# subprocess.run(['zip', zipfile] + data, check=True, cwd=output_dir)


			# create an in-memory zip file
			memory_zip = io.BytesIO()
			with zipfile.ZipFile(memory_zip, 'w') as zf:
				for f in data:
					# get the absolute path
					file_path = os.path.join(output_dir, f)
					# add the file to the zip archive
					zf.write(file_path, arcname=f)

					# the following code is you want to compress the files without folders:
					# # extract the file name from the path
					# file_name = os.path.basename(file_path)
					# # add the file to the zip archive
					# zf.write(file_path, arcname=f)
	 

   
			# set the appropriate headers
			self.set_header("Content-Type", "application/zip")
			self.set_header("Content-Disposition", "attachment; filename=%s.zip" % f"outputs-{id}-{attempt}")
			
			# write the zip file data to the response
			self.write(memory_zip.getvalue())
		
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to download the multiple output files for \"%s/%s\"' % (id,attempt)))



class OutputArchiveDownloadHandler(CORSAuthMixin, tornado.web.StaticFileHandler):

	@role_required([])
	def parse_url_path(self, data):
		# get the given parameters
		(id, attempt) = data.split('/')

		# provide output file if path is specified, otherwise output data archive
		filename_default = 'outputs-%s-%s.zip' % (id, attempt)
		filename = self.get_query_argument('path', filename_default)

		# set up the output from the attempt directory and filename
		self.set_header('content-disposition', 'attachment; filename=\"%s\"' % filename)
		output = os.path.join(env.OUTPUTS_DIR, id, filename)
		return output
	



#-------------------------------------
# VOLUMES Classes
#-------------------------------------

class VolumeQueryHandler(CORSAuthMixin, tornado.web.RequestHandler):

	@role_required([])
	async def get(self, volume_dir=''):

		# get the files/folders from the shared volumes
		def _get_volumes(shared_volumes, volume_dir):
			# get the shared volumes from the environment variable and split them
			# prepare a list to collect file tree outputs from each volume
			all_outputs = []
			# split the "path" into components
			# delete the first folder of path
			volume_dir_components = volume_dir.split('/') if volume_dir else []
			if volume_dir_components:
				matched_volumes = [v for v in shared_volumes if volume_dir.startswith(v)]
			else:
				matched_volumes = shared_volumes
			# iterate over each matched volumes and build its file tree
			for volume in matched_volumes:
				# join the provided path with the current volume
				output_dir = os.path.join(volume, volume_dir)
				# check if the directory exists
				if os.path.exists(output_dir):
					outputs = scan_directory(output_dir)
					all_outputs.append({
						'volume': output_dir,
						'files': outputs
					})
			# retrieve volume files
			return all_outputs

		try:
			# get the files/folders from the datasets
			outputs_workspace = _get_volumes([env.DATASETS_DIR, env.WORKFLOWS_DIR], volume_dir)

			# get the shared volumes from the environment variable
			outputs_shared = _get_volumes(env.SHARED_VOLUMES.split(';'), volume_dir)

			# join datasets + workflows + shared volumes
			all_outputs = outputs_workspace + outputs_shared

			# respond with the combined file trees for all volumes
			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(all_outputs))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to get volume from path \"%s\"' % (volume_dir)))




#-------------------------------------
# TASKS Classes
#-------------------------------------

class TaskQueryHandler(CORSMixin, tornado.web.RequestHandler):

	async def get(self):
		page = int(self.get_query_argument('page', 0))
		page_size = int(self.get_query_argument('page_size', 100))

		db = self.settings['db']
		tasks = await db.task_query(page, page_size)

		self.set_status(200)
		self.set_header('content-type', 'application/json')
		self.write(tornado.escape.json_encode(tasks))

	async def post(self):
		db = self.settings['db']

		# make sure request body is valid
		try:
			task = tornado.escape.json_decode(self.request.body)
		except json.JSONDecodeError:
			self.set_status(422)
			self.write(message(422, 'Ill-formatted JSON'))
			return

		try:
			# append id to task
			task['_id'] = str(bson.ObjectId())

			# extract input features for task
			if task['event'] == 'process_completed':
				# load execution log
				filenames = ['.command.log', '.command.out', '.command.err']
				filenames = [os.path.join(task['trace']['workdir'], filename) for filename in filenames]
				files = [open(filename) for filename in filenames if os.path.exists(filename)]
				lines = [line.strip() for f in files for line in f]

				# parse input features from trace directives
				PREFIX = '#TRACE'
				lines = [line[len(PREFIX):] for line in lines if line.startswith(PREFIX)]
				items = [line.split('=') for line in lines]
				conditions = {k.strip(): v.strip() for k, v in items}

				# append input features to task trace
				task['trace'] = {**task['trace'], **conditions}

			# save task
			await db.task_create(task)

			# update workflow status on completed event
			if task['event'] == 'completed':
				# get workflow
				workflow_id = task['runName'].split('-')[1]
				workflow = await db.workflow_get(workflow_id)
				# get last attempt because has to be the running one
				n_attempt = int(workflow['n_attempts'] - 1)

				# # update workflow status
				# success = task['metadata']['workflow']['success']
				# if success:
				# 	workflow['status'] = 'completed'
				# 	workflow['attempts'][n_attempt]['status'] = 'completed'

				# else:
				# 	workflow['status'] = 'failed'
				# 	workflow['attempts'][n_attempt]['status'] = 'failed'

				await db.workflow_update(workflow['_id'], workflow)

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode({ '_id': task['_id'] }))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to save task'))



class TaskLogHandler(CORSMixin, tornado.web.RequestHandler):

	async def get(self, id):
		db = self.settings['db']

		try:
			# get workflow
			task = await db.task_get(id)
			workdir = task['trace']['workdir']

			# construct response data
			data = {
				'_id': id,
				'out': '',
				'err': ''
			}

			# append log files if they exist
			out_file = os.path.join(workdir, '.command.out')
			err_file = os.path.join(workdir, '.command.err')

			if os.path.exists(out_file):
				f = open(out_file)
				data['out'] = ''.join(f.readlines())

			if os.path.exists(err_file):
				f = open(err_file)
				data['err'] = ''.join(f.readlines())

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(data))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to fetch log for workflow \"%s\"' % id))



class TaskQueryPipelinesHandler(CORSMixin, tornado.web.RequestHandler):

	async def get(self):
		db = self.settings['db']

		try:
			# query pipelines from database
			pipelines = await db.task_query_pipelines()

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(pipelines))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to perform query'))
			raise e



class TaskQueryPipelineHandler(CORSMixin, tornado.web.RequestHandler):

	async def get(self, pipeline):
		db = self.settings['db']

		try:
			# query tasks from database
			pipeline = pipeline.lower()
			tasks = await db.task_query_pipeline(pipeline)
			tasks = [task['trace'] for task in tasks]

			# separate tasks into dataframes by process
			process_names = list(set([task['process'] for task in tasks]))
			dfs = {}

			for process in process_names:
				dfs[process] = [task for task in tasks if task['process'] == process]

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(dfs))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to perform query'))
			raise e



class TaskArchiveHandler(CORSMixin, tornado.web.RequestHandler):

	async def get(self, pipeline):
		db = self.settings['db']

		try:
			# query tasks from database
			pipeline = pipeline.lower()
			tasks = await db.task_query_pipeline(pipeline)
			tasks = [task['trace'] for task in tasks]

			# separate tasks into dataframes by process
			process_names = list(set([task['process'] for task in tasks]))
			dfs = {}

			for process in process_names:
				dfs[process] = pd.DataFrame([task for task in tasks if task['process'] == process])

			# change to trace directory
			os.chdir(env.TRACES_DIR)

			# save dataframes to csv files
			for process in process_names:
				filename = 'trace.%s.txt' % (process)
				dfs[process].to_csv(filename, sep='\t', index=False)

			# create zip archive of trace files
			zipfile = 'trace.%s.zip' % (pipeline.replace('/', '__'))
			files = ['trace.%s.txt' % (process) for process in process_names]

			subprocess.run(['zip', zipfile] + files, check=True)
			subprocess.run(['rm', '-f'] + files, check=True)

			# return to working directory
			os.chdir('..')

			self.set_status(200)
			self.write(message(200, 'Archive was created'))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to create archive'))
			raise e



class TaskArchiveDownloadHandler(CORSMixin, tornado.web.StaticFileHandler):

	def parse_url_path(self, pipeline):
		# get filename of trace archive
		filename = 'trace.%s.zip' % (pipeline.replace('/', '__'))

		self.set_header('content-disposition', 'attachment; filename=\"%s\"' % filename)
		return filename



class TaskVisualizeHandler(CORSMixin, tornado.web.RequestHandler):

	async def post(self):
		db = self.settings['db']

		try:
			# parse request body
			data = tornado.escape.json_decode(self.request.body)

			# query task dataset from database
			pipeline = data['pipeline'].lower()
			tasks = await db.task_query_pipeline(pipeline)
			tasks = [task['trace'] for task in tasks]
			tasks_process = [task for task in tasks if task['process'] == data['process']]

			df = pd.DataFrame(tasks_process)

			# prepare visualizer args
			args = data['args']
			args['plot_name'] = str(bson.ObjectId())

			if args['selectors'] == '':
				args['selectors'] = []
			else:
				args['selectors'] = args['selectors'].split(' ')

			# append columns from merge process if specified
			if 'merge_process' in args:
				# load merge data
				tasks_merge = [task for task in tasks if task['process'] == args['merge_process']]
				df_merge = pd.DataFrame(tasks_merge)

				# remove duplicate columns
				dupe_columns = set(df.columns).intersection(df_merge.columns)
				dupe_columns.remove(args['merge_key'])
				df_merge.drop(columns=dupe_columns, inplace=True)

				# append merge columns to data
				df = df.merge(df_merge, on=args['merge_key'], how='left', copy=False)

			# create visualization
			outfile = Visualizer.visualize(df, args)

			# encode image file into base64
			with open(outfile, 'rb') as f:
				image_data = base64.b64encode(f.read()).decode('utf-8')

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(image_data))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to visualize data'))
			raise e



class TaskEditHandler(CORSMixin, tornado.web.RequestHandler):

	async def get(self, id):
		db = self.settings['db']

		try:
			task = await db.task_get(id)

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(task))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to get task \"%s\"' % id))




#-------------------------------------
# MODEL Classes: NOT IMPLEMENTED!!
#-------------------------------------

class ModelTrainHandler(CORSMixin, tornado.web.RequestHandler):

	async def post(self):
		db = self.settings['db']

		try:
			# parse request body
			data = tornado.escape.json_decode(self.request.body)

			# query task dataset from database
			pipeline = data['pipeline'].lower()
			tasks = await db.task_query_pipeline(pipeline)
			tasks = [task['trace'] for task in tasks]
			tasks_process = [task for task in tasks if task['process'] == data['process']]

			df = pd.DataFrame(tasks_process)

			# prepare training args
			args = data['args']
			args['hidden_layer_sizes'] = [int(v) for v in args['hidden_layer_sizes'].split(' ')]
			args['model_name'] = '%s.%s.%s' % (pipeline.replace('/', '__'), data['process'], args['target'])

			if args['selectors'] == '':
				args['selectors'] = []
			else:
				args['selectors'] = args['selectors'].split(' ')

			# append columns from merge process if specified
			if args['merge_process'] != None:
				# load merge data
				tasks_merge = [task for task in tasks if task['process'] == args['merge_process']]
				df_merge = pd.DataFrame(tasks_merge)

				# remove duplicate columns
				dupe_columns = set(df.columns).intersection(df_merge.columns)
				dupe_columns.remove(args['merge_key'])
				df_merge.drop(columns=dupe_columns, inplace=True)

				# append merge columns to data
				df = df.merge(df_merge, on=args['merge_key'], how='left', copy=False)

			# train model
			results = Model.train(df, args)

			# visualize training results
			df = pd.DataFrame()
			df['y_true'] = results['y_true']
			df['y_pred'] = results['y_pred']

			outfile = Visualizer.visualize(df, {
				'xaxis': 'y_true',
				'yaxis': 'y_pred',
				'plot_name': str(bson.ObjectId())
			})

			# encode image file into base64
			with open(outfile, 'rb') as f:
				results['scatterplot'] = base64.b64encode(f.read()).decode('utf-8')

			# remove extra fields from results
			del results['y_true']
			del results['y_pred']

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(results))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to train model'))
			raise e



class ModelConfigHandler(CORSMixin, tornado.web.RequestHandler):

	async def get(self):
		try:
			# parse request body
			pipeline = self.get_argument('pipeline', default=None)
			process = self.get_argument('process', default=None)
			target = self.get_argument('target', default=None)

			# get model config file
			filename = '%s/%s.%s.%s.json' % (env.MODELS_DIR, pipeline.lower().replace('/', '__'), process, target)

			with open(filename, 'r') as f:
				config = json.load(f)

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(config))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to get model config'))
			raise e



class ModelPredictHandler(CORSMixin, tornado.web.RequestHandler):

	async def post(self):
		try:
			# parse request body
			data = tornado.escape.json_decode(self.request.body)
			data['pipeline'] = data['pipeline'].lower()
			data['model_name'] = '%s.%s.%s' % (data['pipeline'].replace('/', '__'), data['process'], data['target'])

			# perform model prediction
			results = Model.predict(data['model_name'], data['inputs'])

			self.set_status(200)
			self.set_header('content-type', 'application/json')
			self.write(tornado.escape.json_encode(results))
		except Exception as e:
			log_exception(e)
			self.set_status(404)
			self.write(message(404, 'Failed to perform model prediction'))
			raise e



if __name__ == '__main__':

	# parse command-line options
	tornado.options.define('backend', default='mongo', help='Database backend to use (file or mongo)')
	tornado.options.define('url-file', default='db.pkl', help='database file for file backend')
	tornado.options.define('url-mongo', default='localhost', help='mongodb service url for mongo backend')
	tornado.options.define('np', default=1, help='number of server processes')
	tornado.options.define('port', default=env.PORT_CORE)
	tornado.options.parse_command_line()

	# initialize auxiliary directories
	os.makedirs(env.WORKFLOWS_DIR, exist_ok=True)
	os.makedirs(env.DATASETS_DIR, exist_ok=True)
	os.makedirs(env.TRACES_DIR, exist_ok=True)
	os.makedirs(env.MODELS_DIR, exist_ok=True)
	os.makedirs(env.OUTPUTS_DIR, exist_ok=True)
	
	# initialize api endpoints
	app = tornado.web.Application([
		(r'/api/login', LoginHandler),
		(r'/api/users', UserQueryHandler),
		(r'/api/users/0', UserCreateHandler),
		(r'/api/users/([a-zA-Z0-9-]+)', UserEditHandler),

		(r'/api/datasets', DatasetQueryHandler),
		(r'/api/datasets/0', DatasetCreateHandler),
		(r'/api/datasets/([a-zA-Z0-9-]+)', DatasetEditHandler),
		(r'/api/datasets/([a-zA-Z0-9-]+)/([a-zA-Z-]+)/([a-zA-Z0-9-_]+)/upload', DatasetUploadHandler),
		(r'/api/datasets/([a-zA-Z0-9-]+)/link', DatasetLinkHandler),
		(r'/api/datasets/([a-zA-Z0-9-]+)/delete', DatasetDeleteHandler),

		(r'/api/workflows', WorkflowQueryHandler),
		(r'/api/workflows/0', WorkflowCreateHandler),
		(r'/api/workflows/([a-zA-Z0-9-]+)', WorkflowEditHandler),
		(r'/api/workflows/([a-zA-Z0-9-]+)/launch', WorkflowLaunchHandler),
		(r'/api/workflows/([a-zA-Z0-9-]+)/cancel', WorkflowCancelHandler),
		(r'/api/workflows/([a-zA-Z0-9-]+)/([0-9]+)/log', WorkflowLogHandler),
		# (r'/api/workflows/([a-zA-Z0-9-]+)/download', WorkflowDownloadHandler, dict(path=env.WORKFLOWS_DIR)),

		(r'/api/outputs/([a-zA-Z0-9-]+)/([0-9]+)', OutputEditHandler),
		(r'/api/outputs/single/(.+)/download', OutputDownloadHandler, dict(path=env.BASE_DIR['workspace'])),
		(r'/api/outputs/multiple/([a-zA-Z0-9-]+)/([0-9]+)/download', OutputMultipleDownloadHandler),
		(r'/api/outputs/archive/(.+)/download', OutputArchiveDownloadHandler, dict(path=env.WORKFLOWS_DIR)),

		(r'/api/volumes/?(.*)', VolumeQueryHandler),

		(r'/api/tasks', TaskQueryHandler),
		(r'/api/tasks/([a-zA-Z0-9-]+)/log', TaskLogHandler),
		(r'/api/tasks/pipelines', TaskQueryPipelinesHandler),
		(r'/api/tasks/pipelines/(.+)', TaskQueryPipelineHandler),
		(r'/api/tasks/archive/(.+)/download', TaskArchiveDownloadHandler, dict(path=env.TRACES_DIR)),
		(r'/api/tasks/archive/(.+)', TaskArchiveHandler),
		(r'/api/tasks/visualize', TaskVisualizeHandler),
		(r'/api/tasks/([a-zA-Z0-9-]+)', TaskEditHandler),

		(r'/api/model/train', ModelTrainHandler),
		(r'/api/model/config', ModelConfigHandler),
		(r'/api/model/predict', ModelPredictHandler),
		(r'/(.*)', tornado.web.StaticFileHandler, dict(path='./client', default_filename='index.html'))
	])

	try:
		# spawn server processes
		server = tornado.httpserver.HTTPServer(app, max_buffer_size=1024 ** 100)
		server.bind(tornado.options.options.port)
		server.start(tornado.options.options.np)

		# connect to database
		if tornado.options.options.backend == 'file':
			app.settings['db'] = backend.FileBackend(os.path.join(env.BASE_DIR['workspace'], tornado.options.options.url_file))

		elif tornado.options.options.backend == 'mongo':
			app.settings['db'] = backend.MongoBackend(tornado.options.options.url_mongo)

		else:
			raise KeyError('Backend must be either \'json\' or \'mongo\'')

		# initialize the admin and guest users
		db = app.settings['db']
		tornado.ioloop.IOLoop.current().run_sync(lambda: initialize_users(db))

		# start the event loop
		print('The API is listening on http://%s:%d' % (env.HOST_NAME, tornado.options.options.port), flush=True)
		tornado.ioloop.IOLoop.current().start()


	except KeyboardInterrupt:
		tornado.ioloop.IOLoop.current().stop()
	