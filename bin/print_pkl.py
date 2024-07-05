import pickle
import json


with open('/opt/nextflow/nextflow-api/db.pkl', 'rb') as f:
    data = pickle.load(f)
print(json.dumps(data, indent=4))