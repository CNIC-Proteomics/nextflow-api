
# Command lines for Dataset

1. List all dataset instances on a nextflow server
```
bash dataset/query.sh http://localhost:8081
```

2. Create a dataset instance
```
bash dataset/create.sh http://localhost:8081 'experiment1'
```

3. Upload dataset data for a dataset instance on a nextflow server
```
bash dataset/upload.sh http://localhost:8081 66212647c63490ba135050a0 "directory-path" "raw_files" /mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-SearchEngine/tests/test1/inputs/raw_files/Jurkat_Fr1.raw

bash dataset/upload.sh http://localhost:8081 66212647c63490ba135050a0 file-path exp_table /mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test1/inputs/exp_table.txt
```

4. Get a dataset instance on a nextflow server
```
bash dataset/get.sh http://localhost:8081 66212647c63490ba135050a0
```

5. Edit a dataset instance on a nextflow server
```
bash dataset/edit.sh http://localhost:8081 66212647c63490ba135050a0 '{"name":"new_name", "description": "Short description", "auth": "jmrodriguezc"}'
```

6. Delete a dataset instance on a nextflow server
```
bash dataset/delete.sh http://localhost:8081 66212647c63490ba135050a0
```


### Test example for nf-PTM-compass using ReCom dataset
```
bash dataset/create.sh http://localhost:8081 'ReCom dataset_2 (TMT_FA)'
bash dataset/upload.sh http://localhost:8081 669146667656a2d7c929a0a6 "directory-path" "recom_files" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test1/inputs/recom_files/TMT_FA_1_fr1.txt"
bash dataset/upload.sh http://localhost:8081 669146667656a2d7c929a0a6 "directory-path" "recom_files" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test1/inputs/recom_files/TMT_FA_1_fr2.txt"
bash dataset/upload.sh http://localhost:8081 669146667656a2d7c929a0a6 "file-path" "exp_table" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test1/inputs/exp_table.txt"
bash dataset/upload.sh http://localhost:8081 669146667656a2d7c929a0a6 "file-path" "database" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test1/inputs/database.fasta"
bash dataset/upload.sh http://localhost:8081 669146667656a2d7c929a0a6 "file-path" "params-file" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test1/inputs/params.ini"
bash dataset/upload.sh http://localhost:8081 669146667656a2d7c929a0a6 "file-path" "sitelist_file" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test1/inputs/sitelist.txt"
bash dataset/upload.sh http://localhost:8081 669146667656a2d7c929a0a6 "file-path" "groupmaker_file" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test1/inputs/groupmaker.txt"
```

### Test example for nf-PTM-compass using RefMod dataset
```
bash dataset/create.sh http://localhost:8081 'RefMod dataset_1'
bash dataset/upload.sh http://localhost:8081 66881f10e563107dfbbc5d96 "directory-path" "refmod_files" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/refmod_files/BA_1_REFRAG.tsv"
bash dataset/upload.sh http://localhost:8081 66881f10e563107dfbbc5d96 "directory-path" "refmod_files" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/refmod_files/BA_2_REFRAG.tsv"
bash dataset/upload.sh http://localhost:8081 66881f10e563107dfbbc5d96 "file-path" "exp_table" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/exp_table.txt"
bash dataset/upload.sh http://localhost:8081 66881f10e563107dfbbc5d96 "file-path" "database" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/database.fasta"
bash dataset/upload.sh http://localhost:8081 66881f10e563107dfbbc5d96 "file-path" "params-file" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/params.ini"
bash dataset/upload.sh http://localhost:8081 66881f10e563107dfbbc5d96 "file-path" "sitelist_file" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/sitelist.txt"
bash dataset/upload.sh http://localhost:8081 66881f10e563107dfbbc5d96 "file-path" "groupmaker_file" "/mnt/tierra/U_Proteomica/UNIDAD/Softwares/jmrodriguezc/nf-PTM-compass/tests/test2/inputs/groupmaker.txt"
```

# Command lines for Workflow

1. List all workflow instances on a nextflow server
```
bash workflow/query.sh http://localhost:8081
```

2. Create a workflow instance
```
bash workflow/create.sh http://localhost:8081 \
'{"pipeline": "https://github.com/CNIC-Proteomics/nf-PTM-compass",
"revision": "main",
"profiles": "guess",
"description": "PTM-compass workflow"
}'
```

3. Edit a workflow instance
```
bash workflow/edit.sh http://localhost:8081 66914843ed0837f367f31de3 \
'{"pipeline": "https://github.com/CNIC-Proteomics/nf-PTM-compass",
"revision": "main",
"profiles": "guess",
"description": "test 2 workflow"
}'
```

4. Launch a workflow instance on a nextflow server

Using ReCom as inputs
```
bash workflow/launch.sh http://localhost:8081 66914843ed0837f367f31de3 \
'{"inputs": [
    {"name": "--recom_files", "type": "directory-path", "value": "669146667656a2d7c929a0a6/recom_files/*"},
    {"name": "--exp_table", "type": "file-path", "value": "669146667656a2d7c929a0a6/exp_table.txt"},
    {"name": "--database", "type": "file-path", "value": "669146667656a2d7c929a0a6/database.fasta"},
    {"name": "--decoy_prefix", "type": "string", "value": "DECOY_"},
    {"name": "--params_file", "type": "file-path", "value": "669146667656a2d7c929a0a6/params-file.ini"},
    {"name": "--sitelist_file", "type": "file-path", "value": "669146667656a2d7c929a0a6/sitelist_file.txt"},
    {"name": "--groupmaker_file", "type": "file-path", "value": "669146667656a2d7c929a0a6/groupmaker_file.txt"}
]
}'
```

Using RefMod as inputs
```
bash workflow/launch.sh http://localhost:8081 66914843ed0837f367f31de3 \
'{"inputs": [
    {"name": "--refmod_files", "type": "directory-path", "value": "66881f10e563107dfbbc5d96/refmod_files/*"},
    {"name": "--exp_table", "type": "file-path", "value": "66881f10e563107dfbbc5d96/exp_table.txt"},
    {"name": "--database", "type": "file-path", "value": "66881f10e563107dfbbc5d96/database.fasta"},
    {"name": "--decoy_prefix", "type": "string", "value": "DECOY_"},
    {"name": "--params_file", "type": "file-path", "value": "66881f10e563107dfbbc5d96/params-file.ini"},
    {"name": "--sitelist_file", "type": "file-path", "value": "66881f10e563107dfbbc5d96/sitelist_file.txt"},
    {"name": "--groupmaker_file", "type": "file-path", "value": "66881f10e563107dfbbc5d96/groupmaker_file.txt"}
]
}'
```

5. Get the log of a workflow instance on a nextflow server
```
bash workflow/log.sh http://localhost:8081 66914843ed0837f367f31de3
```

6. Get a workflow instance on a nextflow server
```
bash workflow/get.sh http://localhost:8081 66914843ed0837f367f31de3
```

7. Cancel a workflow instance on a nextflow server
```
bash workflow/cancel.sh http://localhost:8081 66914843ed0837f367f31de3
```


# Command lines for Workflow (root user???)

1. Delete a workflow instance on a nextflow server
```
bash workflow/delete.sh http://localhost:8081 66914843ed0837f367f31de3
```


# Command lines for outputs

1. Get a list of all outputs for a workflow instance and attempt on a nextflow server
```
bash output/get.sh http://localhost:8081 66914843ed0837f367f31de3 1
```

2. Retrieve all data (all files) for a workflow instance and attempt on a nextflow server
```
bash output/archive.sh http://localhost:8081 66914843ed0837f367f31de3 1
```

3. Download a single file for a workflow instance and attempt on a Nextflow server.
```
bash output/download_single.sh http://localhost:8081 66914843ed0837f367f31de3 1 modules/solver/10_group_maker/experiment_PDMTable_GM.txt
```

4. Download multiple files for a workflow instance and attempt on a Nextflow server.
```
bash output/download_multi.sh http://localhost:8081 66914843ed0837f367f31de3 1 \
'[
    "modules/solver/10_group_maker/experiment_PDMTable_GM.txt",
    "modules/solver/11_joiner/experiment_PDMTable_GM_J.txt"
]'
```

5. Delete the outputs for a workflow intance and attempt on a nextflow server
```
bash output/delete.sh http://localhost:8081 66914843ed0837f367f31de3 1
```



