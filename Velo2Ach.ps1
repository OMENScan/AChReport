#################################################################################
# This script forms the bridge between AChoir(X) and Velociraptor               #
#  AChoir(X) uses CSV files, and Velociraptor uses JSON. This script converts   #
#  and reformats Velociraptor JSON files into CSV Files so that TriageReport    #
#  can read them.  For this to work, please ensure that the JSON files are      #
#  reformatted into the CSV columns that TriageReport expects.  This can be     #
#  done using the following general syntax:                                     #
#                                                                               #
#   Get-Content <Input JSON File Name> | ConvertFrom-Json |                     #
#   Select-Object <colname>, <colname>, <etc..> | Export-Csv <output CSV File>  #
#   -NoTypeInformation                                                          #
#                                                                               #
#################################################################################
Write-Host "[+] This Powershell script Converts the Velociraptor JSON Files to AChoirX CSV Format."
#$VeloDir = Read-Host -Prompt 'Which Directory should we Convert: '
$VeloDir = $args[0]
Write-Host "[+] Converting AutoRuns..."
New-Item -ItemType Directory -Force -Path $Velodir\Arn | out-null
Get-Content $VeloDir\Windows.Sysinternals.Autoruns.json | ConvertFrom-Json | Export-Csv $VeloDir\Arn\Autorun.dat -NoTypeInformation
Write-Host "[+] Converting Chrome History..."
New-Item -ItemType Directory -Force -Path $Velodir\Brw | out-null
Get-Content $VeloDir\Windows.Applications.Chrome.History.json | ConvertFrom-Json | Select-Object visited_url, title, last_visit_time, visit_count, Mtime, typed_count, FullPath, User | Export-Csv $VeloDir\Brw\BrowseHist.csv -NoTypeInformation
Write-Host "[+] Converting Network Connections..."
New-Item -ItemType Directory -Force -Path $Velodir\Sys | out-null
Get-Content $VeloDir\Windows.Network.NetstatEnriched\Netstat.json | ConvertFrom-Json | Select-Object Name, Pid, Type, Laddr.Port, Family, Laddr.IP, Raddr.Port, Ppid, Raddr.IP, Username, Status, CommandLine | Export-Csv $VeloDir\Sys\Cports.csv -NoTypeInformation
Write-Host "[+] Converting DNS Cache..."
Get-Content $VeloDir\Windows.System.DNSCache.json | ConvertFrom-Json | Export-Csv $VeloDir\Sys\DNSCache.csv -NoTypeInformation
Write-Host "[+] Converting Logon Data..."
Get-Content $VeloDir\Custom.Windows.Sysinternals.PSLoggedOn.json | ConvertFrom-Json | Export-Csv $VeloDir\Sys\Logon.dat -NoTypeInformation
Write-Host "[+] Converting PSInfo Data..."
Get-Content $VeloDir\Custom.Windows.Sysinternals.PSInfo.json | ConvertFrom-Json | Export-Csv $VeloDir\Info.dat -NoTypeInformation
Write-Host "[+] Conversion Completed...  Exiting..."
