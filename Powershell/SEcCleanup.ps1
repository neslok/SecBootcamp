# Define variables for execution#
#################################

$clusterdeets = Import-Csv /Users/keith.olsen/Downloads/clusters.csv # csv file with cluster details (IP, userid, password)
$blueprints = @('Fiesta1','Graylog1','SecClients') # Identifies which blueprints will be deleted (names must match)


foreach ($c in $clusterdeets) {
  $prisCentIP = $c.IP
  $RESTAPIUser = $c.login
  $RESTAPIPassword = $c.password


$BaseURL = "https://" + $prisCentIP + ":9440/api/nutanix/v3/"
write-host ""
Write-host "Cleaning" $prisCentIP
write-host ""

$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("Content-Type", "application/json")
#$headers.Add("Authorization", "Basic YWRtaW46cGxvMDBvbHBlUiE=")
$headers.Add("Authorization", "Basic "+[System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($RESTAPIUser+":"+$RESTAPIPassword)))

# Retreive application_profile_reference.uuid from blueprint
$body = "{`"kind`": `"blueprint`"}"
$BPlist = Invoke-RestMethod -SkipCertificateCheck $BaseURL'blueprints/list' -Method 'POST' -Headers $headers -Body $body

$body = "{`"kind`": `"app`"}"
$APPlist = Invoke-RestMethod -SkipCertificateCheck $BaseURL'apps/list' -Method 'POST' -Headers $headers -Body $body


foreach ($x in $blueprints) {
  foreach ($bp in $BPlist.entities) {
    if ($bp.metadata.name -eq $x) {
      $BPuuid = $bp.metadata.uuid

      $BPurl = $BaseURL+'blueprints/'+$BPuuid

      $response = Invoke-RestMethod -SkipCertificateCheck $BPurl -Method 'DELETE' -Headers $headers -Body $body

      write-host "Blueprint"$bp.metadata.name"deleted"
    }
  }
  foreach ($app in $APPlist.entities) {
    if ($app.metadata.name -eq $x) {
      $APPuuid = $app.metadata.uuid

      $APPurl = $BaseURL+'apps/'+$APPuuid

      $response = Invoke-RestMethod -SkipCertificateCheck $APPurl -Method 'DELETE' -Headers $headers -Body $body

      write-host "App"$app.metadata.name"deletion executed"
      write-host ""
    }
  }
}
write-host "#############################"
}
