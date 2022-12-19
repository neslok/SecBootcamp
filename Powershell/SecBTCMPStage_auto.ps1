
# ########## Define variables for execution ############
# Update with information specific to your environment #
########################################################

$clusterdeets = Import-Csv /Users/keith.olsen/Documents/GitHub/SecBootcamp/clusters.csv # csv file with cluster details (IP, userid, password)
$blueprints = @('Fiesta1','Graylog1','SecClients') # Identifies which blueprint files will be used (names must match)
$BPpath = '/Users/keith.olsen/Documents/GitHub/SecBootcamp/' # Path to directory containing blueprint files

# Establishes variables for cluster details

foreach ($c in $clusterdeets) {
  $prisCentIP = $c.IP
  $RESTAPIUser = $c.login
  $RESTAPIPassword = $c.password

  # Creates variable with base API BaseURL

  $BaseURL = "https://" + $prisCentIP + ":9440/api/nutanix/v3/"

  # Creates header file for API calls

  $headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
  $headers.Add("Content-Type", "application/json")
  $headers.Add("Authorization", "Basic "+[System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($RESTAPIUser+":"+$RESTAPIPassword)))

  # Get details (uuids) for project on cluster - needed to update blueprints

  $body = "{`"kind`": `"project`"}"
  $PJlist = Invoke-RestMethod -SkipCertificateCheck $BaseURL'projects/list' -Method 'POST' -Headers $headers -Body $body

  foreach ($p in $PJlist.entities) {
    if ($p.spec.name -eq "KOtest") { #Specifies which project the blueprints/applications will be allocated to
      #write-host $p.spec.name
      #write-host $p.metadata.uuid
      #write-host "Subnet UUID: "$p.spec.resources[0].subnet_reference_list.uuid
      $PJuuid = $p.metadata.uuid
      $SNuuid = $p.spec.resources[0].subnet_reference_list.uuid
    }
  }

  # Get uuid for WinToolsVM on cluster - needed to update SecClients blueprint

  $body = "{`"kind`": `"image`"}"
  $IMGlist = Invoke-RestMethod -SkipCertificateCheck $BaseURL'images/list' -Method 'POST' -Headers $headers -Body $body

  foreach ($i in $IMGlist.entities) {
    if ($i.spec.name -eq "WinToolsVM-Q1CY21.qcow2") {
      #write-host $i.spec.name
      #write-host "Image UUID: "$i.metadata.uuid
      $IMGuuid = $i.metadata.uuid
    }
  }
  write-host ""
  write-host "Provisioning cluster: "$prisCentIP
  write-host ""
  Write-host "Updating/uploading blueprints to Prism Central"

  # Get relevant UUIDs from local BP file (this will be needed to substitution for uuids from cluster)
  foreach ($x in $blueprints) {
    $xBP = Get-Content ($BPpath+$x+'.json') -Raw | ConvertFrom-json -depth 20 #| New-Variable -name "$($x)BP" #-Value  Get-Content ($BPpath+$x+'.json') -Raw | ConvertFrom-json -depth 20

    #$xBP.metadata.name
    $xBP_SNRuuid = $xBP.spec.resources.substrate_definition_list[0].create_spec.resources.nic_list[0].subnet_reference.uuid
    $xBP_IMGRuuid = $xBP.spec.resources.substrate_definition_list[0].create_spec.resources.disk_list[0].data_source_reference.uuid
    #write-host "BP UUIDs:"
    #$xBP_SNRuuid
    #$xBP_IMGRuuid

    # Converts data to json format, and replaces the subnet_reference uuid

    $xBP_json = $xBP | ConvertTo-json -depth 15
    write-host "Updating "$xBP.metadata.name

    $xBP_json = $xBP_json -Replace $xBP_SNRuuid, $SNuuid

    # Updates WintoolsVM IMG uuid in SecClients BP

    if ($xBP.spec.resources.substrate_definition_list[0].create_spec.resources.disk_list[0].data_source_reference.name -eq "WinToolsVM.qcow2"){
      $xBP_json = $xBP_json -Replace $xBP_IMGRuuid, $IMGuuid
    }

    # Converts updated json file back to poweshell objects

    $xBPu = $xBP_json | ConvertFrom-json -depth 15
    #write-host "updated BP UUIDs:"
    #$xBPu.spec.resources.substrate_definition_list[0].create_spec.resources.nic_list[0].subnet_reference.uuid
    #$xBPu.spec.resources.substrate_definition_list[0].create_spec.resources.disk_list[0].data_source_reference.uuid

    # Creates new file name (appends with _U) for updated blueprint file and saves to localhost
    $xBPu_file = ($BPpath+$x+'_U.json')
    #$xBPu_file
    $xBP_json | Out-File $xBPu_file

    # Upload modified blueprint files to PC

    $BPput_url = $BaseURL+'blueprints/import_file'


    $multipartContent = [System.Net.Http.MultipartFormDataContent]::new()
    $stringHeader = [System.Net.Http.Headers.ContentDispositionHeaderValue]::new("form-data")
    $stringHeader.Name = "project_uuid"
    $stringContent = [System.Net.Http.StringContent]::new($PJuuid)
    $stringContent.Headers.ContentDisposition = $stringHeader
    $multipartContent.Add($stringContent)

    $multipartFile = ($BPpath+$x+'_U.json')
    $FileStream = [System.IO.FileStream]::new($multipartFile, [System.IO.FileMode]::Open)
    $fileHeader = [System.Net.Http.Headers.ContentDispositionHeaderValue]::new("form-data")
    $fileHeader.Name = "file"
    $fileHeader.FileName = ($x+'_U.json')
    $fileContent = [System.Net.Http.StreamContent]::new($FileStream)
    $fileContent.Headers.ContentDisposition = $fileHeader
    $multipartContent.Add($fileContent)

    $stringHeader = [System.Net.Http.Headers.ContentDispositionHeaderValue]::new("form-data")
    $stringHeader.Name = "name"
    $stringContent = [System.Net.Http.StringContent]::new($xBP.metadata.name)
    $stringContent.Headers.ContentDisposition = $stringHeader
    $multipartContent.Add($stringContent)

    $stringHeader = [System.Net.Http.Headers.ContentDispositionHeaderValue]::new("form-data")
    $stringHeader.Name = "passphrase"
    $stringContent = [System.Net.Http.StringContent]::new("nx2Tech123!")
    $stringContent.Headers.ContentDisposition = $stringHeader
    $multipartContent.Add($stringContent)

    $body = $multipartContent

    $response = Invoke-RestMethod -SkipCertificateCheck $BPput_url -Method 'POST' -Headers $headers -Body $body

    write-host "Uploading "$xBP.metadata.name
    write-host ""
  }

  # Launch blueprints
    Write-host ""
    Write-host "Launching blueprints to applications:"
    Write-host ""
  # Retreive application_profile_reference.uuid from blueprint
  $body = "{`"kind`": `"blueprint`"}"
  $BPlist = Invoke-RestMethod -SkipCertificateCheck $BaseURL'blueprints/list' -Method 'POST' -Headers $headers -Body $body

  foreach ($bp in $BPlist.entities) {
    $BPuuid = $bp.metadata.uuid
    $BPname = $bp.metadata.name

    $APRurl = $BaseURL+'blueprints/'+$BPuuid+'/runtime_editables'

    $BPrunedit = Invoke-RestMethod -SkipCertificateCheck $APRurl -Method 'GET' -Headers $headers

    $APRuuid = $BPrunedit.resources[0].app_profile_reference.uuid

    #$body = "{`n  `"spec`": {`n    `"app_description`": `"apitest`",`n    `"app_name`": "+'"' +$xBP.metadata.name +'"'+" `n  }`n}"
    $body = "{`n  `"spec`": {`n    `"app_profile_reference`": {`n      `"kind`": `"app_profile`",`n      `"name`": `"Default`",`n  `"uuid`": "+'"' +$APRuuid +'"'+" `n},`n    `"app_description`": `"apitest`",`n    `"app_name`": " +'"' + $BPname +'"'+" `n}`n}"

    $BPlaunch = $BaseURL+'blueprints/'+$BPuuid+'/simple_launch'
    $response = Invoke-RestMethod -SkipCertificateCheck $BPlaunch -Method 'POST' -Headers $headers -Body $body
    write-host "Launching " $BPname
  }
    write-host "****************************"
}
