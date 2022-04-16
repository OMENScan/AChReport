$VeloDir = Read-Host -Prompt 'Which Directory should we Convert: '
Write-Host "Converting AutoRuns..."
New-Item -ItemType Directory -Force -Path $Velodir\Arn | out-null
Get-Content $VeloDir\Windows.Sysinternals.Autoruns.json | ConvertFrom-Json | Export-Csv $VeloDir\Arn\Autorun.dat -NoTypeInformation
Write-Host "Converting Chrome History..."
New-Item -ItemType Directory -Force -Path $Velodir\Brw | out-null
Get-Content $VeloDir\Windows.Applications.Chrome.History.json | ConvertFrom-Json | Export-Csv $VeloDir\Brw\BrowseHist.csv -NoTypeInformation
Write-Host "Converting Network Connections..."
New-Item -ItemType Directory -Force -Path $Velodir\Sys | out-null
Get-Content $VeloDir\Windows.Network.NetstatEnriched\Netstat.json | ConvertFrom-Json | Export-Csv $VeloDir\Sys\Cports.csv -NoTypeInformation
Write-Host "Converting DNS Cache..."
Get-Content $VeloDir\Windows.System.DNSCache.json | ConvertFrom-Json | Export-Csv $VeloDir\Sys\DNSCache.csv -NoTypeInformation
Write-Host "Converting Logon Data..."
Get-Content $VeloDir\Custom.Windows.Sysinternals.PSLoggedOn.json | ConvertFrom-Json | Export-Csv $VeloDir\Sys\Logon.dat -NoTypeInformation
Write-Host "Converting PSInfo Data..."
Get-Content $VeloDir\Custom.Windows.Sysinternals.PSInfo.json | ConvertFrom-Json | Export-Csv $VeloDir\Info.dat -NoTypeInformation
