import os
import ipaddress



# load settings from environment variables
NXF_EXECUTOR = os.environ.get('NXF_EXECUTOR', default='local')
NXF_CONF = os.environ.get('NXF_CONF')
PVC_NAME = os.environ.get('PVC_NAME')



# Define working directories
BASE_DIRS = {
	'k8s':    { 'workspace': '/workspace', 'dataspace': '/dataspace'},
	'local':  { 'workspace': '/workspace', 'dataspace': '/dataspace'},
	'pbspro': { 'workspace': '/workspace', 'dataspace': '/dataspace'},
}
BASE_DIR = BASE_DIRS[NXF_EXECUTOR]

DATASETS_DIR = os.path.join(BASE_DIR['workspace'], '_datasets')
WORKFLOWS_DIR = os.path.join(BASE_DIR['workspace'], '_workflows')
TRACES_DIR = os.path.join(BASE_DIR['workspace'], '_traces')
MODELS_DIR = os.path.join(BASE_DIR['workspace'], '_models')
OUTPUTS_DIR = ''



# Backend-Frontend: Access-Control-Allow-Origin
PORT_CORE = int(os.environ.get('PORT_CORE', 8080))
PORT_APP = int(os.environ.get('PORT_APP', 3000))
HOST_IP = os.environ.get('HOST_IP')

# create HOST list for the cross-reference
CORS_HOSTS = [f"http://localhost:{PORT_APP}"]

# append an external IP host from environment
def is_valid_ip(ip_str):
	try:
		# Intenta crear un objeto IPv4Address o IPv6Address
		ipaddress.ip_address(ip_str)
		return True
	except ValueError:
		return False
if HOST_IP is not None and is_valid_ip(HOST_IP):
	CORS_HOSTS.append(f"http://{HOST_IP}:{PORT_APP}")




# Validate environment settings
if NXF_EXECUTOR == 'k8s' and PVC_NAME is None:
	raise EnvironmentError('Using k8s executor but PVC is not defined')