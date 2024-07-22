import pickle
import json
import sys

# get input arguments
if len(sys.argv) != 2:
    sys.exit("** add the input file (pkl format). E.g. '/workspace/db.pkl'")

# get input rguments
pkl_file = sys.argv[1]

# print pkl file
with open(pkl_file, 'rb') as f:
    data = pickle.load(f)
print(json.dumps(data, indent=4))
