___
## 1.5

### Date 📅 *2025_04*

### Changes in detail

+ An output directory named 'outspace' is used to store the workflow result files.
+ The archive is now a ZIP file instead of a TAR.GZ file.
+ Extend the user session duration.
+ Identify symbolic links that point to directories, and update the corresponding subdirectories and filenames.
+ Reduce the number of deleted files, ensuring the count does not drop below zero.
+ Move the Nextflow cache into the workflow directories.
+ Include attempt descriptions in the log report for easier tracking.
+ Apply the necessary changes to **resume execution**.
+ Cancel ongoing Nextflow executions.
+ Relocate the Nextflow and workflow log files.

___
## 1.4

### Date 📅 *2024_12*

### Changes in detail

+ Fixing a bug creating the global output.


___
## 1.3
```
DATE: 2024_11
```

### Highlights

+ Add *volumes* REST api.

### Changes in detail

+ Add *volumes* method to query the files from the shared volumes.

+ Add client to execute the *volumes* REST api.

+ Add the MongoDB port as constant


___
## 1.2
```
DATE: 2024_10
```

### Highlights

+ Changes for the dataset reports: remove files, add 'name' metadata, ...

+ Exception logs are printed by standard output.

### Changes in detail


___
## 1.1
```
DATE: 2024_08
```

### Highlights

+ Adding the authentication

+ Add the MongoDB in remote mode

### Changes in detail


___
## 1.0
```
DATE: 2024_07
```

### Highlights

+ Release the first beta version.

+ Nextflow-API is a web application and REST API for submitting and monitoring Nextflow pipelines on a variety of execution environments.

### Changes in detail



___
## 0.X
```
DATE: 2024_XX
```

### Highlights

+ Developing the beta version

