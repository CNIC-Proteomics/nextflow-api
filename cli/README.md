
# Command lines for Dataset

1. List all dataset instances on a nextflow server
```
bash dataset/query.sh http://localhost:8080
```

2. Create a dataset instance
```
bash dataset/create.sh http://localhost:8080 'experiment1'
```

3. Upload dataset data for a dataset instance on a nextflow server
```
bash dataset/upload.sh http://localhost:8080 66212647c63490ba135050a0 "directory-path" "raw_files" /mnt/tierra/nf-SearchEngine/tests/test1/inputs/raw_files/Jurkat_Fr1.raw

bash dataset/upload.sh http://localhost:8080 66212647c63490ba135050a0 file-path exp_table /mnt/tierra/nf-PTM-compass/tests/test1/inputs/exp_table.txt
```

4. Get a dataset instance on a nextflow server
```
bash dataset/get.sh http://localhost:8080 66212647c63490ba135050a0
```

5. Edit a dataset instance on a nextflow server
```
bash dataset/edit.sh http://localhost:8080 66212647c63490ba135050a0 '{"name":"new_name", "description": "Short description", "auth": "jmrodriguezc"}'
```

6. Delete a dataset instance on a nextflow server
```
bash dataset/delete.sh http://localhost:8080 66212647c63490ba135050a0
```


### Test example for nf-PTM-compass
```
bash dataset/create.sh http://localhost:8080 'dataset_1'
bash dataset/upload.sh http://localhost:8080 665ee947343d00bd066d7251 "directory-path" "re_files" "/mnt/tierra/nf-PTM-compass/tests/test1/inputs/re_files/JAL_Noa3_iT_ALL.txt"
bash dataset/upload.sh http://localhost:8080 665ee947343d00bd066d7251 "directory-path" "re_files" "/mnt/tierra/nf-PTM-compass/tests/test1/inputs/re_files/JAL_NoCD_iTR_ALL.txt"
bash dataset/upload.sh http://localhost:8080 665ee947343d00bd066d7251 "file-path" "exp_table" "/mnt/tierra/nf-PTM-compass/tests/test1/inputs/exp_table.txt"
bash dataset/upload.sh http://localhost:8080 665ee947343d00bd066d7251 "file-path" "database" "/mnt/tierra/nf-PTM-compass/tests/test1/inputs/database.fasta"
bash dataset/upload.sh http://localhost:8080 665ee947343d00bd066d7251 "file-path" "params-file" "/mnt/tierra/nf-PTM-compass/tests/test1/inputs/params.ini"
bash dataset/upload.sh http://localhost:8080 665ee947343d00bd066d7251 "file-path" "sitelist_file" "/mnt/tierra/nf-PTM-compass/tests/test1/inputs/sitelist.txt"
bash dataset/upload.sh http://localhost:8080 665ee947343d00bd066d7251 "file-path" "groupmaker_file" "/mnt/tierra/nf-PTM-compass/tests/test1/inputs/groupmaker.txt"
```


# Command lines for Workflow

1. List all workflow instances on a nextflow server
```
bash workflow/query.sh http://localhost:8080
```

2. Create a workflow instance
```
bash workflow/create.sh http://localhost:8080 \
'{"pipeline": "https://github.com/CNIC-Proteomics/nf-PTM-compass",
"revision": "main",
"profiles": "guess",
"description": "test workflow"
}'
```

3. Edit a workflow instance
```
bash workflow/edit.sh http://localhost:8080 66447ecf309b2cffc914ac88 \
'{"pipeline": "https://github.com/CNIC-Proteomics/nf-PTM-compass",
"revision": "main",
"profiles": "guess",
"description": "test 2 workflow"
}'
```

4. Launch a workflow instance on a nextflow server
```
bash workflow/launch.sh http://localhost:8080 66447ecf309b2cffc914ac88 \
'{"inputs": [
    {"name": "--re_files", "type": "directory-path", "value": "665ee947343d00bd066d7251/re_files/*"},
    {"name": "--exp_table", "type": "file-path", "value": "665ee947343d00bd066d7251/exp_table.txt"},
    {"name": "--database", "type": "file-path", "value": "665ee947343d00bd066d7251/database.fasta"},
    {"name": "--decoy_prefix", "type": "string", "value": "DECOY_"},
    {"name": "--params_file", "type": "file-path", "value": "665ee947343d00bd066d7251/params-file.ini"},
    {"name": "--sitelist_file", "type": "file-path", "value": "665ee947343d00bd066d7251/sitelist_file.txt"},
    {"name": "--groupmaker_file", "type": "file-path", "value": "665ee947343d00bd066d7251/groupmaker_file.txt"}
]
}'
```

5. Get the log of a workflow instance on a nextflow server
```
bash workflow/log.sh http://localhost:8080 66447ecf309b2cffc914ac88
```

6. Get a workflow instance on a nextflow server
```
bash workflow/get.sh http://localhost:8080 66447ecf309b2cffc914ac88
```

7. Cancel a workflow instance on a nextflow server
```
bash workflow/cancel.sh http://localhost:8080 66447ecf309b2cffc914ac88
```


# Command lines for Workflow (root user???)

1. Delete a workflow instance on a nextflow server
```
bash workflow/delete.sh http://localhost:8080 66447ecf309b2cffc914ac88
```


# Command lines for outputs

1. Get a list of all outputs for a workflow instance and attempt on a nextflow server
```
bash output/get.sh http://localhost:8080 66447ecf309b2cffc914ac88 1
```

2. Retrieve all data (all files) for a workflow instance and attempt on a nextflow server
```
bash output/archive.sh http://localhost:8080 66447ecf309b2cffc914ac88 1
```

3. Download a single file for a workflow instance and attempt on a Nextflow server.
```
bash output/download_single.sh http://localhost:8080 66447ecf309b2cffc914ac88 1 modules/solver/10_group_maker/experiment_PDMTable_GM.txt
```

4. Download multiple files for a workflow instance and attempt on a Nextflow server.
```
bash output/download_multi.sh http://localhost:8080 66447ecf309b2cffc914ac88 1 \
'[
    "modules/solver/10_group_maker/experiment_PDMTable_GM.txt",
    "modules/solver/11_joiner/experiment_PDMTable_GM_J.txt"
]'
```

5. Delete the outputs for a workflow intance and attempt on a nextflow server
```
bash output/delete.sh http://localhost:8080 66447ecf309b2cffc914ac88 1
```



