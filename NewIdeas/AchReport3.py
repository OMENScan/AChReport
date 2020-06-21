#!/usr/bin/env python
####################################################################### 
# Version: v0.88 (Python 3.x)                                         #
# Author.: David Porco                                                #
# Release: 11/16/2018                                                 #
#                                                                     #
#   Read the artifacts output by AChoir and create a report           #
#                                                                     #
#   v0.81 - Copy RegRipper Plugins to subdirectory if not there       #
#   v0.82 - Check Dependencies: Regripper Plugins and LogParser       #
#   v0.83 - Parse Recycle Bin entries using Eric Zimmerman's RBCmd    #
#   v0.84 - Add Color Using Windows ctypes (SetConsoleTextAttribute)  #
#           Note: Console Color Routine taken from:                   #
#           https://github.com/ActiveState/code/blob/master/recipes/  #
#           Python/496901_Change_Windows_Console_Character_Attribute/ #
#           recipe-496901.py                                          #
#            Note: Licence for this code is included in file:         #
#                  ActiveState-LICENSE                                #
#   v0.85 - Recognize Root Dir of AChoir.  Replace Static Calls to    #
#           The C:\AChoir Directory, with the parsed Root Dir.  This  #
#           allows AChReport to Run from AChoir on other Drives       #
#   v0.86 - AChoir 2.8 now supports pathing - Modify AChReport to     #
#           Gather data from dirs and subdirs using os.walk           #
#   v0.87 - Add Launch String for Autoruns.  Add Check for 7045       #
#            (Service Installed), and 4698 (New Sched Task) Events    #
#   v0.88 - Converted to Python3 - Which broke the colorizing         #
#            - Removed Colorizing for now.                            #
#   v0.90 - Fixed Various Unicode errors fornon-ascii chars.          #
#            - Credit goes to Dean Woods for these fixes              #
#   v0.92 - Add Bulk Hashes and IPs for Bulk checking                 #
####################################################################### 

import os
import sys
import csv
import time 
import argparse
import ctypes

parser = argparse.ArgumentParser(description="Format AChoir Output into a Report")
parser.add_argument("-d", dest="dirname", 
                  help="AChoir Extraction Directory Name")
args = parser.parse_args()


###########################################################################
# Where are the Artifacts, What id the Output File Name
###########################################################################
dirname = str(args.dirname)
dirleft, diright = os.path.split(dirname)
htmname = diright + ".htm"
ipsnameall = "AllIps.txt"
hshnameall = "AllHash.txt"


###########################################################################
# Main 
###########################################################################
def main():
    if dirname != "None":
        if os.path.exists(dirname):
            print("[+] Valid AChoir Extraction Directory Found.\n")
        else:
            print("[!] No Valid AChoir Extraction Directory Found.\n")
            sys.exit(1)
    else:
        print("[!] No Valid AChoir Extraction Directory Found.\n")
        sys.exit(1)


    print("[+] Root AChoir Dir: " + dirleft)


    ###########################################################################
    # Checking for RegRipper Plugins (They have to be in the working subdir)
    ###########################################################################
    print("[+] Checking Software Dependencies...")
    if os.path.isfile(".\plugins\compname.pl"):
        print("[+] AChReport Regripper Plugin directory Found!")
    else:
        print("[*] Copying Regripper Plugins From AChoir Install...")
        returned_value = os.system("mkdir plugins")
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper2.8-master\\plugins\\compname.pl .\\plugins\compname.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper2.8-master\\plugins\\shellfolders.pl .\\plugins\shellfolders.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper2.8-master\\plugins\\userassist.pl .\\plugins\\userassist.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper2.8-master\\plugins\\winnt_cv.pl .\\plugins\winnt_cv.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper2.8-master\\plugins\\winver.pl .\\plugins\winver.pl"
        returned_value = os.system(cmdexec)

    GotDepend = 1
    if os.path.isfile(".\plugins\compname.pl"):
        print("[+] Regripper Plugin Found: compname.pl")
    else:
        print("[!] Regripper Plugin NOT Found: compname.pl")
        GotDepend = 0

    if os.path.isfile(".\plugins\shellfolders.pl"):
        print("[+] Regripper Plugin Found: shellfolders.pl")
    else:
        print("[!] Regripper Plugin NOT Found: shellfolders.pl")
        GotDepend = 0

    if os.path.isfile(".\plugins\\userassist.pl"):
        print("[+] Regripper Plugin Found: userassist.pl")
    else:
        print("[!] Regripper Plugin NOT Found: userassist.pl")
        GotDepend = 0

    if os.path.isfile(".\plugins\winnt_cv.pl"):
        print("[+] Regripper Plugin Found: winnt_cv.pl")
    else:
        print("[!] Regripper Plugin NOT Found: winnt_cv.pl")
        GotDepend = 0

    if os.path.isfile(".\plugins\winver.pl"):
        print("[+] Regripper Plugin Found: winver.pl")
    else:
        print("[!] Regripper Plugin NOT Found: winver.pl")
        GotDepend = 0

    if os.path.isfile("logparser.exe"):
        print("[+] LogParser Found: logparser.exe")
    else:
        print("[!] LogParser NOT Found: logparser.exe")
        GotDepend = 0

    if os.path.isfile("logparser.dll"):
        print("[+] LogParser Found: logparser.dll")
    else:
        print("[!] LogParser NOT Found: logparser.dll")
        GotDepend = 0

    if os.path.isfile("logparser.chm"):
        print("[+] LogParser Found: logparser.chm")
    else:
        print("[!] LogParser NOT Found: logparser.chm")
        GotDepend = 0

    if GotDepend == 0:
        print("[!] ALL Dependencies Not Met - Now Exiting.\n")
        quit()


    ###########################################################################
    # Fell Through, Now Process the files and extract data for report
    ###########################################################################
    print("[+] Now Building Additional Data from Sources...")
    print("[+] Generating System Information from Registry...")

    cmdexec = dirleft + "\\RRV\\RegRipper2.8-master\\rip.exe -p winnt_cv -r " + dirname + "\Reg\SOFTWARE > SysInfo.dat"
    returned_value = os.system(cmdexec)

    cmdexec = dirleft + "\\RRV\\RegRipper2.8-master\\rip.exe -p compname -r " + dirname + "\Reg\SYSTEM >> SysInfo.dat"
    returned_value = os.system(cmdexec)

    cmdexec = dirleft + "\\RRV\\RegRipper2.8-master\\rip.exe -p winver -r " + dirname + "\Reg\SOFTWARE >> SysInfo.dat"
    returned_value = os.system(cmdexec)


    print("[+] Generating Prefetch Data...")
    cmdexec = dirleft + "\\SYS\\WinPrefetchView.exe /folder " + dirname + "\prf /scomma WinPrefetchview.csv"
    returned_value = os.system(cmdexec)

    print("[+] Generating User Assist for Multiple User Profiles...")

    reccount = 0

    curdir = dirname + "\\reg"

    for root, dirs, files in os.walk(curdir):
        for fname in files:
            curfile = os.path.join(root, fname)
            if fname.startswith("NTUSER."):
                curouput = "shlasst." + str(reccount)
                cmdexec = dirleft + "\\RRV\\RegRipper2.8-master\\rip.exe -p shellfolders -r " + curfile + " > " + curouput
                returned_value = os.system(cmdexec)

                cmdexec = dirleft + "\\RRV\\RegRipper2.8-master\\rip.exe -p userassist -r " + curfile + " >> " + curouput
                returned_value = os.system(cmdexec)

                reccount = reccount + 1

    print("[+] Generating RDP Success and Failure...")
    cmdexec = "copy " + dirname + "\\evt\\sys32\\Security.evtx"
    returned_value = os.system(cmdexec)

    print("[+] Generating Service Installed (7045) Messages...")
    cmdexec = "copy " + dirname + "\\evt\\sys32\\System.evtx"
    returned_value = os.system(cmdexec)

    ###########################################################################
    # Use Wevtutil to "export" the event log.  This has the effect of         #
    #  clearing any errors - It makes the Event Log more Stable.              #
    ###########################################################################
    print("[+] Stabilizing Security Event Logs...")
    cmdexec = "Wevtutil.exe epl Security.evtx Security1.evtx /lf:True"
    returned_value = os.system(cmdexec)

    print("[+] Stabilizing System Event Logs...")
    cmdexec = "Wevtutil.exe epl System.evtx System1.evtx /lf:True"
    returned_value = os.system(cmdexec)


    ###########################################################################
    # Parse the Events                                                        #
    ###########################################################################
    print("[+] Parsing Security Event Logs...")
    cmdexec = "LogParser.exe \"Select TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 1, '|') as Machine, EXTRACT_TOKEN(Strings, 5, '|') as LoginID, EXTRACT_TOKEN(Strings, 6, '|') as LoginMachine, EXTRACT_TOKEN(Strings, 8, '|') as LogonType, EXTRACT_TOKEN(Strings, 18, '|') as RemoteIP from Security1.evtx where eventid=4624 AND LogonType='10'\" -i:evt -o:csv -q > RDPGood.csv"
    returned_value = os.system(cmdexec)

    cmdexec = "LogParser.exe \"Select TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 5, '|') as LoginID from Security1.evtx where eventid=4625\" -i:evt -o:csv -q > SecEvt4625.csv"
    returned_value = os.system(cmdexec)

    cmdexec = "LogParser.exe \"Select TimeGenerated AS Date, EXTRACT_TOKEN(strings, 0, '|') AS ServiceName, EXTRACT_TOKEN(strings, 1, '|') AS ServicePath, EXTRACT_TOKEN(strings, 4, '|') AS ServiceUser FROM System1.evtx WHERE EventID = 7045\" -i:evt -o:csv -q > SysEvt7045.csv"
    returned_value = os.system(cmdexec)

    cmdexec = "LogParser.exe \"Select TimeGenerated AS Date, SourceName, EventCategoryName, Message FROM Security1.evtx WHERE EventID = 4698\" -i:evt -o:csv -q > SecEvt4698.csv"
    returned_value = os.system(cmdexec)


    ###########################################################################
    # Parse the Recycle Bin                                                   #
    ###########################################################################
    print("[+] Parsing Recycle Bin...")
    cmdexec = dirleft + "\\SYS\\RBCmd.exe -d " + dirname + "\\RBin >> RBin.dat" 
    returned_value = os.system(cmdexec)


    ###########################################################################
    # Parse the $MFT                                                          #
    ###########################################################################
    print("[+] Parsing $MFT...")
    cmdexec = dirleft + "\\DSK\\MFTDump.exe /l /d /v --output=MFTDump.csv " + dirname + "\\RawData\\$MFT" 
    returned_value = os.system(cmdexec)


    ###########################################################################
    # Clean Up.                                                               #
    ###########################################################################
    os.remove("Security.evtx")
    os.remove("Security1.evtx")
    os.remove("System.evtx")
    os.remove("System1.evtx")


    ###########################################################################
    # Fell Through, Now Process the files and extract data for report         #
    ###########################################################################
    print("[+] Now Processing AChoir Extraction: " + dirname)
    print("[+] Writing Report: " + htmname)
    print("[+] Generating HTML/CSS...")

    outfile = open(htmname, "w", encoding='utf8', errors="replace")
    ipsfileall = open(ipsnameall, "w", encoding='utf8', errors="replace")
    hshfileall = open(hshnameall, "w", encoding='utf8', errors="replace")
    ###########################################################################
    # Write HTML Headers & CSS                                                #
    # RESPONSTABLE 2.0 by jordyvanraaij                                       #
    ###########################################################################
    outfile.write("<html><head><style>\n")
    outfile.write("table {margin: 1em 0; width: 100%; overflow: hidden; background: #FFF; color: #024457; border-radius: 10px; border: 1px solid #167F92;}\n")
    outfile.write("table tr {border: 1px solid #D9E4E6;}\n")
    outfile.write("table tr:nth-child(odd) {background-color: #EAF3F3;}\n")
    outfile.write("table th {display: none; border: 1px solid #FFF; background-color: #167F92; color: #FFF; padding: 1em;}\n")
    outfile.write("table th:first-child {display: table-cell; text-align: center;}\n")
    outfile.write("table th:nth-child(2) {display: table-cell;}\n")
    outfile.write("table th:nth-child(2) span {display: none;}\n")
    outfile.write("table th:nth-child(2):after {content: attr(data-th);}\n")
    outfile.write("@media (min-width: 480px) {table th:nth-child(2) span {display: block;} table th:nth-child(2):after {display: none;}}\n")
    outfile.write("table td {display: block; word-wrap: break-word; max-width: 7em;}\n")
    outfile.write("table td:first-child {display: table-cell; text-align: center; border-right: 1px solid #D9E4E6;}\n")
    outfile.write("@media (min-width: 480px) {table td {border: 1px solid #D9E4E6;}}\n")
    outfile.write("table th, table td {text-align: left; margin: .5em 1em;}\n")
    outfile.write("@media (min-width: 480px) {table th, table td {display: table-cell; padding: 1em;}}\n")
    outfile.write("body {padding: 0 2em; font-family: Arial, sans-serif; color: #024457; background: #f2f2f2;}\n")
    outfile.write("h1 {font-family: Verdana; font-weight: normal; color: #024457;}\n")
    outfile.write("h1 span {color: #167F92;}\n")

    outfile.write("</style><title>AChoir Endpoint Report(" + diright + ")</title></head>\n")
    outfile.write("<body>\n")
    outfile.write("<p><Center>\n")
    outfile.write("<a name=Top></a>\n<H1>AChoir Endpoint Report</H1>\n")
    outfile.write("(" + diright + ")<br>\n")

    outfile.write("<table border=1 cellpadding=5 width=100%>\n")
    outfile.write("<tr><td width=6%> <a href=#Top>Top</a> </td>\n")
    outfile.write("<td width=7%> <a href=#Deleted>Deleted</a> </td>\n")
    outfile.write("<td width=7%> <a href=#Active>Active</a> </td>\n")
    outfile.write("<td width=6%> <a href=#ExeTemp>Temp</a> </td>\n")
    outfile.write("<td width=9%> <a href=#Logins>FailLogin</a> </th>\n")
    outfile.write("<td width=7%> <a href=#RDP>RDP</a> </th>\n")
    outfile.write("<td width=7%> <a href=#Browser>Browser</a> </td>\n")
    outfile.write("<td width=8%> <a href=#Prefetch>Prefetch</a> </td>\n")
    outfile.write("<td width=9%> <a href=#UserAssist>UserAssist</a> </td>\n")
    outfile.write("<td width=9%> <a href=#IPConn>IP_Conn</a> </td>\n")
    outfile.write("<td width=6%> <a href=#DNSCache> DNS </a> </td>\n")
    outfile.write("<td width=7%> <a href=#AutoRun>AutoRun</a> </td>\n")
    outfile.write("<td width=6%> <a href=#InstSVC>EVTx</a> </td>\n")
    outfile.write("<td width=6%> <a href=#RBin>RBin</a> </td></tr>\n")
    outfile.write("</table>\n")

    outfile.write("</Center></p>\n")

    # Write Basic Data
    print("[+] Generating Basic Endpoint Information...")
    outfile.write("<H2>Basic Endpoint Information</H2>\n")

    filname = dirname + "\\info.dat"
    dedname = "SysInfo.dat"

    if os.path.isfile(filname):
        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed standard information about\n")
        outfile.write("the endpoint. This information was extracted using the Microsoft SysInternals\n")
        outfile.write("PSInfo.exe utility.  This utility provides you with basic information about\n")
        outfile.write("What version of Windows is running on the endpoint, and how long the\n")
        outfile.write("endpoint has been running (thus when it may have last last been rebooted\n")
        outfile.write("and/or patched).</font></i></p>\n")

        innfile = open(filname, encoding='utf8', errors="replace")
        for innline in innfile:
            if innline.startswith("System information "):
                outfile.write("<b>" + innline.strip() + "</b><br>\n")

            elif innline.startswith("Uptime:"):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("Kernel version:"):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("Product type:"):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("Product version:"):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("Service pack:"):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("Kernel build number:"):
                outfile.write(innline.strip() + "<br>")

            elif innline.startswith("Registered organization:"):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("Registered owner:"):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("Applications:"):
                break

        innfile.close()

    elif os.path.isfile(dedname):
        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed standard information about\n")
        outfile.write("the endpoint. This information was extracted from the SYSTEM and SOFTWARE Registry Hives\n")
        outfile.write("using RegRipper.</font></i></p>\n")

        innfile = open(dedname, encoding='utf8', errors="replace")
        for innline in innfile:
            if innline.startswith("ComputerName "):
                outfile.write("<b>" + innline.strip() + "</b><br>\n")

            elif innline.startswith("TCP/IP Hostname "):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("ProductName "):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("CSDVersion"):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("InstallDate "):
                outfile.write(innline.strip() + "<br>\n")

        innfile.close()
        os.remove(dedname)

    else:
        outfile.write("<p><i><font color=firebrick>AChoir was not able to parse standard information about\n")
        outfile.write("the endpoint.</font></i></p>\n")
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Clean Up.                                                               #
    ###########################################################################
    os.remove("SysInfo.dat")


    ###########################################################################
    # Write Logon Data                                                        #
    ###########################################################################
    print("[+] Generating Logon Information...")
    outfile.write("<hr><H2>Logon Information</H2>\n")

    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about what Users are \n")
    outfile.write("Logged in to the endpoint. This information was extracted using the Microsoft \n")
    outfile.write("SysInternals PSLoggedon.exe utility.  This information will help you \n")
    outfile.write("determine who may be actively accessing this endpoint.</font></i></p>\n")

    filname = dirname + "\\sys\\Logon.dat"

    if os.path.isfile(filname):
        innfile = open(filname, encoding='utf8', errors="replace")

        for innline in innfile:
            outfile.write(innline.strip() + "<br>\n")
        innfile.close()
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Small Deleted Files ($MFT) - (Use Python CSV Reader Module)             #
    ###########################################################################
    print("[+] Generating Deleted Files $MFT Information...")
    filname = "MFTDump.csv"

    if os.path.isfile(filname):
        reccount = 0
        outfile.write("<a name=Deleted></a>\n<hr><H2>Small Deleted Files (Between 1 Meg and 10 meg)</H2>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about Deleted Files \n")
        outfile.write("that are between 1 and 10 Megabytes.  This can be completely normal, or it \n")
        outfile.write("may indicate that small data files were created on the endpoint to \n")
        outfile.write("exfiltrate data - and then those files were deleted. Look through these \n")
        outfile.write("files to see where they were located, and what their File Names were to \n")
        outfile.write("determine if they look suspicious.</font></i></p>\n")

        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        outfile.write("<tr><th width=40%> Full Path </th>\n")
        outfile.write("<th width=15%> Created </th>\n")
        outfile.write("<th width=15%> Accessed </th>\n")
        outfile.write("<th width=15%> Modified </th>\n")
        outfile.write("<th width=15%> Size </th></tr>\n")

        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter='\t')
            for csvrow in csvread:
                if len(csvrow) > 13:
                    # Is it a Deleted File
                    if csvrow[1] == "1":
                        FileSize = csvrow[10]
                        if (FileSize.isdigit and len(FileSize) > 1):
                            nFileSize = int(FileSize)
                            if (nFileSize > 1000000 and nFileSize < 10000000):
                                outfile.write("<tr><td width=40%>" + csvrow[13] + "</td>\n")
                                outfile.write("<td width=15%>" + csvrow[6] + "</td>\n")
                                outfile.write("<td width=15%>" + csvrow[7] + "</td>\n")
                                outfile.write("<td width=15%>" + csvrow[8] + "</td>\n")
                                outfile.write("<td width=15%>" + "{:,}".format(nFileSize) + "</td></tr>\n")
                                reccount = reccount + 1
        outfile.write("</table>\n")
        # csvfile.close()

        if reccount < 1:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Medium Deleted Files ($MFT) - (Use Python CSV Reader Module)            #
    ###########################################################################
    filname = "MFTDump.csv"

    if os.path.isfile(filname):
        reccount = 0
        outfile.write("\n<hr><H2>Medium Deleted Files (Between 10 Meg and 100 meg)</H2>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about Deleted Files \n")
        outfile.write("that are between 10 and 100 Megabytes.  This can be completely normal, or it \n")
        outfile.write("may indicate that small data files were created on the endpoint to \n")
        outfile.write("exfiltrate data - and then those files were deleted. Look through these \n")
        outfile.write("files to see where they were located, and what their File Names were to \n")
        outfile.write("determine if they look suspicious.</font></i></p>\n")

        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        outfile.write("<tr><th width=40%> Full Path </th>\n")
        outfile.write("<th width=15%> Created </th>\n")
        outfile.write("<th width=15%> Accessed </th>\n")
        outfile.write("<th width=15%> Modified </th>\n")
        outfile.write("<th width=15%> Size </th></tr>\n")

        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter='\t')
            for csvrow in csvread:
                if len(csvrow) > 13:
                    # Is it a Deleted File
                    if csvrow[1] == "1":
                        FileSize = csvrow[10]
                        if (FileSize.isdigit and len(FileSize) > 1):
                            nFileSize = int(FileSize)
                            if (nFileSize > 10000000 and nFileSize < 100000000):
                                outfile.write("<tr><td width=40%>" + csvrow[13] + "</td>\n")
                                outfile.write("<td width=15%>" + csvrow[6] + "</td>\n")
                                outfile.write("<td width=15%>" + csvrow[7] + "</td>\n")
                                outfile.write("<td width=15%>" + csvrow[8] + "</td>\n")
                                outfile.write("<td width=15%>" + "{:,}".format(nFileSize) + "</td></tr>\n")
                                reccount = reccount + 1
        outfile.write("</table>\n")
        # csvfile.close()

        if reccount < 1:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Large Deleted Files ($MFT) - (Use Python CSV Reader Module)             #
    ###########################################################################
    filname = "MFTDump.csv"

    if os.path.isfile(filname):
        reccount = 0
        outfile.write("\n<hr><H2>Large Deleted Files (Over 100 Meg)</H2>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about Deleted Files \n")
        outfile.write("that are larger than 100 Megabytes.  This can be completely normal, or it \n")
        outfile.write("may indicate that large data files were created on the endpoint to \n")
        outfile.write("exfiltrate data - and then those files were deleted. Look through these \n")
        outfile.write("files to see where they were located, and what their File Names were to \n")
        outfile.write("determine if they look suspicious.</font></i></p>\n")

        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        outfile.write("<tr><th width=40%> Full Path </th>\n")
        outfile.write("<th width=15%> Created </th>\n")
        outfile.write("<th width=15%> Accessed </th>\n")
        outfile.write("<th width=15%> Modified </th>\n")
        outfile.write("<th width=15%> Size </th></tr>\n")

        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter='\t')
            for csvrow in csvread:
                if len(csvrow) > 13:
                    # Is it a Deleted File
                    if csvrow[1] == "1":
                        FileSize = csvrow[10]
                        if (FileSize.isdigit and len(FileSize) > 1):
                            nFileSize = int(FileSize)
                            if nFileSize > 100000000:
                                outfile.write("<tr><td width=40%>" + csvrow[13] + "</td>\n")
                                outfile.write("<td width=15%>" + csvrow[6] + "</td>\n")
                                outfile.write("<td width=15%>" + csvrow[7] + "</td>\n")
                                outfile.write("<td width=15%>" + csvrow[8] + "</td>\n")
                                outfile.write("<td width=15%>" + "{:,}".format(nFileSize) + "</td></tr>\n")
                                reccount = reccount + 1
        outfile.write("</table>\n")
        # csvfile.close()

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")



    ###########################################################################
    # Large Active Files ($MFT) - (Use Python CSV Reader Module)              #
    ###########################################################################
    print("[+] Generating Active Files $MFT Information...")
    filname = "MFTDump.csv"

    if os.path.isfile(filname):
        reccount = 0
        outfile.write("<a name=Active></a>\n<hr>\n<H2>Large Active Files (Over 100 Meg)</H2>\n")


        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about(Active) Files \n")
        outfile.write("that are larger than 100 Megabytes.  This can be completely normal, or it \n")
        outfile.write("may indicate that large data files were created on the endpoint to \n")
        outfile.write("exfiltrate data.  Look through these \n")
        outfile.write("files to see where they were located, and what their File Names were to \n")
        outfile.write("determine if they look suspicious.</font></i></p>\n")

        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        outfile.write("<tr><th width=40%> Full Path </th>\n")
        outfile.write("<th width=15%> Created </th>\n")
        outfile.write("<th width=15%> Accessed </th>\n")
        outfile.write("<th width=15%> Modified </th>\n")
        outfile.write("<th width=15%> Size </th></tr>\n")

        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter='\t')
            for csvrow in csvread:
                if len(csvrow) > 13:
                    # Is it a Deleted File
                    if csvrow[1] == "0":
                        FileSize = csvrow[10]
                        if (FileSize.isdigit and len(FileSize) > 1):
                            nFileSize = int(FileSize)
                            if nFileSize > 100000000:
                                outfile.write("<tr><td width=40%>" + csvrow[13] + "</td>\n")
                                outfile.write("<td width=15%>" + csvrow[6] + "</td>\n")
                                outfile.write("<td width=15%>" + csvrow[7] + "</td>\n")
                                outfile.write("<td width=15%>" + csvrow[8] + "</td>\n")
                                outfile.write("<td width=15%>" + "{:,}".format(nFileSize) + "</td></tr>\n")
                                reccount = reccount + 1
        outfile.write("</table>\n")
        # csvfile.close()

        if reccount < 1:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")



    ###########################################################################
    # Active Exe Files in Temp Directories - (Use Python CSV Reader Module)   #
    ###########################################################################
    print("[+] Generating Active Files in Temp Directories...")
    filname = "MFTDump.csv"

    if os.path.isfile(filname):
        reccount = 0
        outfile.write("<a name=ExeTemp></a>\n<hr>\n<H2>Active Executable Files in Temp Directories</H2>\n")


        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about Active Executable Files \n")
        outfile.write("in Temp Directories.  These files can indicate hostile executables (malware) that have been \n")
        outfile.write("downloaded and executed from Temp Directories.  This can indicate normal behavior, however \n")
        outfile.write("malware is often executed from Temp Directories.  Review these\n")
        outfile.write("files to see if they appear to be malicious - a good indicator is if the executable has a \n")
        outfile.write("name that appears to be randomly generated.</font></i></p>\n")

        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        outfile.write("<tr><th width=40%> Full Path </th>\n")
        outfile.write("<th width=15%> Created </th>\n")
        outfile.write("<th width=15%> Accessed </th>\n")
        outfile.write("<th width=15%> Modified </th>\n")
        outfile.write("<th width=15%> Size </th></tr>\n")

        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter='\t')
            for csvrow in csvread:
                if len(csvrow) > 13:
                    # Is it an Active File
                    if csvrow[1] == "0":
                        FullPath = csvrow[13]
                        lFullPath = FullPath.lower()
                        if "\\temp\\" in lFullPath and ".exe" in lFullPath:
                            FileSize = csvrow[10]
                            if (FileSize.isdigit and len(FileSize) > 1):
                                nFileSize = int(FileSize)
                            else:
                                nFileSize = 0
                            outfile.write("<tr><td width=40%>" + csvrow[13] + "</td>\n")
                            outfile.write("<td width=15%>" + csvrow[6] + "</td>\n")
                            outfile.write("<td width=15%>" + csvrow[7] + "</td>\n")
                            outfile.write("<td width=15%>" + csvrow[8] + "</td>\n")
                            outfile.write("<td width=15%>" + "{:,}".format(nFileSize) + "</td></tr>\n")
                            reccount = reccount + 1
        outfile.write("</table>\n")

        if reccount < 1:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Deleted Exe Files in Temp Directories - (Use Python CSV Reader Module)  #
    ###########################################################################
    print("[+] Generating Deleted Files in Temp Directories...")
    filname = "MFTDump.csv"

    if os.path.isfile(filname):
        reccount = 0
        outfile.write("<a name=ExeTemp></a>\n<hr>\n<H2>Deleted Executable Files in Temp Directories</H2>\n")


        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about Deleted Executable Files \n")
        outfile.write("in Temp Directories.  These files can indicate hostile executables (malware) that have been \n")
        outfile.write("downloaded, executed, then deleted from Temp Directories.  This can indicate normal behavior, however \n")
        outfile.write("malware is often executed from Temp Directories.  Review these\n")
        outfile.write("files to see if they appear to be malicious - a good indicator is if the deleted executable has a \n")
        outfile.write("name that appears to be randomly generated.</font></i></p>\n")

        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        outfile.write("<tr><th width=40%> Full Path </th>\n")
        outfile.write("<th width=15%> Created </th>\n")
        outfile.write("<th width=15%> Accessed </th>\n")
        outfile.write("<th width=15%> Modified </th>\n")
        outfile.write("<th width=15%> Size </th></tr>\n")

        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter='\t')
            for csvrow in csvread:
                if len(csvrow) > 13:
                    # Is it a Deleted File
                    if csvrow[1] == "1":
                        FullPath = csvrow[13]
                        lFullPath = FullPath.lower()
                        if "\\temp\\" in lFullPath and ".exe" in lFullPath:
                            FileSize = csvrow[10]
                            if (FileSize.isdigit and len(FileSize) > 1):
                                nFileSize = int(FileSize)
                            else:
                                nFileSize = 0
                            outfile.write("<tr><td width=40%>" + csvrow[13] + "</td>\n")
                            outfile.write("<td width=15%>" + csvrow[6] + "</td>\n")
                            outfile.write("<td width=15%>" + csvrow[7] + "</td>\n")
                            outfile.write("<td width=15%>" + csvrow[8] + "</td>\n")
                            outfile.write("<td width=15%>" + "{:,}".format(nFileSize) + "</td></tr>\n")
                            reccount = reccount + 1
        outfile.write("</table>\n")

        if reccount < 1:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Clean Up.                                                               #
    ###########################################################################
    os.remove("MFTDump.csv")
    os.remove("MFTDump.log")


    ###########################################################################
    # Write Success RDP Logins (Use Python CSV Reader Module)                 #
    ###########################################################################
    print("[+] Generating Sucessful RDP Login Information...")
    outfile.write("<a name=RDP></a>\n<hr>\n<H2>Successful RDP Logins</H2>\n")

    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
    outfile.write("succesful RDP Logins.  These are EventID 4624-LogonType 10 events in the \n")
    outfile.write("Windows Security Event Log.  These Entries indicate that someone remotely \n")
    outfile.write("Logged in to this endpoint using RDP.  This may be completely normal - or it may \n")
    outfile.write("indicate that a hostile actor has compromised RDP credentials. Focus on the RemoteIPs \n")
    outfile.write("to determine if they look suspicious.</font></i></p>\n")

    reccount = 0
    filname = "RDPGood.csv"

    if os.path.isfile(filname):
        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
            for csvrow in csvread:
                if len(csvrow) > 4:
                    if reccount == 0:
                        tdtr = "th"
                    else:
                        tdtr = "td"

                    outfile.write("<tr><" + tdtr + " width=20%>" + csvrow[0] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=15%>" + csvrow[1] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=15%>" + csvrow[2] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=20%>" + csvrow[3] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=10%>" + csvrow[4] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=20%>" + csvrow[5] + "</" + tdtr + "></tr>\n")

                    reccount = reccount + 1
        outfile.write("</table>\n")
        os.remove(filname)

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Write Failed Logins (Use Python CSV Reader Module)                      #
    ###########################################################################
    print("[+] Generating Failed Logins Information...")
    outfile.write("<a name=Logins></a>\n<hr>\n<H2>Failed Logins</H2>\n")

    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
    outfile.write("Failed Logins.  These are EventID 4625 events in the Windows Security Event Log.\n")
    outfile.write("These Entries indicate that someone (or multiple people) failed to Login to this \n")
    outfile.write("machine.  High numbers of failed logins can indicate BRUTE FORCE Hacking, and small \n")
    outfile.write("numbers of attempts against MANY DIFFERENT UserIDs can indicate PASSWORD SPRAYING.\n")
    outfile.write(" Focus on both the number of attempts and the UserIDs to see if the failed logins \n")
    outfile.write(" look suspicious.</font></i></p>\n")

    reccount = 0
    filname = "SecEvt4625.csv"

    dedupCol = []
    dedupCnt = []

    if os.path.isfile(filname):
        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        outfile.write("<tr><th width=75%> Attempted UserId </th>\n")
        outfile.write("<th width=25%> Count </th></tr>\n")

        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
            for csvrow in csvread:
                ldedupKey = csvrow[1].lower()
                if csvrow[0].lower() == "date":
                    pass
                elif ldedupKey in dedupCol:
                    reccount = reccount + 1
                    curCnt = dedupCnt[dedupCol.index(ldedupKey)]
                    curCnt += 1
                    dedupCnt[dedupCol.index(ldedupKey)] = curCnt
                else:
                    dedupCol.append(ldedupKey)
                    dedupCnt.append(1)


        if reccount > 0:
            reccount = 0
            dedupCnt, dedupCol = list(zip(*sorted(zip(dedupCnt, dedupCol), reverse=True)))

            totIdx = len(dedupCol)
            for curIdx in range(0, totIdx):
                outfile.write("<tr><td width=75%>" + dedupCol[curIdx] + "</td>\n")
                outfile.write("<td width=25%>" + str(dedupCnt[curIdx]) + "</td></tr>\n")

                reccount = reccount + 1

        outfile.write("</table>\n")
        os.remove(filname)

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")



    ###########################################################################
    # Write File Browser Data/Archive types  (Use Python CSV Reader Module)   #
    ###########################################################################
    print("[+] Generating File History access to Archive Files...")
    outfile.write("<a name=Browser></a>\n<hr>\n<H2>File Browse (Archive files) History Information</H2>\n")
    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
    outfile.write("Accessed Files that have an Archive File Type (i.e. .Arc, .Rar, .Zip, .Tar, .7z, .Cab)\n")
    outfile.write("These Entries indicate that someone (or multiple people) archived data into a compressed\n")
    outfile.write("file format.  This is often used by hostile actors to gather up data for future (or past)\n")
    outfile.write("exfiltration.  Focus on any and all files that indicate data was archived, especially \n")
    outfile.write("in Temporary Directories.</font></i></p>\n")

    reccount = 0
    filname = dirname + "\\brw\\BrowseHist.csv"
    outfile.write("<table border=1 cellpadding=5 width=100%>\n")

    if os.path.isfile(filname):
        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
            for csvrow in csvread:
                if len(csvrow) > 7:
                    if reccount == 0:
                        tdtr = "th"
                    else:
                        tdtr = "td"

                    fullURL = csvrow[0]
                    if fullURL.startswith("file:///") or reccount == 0:
                        if ".rar" in fullURL or ".tgz" in fullURL or ".gz" in fullURL or ".tar" in fullURL or ".cab" in fullURL or ".zip" in fullURL or ".arc" in fullURL or ".7z" in fullURL or ".cab" in fullURL or reccount == 0:
                            outfile.write("<tr><" + tdtr + " width=15%>" + csvrow[2] + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=5%>" + csvrow[3] + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=60%>" + csvrow[0] + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + csvrow[6] + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + csvrow[7] + "</" + tdtr + "></tr>\n")

                            reccount = reccount + 1
        outfile.write("</table>\n")

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")



    ###########################################################################
    # Write Web Browser Data (Use Python CSV Reader Module)                   #
    ###########################################################################
    print("[+] Generating File and Web Browser Information...")
    outfile.write("<hr>\n<H2>File Browse History Information</H2>\n")
    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
    outfile.write("accessed files. These files were accessed on the machine and may indicate hostile\n")
    outfile.write("program installation or execution, as well as access to sensitive or hostile files.\n")
    outfile.write("This can also be completely normal activity.  Review the files accessed for anything \n")
    outfile.write("that appears to be suspicious, especially programs that that were run, files that were\n")
    outfile.write("accessed or archive files created.</font></i></p>\n")


    reccount = 0
    filname = dirname + "\\brw\\BrowseHist.csv"
    outfile.write("<table border=1 cellpadding=5 width=100%>\n")

    if os.path.isfile(filname):
        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
            for csvrow in csvread:
                if len(csvrow) > 7:
                    if reccount == 0:
                        tdtr = "th"
                    else:
                        tdtr = "td"

                    fullURL = csvrow[0]
                    if fullURL.startswith("file:///") or reccount == 0:
                        outfile.write("<tr><" + tdtr + " width=15%>" + csvrow[2] + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=5%>" + csvrow[3] + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=60%>" + csvrow[0] + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=10%>" + csvrow[6] + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=10%>" + csvrow[7] + "</" + tdtr + "></tr>\n")

                        reccount = reccount + 1
        outfile.write("</table>\n")

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Write Web Browser Data (Use Python CSV Reader Module)                   #
    ###########################################################################
    outfile.write("<hr>\n<H2>Internet Browse History Information</H2>\n")

    reccount = 0
    filname = dirname + "\\brw\\BrowseHist.csv"
    outfile.write("<table border=1 cellpadding=5 width=100%>\n")

    if os.path.isfile(filname):
        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
            for csvrow in csvread:
                if len(csvrow) > 7:
                    if reccount == 0:
                        tdtr = "th"
                    else:
                        tdtr = "td"

                    fullURL = csvrow[0]
                    if not fullURL.startswith("file:///"):
                        outfile.write("<tr><" + tdtr + " width=15%>" + csvrow[2] + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=5%>" + csvrow[3] + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=60%>" + csvrow[0] + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=10%>" + csvrow[6] + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=10%>" + csvrow[7] + "</" + tdtr + "></tr>\n")

                        reccount = reccount + 1
        outfile.write("</table>\n")

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Write Prefetch Data (Use Python CSV Reader Module)                      #
    ###########################################################################
    print("[+] Generating Prefetch Information...")
    outfile.write("<a name=Prefetch></a>\n<hr>\n<H2>Prefetch History Information</H2>\n")
    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
    outfile.write("Prefetch files. Prefetch files are generated by Windows to make loading previously \n")
    outfile.write("executed programs faster when they are executed again.  These files are forensically \n")
    outfile.write("interesting because they indicate that a program was excuted, as well as when and how \n")
    outfile.write("many times.  This is normal behavior and does not in-itself indicate hostile behavior. \n")
    outfile.write("However, a quick look at the prefetch files is a good way to see in anything executed \n")
    outfile.write("appears to be suspicious.  Review this section to see if anything looks out of the \n")
    outfile.write("ordinary, or appears to be malicious.</font></i></p>\n")

    reccount = 0
    filname = "WinPrefetchView.csv"

    if os.path.isfile(filname):
        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        outfile.write("<tr><th width=20%> FileName </th>\n")
        outfile.write("<th width=15%> Created </th>\n")
        outfile.write("<th width=15%> Modified </th>\n")
        outfile.write("<th width=15%> Last Run </th>\n")
        outfile.write("<th width=5%> Times </th>\n")
        outfile.write("<th width=30%> Path </th></tr>\n")

        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
            for csvrow in csvread:
                if len(csvrow) > 7:
                    reccount = reccount + 1
                    outfile.write("<tr bgcolor=E0E0E0><td width=20%>" + csvrow[0] + "</td>\n")
                    outfile.write("<td width=15%>" + csvrow[1] + "</td>\n")
                    outfile.write("<td width=15%>" + csvrow[2] + "</td>\n")
                    outfile.write("<td width=15%>" + csvrow[7] + "</td>\n")
                    outfile.write("<td width=5%>" + csvrow[6] + "</td>\n")
                    outfile.write("<td width=30%>" + csvrow[5] + "</td></tr>\n")
        outfile.write("</table>\n")
        os.remove(filname)

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Write Connection Data (Use Python CSV Reader Module)                    #
    ###########################################################################
    print("[+] Generating IP Connections Information...")
    outfile.write("<a name=IPConn></a>\n<hr>\n<H2>IP Connections Information</H2>\n")

    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
    outfile.write("Windows IP Connections (TCP and UDP). It is not unusual for many programs to open \n")
    outfile.write("TCP or UDP connections to communicate.  However, many malicious programs also open \n")
    outfile.write("TCP and/or UDP ports. To identify possibly malicious (C2) connections, look through \n")
    outfile.write("this section for unusual program names and/or unusual port numbers. Also look for \n")
    outfile.write("programs (like NotePad) which should never open a connection. If you suspect a \n")
    outfile.write("malicious port has been opened, use Open Source Intel like VirusTotal to check if the \n")
    outfile.write("IP Address is known to be malicious.  This report has automatically created links to \n")
    outfile.write("VirusTotal for your convenience.</font></i></p>\n")

    reccount = 0
    filname = dirname + "\\sys\\CPorts.csv"

    if os.path.isfile(filname):
        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        outfile.write("<tr><th width=13%> Process </th>\n")
        outfile.write("<th width=5%> Prot. </th>\n")
        outfile.write("<th width=10%> Local IP </th>\n")
        outfile.write("<th width=5%> LPort </th>\n")
        outfile.write("<th width=10%> Remote IP </th>\n")
        outfile.write("<th width=5%> RPort </th>\n")
        outfile.write("<th width=15%> RHost </th>\n")
        outfile.write("<th width=7%> State </th>\n")
        outfile.write("<th width=30%> Process Path </th></tr>\n")

        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
            for csvrow in csvread:
                if len(csvrow) > 11:
                    reccount = reccount + 1
                    outfile.write("<tr bgcolor=E0E0E0><td width=13%>" + csvrow[0] + "</td>\n")
                    outfile.write("<td width=5%>" + csvrow[2] + "</td>\n")
                    outfile.write("<td width=10%>" + csvrow[5] + "</td>\n")
                    outfile.write("<td width=5%>" + csvrow[3] + "</td>\n")
                    outfile.write("<td width=10%> <A href=https://www.virustotal.com/#/search/" + csvrow[8] + ">" + csvrow[8] + "</a> </td>\n")
                    outfile.write("<td width=5%>" + csvrow[6] + "</td>\n")
                    outfile.write("<td width=15%>" + csvrow[9] + "</td>\n")
                    outfile.write("<td width=7%>" + csvrow[10] + "</td>\n")
                    outfile.write("<td width=30%>" + csvrow[11] + "</td></tr>\n")

                    # Write out IP Address for Bulk Lookup 
                    ipsfileall.write(csvrow[8] + "\n")

        outfile.write("</table>\n")

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")



    ###########################################################################
    # Write User Assist Data (Use Python CSV Reader Module)                   #
    ###########################################################################
    print("[+] Generating User Assist Information...")
    outfile.write("<a name=UserAssist></a>\n<hr>\n<H2>HKCU User Assist Information</H2>\n")
    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
    outfile.write("the Windows UserAssist Registry Keys (Both System and User Hives). UserAssist keys \n")
    outfile.write("are created by Windows to save program window locations.  These files are forensically \n")
    outfile.write("interesting because they indicate that a program was excuted by a user, and the last \n")
    outfile.write("time it was executed.  This is normal behavior and does not in-itself indicate hostile behavior. \n")
    outfile.write("However, a quick look at the UserAssist Keys is a good way to see if anything executed \n")
    outfile.write("appears to be suspicious.  Review this section to see if anything looks out of the \n")
    outfile.write("ordinary, or appears to be malicious.</font></i></p>\n")

    reccount = 0
    filname = dirname + "\\sys\\UserAssist.csv"

    if os.path.isfile(filname):
        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        outfile.write("<tr><th width=13%> Modified Time </th>\n")
        outfile.write("<th width=5%> Modified Count </th>\n")
        outfile.write("<th width=30%> Item Name </th></tr>\n")

        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
            for csvrow in csvread:
                if len(csvrow) > 3:
                    reccount = reccount + 1
                    outfile.write("<tr bgcolor=E0E0E0><td width=15%>" + csvrow[3] + "</td>\n")
                    outfile.write("<td width=5%>" + csvrow[2] + "</td>\n")
                    outfile.write("<td width=30%>" + csvrow[0] + "</td></tr>\n")
        outfile.write("</table>\n")

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")



    ###########################################################################
    # Write Other User Assist Data (Gathered from RegRipper Earlier)          #
    ###########################################################################
    outfile.write("<hr>\n<H2>Other User Assist Information</H2>\n")

    filcount = 0

    for curfile in os.listdir("."):
        if curfile.startswith("shlasst."):
            # Find the Desktop Directory (That tells us the user)
            filcount = filcount + 1
            outfile.write("<table border=1 cellpadding=5 width=100%>\n")

            innfile = open(curfile, encoding='utf8', errors="replace")
            for innline in innfile:
                if innline.startswith("Desktop "):
                    outfile.write("<tr><th width=100%>" + innline.strip()  + "</th></tr>\n")
            innfile.close()

            outfile.write("<tr><td style=\"text-align: left\">\n")

            reccount = 0 
            innfile = open(curfile, encoding='utf8', errors="replace")
            for innline in innfile:
                if innline.startswith("shellfolders "):
                    outfile.write("<h2>" + innline.strip()  + "</h2><br>\n")
                elif innline.startswith("UserAssist"):
                    outfile.write("<hr><h2>" + innline.strip()  + "</h2><br>\n")
                else:
                    outfile.write(innline.strip()  + "<br>\n")
                reccount = reccount + 1
            innfile.close()
            outfile.write("</td></tr></table>\n")
            os.remove(curfile)

            if reccount < 2:
                outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
            else:
                outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

    if filcount < 2:
        outfile.write("<p><b><font color = red> No User Assist (NTUSER.DAT) Data Found! </font></b></p>\n")



    ###########################################################################
    # Write AutoRunsc Data (Run and RunOnce) (Use Python CSV Reader Module)   #
    ###########################################################################
    print("[+] Generating AutoRuns Information...")

    outfile.write("<a name=AutoRun></a>\n<hr>\n<H2>AutoRun Information (Run And RunOnce)</H2>\n")

    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
    outfile.write("Run and RunOnce Registry Keys.  These are THE MOST common Registry keys where malicious \n")
    outfile.write("programs(MalWare) can reside.  These Registry keys allow malware to PERSIST across \n")
    outfile.write("system reboots.  These Registry Keys can also be used for legitimate software and  \n")
    outfile.write("utilities.  Some good indicators that Run Keys are being used maliciously is if they \n")
    outfile.write("run programs that have random file names, or are installed/run from Temp Directories. \n")
    outfile.write("Focus on both the file names, and where the programs are located to determine if they \n")
    outfile.write("look suspicious.</font></i></p>\n")

    outfile.write("<table border=1 cellpadding=5 width=100%>\n")
    outfile.write("<tr><th width=10%> Time </th>\n")
    outfile.write("<th width=30%> Entry Location </th>\n")
    outfile.write("<th width=10%> Entry </th>\n")
    outfile.write("<th width=30%> Image Path <hr> Launch String</th>\n")
    outfile.write("<th width=15%> MD5 </th>\n")
    outfile.write("<th width=5%> Enabled </th></tr>\n")

    reccount = 0
    filname = dirname + "\\arn\\AutoRun.dat"

    if os.path.isfile(filname):
        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
            for csvrow in csvread:
                if len(csvrow) > 10:
                    if "currentversion\\run" in csvrow[1].lower():
                        outfile.write("<tr><td width=10%>" + csvrow[0] + "</td>\n")
                        outfile.write("<td width=30%>" + csvrow[1] + "</td>\n")
                        outfile.write("<td width=10%>" + csvrow[2] + "</td>\n")
                        outfile.write("<td width=30%>" + csvrow[8] + "<hr>" + csvrow[10] + "</td>\n")
                        if len(csvrow) > 11:
                            outfile.write("<td width=15%> <A href=https://www.virustotal.com/#/search/" + csvrow[11] + ">" + csvrow[11] + "</a> </td>\n")
                        else:
                            outfile.write("<td width=15%> No MD5 Available </td>\n")
                        outfile.write("<td width=5%>" + csvrow[3] + "</td></tr>\n")

                        reccount = reccount + 1
        outfile.write("</table>\n")

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Write AutoRunsc Data (Use Python CSV Reader Module)                     #
    ###########################################################################
    outfile.write("<hr>\n<H2>AutoRun Information (All)</H2>\n")

    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
    outfile.write("several AutoRun settings.  These can show several different places where malicious \n")
    outfile.write("programs(MalWare) can reside.  These settings can allow malware to PERSIST across \n")
    outfile.write("system reboots.  These settings can also be used for legitimate software and  \n")
    outfile.write("utilities.  Some good indicators that these settings are being used maliciously is if they \n")
    outfile.write("run programs that have random file names, or are installed/run from Temp Directories. \n")
    outfile.write("Focus on both the file names, and where the programs are located to determine if they \n")
    outfile.write("look suspicious.</font></i></p>\n")

    outfile.write("<table border=1 cellpadding=5 width=100%>\n")

    reccount = 0
    filname = dirname + "\\arn\\AutoRun.dat"

    if os.path.isfile(filname):
        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
            for csvrow in csvread:
                if len(csvrow) > 10:
                    if reccount == 0:
                        tdtr = "th"
                        Hash = "MD5"
                    else:
                        tdtr = "td"
                        Hash = "No MD5 Available"

                    outfile.write("<tr><" + tdtr + " width=10%>" + csvrow[0] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=30%>" + csvrow[1] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=10%>" + csvrow[2] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=30%>" + csvrow[8] + "<hr>" + csvrow[10] + "</" + tdtr + ">\n")
                    if len(csvrow) > 11:
                        outfile.write("<" + tdtr + " width=15%> <A href=https://www.virustotal.com/#/search/" + csvrow[11] + ">" + csvrow[11] + "</a> </td>\n")

                        # Write out Hash for Bulk Lookup 
                        hshfileall.write(csvrow[11] + "\n")
                    else:
                        outfile.write("<" + tdtr + " width=15%> " + Hash + " </td>\n")
                    outfile.write("<" + tdtr + " width=5%>" + csvrow[3] + "</" + tdtr + "></tr>\n")

                    reccount = reccount + 1
        outfile.write("</table>\n")

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Write 7045 Installed Sesrvices Log Entries                              #
    ###########################################################################
    print("[+] Generating 7045 Installed Services Logs...")
    outfile.write("<a name=InstSvc></a>\n<hr>\n<H2>Installed Services</H2>\n")

    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
    outfile.write("Installed Services.  These are EventID 7045 System Events in the \n")
    outfile.write("Windows System Event Log.  These Entries indicate that a service was installed. \n")
    outfile.write("This may be completely normal - or it may indicate that a hostile actor has installed \n")
    outfile.write("a hostile or malicious service. Focus on the Service Names (For instance Random Names) \n")
    outfile.write("and the Service Executables (for instance Powershell, WMIC, or other suspicious executables) \n")
    outfile.write("which may indicate malicious intent.</font></i></p>\n")

    reccount = 0
    filname = "SysEvt7045.csv"

    if os.path.isfile(filname):
        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
            for csvrow in csvread:
                if len(csvrow) > 3:
                    if reccount == 0:
                        tdtr = "th"
                    else:
                        tdtr = "td"

                    outfile.write("<tr><" + tdtr + " width=15%>" + csvrow[0] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=30%>" + csvrow[1] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=45%>" + csvrow[2] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=10%>" + csvrow[3] + "</" + tdtr + "></tr>\n")

                    reccount = reccount + 1
        outfile.write("</table>\n")
        os.remove(filname)

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Write 4698 New Sched Tasks Log Entries                                  #
    ###########################################################################
    print("[+] Generating 4698 New Sched Tasks Logs...")
    outfile.write("<a name=NewTask></a>\n<hr>\n<H2>New Scheduled Tasks</H2>\n")

    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
    outfile.write("New Scheduled Tasks.  These are EventID 4698 System Events in the \n")
    outfile.write("Windows Security Event Log. <b>IMPORTANT NOTE: IF OBJECT ACCESS AUDITING WAS NOT ENABLED \n")
    outfile.write("4698 MESSAGES WILL NOT BE GENERATED!</b> - You can always review Current Scheduled tasks \n")
    outfile.write("in the <a href=#AutoRun>AutoRun Section</a>.  If Object Access Auditing was enabled on \n")
    outfile.write("this endpoint, these 4698 log entries indicate that a New Task \n")
    outfile.write("was scheduled. This may be completely normal - or it may indicate that a hostile actor has \n")
    outfile.write("scheduled a hostile or malicious task. Focus on the Task Names and Executables \n")
    outfile.write("(for instance Powershell, WMIC, or others suspicious executables) \n")
    outfile.write("which may indicate malicious intent.</font></i></p>\n")

    reccount = 0
    filname = "SecEvt4698.csv"

    if os.path.isfile(filname):
        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
            for csvrow in csvread:
                if len(csvrow) > 3:
                    if reccount == 0:
                        tdtr = "th"
                    else:
                        tdtr = "td"

                    outfile.write("<tr><" + tdtr + " width=15%>" + csvrow[0] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=25%>" + csvrow[1] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=30%>" + csvrow[2] + "</" + tdtr + ">\n")
                    outfile.write("<" + tdtr + " width=30%>" + csvrow[3] + "</" + tdtr + "></tr>\n")

                    reccount = reccount + 1
        outfile.write("</table>\n")
        os.remove(filname)

        if reccount < 2:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Write DNS Cache Data = Flat File.                                       #
    ###########################################################################
    print("[+] DNS Cache Information...")

    outfile.write("<a name=DNSCache></a>\n<hr>\n<H2>DNS Cache (IPConfig /displaydns)</H2>\n")

    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
    outfile.write("Cached DNS. These entries show the DNS resolution that the endpoint did.  This can indicate \n")
    outfile.write("Web Sites, Chat Programs, or C2 communication using FQDN (Fully Qualified Domain Name) \n")
    outfile.write("These domains can often be used for legitimate software and \n")
    outfile.write("utilities.  Some good indicators that these domains are maliciously is if they \n")
    outfile.write("have random names or show up in Virus Total (or other Open Source Threat Feeds) as \n")
    outfile.write("malicious.  If you are unsure, Check both the Domain and IP in Virus Total, ZScaler, or \n")
    outfile.write("URLQuery. This report has already linked the A and PTR Records to check VirusTotal</font></i></p>\n")

    reccount = 0
    writeRow = 0
    LastRec = ""
    filname = dirname + "\\sys\\IPCfgDNS.dat"

    if os.path.isfile(filname):
        outfile.write("<table border=1 cellpadding=5 width=100%>\n")
        outfile.write("<tr><th width=25%> DNS Request </th>\n")
        outfile.write("<th width=25%> Record Name </th>\n")
        outfile.write("<th width=25%> Resolution </th>\n")
        outfile.write("<th width=25%> Record Type </th></tr>\n")

        innfile = open(filname, encoding='utf8', errors="replace")
        for innline in innfile:
            if innline.startswith("    ------"):
                DNSRecName = LastRec
                LastRec = ""

            elif innline.startswith("    Record Name . . . . . :"):
                RecName = innline[28:]

            elif innline.startswith("    Name does not exist."):
                RecName = "NA"                
                RecType = "Does Not Exist"                
                writeRow = 1

            elif innline.startswith("    A (Host) Record . . . :"):
                RecType = innline[28:]
                writeRow = 2

            elif innline.startswith("    SRV Record  . . . . . :"):
                RecType = innline[28:]
                writeRow = 3

            elif innline.startswith("    PTR Record  . . . . . :"):
                RecType = innline[28:]
                writeRow = 4


            if writeRow > 0:
                outfile.write("<tr><td width=25%>" + DNSRecName.strip() + "</td>\n")

                if writeRow == 1:
                    outfile.write("<td width=25%>" + RecName.strip() + "</td>\n")
                    outfile.write("<td width=25%>" + RecType.strip() + "</td>\n")
                    outfile.write("<td width=25%> NA </td></tr>\n")
                elif writeRow == 2:
                    outfile.write("<td width=25%> <A href=https://www.virustotal.com/#/search/" + RecName.strip().lower() + ">" + RecName.strip() + "</a> </td>\n")
                    outfile.write("<td width=25%> <A href=https://www.virustotal.com/#/search/" + RecType.strip() + ">" + RecType.strip() + "</a> </td>\n")
                    outfile.write("<td width=25%> A (Host) </td></tr>\n")
                    # Write out IP Address for Bulk Lookup 
                    ipsfileall.write(RecType.strip() + "\n")
                elif writeRow == 3:
                    outfile.write("<td width=25%>" + RecName.strip() + "</td>\n")
                    outfile.write("<td width=25%>" + RecType.strip() + "</td>\n")
                    outfile.write("<td width=25%> SRV Record </td></tr>\n")
                elif writeRow == 4:
                    outfile.write("<td width=25%> <A href=https://www.virustotal.com/#/search/" + RecName.strip().lower() + ">" + RecName.strip() + "</a> </td>\n")
                    outfile.write("<td width=25%> <A href=https://www.virustotal.com/#/search/" + RecType.strip() + ">" + RecType.strip() + "</a> </td>\n")
                    outfile.write("<td width=25%> PTR Record </td></tr>\n")
                else:
                    outfile.write("<td width=25%>" + RecName.strip() + "</td>\n")
                    outfile.write("<td width=25%>" + RecType.strip() + "</td>\n")
                    outfile.write("<td width=25%> Unknown </td></tr>\n")

                RecName = ""                
                RecType = ""                
                writeRow = 0              

            LastRec = innline.strip()

        outfile.write("</table>\n")
        innfile.close()
    else:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")


    ###########################################################################
    # Write Out Recycle Bin data ($I Files)                                   #
    ###########################################################################
    print("[+] Generating Recycle Bin ($Recycle.Bin) Information...")
    outfile.write("<a name=RBin></a>\n<hr>\n<H2>Recycle Bin ($Recycle.Bin) Information</H2>\n")

    reccount = 0
    filname = "RBin.dat"

    if os.path.isfile(filname):
        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed the Recycle Bin\n")
        outfile.write("($Recycle.Bin $I entries). This information was parsed using Eric Zimmerman's\n")
        outfile.write("RBCmd.exe utility.  This utility provides you with basic information about\n")
        outfile.write("files that were found in the endpoint Recycle Bin (Deleted).  This can be perfectly\n")
        outfile.write("normal activity, or can indicate that an actor deleted files to hide their activity.\n")
        outfile.write("Please note: Some actors have been known to hide malware in the Recycle Bin.</font></i></p>\n")

        outfile.write("<table border=1 cellpadding=5 width=100%>\n")

        innfile = open(filname, encoding='utf8', errors="replace")
        for innline in innfile:
            if innline.startswith("Source file: "):
                outfile.write("<tr><td style=\"text-align: left\">\n")
                outfile.write("<b>" + innline.strip() + "</b><br>\n")
                reccount = reccount + 1

            elif innline.startswith("Version: "):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("File size: "):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("File name: "):
                outfile.write(innline.strip() + "<br>\n")

            elif innline.startswith("Deleted on:"):
                outfile.write(innline.strip() + "</td></tr>\n")

        outfile.write(innline.strip() + "</table>\n")
        innfile.close()
        os.remove(filname)

        if reccount < 1:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

    else:
        outfile.write("<p><i><font color=firebrick>AChoir was not able to parse\n")
        outfile.write("the endpoint Recycle Bin information.</font></i></p>\n")
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")



    ###########################################################################
    # Write Uniq IP and Hash Files                                            #
    ###########################################################################
    ipsfileall.close() 
    hshfileall.close() 

    print("[+] De-Duplicating Bulk IP Addresses...")

    outfile.write("<a name=BulkIPs></a>\n<hr>\n<H2>Bulk IP Address Data</H2>\n")
    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed and de-duplicated \n")
    outfile.write("information about IP Addresses it Identified. These can be bulk checked using your favorite \n")
    outfile.write("Threat Intel tools to determine if any of the IP addresses on this machine are \n")
    outfile.write("known to be malicious. </font></i></p>\n")

    reccount = 0
    ipsset = set()
    with open(ipsnameall) as ipsfileall:
        for ipsline in ipsfileall:
            if ipsline != "\n" and ipsline != "0.0.0.0\n" and ipsline != "::\n" and ipsline not in ipsset:
                outfile.write(ipsline + "<br>")
                ipsset.add(ipsline)
                reccount = reccount + 1

    if reccount < 1:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
    else:
        outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")



    print("[+] De-Duplicating Bulk Hashes...")

    outfile.write("<a name=BulkHash></a>\n<hr>\n<H2>Bulk File Hash Data</H2>\n")
    outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed and de-duplicated \n")
    outfile.write("information about Executable File Hashes it Identified. These can be bulk checked \n")
    outfile.write("using your favorite Threat Intel tools to determine if any of the File Hashes on \n")
    outfile.write("this machine are known to be malicious. </font></i></p>\n")

    reccount = 0
    hshset = set()
    with open(hshnameall) as hshfileall:
        for hshline in hshfileall:
            if hshline != "\n" and hshline != "MD5\n" and hshline not in hshset:
                outfile.write(hshline + "<br>")
                hshset.add(hshline)
                reccount = reccount + 1

    if reccount < 1:
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
    else:
        outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")


    ###########################################################################
    #Write HTML Trailer Data                                                  #
    ###########################################################################
    outfile.write("<hr><h1><Center> * * * End Report * * * </Center></h1>\n")
    outfile.write("</body></html>\n")
    outfile.close() 

    print("[+] AChoir Report Processing Complete!\n")



if __name__ == "__main__":
    main()
