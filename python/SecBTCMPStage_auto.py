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
clusterdeets = '/Users/keith.olsen/Documents/GitHub/SecBootcamp/clusters.csv'   # CSV sheet with cluster IP, login, and password
BPpath = '/Users/keith.olsen/Documents/GitHub/SecBootcamp/' # Directory where BP json files are located
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
        print("Provisioning cluster: "+prisCentIP)
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

        # Get project details (project uuid and subnet uuid)

        PJpayload = {'kind': 'project'}
        json_PJpayload = json.dumps(PJpayload)

        json_PJlist = requests.request("POST", baseurl + "projects/list", headers=headers, data=json_PJpayload, verify=False).json()

        PJlist = json.dumps(json_PJlist)

        for each in json_PJlist['entities']:
            if (each['spec']['name']) == "BootcampInfra":
                PJUuid = (each['metadata']['uuid'])
                PJName = (each['spec']['name'])
                SNUuid = (each['spec']['resources']['subnet_reference_list'][0]['uuid'])
                SNName = (each['spec']['resources']['subnet_reference_list'][0]['name'])

        # Get image uuid from PC for SecClients BP

        IMGpayload = {'kind': 'image'}
        json_IMGpayload = json.dumps(IMGpayload)

        IMGlist = requests.request("POST", baseurl + "images/list", headers=headers, data=json_IMGpayload, verify=False).json()

        json_IMGlist = json.dumps(IMGlist)

        for each in IMGlist['entities']:
            if (each['status']['name']) == "WinToolsVM-Q1CY21.qcow2":
                IMGUuid = (each['metadata']['uuid'])

        # Replaces UUIDs in supplied blueprints with UUIDs from cluster

        for x in blueprints:
            FilePath = (BPpath + x + ".json")
            with open(FilePath) as json_file:
                blueprint = json.load(json_file)
                blueprintU = json.dumps(blueprint)
            for eachvm in blueprint['spec']['resources']['substrate_definition_list']:
                for eachnic in eachvm['create_spec']['resources']['nic_list']:
                    #print(eachvm['name'] + " " + eachnic['subnet_reference']['uuid'])
                    SNRuuid = eachnic['subnet_reference']['uuid']
                if eachvm['create_spec']['resources']['disk_list'][0]['data_source_reference']['name'] == "WinToolsVM.qcow2":
                    IMGRuuid = eachvm['create_spec']['resources']['disk_list'][0]['data_source_reference']['uuid']
                    #print(IMGRuuid)
            # Replace UUIDs
                    blueprintU = re.sub(IMGRuuid, IMGUuid, blueprintU)  # Only SecClients requires image update
            blueprintU = re.sub(SNRuuid, SNUuid, blueprintU)  # All VMs get network update

            # Writes updated blueprint back to same directory, appending with "_U" at end of file
            print("Updating "+ x + ".json")
            with open(BPpath + x + "_U.json", 'w') as outfile:
                outfile.write(blueprintU)

            # Upload the BP JSON files up to Prism Central

            BPput_url = baseurl + "blueprints/import_file"
            BPUP_headers = {'Authorization': "Basic " + authKey}

            payload = {'project_uuid': PJUuid, 'name': x, 'passphrase': 'nx2Tech123!'}

            files = [
                ('file',(x + '_U.json',open(BPpath + x + "_U.json",'rb'),'application/json'))
            ]
            print("Uploading " + x + "_U.json")
            print()
            response = requests.request("POST", BPput_url, headers=BPUP_headers, data=payload, files=files, verify=False)

            # print(response)

        # Launch the blueprints

        # Get app_profile_reference uuid
        print("Launching blueprints to applications:")
        BPpayload = {"kind": "blueprint"}
        BPpayload = json.dumps(BPpayload)

        BPlist = requests.request("POST", baseurl + "blueprints/list", headers=headers, data=BPpayload, verify=False).json()

        for each in BPlist['entities']:
            BPUuid = (each['status']['uuid'])
            BPName = (each['status']['name'])

            BPurl = baseurl + "/blueprints/" + BPUuid + "/runtime_editables"

            payload={}

            APRresponse = requests.request("GET", BPurl, headers=headers, data=payload, verify=False).json()
            APRuuid = APRresponse['resources'][0]['app_profile_reference']['uuid']
            #print(APRuuid)

            launch_payload = {
                'spec': {
                    'app_name': BPName,
                    'app_description': BPName,
                    'app_profile_reference': {
                    'kind': 'app_profile',
                    'name': 'Default',
                    'uuid': APRuuid
                    }
                }
            }
            json_launch = json.dumps(launch_payload)
            #print(json_launch)
            BPlaunch = requests.request("POST", baseurl + "blueprints/" + BPUuid + "/simple_launch", headers=headers, data=json_launch, verify=False)
            #print(BPlaunch.text)
            print(BPName + " launched")
        print("########################################################")