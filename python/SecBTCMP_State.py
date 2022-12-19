from requests import request
import json
from http.client import HTTPSConnection
from base64 import b64encode
import re
import time
import csv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#
# Defines Prism Central variables - update these with your HPOC details (uncomment for single cluster config)

# pcUserID = 'admin'
# pcPassword = 'nx2Tech123!'
# #prisCentIP = '10.38.3.73'
# prisCentIP = input("Enter Prism Central IP: ")

clusterdeets = '/Users/keith.olsen/Documents/GitHub/SecBootcamp/clusters.csv' # Path to csv file with cluster info

# Reads in cluster details from csv file

with open(clusterdeets) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    next(readCSV)
    for row in readCSV:
        prisCentIP = (row[0])
        #print(prisCentIP)
        pcUserID = (row[1])
        #print(pcUserID)
        pcPassword = (row[2])
        #print(pcPassword)



        # This sets up the https connection

        c = HTTPSConnection(prisCentIP)


        # # Creates encoded Authorization value

        userpass = pcUserID + ":" + pcPassword
        buserAndPass = b64encode(userpass.encode("ascii"))
        authKey = (buserAndPass.decode("ascii"))

        headers = {
            'Content-Type': "application/json",
            'Authorization': "Basic " + authKey,
            'cache-control': "no-cache"
        }

        # # Defines base url for API calls

        baseurl = "https://" + prisCentIP + ":9440/api/nutanix/v3/"

        # Get APP list

        APPpayload = {'kind': 'app'}

        json_APPpayload = json.dumps(APPpayload)

        APPlist = request("POST", baseurl + "apps/list", headers=headers, data=json_APPpayload, verify=False).json()
        json_APPlist = json.dumps(APPlist)

        print(json_APPlist)

        #print(APPlist)
        print()
        print(prisCentIP)
        for each in APPlist['entities']:
            APPUuid = (each['status']['uuid'])
            APPName = (each['status']['name'])
            APPStat = (each['status']['state'])
            print(APPName + " " + APPStat)


