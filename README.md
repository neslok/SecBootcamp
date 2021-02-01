# SecBootcamp

This bootcamp provides users with an overview/walk-through of the basic security features of the Nutanix HCI Platform.

Things to note:

1. Some of these tasks are completed only once on a cluster, so it's reccomended to use single node clusters to provide each participant with thier own dedicated environment.

2. Stage your HPOC(s) with the Enterprise Private Cloud - this provides a functioning AD environment for the Flow VDI lab, as well as the WintoolsVM image which is utilzed in the labs.

3. There are scripts (python and powershell) which will complete the final staging tasks - this bootcamp is not about deploying VMs, blueprints or applications, so this is completed prior to the participant accessing the environment.

4. VERY IMPORTANT - you will need to update the variables in the script for your environment before using it. These are:
  - local path to the blueprint JSON files
  - the names for the blueprint files
These are located at the begining of the script, and are commented for ease of location.

5. If you have several clusters to prepare, use SecBTCMPStage_auto.py. It will read in PC IP, admin login and password from a csv file - must be ipaddress,loginID,password , with a new row for each cluster -  (example in repo)  - a single script execution can stage mutiple environments without human intervention.
NOTE - if saving from Excel, make sure the file format is Comma Seperated Values(.csv) - NOT CSV UTF-8 (Comma delimited)(.csv) - it sticks some junk at the beginning of row 1, which causes the script to ignore it.
