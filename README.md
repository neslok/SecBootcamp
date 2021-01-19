# SecBootcamp

This bootcamp provides users with an overview/walk-through of the basic security features of the Nutanix HCI Platform.

Things to note:

1. Some of these tasks are completed only once on a cluster, so it's reccomended to use single node clusters to provide each participant with thier own dedicated environment.

2. Stage your HPOC(s) with the Enterprise Private Cloud - this provides a functioning AD environment for the Flow VDI lab, as well as the WintoolsVM image which is utilzed in the labs.

3. There is a python script which will complete the final staging tasks - this bootcamp is not about deploying VMs, blueprints or applications, so this is completed prior to the participant accessing the environment.

4. VERY IMPORTANT - you will need to update the variables in the script for your environment before using it. These are:
  - admin credentials for your HPOC(s)
  - local path to the blueprint JSON files
These are located at the begining of the script, and are commented for ease of location.

5. 
