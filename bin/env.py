import os

# load settings from environment variables
NXF_EXECUTOR = os.environ.get('NXF_EXECUTOR', default='local')
NXF_CONF = os.environ.get('NXF_CONF')
PVC_NAME = os.environ.get('PVC_NAME')

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
CORS_HOSTS = [
	'http://localhost:3000',
	'http://10.142.33.54:3000'
]

# validate environment settings
if NXF_EXECUTOR == 'k8s' and PVC_NAME is None:
	raise EnvironmentError('Using k8s executor but PVC is not defined')