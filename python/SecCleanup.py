import requests
import json
from http.client import HTTPSConnection
from base64 import b64encode
import re
import time
import csv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# define path to local files (blueprints and cluster(s) details) - Update these for your local system accordingly.
##################################################################################################################
clusterdeets = '/Users/keith.olsen/Downloads/clusters.csv'   # CSV sheet with cluster IP, login, and password
BPpath = '/Users/keith.olsen/Downloads/' # Directory where BP json files are located
blueprints = ["Fiesta1", "Graylog1", "SecClients"]
##################################################################################################################

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
        print()
        print("Cleaning cluster: "+prisCentIP)
        print()
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

        # Find SecClients BP uuid and name
        for x in blueprints:
            for bp in BPlist['entities']:
                if (bp['status']['name']) == x:
                    BPUuid = (bp['status']['uuid'])
                    
                
            BPurl = baseurl + "/blueprints/" + BPUuid
            payload = {}
            response = requests.request("DELETE", BPurl, headers=headers, data=payload, verify=False).json()

            print(x + " blueprint DELETED")

            # DELETE Apps

            # Get app list

            APPpayload = {'kind': 'app'}
            json_APPpayload = json.dumps(APPpayload)

            APPlist = requests.request("POST", baseurl + "apps/list", headers=headers, data=json_APPpayload, verify=False).json()
            json_APPlist = json.dumps(APPlist)

            #print(APPlist)

            # DELETE APPS

            for app in APPlist['entities']:
                if (app['metadata']['name']) == x:
                    APPUuid = (app['metadata']['uuid'])

                APPurl = baseurl + "/apps/" + APPUuid
                payload = {}

                APRresponse = requests.request("DELETE", APPurl, headers=headers, data=payload, verify=False).json()
            print(x + " application deletion started")
            print()

