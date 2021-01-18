#!/usr/bin/env python
####################################################################### 
# Version: beta v0.96 (Python 3.x)                                    #
# Author.: David Porco                                                #
# Release: 01/17/2021                                                 #
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
#   v0.92 - Add Indicators - Hashes / IP / Domain for bulk checking   #
#         - Add Callapsible Sectionto make reading easier             #
#   v0.93 - RegRipper 2.8 No Longer available - Use v3.0              #
#           replace winnt_cv plugin with source_os plugin             #
#   v0.94 - Minor modifications to work with AChoirX                  #
#   v0.95 - Add Configuration File (Select Report Sections to Run)    #
#   v0.96 - Add some error correction if Source files are missing     #
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
parser.add_argument("-c", dest="cfgname", default="AChReport.cfg", 
                  help="AChoir Report Configuration File")
args = parser.parse_args()


###########################################################################
# Where are the Artifacts, What id the Output File Name
###########################################################################
cfgname = str(args.cfgname)
dirname = str(args.dirname)
dirleft, diright = os.path.split(dirname)
htmname = diright + ".htm"
ipsnameall = "AllIps.txt"
domnameall = "AllDoms.txt"
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
    # Checking for RegRipper Plugins (They have to be in the working subdir)  #
    ###########################################################################
    print("[+] Checking Software Dependencies...")
    if os.path.isfile(".\plugins\compname.pl"):
        print("[+] AChReport Regripper Plugin directory Found!")
    else:
        print("[*] Copying Regripper Plugins From AChoir Install...")
        returned_value = os.system("mkdir plugins")
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper3.0-master\\plugins\\compname.pl .\\plugins\compname.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper3.0-master\\plugins\\shellfolders.pl .\\plugins\shellfolders.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper3.0-master\\plugins\\userassist.pl .\\plugins\\userassist.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper3.0-master\\plugins\\source_os.pl .\\plugins\source_os.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper3.0-master\\plugins\\winver.pl .\\plugins\winver.pl"
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

    if os.path.isfile(".\plugins\source_os.pl"):
        print("[+] Regripper Plugin Found: source_os.pl")
    else:
        print("[!] Regripper Plugin NOT Found: source_os.pl")
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
    # Fell Through - Look for Config File                                     #
    ###########################################################################
    RunAllAll = RunSmlDel = RunMedDel = RunLrgDel = RunLrgAct = RunTmpAct = RunTmpDel = 0
    RunSucRDP = RunFaiLgn = RunFBrArc = RunFBrHst = RunIBrHst = RunPrfHst = RunIPCons = 0
    RunUsrAst = RunAutoRn = RunServic = RunScTask = RunDNSInf = RunRcyBin = RunIndIPs = 0
    RunIndHsh = RunIndDom = 0
    SrcMFT = SrcRBin = SrcEvtx = SrcPrf = SrcNTUsr = SrcSysReg = SrcSysTxt = 0

    print("[+] Checking For Config File...")
    if os.path.isfile(cfgname):
        print("[+] Config File Found (" + cfgname + "), Now Parsing Config Options...")

        cfgfile = open(cfgname, encoding='utf8', errors="replace")

        for cfgline in cfgfile:
            if cfgline.startswith("*"):
                pass

            if cfgline.startswith("Run:AllAll"):
                SrcMFT = 1
                RunAllAll = 1

            elif cfgline.startswith("Run:SmallDeleted"):
                SrcMFT = 1
                RunSmlDel = 1

            elif cfgline.startswith("Run:MediumDeleted"):
                SrcMFT = 1
                RunMedDel = 1

            elif cfgline.startswith("Run:LargeDeleted"):
                SrcMFT = 1
                RunLrgDel = 1

            elif cfgline.startswith("Run:LargeActive"):
                SrcMFT = 1
                RunLrgAct = 1

            elif cfgline.startswith("Run:TempActiveExe"):
                SrcMFT = 1
                RunTmpAct = 1

            elif cfgline.startswith("Run:TempDeletedExe"):
                SrcMFT = 1
                RunTmpDel = 1

            elif cfgline.startswith("Run:SuccessRDP"):
                SrcEvtx = 1
                RunSucRDP = 1

            elif cfgline.startswith("Run:FailedLogins"):
                SrcEvtx = 1
                RunFaiLgn = 1

            elif cfgline.startswith("Run:FileBrowseArchive"):
                RunFBrArc = 1

            elif cfgline.startswith("Run:FileBrowseHistory"):
                RunFBrHst = 1

            elif cfgline.startswith("Run:InetBrowseHistory"):
                RunIBrHst = 1

            elif cfgline.startswith("Run:PrefetchHistory"):
                SrcPrf = 1
                RunPrfHst = 1

            elif cfgline.startswith("Run:IPConnectionInfo"):
                RunIPCons = 1

            elif cfgline.startswith("Run:UserAssist"):
                SrcNTUsr = 1
                RunUsrAst = 1

            elif cfgline.startswith("Run:AutoRuns"):
                RunAutoRn = 1

            elif cfgline.startswith("Run:Services"):
                SrcEvtx = 1
                RunServic = 1

            elif cfgline.startswith("Run:ScheduledTasks"):
                SrcEvtx = 1
                RunScTask = 1

            elif cfgline.startswith("Run:DNSCache"):
                RunDNSInf = 1

            elif cfgline.startswith("Run:RecycleBin"):
                SrcRBin = 1
                RunRcyBin = 1

            elif cfgline.startswith("Run:IndicatorsIP"):
                RunIndIPs = 1

            elif cfgline.startswith("Run:IndicatorsHash"):
                RunIndHsh = 1

            elif cfgline.startswith("Run:IndicatorsDomain"):
                RunIndDom = 1

    else:
        print("[!] Config File Not Found (" + cfgname + "), Default Setting Configured.")
        RunAllAll = 1



    ###########################################################################
    # Fell Through, Now Process the files and extract data for report
    ###########################################################################
    print("[+] Now Building Additional Data from Sources...")
    print("[+] Generating System Information from Registry...")
    
    regName = dirname + "\Reg\SOFTWARE"
    if os.path.isfile(regName):
        SrcSysReg = 1
    
        exeName = dirleft + "\\RRV\\RegRipper3.0-master\\rip.exe"
        if os.path.isfile(exeName):
            cmdexec = dirleft + "\\RRV\\RegRipper3.0-master\\rip.exe -p source_os -r " + dirname + "\Reg\SOFTWARE > SysInfo.dat"
            returned_value = os.system(cmdexec)

            cmdexec = dirleft + "\\RRV\\RegRipper3.0-master\\rip.exe -p winver -r " + dirname + "\Reg\SOFTWARE >> SysInfo.dat"
            returned_value = os.system(cmdexec)

            SrcSysTxt = 1
        else:
            print("[!] RegRipper Not Found...")
            SrcSysReg = 0

    else:
        print("[!] SOFTWARE Registry Not Found...")
        SrcSysReg = 0


    regName = dirname + "\Reg\SYSTEM"
    if os.path.isfile(regName):
        SrcSysReg = 1

        exeName = dirleft + "\\RRV\\RegRipper3.0-master\\rip.exe"
        if os.path.isfile(exeName):
            cmdexec = dirleft + "\\RRV\\RegRipper3.0-master\\rip.exe -p compname -r " + dirname + "\Reg\SYSTEM >> SysInfo.dat"
            returned_value = os.system(cmdexec)

            SrcSysTxt = 1
        else:
            print("[!] RegRipper Not Found...")
            SrcSysReg = 0
    else:
        print("[!] SYSTEM Registry Not Found...")
        SrcSysReg = 0


    if RunAllAll == 1 or SrcPrf == 1:
        print("[+] Generating Prefetch Data...")
        exeName = dirleft + "\\SYS\\WinPrefetchView.exe"

        if os.path.isfile(exeName):
            cmdexec = dirleft + "\\SYS\\WinPrefetchView.exe /folder " + dirname + "\prf /scomma WinPrefetchview.csv"
            returned_value = os.system(cmdexec)
        else:
            print("[!] WinPrefetchView Not Found...")
            SrcPrf = 0
    else:
        print("[+] Bypassing Prefetch Data...")


    if RunAllAll == 1 or SrcNTUsr == 1:
      print("[+] Generating User Assist for Multiple User Profiles...")
      reccount = 0
      curdir = dirname + "\\reg"

      for root, dirs, files in os.walk(curdir):
          for fname in files:
              curfile = os.path.join(root, fname)
              if fname.startswith("NTUSER."):
                  curouput = "shlasst." + str(reccount)
                  cmdexec = dirleft + "\\RRV\\RegRipper3.0-master\\rip.exe -p shellfolders -r " + curfile + " > " + curouput
                  returned_value = os.system(cmdexec)

                  cmdexec = dirleft + "\\RRV\\RegRipper3.0-master\\rip.exe -p userassist -r " + curfile + " >> " + curouput
                  returned_value = os.system(cmdexec)

                  reccount = reccount + 1
    else:
      print("[+] ByPassing User Assist for Multiple User Profiles...")


    if RunAllAll == 1 or SrcEvtx == 1:
        print("[+] Generating Event Log Entries...")
        print("[+] Generating RDP Success and Failure...")

        EvtName = dirname + "\\evt\\sys32\\Security.evtx"
        if os.path.isfile(EvtName):
            cmdexec = "copy " + EvtName
            returned_value = os.system(cmdexec)
        else:
            EvtName = dirname + "\\evt\\nativ\\Security.evtx"
            if os.path.isfile(EvtName):
                cmdexec = "copy " + EvtName
                returned_value = os.system(cmdexec)
            else:
                SrcEvtx = 0
                print("[!] Security Event Log Not Found...")


        print("[+] Generating Service Installed (7045) Messages...")

        EvtName = dirname + "\\evt\\sys32\\System.evtx"
        if os.path.isfile(EvtName):
            cmdexec = "copy " + EvtName
            returned_value = os.system(cmdexec)
        else:
            EvtName = dirname + "\\evt\\nativ\\System.evtx"
            if os.path.isfile(EvtName):
                cmdexec = "copy " + EvtName
                returned_value = os.system(cmdexec)
            else:
                SrcEvtx = 0
                print("[!] System Event Log Not Found...")


        ###########################################################################
        # Use Wevtutil to "export" the event log.  This has the effect of         #
        #  clearing any errors - It makes the Event Log more Stable.              #
        ###########################################################################
        if SrcEvtx == 1:
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
        else:
            print("[!] Error Parsing Event Log Entries...")
    else:
        print("[+] Bypassing Event Log Entries...")



    ###########################################################################
    # Parse the Recycle Bin                                                   #
    ###########################################################################
    if RunAllAll == 1 or SrcRBin == 1:
        print("[+] Parsing Recycle Bin...")

        exeName = dirleft + "\\SYS\\RBCmd.exe"
        if os.path.isfile(exeName):
            cmdexec = dirleft + "\\SYS\\RBCmd.exe -d " + dirname + "\\RBin >> RBin.dat" 
            returned_value = os.system(cmdexec)
        else:
            print("[!] RBCmd Recycle Bin Parser Not Found...")
            SrcRBin = 0
    else:
        print("[+] Bypass Parsing Recycle Bin...")


    ###########################################################################
    # Parse the $MFT                                                          #
    ###########################################################################
    if RunAllAll == 1 or SrcMFT == 1:
        print("[+] Parsing $MFT...")
        MFTFound = 0

        exeName = dirleft + "\\DSK\\MFTDump.exe"
        if os.path.isfile(exeName):
            MFTName = dirname + "\\RawData\\$MFT"
            if os.path.isfile(MFTName):
                cmdexec = dirleft + "\\DSK\\MFTDump.exe /l /d /v --output=MFTDump.csv " + MFTName 
                returned_value = os.system(cmdexec)
                MFTFound = 1

            MFTName = dirname + "\\RawData\\MFT-C"
            if os.path.isfile(MFTName):
                cmdexec = dirleft + "\\DSK\\MFTDump.exe /l /d /v --output=MFTDump.csv " + MFTName
                returned_value = os.system(cmdexec)
                MFTFound = 1

            if MFTFound == 0:
                print("[!] Error Parsing MFT (No MFT Found)...")
                SrcMFT = 0
        else:
            print("[+] MFTDump Parser Not Found...")
            SrcMFT = 0
    else:
        print("[+] Bypass Parsing $MFT...")



    ###########################################################################
    # Clean Up.                                                               #
    ###########################################################################
    if RunAllAll == 1 or SrcEvtx == 1:
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
    domfileall = open(domnameall, "w", encoding='utf8', errors="replace")
    hshfileall = open(hshnameall, "w", encoding='utf8', errors="replace")
    ###########################################################################
    # Write HTML Headers & CSS                                                #
    # RESPONSTABLE 2.0 by jordyvanraaij                                       #
    # CSS Expand / Collapse Code From: CodePen                                #
    # By: Joshua Azemoh                                                       #
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

    outfile.write(".collapse {display: none;}\n")
    outfile.write(".collapse + label {cursor: pointer; display: block; font-weight: bold; line-height: 21px; margin-bottom: 5px;}\n")
    outfile.write(".collapse + label + div {display: none; margin-bottom: 10px;}\n")
    outfile.write(".collapse:checked + label + div {display: block;}\n")
    outfile.write(".collapse + label:before {background-color: #4F5150; -webkit-border-radius: 10px; -moz-border-radius: 10px;\n")
    outfile.write(" border-radius: 10px; color: #FFFFFF; content: \"+\"; display: block; float: left; font-weight: bold; height: 20px;\n")
    outfile.write(" line-height: 20px; margin-right: 5px; text-align: center; width: 20px;}\n")
    outfile.write(".collapse:checked + label:before {content: \"\\2212\";}\n")

    outfile.write("</style><title>AChoir Endpoint Report(" + diright + ")</title></head>\n")
    outfile.write("<body>\n")
    outfile.write("<p><Center>\n")
    outfile.write("<a name=Top></a>\n<H1>AChoir Endpoint Report</H1>\n")
    outfile.write("(" + diright + ")<br>\n")

    outfile.write("<table border=1 cellpadding=3 width=100%>\n")
    outfile.write("<tr><td width=6%> <a href=#Top>Top</a> </td>\n")

    if RunAllAll == 1 or RunSmlDel == 1:
        outfile.write("<td width=7%> <a href=#Deleted>Deleted</a> </td>\n")

    if RunAllAll == 1 or RunLrgAct == 1:
        outfile.write("<td width=7%> <a href=#Active>Active</a> </td>\n")

    if RunAllAll == 1 or RunTmpAct == 1:
        outfile.write("<td width=6%> <a href=#ExeTemp>Temp</a> </td>\n")

    if RunAllAll == 1 or RunFaiLgn == 1:
        outfile.write("<td width=8%> <a href=#Logins>FailLogn</a> </th>\n")

    if RunAllAll == 1 or RunSucRDP == 1:
        outfile.write("<td width=7%> <a href=#RDP>RDP</a> </th>\n")

    if RunAllAll == 1 or RunFBrArc == 1:
        outfile.write("<td width=7%> <a href=#Browser>Browser</a> </td>\n")

    if RunAllAll == 1 or RunPrfHst == 1:
        outfile.write("<td width=8%> <a href=#Prefetch>Prefetch</a> </td>\n")

    if RunAllAll == 1 or RunUsrAst == 1:
        outfile.write("<td width=8%> <a href=#UserAssist>UsrAssist</a> </td>\n")

    if RunAllAll == 1 or RunIPCons == 1:
        outfile.write("<td width=6%> <a href=#IPConn>IPCon</a> </td>\n")

    if RunAllAll == 1 or RunDNSInf == 1:
        outfile.write("<td width=6%> <a href=#DNSCache> DNS </a> </td>\n")

    if RunAllAll == 1 or RunAutoRn == 1:
        outfile.write("<td width=7%> <a href=#AutoRun>AutoRun</a> </td>\n")

    if RunAllAll == 1 or RunServic == 1:
        outfile.write("<td width=6%> <a href=#InstSVC>EVTx</a> </td>\n")

    if RunAllAll == 1 or RunRcyBin == 1:
        outfile.write("<td width=6%> <a href=#RBin>RBin</a> </td>\n")

    if RunAllAll == 1 or RunIndIPs == 1:
        outfile.write("<td width=5%> <a href=#BulkIPs>IOC</a> </td></tr>\n")

    outfile.write("</table>\n")
    outfile.write("</Center></p>\n")

    # Write Basic Data
    if SrcSysTxt == 1:
        print("[+] Generating Basic Endpoint Information...")

        outfile.write("<input class=\"collapse\" id=\"id01\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id01\">\n")
        outfile.write("<H2>Basic Endpoint Information</H2>\n")
        outfile.write("</label><div><hr>\n")

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

                elif innline.startswith("ReleaseID"):
                    outfile.write(innline.strip() + "<br>\n")

                elif innline.startswith("RegisteredOwner"):
                    outfile.write(innline.strip() + "<br>\n")

                elif innline.startswith("InstallDate "):
                    outfile.write(innline.strip() + "<br>\n")

            innfile.close()

        else:
            outfile.write("<p><i><font color=firebrick>AChoir was not able to parse standard information about\n")
            outfile.write("the endpoint.</font></i></p>\n")
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

        ###########################################################################
        # Clean Up.                                                               #
        ###########################################################################
        os.remove(dedname)
    else:
        print("[!] Error Generating Basic Endpoint Information...")


    ###########################################################################
    # Write Logon Data                                                        #
    ###########################################################################
    print("[+] Generating Logon Information...")
    outfile.write("<input class=\"collapse\" id=\"id02\" type=\"checkbox\" checked>\n")
    outfile.write("<label for=\"id02\">\n")
    outfile.write("<H2>Logon Information</H2>\n")
    outfile.write("</label><div><hr>\n")

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
        print("[!] Error Generating Logon Information...")
        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")

    outfile.write("</div>\n")


    ###########################################################################
    # Small Deleted Files ($MFT) - (Use Python CSV Reader Module)             #
    ###########################################################################
    if (RunAllAll == 1 or RunSmlDel == 1) and SrcMFT == 1:
        print("[+] Generating Small Deleted Files $MFT Information...")
        filname = "MFTDump.csv"

        if os.path.isfile(filname):
            reccount = 0
            outfile.write("<a name=Deleted></a>\n")
            outfile.write("<input class=\"collapse\" id=\"id03\" type=\"checkbox\" checked>\n")
            outfile.write("<label for=\"id03\">\n")
            outfile.write("<H2>Small Deleted Files (Between 1 Meg and 10 meg)</H2>\n")
            outfile.write("</label><div><hr>\n")

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

        outfile.write("</div>\n")
    else:
        print("[+] Bypassing Small Deleted Files $MFT Information...")



    ###########################################################################
    # Medium Deleted Files ($MFT) - (Use Python CSV Reader Module)            #
    ###########################################################################
    if (RunAllAll == 1 or RunMedDel == 1) and SrcMFT == 1:
        print("[+] Generating Medium Deleted Files $MFT Information...")
        filname = "MFTDump.csv"

        if os.path.isfile(filname):
            reccount = 0
            outfile.write("<input class=\"collapse\" id=\"id04\" type=\"checkbox\" checked>\n")
            outfile.write("<label for=\"id04\">\n")
            outfile.write("<H2>Medium Deleted Files (Between 10 Meg and 100 meg)</H2>\n")
            outfile.write("</label><div><hr>\n")

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

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing Medium Deleted Files $MFT Information...")


    ###########################################################################
    # Large Deleted Files ($MFT) - (Use Python CSV Reader Module)             #
    ###########################################################################
    if (RunAllAll == 1 or RunLrgDel == 1) and SrcMFT == 1:
        print("[+] Generating Large Deleted Files $MFT Information...")
        filname = "MFTDump.csv"

        if os.path.isfile(filname):
            reccount = 0
            outfile.write("<input class=\"collapse\" id=\"id05\" type=\"checkbox\" checked>\n")
            outfile.write("<label for=\"id05\">\n")
            outfile.write("<H2>Large Deleted Files (Over 100 Meg)</H2>\n")
            outfile.write("</label><div><hr>\n")

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

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing Large Deleted Files $MFT Information...")



    ###########################################################################
    # Large Active Files ($MFT) - (Use Python CSV Reader Module)              #
    ###########################################################################
    if (RunAllAll == 1 or RunLrgAct == 1) and SrcMFT == 1:
        print("[+] Generating Large Active Files $MFT Information...")
        filname = "MFTDump.csv"

        if os.path.isfile(filname):
            reccount = 0
            outfile.write("<a name=Active></a>\n")
            outfile.write("<input class=\"collapse\" id=\"id06\" type=\"checkbox\" checked>\n")
            outfile.write("<label for=\"id06\">\n")
            outfile.write("<H2>Large Active Files (Over 100 Meg)</H2>\n")
            outfile.write("</label><div><hr>\n")

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

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing Large Active Files $MFT Information...")



    ###########################################################################
    # Active Exe Files in Temp Directories - (Use Python CSV Reader Module)   #
    ###########################################################################
    if (RunAllAll == 1 or RunTmpAct == 1) and SrcMFT == 1:
        print("[+] Generating Active Files in Temp Directories...")
        filname = "MFTDump.csv"

        if os.path.isfile(filname):
            reccount = 0
            outfile.write("<a name=ExeTemp></a>\n")
            outfile.write("<input class=\"collapse\" id=\"id07\" type=\"checkbox\" checked>\n")
            outfile.write("<label for=\"id07\">\n")
            outfile.write("<H2>Active Executable Files in Temp Directories</H2>\n")
            outfile.write("</label><div><hr>\n")

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

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing Active Files in Temp Directories...")



    ###########################################################################
    # Deleted Exe Files in Temp Directories - (Use Python CSV Reader Module)  #
    ###########################################################################
    if (RunAllAll == 1 or RunTmpDel == 1) and SrcMFT == 1:
        print("[+] Generating Deleted Files in Temp Directories...")
        filname = "MFTDump.csv"

        if os.path.isfile(filname):
            reccount = 0
            outfile.write("<a name=DelExeTemp></a>\n")
            outfile.write("<input class=\"collapse\" id=\"id08\" type=\"checkbox\" checked>\n")
            outfile.write("<label for=\"id08\">\n")
            outfile.write("<H2>Deleted Executable Files in Temp Directories</H2>\n")
            outfile.write("</label><div><hr>\n")

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

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing Deleted Files in Temp Directories...")



    ###########################################################################
    # Clean Up.                                                               #
    ###########################################################################
    if RunAllAll == 1 or SrcMFT == 1:
        os.remove("MFTDump.csv")
        os.remove("MFTDump.log")


    ###########################################################################
    # Write Success RDP Logins (Use Python CSV Reader Module)                 #
    ###########################################################################
    if (RunAllAll == 1 or RunSucRDP == 1) and SrcEvtx == 1:
        print("[+] Generating Sucessful RDP Login Information...")
        outfile.write("<a name=RDP></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id09\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id09\">\n")
        outfile.write("<H2>Successful RDP Logins</H2>\n")
        outfile.write("</label><div><hr>\n")

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

                        # Write out IP Address for Bulk Lookup 
                        ipsfileall.write(csvrow[5] + "\n")

                        reccount = reccount + 1

            outfile.write("</table>\n")
            os.remove(filname)

            if reccount < 2:
                print("[!] No RDP Logins Found...")
                outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
            else:
                outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

        else:
            print("[!] No RDP Login Information Found...")
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing Sucessful RDP Login Information...")



    ###########################################################################
    # Write Failed Logins (Use Python CSV Reader Module)                      #
    ###########################################################################
    if (RunAllAll == 1 or RunFaiLgn == 1) and SrcEvtx == 1:
        print("[+] Generating Failed Logins Information...")
        outfile.write("<a name=Logins></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id10\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id10\">\n")
        outfile.write("<H2>Failed Logins</H2>\n")
        outfile.write("</label><div><hr>\n")

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

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing Failed Logins Information...")



    ###########################################################################
    # Write File Browser Data/Archive types  (Use Python CSV Reader Module)   #
    ###########################################################################
    if RunAllAll == 1 or RunFBrArc == 1:
        print("[+] Generating File History access to Archive Files...")
        outfile.write("<a name=Browser></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id11\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id11\">\n")
        outfile.write("<H2>File Browse (Archive files) History Information</H2>\n")
        outfile.write("</label><div><hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
        outfile.write("Accessed Files that have an Archive File Type (i.e. .Arc, .Rar, .Zip, .Tar, .7z, .Cab)\n")
        outfile.write("These Entries indicate that someone (or multiple people) archived data into a compressed\n")
        outfile.write("file format.  This is often used by hostile actors to gather up data for future (or past)\n")
        outfile.write("exfiltration.  Focus on any and all files that indicate data was archived, especially \n")
        outfile.write("in Temporary Directories.</font></i></p>\n")

        reccount = 0
        filname = dirname + "\\brw\\BrowseHist.csv"

        if os.path.isfile(filname):
            outfile.write("<table border=1 cellpadding=5 width=100%>\n")
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
            print("[!] Bypassing File History access to Archive Files (No Input Data) ...")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing File History access to Archive Files...")



    ###########################################################################
    # Write Web Browser Data (Use Python CSV Reader Module)                   #
    ###########################################################################
    if RunAllAll == 1 or RunFBrHst == 1:
        print("[+] Generating File and Web Browser Information...")
        outfile.write("<a name=BrwFilHist></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id12\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id12\">\n")
        outfile.write("<H2>File Browse History Information</H2>\n")
        outfile.write("</label><div><hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
        outfile.write("accessed files. These files were accessed on the machine and may indicate hostile\n")
        outfile.write("program installation or execution, as well as access to sensitive or hostile files.\n")
        outfile.write("This can also be completely normal activity.  Review the files accessed for anything \n")
        outfile.write("that appears to be suspicious, especially programs that that were run, files that were\n")
        outfile.write("accessed or archive files created.</font></i></p>\n")

        reccount = 0
        filname = dirname + "\\brw\\BrowseHist.csv"

        if os.path.isfile(filname):
            outfile.write("<table border=1 cellpadding=5 width=100%>\n")
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
            print("[!] Bypassing File History (No Input Data) ...")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing File and Web Browser Information...")



    ###########################################################################
    # Write Web Browser Data (Use Python CSV Reader Module)                   #
    ###########################################################################
    if RunAllAll == 1 or RunIBrHst == 1:
        print("[+] Generating Web Browser Internet History Information...")
        outfile.write("<a name=BrwHist></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id13\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id13\">\n")
        outfile.write("<H2>Internet Browse History Information</H2>\n")
        outfile.write("</label><div><hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
        outfile.write("Web Browsing History. Web Browsing History can show Suspicious URLs that were \n")
        outfile.write("visited on this machine.  Pay special attention to the URL strings. \n")
        outfile.write("This can also be completely normal activity.  Review the URLs for anything \n")
        outfile.write("that appears to be suspicious, especially unusual URL string that might \n")
        outfile.write("indicate malicious C2 activity or strings that may indicate access to Phishing sites.</font></i></p>\n")

        reccount = 0
        filname = dirname + "\\brw\\BrowseHist.csv"

        if os.path.isfile(filname):
            outfile.write("<table border=1 cellpadding=5 width=100%>\n")
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

                            # Write out Domain for Bulk Lookup 
                            url_split = csvrow[0].split('/')
                            if len(url_split) > 2:
                                domfileall.write(url_split[2] + "\n")

                            reccount = reccount + 1

            outfile.write("</table>\n")

            if reccount < 2:
                outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
            else:
               outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

        else:
            print("[!] Bypassing Web Browsing History (No Input Data) ...")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing Web Browser Internet History Information...")



    ###########################################################################
    # Write Prefetch Data (Use Python CSV Reader Module)                      #
    ###########################################################################
    if (RunAllAll == 1 or RunPrfHst == 1) and SrcPrf == 1:
        print("[+] Generating Prefetch Information...")
        outfile.write("<a name=Prefetch></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id14\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id14\">\n")
        outfile.write("<H2>Prefetch History Information</H2>\n")
        outfile.write("</label><div><hr>\n")

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
            print("[!] Bypassing Prefetch Information (No Input Data)...")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing Prefetch Information...")



    ###########################################################################
    # Write Connection Data (Use Python CSV Reader Module)                    #
    ###########################################################################
    if RunAllAll == 1 or RunIPCons == 1:
        print("[+] Generating IP Connections Information...")
        outfile.write("<a name=IPConn></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id15\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id15\">\n")
        outfile.write("<H2>IP Connections Information</H2>\n")
        outfile.write("</label><div><hr>\n")

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
            print("[!] Bypassing IP Connections Information (No Input Data) ...")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")


    else:
        print("[+] Bypassing IP Connections Information...")



    ###########################################################################
    # Write User Assist Data (Use Python CSV Reader Module)                   #
    ###########################################################################
    if RunAllAll == 1 or RunUsrAst == 1:
        print("[+] Generating User Assist Information...")
        outfile.write("<a name=UserAssist></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id16\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id16\">\n")
        outfile.write("<H2>HKCU User Assist Information</H2>\n")
        outfile.write("</label><div><hr>\n")

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
            print("[!] Bypassing User Assist Information (No Input Data)...")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")



        ###########################################################################
        # Write Other User Assist Data (Gathered from RegRipper Earlier)          #
        ###########################################################################
        outfile.write("<a name=MoreUsrAst></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id17\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id17\">\n")
        outfile.write("<H2>Other User Assist Information</H2>\n")
        outfile.write("</label><div><hr>\n")

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
            print("[!] No User Assist Information (No Input Data)...")
            outfile.write("<p><b><font color = red> No User Assist (NTUSER.DAT) Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing User Assist Information...")



    ###########################################################################
    # Write AutoRunsc Data (Run and RunOnce) (Use Python CSV Reader Module)   #
    ###########################################################################
    if RunAllAll == 1 or RunAutoRn == 1:
        print("[+] Generating AutoRuns Information...")

        outfile.write("<a name=AutoRun></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id18\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id18\">\n")
        outfile.write("<H2>AutoRun Information (Run And RunOnce)</H2>\n")
        outfile.write("</label><div><hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
        outfile.write("Run and RunOnce Registry Keys.  These are THE MOST common Registry keys where malicious \n")
        outfile.write("programs(MalWare) can reside.  These Registry keys allow malware to PERSIST across \n")
        outfile.write("system reboots.  These Registry Keys can also be used for legitimate software and  \n")
        outfile.write("utilities.  Some good indicators that Run Keys are being used maliciously is if they \n")
        outfile.write("run programs that have random file names, or are installed/run from Temp Directories. \n")
        outfile.write("Focus on both the file names, and where the programs are located to determine if they \n")
        outfile.write("look suspicious.</font></i></p>\n")

        reccount = 0
        filname = dirname + "\\arn\\AutoRun.dat"

        if os.path.isfile(filname):
            outfile.write("<table border=1 cellpadding=5 width=100%>\n")
            outfile.write("<tr><th width=10%> Time </th>\n")
            outfile.write("<th width=30%> Entry Location </th>\n")
            outfile.write("<th width=10%> Entry </th>\n")
            outfile.write("<th width=30%> Image Path <hr> Launch String</th>\n")
            outfile.write("<th width=15%> MD5 </th>\n")
            outfile.write("<th width=5%> Enabled </th></tr>\n")

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
                print("[!] No Autoruns Information Found...")
                outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
            else:
                outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

        else:
            print("[!] Bypassing AutoRuns Information (No Input Data)...")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")


        ###########################################################################
        # Write AutoRunsc Data (Use Python CSV Reader Module)                     #
        ###########################################################################
        outfile.write("<a name=AllAutoRun></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id19\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id19\">\n")
        outfile.write("<H2>AutoRun Information (All)</H2>\n")
        outfile.write("</label><div><hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
        outfile.write("several AutoRun settings.  These can show several different places where malicious \n")
        outfile.write("programs(MalWare) can reside.  These settings can allow malware to PERSIST across \n")
        outfile.write("system reboots.  These settings can also be used for legitimate software and  \n")
        outfile.write("utilities.  Some good indicators that these settings are being used maliciously is if they \n")
        outfile.write("run programs that have random file names, or are installed/run from Temp Directories. \n")
        outfile.write("Focus on both the file names, and where the programs are located to determine if they \n")
        outfile.write("look suspicious.</font></i></p>\n")

        reccount = 0
        filname = dirname + "\\arn\\AutoRun.dat"

        if os.path.isfile(filname):
            outfile.write("<table border=1 cellpadding=5 width=100%>\n")
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
                print("[!] No Autoruns Information Found...")
                outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
            else:
                outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

        else:
            print("[!] Bypassing AutoRuns Information (No Input Data)...")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing AutoRuns Information...")



    ###########################################################################
    # Write 7045 Installed Services Log Entries                               #
    ###########################################################################
    if (RunAllAll == 1 or RunServic == 1) and SrcEvtx ==1:
        print("[+] Generating 7045 Installed Services Logs...")
        outfile.write("<a name=InstSvc></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id20\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id20\">\n")
        outfile.write("<H2>Installed Services</H2>\n")
        outfile.write("</label><div><hr>\n")

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
                print("[!] No  Installed Services Found...")
                outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
            else:
                outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
        else:
            print("[!] No Installed Services Found (No Input Data)...")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing 7045 Installed Services Logs...")



    ###########################################################################
    # Write 4698 New Sched Tasks Log Entries                                  #
    ###########################################################################
    if RunAllAll == 1 or RunScTask == 1:
        print("[+] Generating 4698 New Sched Tasks Logs...")
        outfile.write("<a name=NewTask></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id21\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id21\">\n")
        outfile.write("<H2>New Scheduled Tasks</H2>\n")
        outfile.write("</label><div><hr>\n")

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
            print("[!] No New Scheduled Tasks Found (No Input Data)...")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing 4698 New Sched Tasks Logs...")



    ###########################################################################
    # Write DNS Cache Data = Flat File.                                       #
    ###########################################################################
    if RunAllAll == 1 or RunDNSInf == 1:
        print("[+] Generating DNS Cache Information...")

        outfile.write("<a name=DNSCache></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id22\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id22\">\n")
        outfile.write("<H2>DNS Cache (IPConfig /displaydns)</H2>\n")
        outfile.write("</label><div><hr>\n")

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

                        # Write out Domain for Bulk Lookup 
                        domfileall.write(RecName.strip() + "\n")
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
            print("[!] No DNS Cache Data  Found (No Input Data)...")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing DNS Cache Information...")



    ###########################################################################
    # Write Out Recycle Bin data ($I Files)                                   #
    ###########################################################################
    if (RunAllAll == 1 or RunRcyBin == 1) and SrcRBin == 1:
        print("[+] Generating Recycle Bin ($Recycle.Bin) Information...")

        outfile.write("<a name=RBin></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id23\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id23\">\n")
        outfile.write("<H2>Recycle Bin ($Recycle.Bin) Information</H2>\n")
        outfile.write("</label><div><hr>\n")

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
            print("[!] No Recycle Bin Data Found (No Input Data)...")
            outfile.write("<p><i><font color=firebrick>AChoir was not able to parse\n")
            outfile.write("the endpoint Recycle Bin information.</font></i></p>\n")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing Recycle Bin ($Recycle.Bin) Information...")



    ###########################################################################
    # Write Uniq IP and Hash Files                                            #
    ###########################################################################
    ipsfileall.close() 
    domfileall.close() 
    hshfileall.close() 

    if RunAllAll == 1 or RunIndIPs == 1:
        print("[+] De-Duplicating Bulk IP Addresses...")

        outfile.write("<a name=BulkIPs></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id24\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id24\">\n")
        outfile.write("<H2>Indicators: IP Address Data</H2>\n")
        outfile.write("</label><div><hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed and de-duplicated \n")
        outfile.write("information about IP Addresses it Identified. These were found in Active Connections, \n")
        outfile.write("Resolved DNS Queries, and RDP Logins. These can be bulk checked using your favorite \n")
        outfile.write("Threat Intel tools to determine if any of the IP addresses on this machine are \n")
        outfile.write("known to be malicious. </p><p><b>Important Note: This section will ONLY report \n")
        outfile.write("Indicators found during the processing of other sections - It WILL NOT be complete \n")
        outfile.write("if you have disabled the relevant sections.</b></font></i></p>\n")

        reccount = 0
        recdupl = 0
        ipsset = set()
        with open(ipsnameall) as ipsfileall:
            for ipsline in ipsfileall:
                if ipsline != "\n" and ipsline != "0.0.0.0\n" and ipsline != "::\n" and ipsline not in ipsset:
                    outfile.write(ipsline + "<br>")
                    ipsset.add(ipsline)
                    reccount = reccount + 1
                else:
                    recdupl = recdupl + 1

        if reccount < 1:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "<br>\n")
            outfile.write("Duplicates Found: " + str(recdupl) + "</p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing Bulk IP Addresses...")



    if RunAllAll == 1 or RunIndHsh == 1:
        print("[+] De-Duplicating Bulk Hashes...")

        outfile.write("<a name=BulkHash></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id25\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id25\">\n")
        outfile.write("<H2>Indicators: File Hash Data</H2>\n")
        outfile.write("</label><div><hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed and de-duplicated \n")
        outfile.write("information about Executable File Hashes it Identified. These were found in the \n")
        outfile.write("Autorun programs for this workstation. These can be bulk checked \n")
        outfile.write("using your favorite Threat Intel tools to determine if any of the File Hashes \n")
        outfile.write("identified on this machine are known to be malicious. </p><p><b>Important \n")
        outfile.write("Note: This section will ONLY report Indicators found during the processing \n")
        outfile.write("of other sections - It WILL NOT be complete if you have disabled the relevant \n")
        outfile.write("sections.</b></font></i></p>\n")

        reccount = 0
        recdupl = 0
        hshset = set()
        with open(hshnameall) as hshfileall:
            for hshline in hshfileall:
                if hshline != "\n" and hshline != "MD5\n" and hshline not in hshset:
                    outfile.write(hshline + "<br>")
                    hshset.add(hshline)
                    reccount = reccount + 1
                else:
                    recdupl = recdupl + 1

        if reccount < 1:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "<br>\n")
            outfile.write("Duplicates Found: " + str(recdupl) + "</p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] ByPassing Bulk Hashes...")



    if RunAllAll == 1 or RunIndDom == 1:
        print("[+] De-Duplicating Bulk Domains...")

        outfile.write("<a name=BulkDoms></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id26\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id26\">\n")
        outfile.write("<H2>Indicators: Domain Data</H2>\n")
        outfile.write("</label><div><hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed and de-duplicated \n")
        outfile.write("information about Internet Domains it Identified. These were found in the \n")
        outfile.write("Browser History and DNS Cache for this workstation. These can be bulk checked \n")
        outfile.write("using your favorite Threat Intel tools to determine if any of the Domains \n")
        outfile.write("identified on this machine are known to be malicious. </p><p><b>Important \n")
        outfile.write("Note: This section will ONLY report Indicators found during the processing \n")
        outfile.write("of other sections - It WILL NOT be complete if you have disabled the relevant \n")
        outfile.write("sections.</b></font></i></p>\n")

        reccount = 0
        recdupl = 0
        domset = set()
        with open(domnameall) as domfileall:
            for domline in domfileall:
                if domline != "\n" and domline != "MD5\n" and domline not in domset:
                    outfile.write(domline + "<br>")
                    domset.add(domline)
                    reccount = reccount + 1
                else:
                    recdupl = recdupl + 1

        if reccount < 1:
            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "<br>\n")
            outfile.write("Duplicates Found: " + str(recdupl) + "</p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing Bulk Domains...")



    os.remove(ipsnameall)
    os.remove(domnameall)
    os.remove(hshnameall)



    ###########################################################################
    #Write HTML Trailer Data                                                  #
    ###########################################################################
    outfile.write("<hr><h1><Center> * * * End Report * * * </Center></h1>\n")
    outfile.write("</body></html>\n")
    outfile.close() 

    print("[+] AChoir Report Processing Complete!\n")



if __name__ == "__main__":
    main()
