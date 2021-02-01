
# ########## Define variables for execution ############
# Update with information specific to your environment #
########################################################

$clusterdeets = Import-Csv /Users/keith.olsen/Downloads/clusters.csv # csv file with cluster details (IP, userid, password)
$blueprints = @('Fiesta1','Graylog1','SecClients') # Identifies which blueprint files will be used (names must match)
$BPpath = '/Users/keith.olsen/Downloads/' # Path to directory containing blueprint files

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

  write-host ""
  write-host "App status on cluster:"$prisCentIP
  write-host ""

  $body = "{`"kind`": `"app`"}"
  $APPlist = Invoke-RestMethod -SkipCertificateCheck $BaseURL'apps/list' -Method 'POST' -Headers $headers -Body $body

  foreach ($app in $APPlist.entities) {
      write-host $app.status.name $app.status.state

    }
    Write-host "###############################"
  }
