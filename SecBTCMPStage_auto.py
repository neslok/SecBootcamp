import requests
import json
from http.client import HTTPSConnection
from base64 import b64encode
import re
import time
import csv



#define path to local files (blueprints and cluster(s) details) - Update these for your local system accordingly.

clusterdeets = '/Users/keith.olsen/Downloads/clusters.csv'
FiestaPath = '/Users/keith.olsen/Downloads/Fiesta_Sec.json'
SecClientsPath = '/Users/keith.olsen/Downloads/SecClients.json'
GraylogPath = '/Users/keith.olsen/Downloads/Graylog1.json'

# Defines Prism Central variables - update these with your HPOC details (uncomment for single cluster config)

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

        # Get relevant UUIDs from local BP file (this will be needed to substitution for uuids from cluster

        with open(SecClientsPath) as json_file:
            blueprint = json.load(json_file)
            for eachvm in blueprint['spec']['resources']['substrate_definition_list']:
                for eachnic in eachvm['create_spec']['resources']['nic_list']:
                    #print(eachvm['name'] + " " + eachnic['subnet_reference']['uuid'])
                    SecCliSNRuuid = eachnic['subnet_reference']['uuid']
                for eachimg in eachvm['create_spec']['resources']['disk_list']:
                    SecCliIMGRuuid = eachimg['data_source_reference']['uuid']
                    #print(eachimg['data_source_reference']['uuid'])

        with open(FiestaPath) as json_file:
            blueprint = json.load(json_file)
            for eachvm in blueprint['spec']['resources']['substrate_definition_list']:
                for eachnic in eachvm['create_spec']['resources']['nic_list']:
                    #print(eachvm['name'] + " " + eachnic['subnet_reference']['uuid'])
                    Fiesta_SNRuuid = eachnic['subnet_reference']['uuid']

        with open(GraylogPath) as json_file:
            blueprint = json.load(json_file)
            for eachvm in blueprint['spec']['resources']['substrate_definition_list']:
                for eachnic in eachvm['create_spec']['resources']['nic_list']:
                    #print(eachvm['name'] + " " + eachnic['subnet_reference']['uuid'])
                    GL_SNRuuid = eachnic['subnet_reference']['uuid']

        print("Provisioning: " + prisCentIP)

        # Get project details (project uuid and subnet uuid)

        PJpayload = {'kind': 'project'}
        json_PJpayload = json.dumps(PJpayload)

        json_PJlist = requests.request("POST", baseurl + "projects/list", headers=headers, data=json_PJpayload,verify=False).json()

        PJlist = json.dumps(json_PJlist)

        for each in json_PJlist['entities']:
            if (each['spec']['name']) == "BootcampInfra":
                PJUuid = (each['metadata']['uuid'])
                PJName = (each['spec']['name'])
                SNUuid = (each['spec']['resources']['subnet_reference_list'][0]['uuid'])
                SNName = (each['spec']['resources']['subnet_reference_list'][0]['name'])
        print("Cluster info:")
        print("Project = " + PJName + ", " + PJUuid)
        print("Subnet = " + SNName + ", " + SNUuid)




        # Put the BP file up to Prism Central

        #Specify URL to upload to

        BPput_url = baseurl + "blueprints/import_file"

        # Put Fiesta
        payload = {'project_uuid': PJUuid, 'name': 'Fiesta1', 'passphrase': 'nx2Tech123!'}

        files = [
            ('file', ('Fiesta-Multi_KOv2.json', open(FiestaPath, 'rb'), 'application/json'))
        ]
        BPUP_headers = {'Authorization': "Basic " + authKey}

        response = requests.request("POST", BPput_url, headers=BPUP_headers, data=payload, files=files, verify=False)

        print("Fiesta uploaded")

        # Put SecClients

        payload2 = {'project_uuid': PJUuid, 'name': 'SecClients', 'passphrase': 'nx2Tech123!'}

        files2 = [
            ('file', ('SecClient.json', open(SecClientsPath, 'rb'), 'application/json'))
        ]
        BPUP_headers = {'Authorization': "Basic " + authKey}

        response2 = requests.request("POST", BPput_url, headers=BPUP_headers, data=payload2, files=files2, verify=False)

        print("SecClients uploaded")

        #print(response2.text)

        # Put Graylog

        GL_payload = {'project_uuid': PJUuid, 'name': 'Graylog', 'passphrase': 'nx2Tech123!'}

        files3 = [
            ('file', ('Graylog1.json', open(GraylogPath, 'rb'), 'application/json'))
        ]
        BPUP_headers = {'Authorization': "Basic " + authKey}

        response3 = requests.request("POST", BPput_url, headers=BPUP_headers, data=GL_payload, files=files3, verify=False)

        print("Graylog uploaded")

        #print(response3.text)

        #wait 5 sec after upload

        time.sleep(5)

        #UPDATE SECCLIENTS BLURPRINT

        #Get image uuid from PC for SecClients BP

        IMGpayload = {'kind': 'image'}
        json_IMGpayload = json.dumps(IMGpayload)

        IMGlist = requests.request("POST", baseurl + "images/list", headers=headers, data=json_IMGpayload, verify=False).json()

        json_IMGlist = json.dumps(IMGlist)

        for each in IMGlist['entities']:
            if (each['status']['name']) == "WinToolsVM.qcow2":
                IMGUuid = (each['metadata']['uuid'])
                IMGName = (each['status']['name'])

        print("Image = " + IMGName + ", " + IMGUuid)
        #print(json_IMGlist)

        #Get blueprint info for SecClients (uuid)

        BPpayload = {'kind': 'blueprint'}

        json_BPpayload = json.dumps(BPpayload)

        BPlist = requests.request("POST", baseurl + "blueprints/list", headers=headers, data=json_BPpayload, verify=False).json()

        for each in BPlist['entities']:
            if (each['status']['name']) == "SecClients":
                SecCliBPUuid = (each['status']['uuid'])
                SecCliBPName = (each['status']['name'])

        print("Blueprint = " + SecCliBPName + ", " + SecCliBPUuid)

        #Get SecClients spec and metadata from PC

        BPurl = baseurl + "/blueprints/" + SecCliBPUuid
        payload = {}

        #print(BPurl)

        SecCliBPresponse = requests.request("GET", BPurl, headers=headers, data=payload, verify=False).json()

        #print(BPresponse)

        SecClibp_spec = json.dumps(SecCliBPresponse['spec'])
        SecClibp_meta = json.dumps(SecCliBPresponse['metadata'])

        # print(bp_meta)
        #print(SecClibp_spec)

        #Substitute image and subnet uuids from blueprint with correct ones from PC
        #print(SecCliIMGRuuid, SecCliSNRuuid)
        #print(IMGUuid, SNUuid)

        SecClibp_spec2 = re.sub(SecCliIMGRuuid, IMGUuid, SecClibp_spec)
        SecClibp_SNuuid_update = re.sub(SecCliSNRuuid, SNUuid, SecClibp_spec2)

        #Update SecClients blueprint spec with version with new uuids

        SecClibp_spec_update = '{ "spec": ' + SecClibp_SNuuid_update + ', "api_version": "3.0", "metadata": ' + SecClibp_meta + '}'
        #print(SecClibp_spec_update)

        SecCliBP_updateRsp = requests.request("PUT", BPurl, headers=headers, data=SecClibp_spec_update, verify=False).json()

        print("SecClients updated")

        #UPDATE FIESTA BLUEPRINT

        # Extracts blueprint name and uuid from BPlist for specified blueprint in "if" statement.

        for each in BPlist['entities']:
            if (each['status']['name']) == "Fiesta1":  # Edit blueprint name as required.
                Fiesta_BPUuid = (each['status']['uuid'])
                Fiesta_BPName = (each['status']['name'])

        print("Blueprint = " + Fiesta_BPName + ", " + Fiesta_BPUuid)

        # Retrieves the details (spec) for the
        BPurl = baseurl + "/blueprints/" + Fiesta_BPUuid
        payload={}

        #print(BPurl)

        BPresponse = requests.request("GET", BPurl, headers=headers, data=payload, verify=False).json()

        #print(BPresponse)

        Fiesta_bp_spec = json.dumps(BPresponse['spec'])
        Fiesta_bp_meta = json.dumps(BPresponse['metadata'])

        # print(bp_meta)
        #print(bp_spec)

        Fiesta_bp_SNuuid_update = re.sub(Fiesta_SNRuuid, SNUuid, Fiesta_bp_spec)
        Fiesta_bp_spec_update = '{ "spec": ' + Fiesta_bp_SNuuid_update + ', "api_version": "3.0", "metadata": ' + Fiesta_bp_meta + '}'
        #print(bp_spec_update)

        BP_updateRsp = requests.request("PUT", BPurl, headers=headers, data=Fiesta_bp_spec_update, verify=False).json()

        print("Fiesta updated")

        #UPDATE GRAYLOG BLUEPRINT

        # Extracts blueprint name and uuid from BPlist for specified blueprint in "if" statement.

        for each in BPlist['entities']:
            if (each['status']['name']) == "Graylog":  # Edit blueprint name as required.
                GL_BPUuid = (each['status']['uuid'])
                GL_BPName = (each['status']['name'])

        print("Blueprint = " + GL_BPName + ", " + GL_BPUuid)

        # Retrieves the details (spec) for the
        BPurl = baseurl + "/blueprints/" + GL_BPUuid
        payload={}

        #print(BPurl)

        BPresponse = requests.request("GET", BPurl, headers=headers, data=payload, verify=False).json()

        #print(BPresponse)

        GL_bp_spec = json.dumps(BPresponse['spec'])
        GL_bp_meta = json.dumps(BPresponse['metadata'])

        # print(bp_meta)
        #print(bp_spec)

        GL_bp_SNuuid_update = re.sub(GL_SNRuuid, SNUuid, GL_bp_spec)
        GL_bp_spec_update = '{ "spec": ' + GL_bp_SNuuid_update + ', "api_version": "3.0", "metadata": ' + GL_bp_meta + '}'
        #print(bp_spec_update)

        BP_updateRsp = requests.request("PUT", BPurl, headers=headers, data=GL_bp_spec_update, verify=False).json()

        print("Graylog updated")



        #Launch the blueprints

        #Get app_profile_reference uuid

        BPpayload = {'kind': 'blueprint'}

        json_BPpayload = json.dumps(BPpayload)

        BPlist = requests.request("POST", baseurl + "blueprints/list", headers=headers, data=json_BPpayload, verify=False).json()

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
            print("Launch of " + BPName + " executed")