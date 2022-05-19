# Huawei RAN OSS U2000
Script for auto upload and execute MML command to U2000, and download results from OSS HUAWEI U2000 to local storage.

1. Need create MML commands file for example "file1.txt".
2. Call thread_function
```python
def thread_function(args):
    api.U2020Api(ftp_auth=args[0], nbi_auth=args[1], oss_name=args[2], oss_ip=args[3], ftp_port=args[4],
                 nbi_port=args[5], dict_with_files=args[6]).auto()
```
with credentials and connection settings: 
```python
    ftp_auth  # tuple with first login and second password for ftp
    nbi_auth  # tuple with first login and second password for nbi
    oss_name  # str name
    oss_ip  # str ip
    ftp_port  # int ftp port
    nbi_port  # int nbi port
    dict_with_files  # dict of mml files with key - file_name and value - file_path
```

Can work with thread pool:
```python
thread_pool()
```

Method for auto work in api.py:
```python
def auto(self, nbi_connect_timeout=60, nbi_command_timeout=3600):
    self.upload_to_oss() # Upload MML command on FTP U2000.
    self.execute_on_oss(connect_timeout=nbi_connect_timeout, command_timeout=nbi_command_timeout) # Execute MML commands on NBI U2000.
    self.download_from_oss() # Download MML commands execution results on FTP from U2000.
```
