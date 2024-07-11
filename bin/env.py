import os
import socket

# load settings from environment variables
NXF_EXECUTOR = os.environ.get('NXF_EXECUTOR', default='local')
NXF_CONF = os.environ.get('NXF_CONF')
PVC_NAME = os.environ.get('PVC_NAME')
PORT_CORE = int(os.environ.get('PORT_CORE', 8080))

# define working directories
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

# Frontend: Access-Control-Allow-Origin
PORT_APP = int(os.environ.get('PORT_APP', 3000))

# get the IP address
def get_ipv4_address():
	hostname = socket.gethostname()
	ip_address = socket.gethostbyname(hostname)
	return ip_address

# create HOST list for the cross-reference
CORS_HOSTS = [
	f"http://localhost:{PORT_APP}",
	f"http://{get_ipv4_address()}:{PORT_APP}",
]
print( "CORS ")
print(CORS_HOSTS)

# validate environment settings
if NXF_EXECUTOR == 'k8s' and PVC_NAME is None:
	raise EnvironmentError('Using k8s executor but PVC is not defined')