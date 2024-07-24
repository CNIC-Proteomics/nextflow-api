
# Command lines for User

1. Register a user instance
```
bash user/create.sh http://localhost:8081 'guess2' 'guess2'
```

2. Login with a user
```
bash user/login.sh http://localhost:8081 'guess' 'guess' token.txt
bash user/login.sh http://localhost:8081 'guess2' 'guess2' token.txt

bash user/login.sh http://localhost:8081 'admin' '123.qwe' token.txt
```

3. Edit a user (admin user)
```
bash user/edit.sh http://localhost:8081 token.txt 'guess2' '{"role": "guess2", "password": "guess3"}'
```

4. Get a user instance (admin user)
```
bash user/get.sh http://localhost:8081 token.txt 'guess2'
```

5. List all user instances (admin user)
```
bash user/query.sh http://localhost:8081 token.txt
```

6. Delete a user (admin user)
```
bash user/delete.sh http://localhost:8081 token.txt 'guess2'
```

# Command lines for Dataset

1. List all dataset instances on a nextflow server
```
bash dataset/query.sh http://localhost:8081 token.txt
```

2. Create a dataset instance
```
bash dataset/create.sh http://localhost:8081 token.txt '{"experiment": "experiment1", "description": "Short description of dataset"}' dataset_id.txt
```

3. Upload dataset data for a dataset instance on a nextflow server
```
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "directory-path" "raw_files" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-SearchEngine/tests/test_Raws_1/inputs/raw_files/Jurkat_Fr1.raw"

bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "file-path" "exp_table" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test_Recom_1/inputs/exp_table.txt"
```

4. Get a dataset instance on a nextflow server
```
bash dataset/get.sh http://localhost:8081 token.txt dataset_id.txt
```

5. Edit a dataset instance on a nextflow server
```
bash dataset/edit.sh http://localhost:8081 token.txt dataset_id.txt '{"description": "Short description of dataset 2"}'
```

6. Delete a dataset instance on a nextflow server (admin user)
```
bash dataset/delete.sh http://localhost:8081 token.txt dataset_id.txt
```


### Test example for nf-PTM-compass using ReCom dataset
```
bash dataset/create.sh http://localhost:8081 token.txt '{"experiment": "ReCom_dataset_1", "description": "ReCom dataset_1 (TMT_FA)"}' dataset_id.txt
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "directory-path" "recom_files" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test_Recom_1/inputs/recom_files/TMT_FA_1_fr1.txt"
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "directory-path" "recom_files" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test_Recom_1/inputs/recom_files/TMT_FA_1_fr2.txt"
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "file-path" "exp_table" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test_Recom_1/inputs/exp_table.txt"
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "file-path" "database" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test_Recom_1/inputs/database.fasta"
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "file-path" "params-file" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test_Recom_1/inputs/params.ini"
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "file-path" "sitelist_file" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test_Recom_1/inputs/sitelist.txt"
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "file-path" "groupmaker_file" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test_Recom_1/inputs/groupmaker.txt"
```

### Test example for nf-PTM-compass using RefMod dataset
```
bash dataset/create.sh http://localhost:8081 token.txt '{"experiment": "RefMod", "description": "RefMod dataset_1 (BA_DIA)"}' dataset_id.txt
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "directory-path" "refmod_files" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/refmod_files/BA_1_REFRAG.tsv"
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "directory-path" "refmod_files" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/refmod_files/BA_2_REFRAG.tsv"
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "file-path" "exp_table" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/exp_table.txt"
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "file-path" "database" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/database.fasta"
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "file-path" "params-file" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/params.ini"
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "file-path" "sitelist_file" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/sitelist.txt"
bash dataset/upload.sh http://localhost:8081 token.txt dataset_id.txt "file-path" "groupmaker_file" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/groupmaker.txt"
```

# Command lines for Workflow

1. List all workflow instances on a nextflow server
```
bash workflow/query.sh http://localhost:8081 token.txt
```

2. Create a workflow instance
```
bash workflow/create.sh http://localhost:8081 token.txt \
'{"pipeline": "https://github.com/CNIC-Proteomics/nf-PTM-compass",
"revision": "0.1.0",
"profiles": "guess",
"description": "PTM-compass workflow"
}' workflow_id.txt
```

3. Edit a workflow instance
```
bash workflow/edit.sh http://localhost:8081 token.txt workflow_id.txt \
'{"pipeline": "https://github.com/CNIC-Proteomics/nf-PTM-compass",
"revision": "0.1.0",
"profiles": "guess",
"description": "PTM-compass workflow"
}'
```

4. Launch a workflow instance on a nextflow server

Using ReCom as inputs
```
bash workflow/launch.sh http://localhost:8081 token.txt workflow_id.txt \
'{"inputs": [
    {"name": "--recom_files", "type": "directory-path", "value": "'"$(cat dataset_id.txt)"'/recom_files/*"},
    {"name": "--exp_table", "type": "file-path", "value": "'"$(cat dataset_id.txt)"'/exp_table.txt"},
    {"name": "--database", "type": "file-path", "value": "'"$(cat dataset_id.txt)"'/database.fasta"},
    {"name": "--decoy_prefix", "type": "string", "value": "DECOY_"},
    {"name": "--params_file", "type": "file-path", "value": "'"$(cat dataset_id.txt)"'/params-file.ini"},
    {"name": "--sitelist_file", "type": "file-path", "value": "'"$(cat dataset_id.txt)"'/sitelist_file.txt"},
    {"name": "--groupmaker_file", "type": "file-path", "value": "'"$(cat dataset_id.txt)"'/groupmaker_file.txt"}
]
}'
```

Using RefMod as inputs
```
bash workflow/launch.sh http://localhost:8081 token.txt workflow_id.txt \
'{"inputs": [
    {"name": "--refmod_files", "type": "directory-path", "value": "'"$(cat dataset_id.txt)"'/refmod_files/*"},
    {"name": "--exp_table", "type": "file-path", "value": "'"$(cat dataset_id.txt)"'/exp_table.txt"},
    {"name": "--database", "type": "file-path", "value": "'"$(cat dataset_id.txt)"'/database.fasta"},
    {"name": "--decoy_prefix", "type": "string", "value": "DECOY_"},
    {"name": "--params_file", "type": "file-path", "value": "'"$(cat dataset_id.txt)"'/params-file.ini"},
    {"name": "--sitelist_file", "type": "file-path", "value": "'"$(cat dataset_id.txt)"'/sitelist_file.txt"},
    {"name": "--groupmaker_file", "type": "file-path", "value": "'"$(cat dataset_id.txt)"'/groupmaker_file.txt"}
]
}'
```

5. Get the log of a workflow instance on a nextflow server
```
bash workflow/log.sh http://localhost:8081 token.txt workflow_id.txt 4
```

6. Get a workflow instance on a nextflow server
```
bash workflow/get.sh http://localhost:8081 token.txt workflow_id.txt
```

7. Cancel a workflow instance on a nextflow server
```
bash workflow/cancel.sh http://localhost:8081 token.txt workflow_id.txt
```

8. Delete a workflow instance on a nextflow server (admin user)
```
bash workflow/delete.sh http://localhost:8081 token.txt workflow_id.txt
```


# Command lines for outputs

1. Get a list of all outputs for a workflow instance and attempt on a nextflow server
```
bash output/get.sh http://localhost:8081 token.txt workflow_id.txt 4
```

2. Retrieve all data (all files) for a workflow instance and attempt on a nextflow server
```
bash output/archive.sh http://localhost:8081 token.txt workflow_id.txt 4
```

3. Download a single file for a workflow instance and attempt on a Nextflow server.
```
bash output/download_single.sh http://localhost:8081 token.txt workflow_id.txt 4 modules/solver/11_group_maker/experiment_PDMTable_GM.txt
```

4. Download multiple files for a workflow instance and attempt on a Nextflow server.
```
bash output/download_multi.sh http://localhost:8081 token.txt workflow_id.txt 4 \
'[
    "modules/solver/11_group_maker/experiment_PDMTable_GM.txt",
    "modules/solver/12_joiner/experiment_PDMTable_GM_J.txt"
]'
```

5. Delete the outputs for a workflow intance and attempt on a nextflow server
```
bash output/delete.sh http://localhost:8081 token.txt workflow_id.txt 1
```



