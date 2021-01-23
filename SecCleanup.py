import requests
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

clusterdeets = '/Users/keith.olsen/Downloads/clusters.csv'

# pcUserID = 'admin'
# pcPassword = 'nx2Tech123!'
# #prisCentIP = '10.38.3.73'
# prisCentIP = input("Enter Prism Central IP: ")

# Reads in cluster details from csv file

with open(clusterdeets) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
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



        # #Get blueprint info

        BPpayload = {'kind': 'blueprint'}

        json_BPpayload = json.dumps(BPpayload)

        BPlist = requests.request("POST", baseurl + "blueprints/list", headers=headers, data=json_BPpayload, verify=False).json()
        
        print()
        print(prisCentIP)

        # Find SecClients BP uuid and name
        for each in BPlist['entities']:
            if (each['status']['name']) == "SecClients":
                SecCliBPUuid = (each['status']['uuid'])
                SecCliBPName = (each['status']['name'])

        #DELETE SecClients blueprint

        BPurl = baseurl + "/blueprints/" + SecCliBPUuid
        payload = {}

        SecCliBPresponse = requests.request("DELETE", BPurl, headers=headers, data=payload, verify=False).json()

        print("SecClients blueprint DELETED")

        #DELETE FIESTA BLUEPRINT

        # Extracts blueprint name and uuid from BPlist for specified blueprint in "if" statement.

        for each in BPlist['entities']:
            if (each['status']['name']) == "Fiesta1":  # Edit blueprint name as required.
                Fiesta_BPUuid = (each['status']['uuid'])
                Fiesta_BPName = (each['status']['name'])

        BPurl = baseurl + "/blueprints/" + Fiesta_BPUuid

        payload = {}

        #print(BPurl)

        BPresponse = requests.request("DELETE", BPurl, headers=headers, data=payload, verify=False).json()

        print("Fiesta blueprint DELETED")

        #DELETE GRAYLOG BLUEPRINT

        # Extracts blueprint name and uuid from BPlist for specified blueprint in "if" statement.

        for each in BPlist['entities']:
            if (each['status']['name']) == "Graylog":  # Edit blueprint name as required.
                GL_BPUuid = (each['status']['uuid'])
                GL_BPName = (each['status']['name'])

        BPurl = baseurl + "/blueprints/" + GL_BPUuid

        payload = {}

        #print(BPurl)

        BPresponse = requests.request("DELETE", BPurl, headers=headers, data=payload, verify=False).json()

        print("Graylog blueprint DELETED")

        # DELETE Apps

        # Get app list

        APPpayload = {'kind': 'app'}

        json_APPpayload = json.dumps(APPpayload)

        APPlist = requests.request("POST", baseurl + "apps/list", headers=headers, data=json_APPpayload, verify=False).json()
        json_APPlist = json.dumps(APPlist)

        #print(APPlist)

        # DELETE APPS
        print()
        for each in APPlist['entities']:
            APPUuid = (each['status']['uuid'])
            APPName = (each['status']['name'])

            APPurl = baseurl + "/apps/" + APPUuid

            payload = {}

            APRresponse = requests.request("DELETE", APPurl, headers=headers, data=payload, verify=False).json()
            print(APPName + " application deletion started")
