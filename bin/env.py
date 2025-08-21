import os
import ipaddress
import re

# Nextflow variables -----
NXF_API_HOME = os.environ.get('NXF_API_HOME', '/opt/nextflow-api')



# Nextflow variables -----
NXF_EXECUTOR = os.environ.get('NXF_EXECUTOR', default='local')
NXF_CONF = os.environ.get('NXF_CONF')
PVC_NAME = os.environ.get('PVC_NAME')



# Define working directories -----
DATASPACE_HOME = os.environ.get('WORKSPACE_HOME', '/dataspace')
WORKSPACE_HOME = os.environ.get('WORKSPACE_HOME', '/workspace')
OUTSPACE_HOME = os.environ.get('OUTSPACE_HOME', '/outspace')
BASE_DIRS = {
	'k8s':    { 'dataspace': DATASPACE_HOME, 'workspace': WORKSPACE_HOME, 'outspace': OUTSPACE_HOME },
	'local':  { 'dataspace': DATASPACE_HOME, 'workspace': WORKSPACE_HOME, 'outspace': OUTSPACE_HOME },
	'pbspro': { 'dataspace': DATASPACE_HOME, 'workspace': WORKSPACE_HOME, 'outspace': OUTSPACE_HOME },
}
BASE_DIR = BASE_DIRS[NXF_EXECUTOR]

DATASETS_DIR = os.path.join(BASE_DIR['dataspace'], '_datasets')
WORKFLOWS_DIR = os.path.join(BASE_DIR['workspace'], '_workflows')
TRACES_DIR = os.path.join(BASE_DIR['workspace'], '_traces')
MODELS_DIR = os.path.join(BASE_DIR['workspace'], '_models')
OUTPUTS_DIR = os.path.join(BASE_DIR['outspace'], '_outputs')



# Backend-Frontend: Access-Control-Allow-Origin -----
PORT_CORE = int(os.environ.get('PORT_CORE', 8080))
PORT_APP = int(os.environ.get('PORT_APP', 3000))
HOST_NAME = os.environ.get('HOST_NAME')

# create HOST list for the cross-reference
CORS_HOSTS = [f"http://localhost:{PORT_APP}"]

# append an external IP host from environment
def is_valid_host(host_str):
	# check if it's a valid IP
	try:
		ipaddress.ip_address(host_str)
		return True
	except ValueError:
		pass  # it's not an IP, so check if it's a valid hostname
	# define a regex for valid hostnames (RFC 1035)
	hostname_regex = re.compile(r'^(?!-)[A-Za-z0-9.-]{1,253}(?<!-)$')
	return bool(hostname_regex.match(host_str))
if HOST_NAME is not None and is_valid_host(HOST_NAME):
	CORS_HOSTS.append(f"http://{HOST_NAME}:{PORT_APP}")
print(f'** CORS: {CORS_HOSTS}')



# Shared Volumes section -----
SHARED_VOLUMES = os.environ.get('SHARED_VOLUMES')



# MongoDB section -----
MONGODB_DB = os.environ.get('MONGODB_DB')



# Users section -----
# jwt variables
JWT_SECRET = os.environ.get('JWT_SECRET', 'your_jwt_secret')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_EXP_DELTA_SECONDS = int(os.environ.get('JWT_EXP_DELTA_SECONDS', 14400)) # 4h of user session
# guest user
USER_GUEST = os.environ.get('USER_GUEST', 'guest')
PWD_GUEST = os.environ.get('PWD_GUEST', 'guest')
# admin user
USER_ADMIN = os.environ.get('USER_ADMIN', 'admin')
PWD_ADMIN = os.environ.get('PWD_ADMIN', 'admin')



# Validate environment settings -----
if NXF_EXECUTOR == 'k8s' and PVC_NAME is None:
	raise EnvironmentError('Using k8s executor but PVC is not defined')