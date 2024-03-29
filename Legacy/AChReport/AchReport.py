#!/usr/bin/env python
####################################################################### 
# Version: beta v0.99 (Python 3.x)                                    #
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
#   v0.97 - Add Regripper AmCache Parser                              #
#   v0.98 - Integrate F-Secure Countercept ChainSaw with AChReport    #
#   v0.99 - Pre-Cleanup Any Leftover Files                            #
#   v0.99a - Bug deleting directory when there is no Chainsaw output  #
#   v0.99b - Add DNSCache ouput from veloceraptor                     #
#   v0.99c - Add LNK Analysis and Powershell Logs                     #
#   v0.99d - Minor Bug Fixes                                          #
#   v0.99e - Add Raw XML Sched Task Parsing                           #
#   v0.99f - Add IOC Search                                           #
#   v0.99g - Shell Bags Processing using Eric Zimmerman's SBECmd      #
#   v0.99h - Make Tables Sortable, Add TZ Information                 #
#            Convert to latest version of Chainsaw                    #
####################################################################### 
import os
import sys
import csv
import time 
import argparse
import ctypes
import requests
import glob
import shutil
import datetime
from zipfile import ZipFile

parser = argparse.ArgumentParser(description="Format AChoir Output into a Report")
parser.add_argument("-d", dest="dirname", 
                  help="AChoir Extraction Directory Name")
parser.add_argument("-c", dest="cfgname", default="AChReport.cfg", 
                  help="AChoir Report Configuration File")
args = parser.parse_args()


###########################################################################
# Where are the Artifacts, What is the Output File Name
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
    # Get the local time zone - some utils use local instead of UTC           #
    ###########################################################################
    now = datetime.datetime.now()
    local_now = now.astimezone()
    local_tz = local_now.tzinfo
    local_tzname = local_tz.tzname(local_now)
    print("[+] Local Times Zone: " + local_tzname)


    ###########################################################################
    # Checking for RegRipper Plugins (They have to be in the working subdir)  #
    ###########################################################################
    print("[+] Checking Software Dependencies...")
    if os.path.isfile(".\plugins\compname.pl"):
        print("[+] AChReport Regripper Plugin directory Found!")
    else:
        print("[*] Copying Regripper Plugins From AChoir Install...")
        returned_value = os.system("mkdir plugins")
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper3.0-master\\plugins\\compname.pl .\\plugins\\compname.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper3.0-master\\plugins\\shellfolders.pl .\\plugins\\shellfolders.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper3.0-master\\plugins\\userassist.pl .\\plugins\\userassist.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper3.0-master\\plugins\\source_os.pl .\\plugins\\source_os.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper3.0-master\\plugins\\winver.pl .\\plugins\\winver.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper3.0-master\\plugins\\amcache.pl .\\plugins\\amcache.pl"
        returned_value = os.system(cmdexec)
        cmdexec = "Copy " + dirleft + "\\RRV\\RegRipper3.0-master\\plugins\\timezone.pl .\\plugins\\timezone.pl"
        returned_value = os.system(cmdexec)


    GotDepend = 1
    if os.path.isfile(".\\plugins\\compname.pl"):
        print("[+] Regripper Plugin Found: compname.pl")
    else:
        print("[!] Regripper Plugin NOT Found: compname.pl")
        GotDepend = 0

    if os.path.isfile(".\\plugins\\shellfolders.pl"):
        print("[+] Regripper Plugin Found: shellfolders.pl")
    else:
        print("[!] Regripper Plugin NOT Found: shellfolders.pl")
        GotDepend = 0

    if os.path.isfile(".\\plugins\\userassist.pl"):
        print("[+] Regripper Plugin Found: userassist.pl")
    else:
        print("[!] Regripper Plugin NOT Found: userassist.pl")
        GotDepend = 0

    if os.path.isfile(".\\plugins\\source_os.pl"):
        print("[+] Regripper Plugin Found: source_os.pl")
    else:
        print("[!] Regripper Plugin NOT Found: source_os.pl")
        GotDepend = 0

    if os.path.isfile(".\\plugins\\winver.pl"):
        print("[+] Regripper Plugin Found: winver.pl")
    else:
        print("[!] Regripper Plugin NOT Found: winver.pl")
        GotDepend = 0

    if os.path.isfile(".\\plugins\\amcache.pl"):
        print("[+] Regripper Plugin Found: amcache.pl")
    else:
        print("[!] Regripper Plugin NOT Found: amcache.pl")
        GotDepend = 0

    if os.path.isfile(".\\plugins\\timezone.pl"):
        print("[+] Regripper Plugin Found: timezone.pl")
    else:
        print("[!] Regripper Plugin NOT Found: timezone.pl")
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
    RunIndHsh = RunIndDom = RunAmCach = RunChnSaw = RunLnkPrs = RunPwsLog = RunShlBag = 0

    HasIOCs = 0

    SrcMFT = SrcRBin = SrcEvtx = SrcPrf = SrcNTUsr = SrcSysReg = SrcSysTxt = SrcAmCach = 0
    SrcAmCTxt = SrcLnkPrs = SrcPwsLog = 0

    PreIOC = " <b><font color=red>"
    PostIOC = "</font></b> "
    PreIOC2 = " <b><font color=red>"
    PostIOC2 = "</font></b> "

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

            elif cfgline.startswith("Run:AmCache"):
                SrcAmCach = 1
                RunAmCach = 1

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

            elif cfgline.startswith("Run:Chainsaw"):
                SrcEvtx = 1
                RunChnSaw = 1

            elif cfgline.startswith("Run:IndicatorsIP"):
                RunIndIPs = 1

            elif cfgline.startswith("Run:IndicatorsHash"):
                RunIndHsh = 1

            elif cfgline.startswith("Run:IndicatorsDomain"):
                RunIndDom = 1

            elif cfgline.startswith("Run:LnkParse"):
                RunLnkPrs = 1

            elif cfgline.startswith("Run:PShelLog"):
                RunPwsLog = 1

            elif cfgline.startswith("Run:ShellBags"):
                RunShlBag = 1

            elif cfgline.startswith("IOC:"):
                if HasIOCs == 0:
                    print("[+] Adding IOCs for Searching...")
                    HasIOCs = 1                
                    IOCList = []
                IOCList.append(cfgline[4:].strip().lower())

    else:
        print("[!] Config File Not Found (" + cfgname + "), Default Setting Configured.")
        RunAllAll = 1


    ###########################################################################
    # Pre-Cleanup to delete any Leftover temp files from failed runs
    ###########################################################################
    print("[+] Now Deleting old report temp files...")

    if os.path.isfile("Security.evtx"):
        os.remove("Security.evtx")
    if os.path.isfile("Security1.evtx"):
        os.remove("Security1.evtx")
    if os.path.isfile("System.evtx"):
        os.remove("System.evtx")
    if os.path.isfile("System1.evtx"):
        os.remove("System1.evtx")
    if os.path.isfile("SysInfo.dat"):
        os.remove("SysInfo.dat")
    if os.path.isfile("TZInfo.dat"):
        os.remove("TZInfo.dat")
    if os.path.isfile("MFTDump.csv"):
        os.remove("MFTDump.csv")
    if os.path.isfile("MFTDump.log"):
        os.remove("MFTDump.log")
    if os.path.isfile("RDPGood.csv"):
        os.remove("RDPGood.csv")
    if os.path.isfile("SecEvt4625.csv"):
        os.remove("SecEvt4625.csv")
    if os.path.isfile("WinPrefetchView.csv"):
        os.remove("WinPrefetchView.csv")
    if os.path.isfile("AmCache.dat"):
        os.remove("AmCache.dat")
    if os.path.isfile("SysEvt7045.csv"):
        os.remove("SysEvt7045.csv")
    if os.path.isfile("SecEvt4698.csv"):
        os.remove("SecEvt4698.csv")
    if os.path.isfile("RBin.dat"):
        os.remove("RBin.dat")
    if os.path.isfile("LNKFiles.csv"):
        os.remove("LNKFiles.csv")

    for curfile in os.listdir("."):
        if curfile.startswith("shlasst."):
            os.remove(curfile)

    if os.path.isdir(".\\ShellBags"):
        for curfile in os.listdir(".\\ShellBags"):
            os.remove(".\\ShellBags\\" + curfile)

    ChSwSubDir = ""
    for ChName in glob.glob('.\\**\account_tampering.csv', recursive=True):
        os.remove(ChName)
        if ChSwSubDir == "":
            Path_File = os.path.split(ChName)
            ChSwSubDir = Path_File[0]

    for ChName in glob.glob('.\\**\antivirus.csv', recursive=True):
        os.remove(ChName)
        if ChSwSubDir == "":
            Path_File = os.path.split(ChName)
            ChSwSubDir = Path_File[0]

    for ChName in glob.glob('.\\**\lateral_movement.csv', recursive=True):
        os.remove(ChName)
        if ChSwSubDir == "":
            Path_File = os.path.split(ChName)
            ChSwSubDir = Path_File[0]

    for ChName in glob.glob('.\\**\log_tampering.csv', recursive=True):
        os.remove(ChName)
        if ChSwSubDir == "":
            Path_File = os.path.split(ChName)
            ChSwSubDir = Path_File[0]

    for ChName in glob.glob('.\\**\sigma.csv', recursive=True):
        os.remove(ChName)
        if ChSwSubDir == "":
            Path_File = os.path.split(ChName)
            ChSwSubDir = Path_File[0]

    if ChSwSubDir != "":
        ChSwLeftOvers = ChSwSubDir + "\\**\*.csv"
        for ChName in glob.glob(ChSwLeftOvers, recursive=True):
            os.remove(ChName)
        shutil.rmtree(ChSwSubDir)


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

            cmdexec = dirleft + "\\RRV\\RegRipper3.0-master\\rip.exe -p timezone -r " + dirname + "\Reg\SYSTEM > TZInfo.dat"
            returned_value = os.system(cmdexec)

            SrcSysTxt = 1
        else:
            print("[!] RegRipper Not Found...")
            SrcSysReg = 0
    else:
        print("[!] SYSTEM Registry Not Found...")
        SrcSysReg = 0


    print("[+] Generating AmCache Information from Registry...")
    regName = dirname + "\Reg\AmCache.hve"
    if os.path.isfile(regName):
        SrcAmCach = 1

        exeName = dirleft + "\\RRV\\RegRipper3.0-master\\rip.exe"
        if os.path.isfile(exeName):
            cmdexec = dirleft + "\\RRV\\RegRipper3.0-master\\rip.exe -p amcache -r " + dirname + "\Reg\AmCache.hve > AmCache.dat"
            returned_value = os.system(cmdexec)

            SrcAmCTxt = 1
        else:
            print("[!] RegRipper Not Found...")
            SrcAmCach = 0
    else:
        print("[!] AmCache Registry Not Found...")
        SrcAmCach = 0


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
                fnameUpper = fname.upper()
                curfile = os.path.join(root, fname)

                if fnameUpper.startswith("NTUSER.") and fnameUpper.endswith(".DAT"):
                    curouput = "shlasst." + str(reccount)

                    astfile = open(curouput, "w", encoding='utf8', errors="replace")
                    astfile.write("<h2>User Registry: " + curfile + "</h2>\n")
                    astfile.close()

                    cmdexec = dirleft + "\\RRV\\RegRipper3.0-master\\rip.exe -p shellfolders -r " + curfile + " >> " + curouput
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
            cmdexec = "LogParser.exe \"Select to_utctime(Timegenerated) AS Date, EXTRACT_TOKEN(Strings, 1, '|') as Machine, EXTRACT_TOKEN(Strings, 5, '|') as LoginID, EXTRACT_TOKEN(Strings, 6, '|') as LoginMachine, EXTRACT_TOKEN(Strings, 8, '|') as LogonType, EXTRACT_TOKEN(Strings, 18, '|') as RemoteIP from Security1.evtx where eventid=4624 AND LogonType='10'\" -i:evt -o:csv -q > RDPGood.csv"
            returned_value = os.system(cmdexec)

            cmdexec = "LogParser.exe \"Select to_utctime(Timegenerated) AS Date, EXTRACT_TOKEN(Strings, 5, '|') as LoginID from Security1.evtx where eventid=4625\" -i:evt -o:csv -q > SecEvt4625.csv"
            returned_value = os.system(cmdexec)

            cmdexec = "LogParser.exe \"Select to_utctime(Timegenerated) AS Date, EXTRACT_TOKEN(strings, 0, '|') AS ServiceName, EXTRACT_TOKEN(strings, 1, '|') AS ServicePath, EXTRACT_TOKEN(strings, 4, '|') AS ServiceUser FROM System1.evtx WHERE EventID = 7045\" -i:evt -o:csv -q > SysEvt7045.csv"
            returned_value = os.system(cmdexec)

            cmdexec = "LogParser.exe \"Select to_utctime(Timegenerated) AS Date, SourceName, EventCategoryName, Message FROM Security1.evtx WHERE EventID = 4698\" -i:evt -o:csv -q > SecEvt4698.csv"
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
            cmdexec = dirleft + "\\SYS\\RBCmd.exe --dt \"yyyy-MM-dd HH:mm:ss K\" -d " + dirname + "\\RBin >> RBin.dat" 
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

    outfile.write("</style><script src=\"sortable-Ach.js\"></script>\n")
    outfile.write("<title>AChoir Endpoint Report(" + diright + ")</title></head>\n")


    outfile.write("<body>\n")
    outfile.write("<p><Center>\n")
    outfile.write("<a name=Top></a>\n<H1>AChoir Endpoint Report</H1>\n")
    outfile.write("(" + diright + ")<br>\n")

    outfile.write("<table border=1 cellpadding=3 width=100%>\n")
    outfile.write("<tr><td width=5%> <a href=#Top>Top</a> </td>\n")

    if RunAllAll == 1 or RunSmlDel == 1:
        outfile.write("<td width=5%> <a href=#Deleted>Deltd</a> </td>\n")

    if RunAllAll == 1 or RunLrgAct == 1:
        outfile.write("<td width=5%> <a href=#Active>Activ</a> </td>\n")

    if RunAllAll == 1 or RunTmpAct == 1:
        outfile.write("<td width=5%> <a href=#ExeTemp>Temp</a> </td>\n")

    if RunAllAll == 1 or RunFaiLgn == 1:
        outfile.write("<td width=5%> <a href=#Logins>FaiLgn</a> </th>\n")

    if RunAllAll == 1 or RunSucRDP == 1:
        outfile.write("<td width=5%> <a href=#RDP>RDP</a> </th>\n")

    if RunAllAll == 1 or RunFBrArc == 1:
        outfile.write("<td width=5%> <a href=#Browser>Brwsr</a> </td>\n")

    if RunAllAll == 1 or RunPrfHst == 1:
        outfile.write("<td width=5%> <a href=#Prefetch>Pref</a> </td>\n")

    if RunAllAll == 1 or RunAmCach == 1:
        outfile.write("<td width=5%> <a href=#AmCache>AmCsh</a> </td>\n")

    if RunAllAll == 1 or RunUsrAst == 1:
        outfile.write("<td width=5%> <a href=#UserAssist>UsrAst</a> </td>\n")

    if RunAllAll == 1 or RunShlBag == 1:
        outfile.write("<td width=5%> <a href=#ShellBags>ShlBg</a> </td>\n")

    if RunAllAll == 1 or RunIPCons == 1:
        outfile.write("<td width=5%> <a href=#IPConn>IPCon</a> </td>\n")

    if RunAllAll == 1 or RunDNSInf == 1:
        outfile.write("<td width=5%> <a href=#DNSCache>DNS</a> </td>\n")

    if RunAllAll == 1 or RunAutoRn == 1:
        outfile.write("<td width=5%> <a href=#AutoRun>AutRun</a> </td>\n")

    if RunAllAll == 1 or RunServic == 1:
        outfile.write("<td width=5%> <a href=#InstSVC>EVTx</a> </td>\n")

    if RunAllAll == 1 or RunRcyBin == 1:
        outfile.write("<td width=5%> <a href=#RBin>RBin</a> </td>\n")

    if RunAllAll == 1 or RunPwsLog == 1:
        outfile.write("<td width=5%> <a href=#PShell>Pshl</a> </td>\n")

    if RunAllAll == 1 or RunLnkPrs == 1:
        outfile.write("<td width=5%> <a href=#LNKFiles>LNK</a> </td>\n")

    if RunAllAll == 1 or RunChnSaw == 1:
        outfile.write("<td width=5%> <a href=#ChainSaw>ChSw</a> </td>\n")

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
        TZname = "TZInfo.dat"

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


        if os.path.isfile(TZname):
            outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed Time Zone information about\n")
            outfile.write("the endpoint. This information was extracted from the SYSTEM registry.</font></i></p>\n")

            innfile = open(TZname, encoding='utf8', errors="replace")
            for innline in innfile:

                if innline.startswith("TimeZoneInformation"):
                    outfile.write("<b>" + innline.strip() + "</b><br>\n")

                elif innline.startswith("ControlSet"):
                    outfile.write(innline.strip() + "<br>\n")

                elif innline.startswith("  StandardName"):
                    outfile.write(innline.strip() + "<br>\n")

                elif innline.startswith("  DaylightName"):
                    outfile.write(innline.strip() + "<br>\n")

                elif innline.startswith("  Bias"):
                    outfile.write(innline.strip() + "<br>\n")

                elif innline.startswith("  ActiveTimeBias"):
                    outfile.write(innline.strip() + "<br>\n")

                elif innline.startswith("  TimeZoneKeyName"):
                    outfile.write(innline.strip() + "<br>\n")

            innfile.close()
            os.remove(TZname)


            outfile.write("<p><i><font color=firebrick>Important: Understanding the Time Zone of the source endpoint, \n")
            outfile.write("The source collection program(s) Time Zone settings, and the Time Zone of the machine that \n")
            outfile.write("ran this program are critical to ensuring that your timeline is accurate. </font></i></p>\n")
            outfile.write("<p><i><b>Note: TZ of the machine this report was created on is: " + local_tzname + "</b></i></p>\n")


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
            outfile.write("determine if they look suspicious.<font color=gray size=-1><br><br>Source: Parsed $MFT, TZ is UTC</font></font></i></p>\n")

            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=40%> Full Path (+/-)</th>\n")
            outfile.write("<th width=15%> Created (+/-)</th>\n")
            outfile.write("<th width=15%> Accessed (+/-)</th>\n")
            outfile.write("<th width=15%> Modified (+/-)</th>\n")
            outfile.write("<th width=15%> Size (+/-)</th></tr></thead><tbody>\n")

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

                                    RowString = ' '.join(map(str, csvrow))
                                    if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                        PreIOC = " <b><font color=red>"
                                        PostIOC = "</font></b> "
                                    else: 
                                        PreIOC = " "
                                        PostIOC = " "

                                    outfile.write("<tr><td width=40%>" + PreIOC + csvrow[13] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + csvrow[6] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + csvrow[7] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + csvrow[8] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + "{:,}".format(nFileSize) + PostIOC + "</td></tr>\n")
                                    reccount = reccount + 1

            outfile.write("</tbody></table>\n")
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
            outfile.write("determine if they look suspicious.<font color=gray size=-1><br><br>Source: Parsed $MFT, TZ is UTC</font></font></i></p>\n")

            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=40%> Full Path (+/-)</th>\n")
            outfile.write("<th width=15%> Created (+/-)</th>\n")
            outfile.write("<th width=15%> Accessed (+/-)</th>\n")
            outfile.write("<th width=15%> Modified (+/-)</th>\n")
            outfile.write("<th width=15%> Size (+/-)</th></tr></thead><tbody>\n")

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

                                    RowString = ' '.join(map(str, csvrow))
                                    if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                        PreIOC = " <b><font color=red>"
                                        PostIOC = "</font></b> "
                                    else: 
                                        PreIOC = " "
                                        PostIOC = " "

                                    outfile.write("<tr><td width=40%>" + PreIOC + csvrow[13] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + csvrow[6] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + csvrow[7] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + csvrow[8] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + "{:,}".format(nFileSize) + PostIOC + "</td></tr>\n")
                                    reccount = reccount + 1

            outfile.write("</tbody></table>\n")
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
            outfile.write("determine if they look suspicious.<font color=gray size=-1><br><br>Source: Parsed $MFT, TZ is UTC</font></font></i></p>\n")

            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=40%> Full Path (+/-)</th>\n")
            outfile.write("<th width=15%> Created (+/-)</th>\n")
            outfile.write("<th width=15%> Accessed (+/-)</th>\n")
            outfile.write("<th width=15%> Modified (+/-)</th>\n")
            outfile.write("<th width=15%> Size (+/-)</th></tr></thead><tbody>\n")

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

                                    RowString = ' '.join(map(str, csvrow))
                                    if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                        PreIOC = " <b><font color=red>"
                                        PostIOC = "</font></b> "
                                    else: 
                                        PreIOC = " "
                                        PostIOC = " "

                                    outfile.write("<tr><td width=40%>" + PreIOC + csvrow[13] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + csvrow[6] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + csvrow[7] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + csvrow[8] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + "{:,}".format(nFileSize) + PostIOC + "</td></tr>\n")
                                    reccount = reccount + 1

            outfile.write("</tbody></table>\n")
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
            outfile.write("determine if they look suspicious.<font color=gray size=-1><br><br>Source: Parsed $MFT, TZ is UTC</font></font></i></p>\n")

            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=40%> Full Path (+/-)</th>\n")
            outfile.write("<th width=15%> Created (+/-)</th>\n")
            outfile.write("<th width=15%> Accessed (+/-)</th>\n")
            outfile.write("<th width=15%> Modified (+/-)</th>\n")
            outfile.write("<th width=15%> Size (+/-)</th></tr></thead><tbody>\n")

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

                                    RowString = ' '.join(map(str, csvrow))
                                    if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                        PreIOC = " <b><font color=red>"
                                        PostIOC = "</font></b> "
                                    else: 
                                        PreIOC = " "
                                        PostIOC = " "

                                    outfile.write("<tr><td width=40%>" + PreIOC + csvrow[13] + PostIOC  + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + csvrow[6] + PostIOC + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + csvrow[7] + PostIOC  + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + csvrow[8] + PostIOC  + "</td>\n")
                                    outfile.write("<td width=15%>" + PreIOC + "{:,}".format(nFileSize) + PostIOC  + "</td></tr>\n")
                                    reccount = reccount + 1

            outfile.write("</tbody></table>\n")
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
            outfile.write("name that appears to be randomly generated.<font color=gray size=-1><br><br>Source: Parsed $MFT, TZ is UTC</font></font></i></p>\n")

            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=40%> Full Path (+/-)</th>\n")
            outfile.write("<th width=15%> Created (+/-)</th>\n")
            outfile.write("<th width=15%> Accessed (+/-)</th>\n")
            outfile.write("<th width=15%> Modified (+/-)</th>\n")
            outfile.write("<th width=15%> Size (+/-)</th></tr></thead><tbody>\n")

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

                                RowString = ' '.join(map(str, csvrow))
                                if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                    PreIOC = " <b><font color=red>"
                                    PostIOC = "</font></b> "
                                else: 
                                    PreIOC = " "
                                    PostIOC = " "

                                outfile.write("<tr><td width=40%>" + PreIOC + csvrow[13] + PostIOC + "</td>\n")
                                outfile.write("<td width=15%>" + PreIOC + csvrow[6] + PostIOC + "</td>\n")
                                outfile.write("<td width=15%>" + PreIOC + csvrow[7] + PostIOC + "</td>\n")
                                outfile.write("<td width=15%>" + PreIOC + csvrow[8] + PostIOC + "</td>\n")
                                outfile.write("<td width=15%>" + PreIOC + "{:,}".format(nFileSize) + PostIOC + "</td></tr>\n")
                                reccount = reccount + 1

            outfile.write("</tbody></table>\n")

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
            outfile.write("name that appears to be randomly generated.<font color=gray size=-1><br><br>Source: Parsed $MFT, TZ is UTC</font></font></i></p>\n")

            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=40%> Full Path (+/-)</th>\n")
            outfile.write("<th width=15%> Created (+/-)</th>\n")
            outfile.write("<th width=15%> Accessed (+/-)</th>\n")
            outfile.write("<th width=15%> Modified (+/-)</th>\n")
            outfile.write("<th width=15%> Size (+/-)</th></tr></thead><tbody>\n")

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

                                RowString = ' '.join(map(str, csvrow))
                                if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                    PreIOC = " <b><font color=red>"
                                    PostIOC = "</font></b> "
                                else: 
                                    PreIOC = " "
                                    PostIOC = " "

                                outfile.write("<tr><td width=40%>" + PreIOC + csvrow[13] + PostIOC + "</td>\n")
                                outfile.write("<td width=15%>" + PreIOC + csvrow[6] + PostIOC + "</td>\n")
                                outfile.write("<td width=15%>" + PreIOC + csvrow[7] + PostIOC + "</td>\n")
                                outfile.write("<td width=15%>" + PreIOC + csvrow[8] + PostIOC + "</td>\n")
                                outfile.write("<td width=15%>" + PreIOC + "{:,}".format(nFileSize) + PostIOC + "</td></tr>\n")
                                reccount = reccount + 1

            outfile.write("</tbody></table>\n")

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
        outfile.write("to determine if they look suspicious.<font color=gray size=-1><br><br>Source: Parsed Security Event Log, TZ is UTC</font></font></i></p>\n")

        reccount = 0
        filname = "RDPGood.csv"

        if os.path.isfile(filname):
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
                csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                for csvrow in csvread:
                    if len(csvrow) > 4:
                        if reccount == 0:
                            tdtr = "th"
                        else:
                            tdtr = "td"

                        # Is it in our IOC List?
                        RowString = ' '.join(map(str, csvrow))
                        if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                            PreIOC = " <b><font color=red>"
                            PostIOC = "</font></b> "
                        else: 
                            PreIOC = " "
                            PostIOC = " "

                        if reccount == 0:
                            outfile.write("<thead>\n")
                            PostIOC += " (+/-)"

                        outfile.write("<tr><" + tdtr + " width=20%>" + PreIOC + csvrow[0] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=15%>" + PreIOC + csvrow[1] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=15%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=20%>" + PreIOC + csvrow[3] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[4] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=20%>" + PreIOC + csvrow[5] + PostIOC + "</" + tdtr + "></tr>\n")

                        if reccount == 0:
                            outfile.write("</thead><tbody>\n")

                        # Write out IP Address for Bulk Lookup 
                        ipsfileall.write(csvrow[5] + "\n")

                        reccount = reccount + 1

            outfile.write("</tbody></table>\n")
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
        outfile.write(" look suspicious.<font color=gray size=-1><br><br>Source: Parsed Security Event Log, TZ is UTC</font></font></i></p>\n")

        reccount = 0
        filname = "SecEvt4625.csv"

        dedupCol = []
        dedupCnt = []

        if os.path.isfile(filname):
            outfile.write("<table class=\"sortable\" class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=75%> Attempted UserId (+/-)</th>\n")
            outfile.write("<th width=25%> Count (+/-)</th></tr></thead><tbody>\n")

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
                    # Is it in our IOC List?
                    RowString = dedupCol[curIdx]
                    if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                        PreIOC = " <b><font color=red>"
                        PostIOC = "</font></b> "
                    else: 
                        PreIOC = " "
                        PostIOC = " "

                    outfile.write("<tr><td width=75%>" + PreIOC + dedupCol[curIdx] + PostIOC + "</td>\n")
                    outfile.write("<td width=25%>" + PreIOC + str(dedupCnt[curIdx]) + PostIOC + "</td></tr>\n")

                    reccount = reccount + 1

            outfile.write("</tbody></table>\n")
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
        outfile.write("in Temporary Directories.<font color=gray size=-1><br><br>Source: Collected Browsers History, Check the \n")
        outfile.write("collection program for TZ. Note: Nirsoft Browsing History View will be source machines local Time.</font></font></i></p>\n")

        reccount = 0
        filname = dirname + "\\brw\\BrowseHist.csv"

        if os.path.isfile(filname):
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
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
                                # Is it in our IOC List?
                                RowString = ' '.join(map(str, csvrow))
                                if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                    PreIOC = " <b><font color=red>"
                                    PostIOC = "</font></b> "
                                else: 
                                    PreIOC = " "
                                    PostIOC = " "

                                if reccount == 0:
                                    outfile.write("<thead>\n")
                                    PostIOC += " (+/-)"

                                outfile.write("<tr><" + tdtr + " width=15%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                                outfile.write("<" + tdtr + " width=5%>" + PreIOC + csvrow[3] + PostIOC + "</" + tdtr + ">\n")
                                outfile.write("<" + tdtr + " width=60%>" + PreIOC + csvrow[0] + PostIOC + "</" + tdtr + ">\n")
                                outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[6] + PostIOC + "</" + tdtr + ">\n")
                                outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[7] + PostIOC + "</" + tdtr + "></tr>\n")

                                if reccount == 0:
                                    outfile.write("</thead><tbody\n")

                                reccount = reccount + 1

            outfile.write("</tbody></table>\n")

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
        outfile.write("accessed or archive files created. \n")
        outfile.write("<font color=gray size=-1><br><br>Source: Collected Browsers History, Check the \n")
        outfile.write("collection program for TZ. Note: Nirsoft Browsing History View will be source machines local Time.</font></font></i></p>\n")


        reccount = 0
        filname = dirname + "\\brw\\BrowseHist.csv"

        if os.path.isfile(filname):
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
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

                            # Is it in our IOC List?
                            RowString = ' '.join(map(str, csvrow))
                            if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                PreIOC = " <b><font color=red>"
                                PostIOC = "</font></b> "
                            else: 
                                PreIOC = " "
                                PostIOC = " "

                            if reccount == 0:
                                outfile.write("<thead>\n")
                                PostIOC += " (+/-)"

                            outfile.write("<tr><" + tdtr + " width=15%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=5%>" + PreIOC + csvrow[3] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=60%>" + PreIOC + csvrow[0] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[6] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[7] + PostIOC + "</" + tdtr + "></tr>\n")

                            if reccount == 0:
                                outfile.write("</thead><tbody>\n")

                            reccount = reccount + 1

            outfile.write("</tbody></table>\n")

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
        outfile.write("indicate malicious C2 activity or strings that may indicate access to Phishing sites. \n")
        outfile.write("<font color=gray size=-1><br><br>Source: Collected Browsers History, Check the \n")
        outfile.write("collection program for TZ. Note: Nirsoft Browsing History View will be source machines local Time.</font></font></i></p>\n")

        reccount = 0
        filname = dirname + "\\brw\\BrowseHist.csv"

        if os.path.isfile(filname):
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
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

                            # Is it in our IOC List?
                            RowString = ' '.join(map(str, csvrow))
                            if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                PreIOC = " <b><font color=red>"
                                PostIOC = "</font></b> "
                            else: 
                                PreIOC = " "
                                PostIOC = " "

                            if reccount == 0:
                                outfile.write("<thead>\n")
                                PostIOC += " (+/-)"

                            outfile.write("<tr><" + tdtr + " width=15%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=5%>" + PreIOC + csvrow[3] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=60%>" + PreIOC + csvrow[0] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[6] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[7] + PostIOC + "</" + tdtr + "></tr>\n")

                            if reccount == 0:
                                outfile.write("</thead><tbody>\n")

                            # Write out Domain for Bulk Lookup 
                            url_split = csvrow[0].split('/')
                            if len(url_split) > 2:
                                domfileall.write(url_split[2] + "\n")

                            reccount = reccount + 1

            outfile.write("</tbody></table>\n")

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
        outfile.write("ordinary, or appears to be malicious. \n")
        outfile.write("<font color=gray size=-1><br><br>Source: Collected Prefetch files, TZ is UTC.</font></font></i></p>\n")

        reccount = 0
        filname = "WinPrefetchView.csv"

        if os.path.isfile(filname):
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=20%> FileName (+/-)</th>\n")
            outfile.write("<th width=15%> Created (+/-)</th>\n")
            outfile.write("<th width=15%> Modified (+/-)</th>\n")
            outfile.write("<th width=15%> Last Run (+/-)</th>\n")
            outfile.write("<th width=5%> Times (+/-)</th>\n")
            outfile.write("<th width=30%> Path (+/-)</th></tr></thead><tbody>\n")

            with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
                csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                for csvrow in csvread:
                    if len(csvrow) > 7:
                        reccount = reccount + 1

                        # Is it in our IOC List?
                        RowString = ' '.join(map(str, csvrow))
                        if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                            PreIOC = " <b><font color=red>"
                            PostIOC = "</font></b> "
                        else: 
                            PreIOC = " "
                            PostIOC = " "

                        outfile.write("<tr bgcolor=E0E0E0><td width=20%>" + PreIOC + csvrow[0] + PostIOC + "</td>\n")
                        outfile.write("<td width=15%>" + PreIOC + csvrow[1] + PostIOC + "</td>\n")
                        outfile.write("<td width=15%>" + PreIOC + csvrow[2] + PostIOC + "</td>\n")
                        outfile.write("<td width=15%>" + PreIOC + csvrow[7] + PostIOC + "</td>\n")
                        outfile.write("<td width=5%>" + PreIOC + csvrow[6] + PostIOC + "</td>\n")
                        outfile.write("<td width=30%>" + PreIOC + csvrow[5] + PostIOC + "</td></tr>\n")

            outfile.write("</tbody></table>\n")
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
            print("[+] Reading CPorts Output File...")
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=13%> Process (+/-)</th>\n")
            outfile.write("<th width=5%> Prot. (+/-)</th>\n")
            outfile.write("<th width=10%> Local IP (+/-)</th>\n")
            outfile.write("<th width=5%> LPort (+/-)</th>\n")
            outfile.write("<th width=10%> Remote IP (+/-)</th>\n")
            outfile.write("<th width=5%> RPort (+/-)</th>\n")
            outfile.write("<th width=15%> RHost (+/-)</th>\n")
            outfile.write("<th width=7%> State (+/-)</th>\n")
            outfile.write("<th width=30%> Process Path (+/-)</th></tr></thead><tbody>\n")

            with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
                csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                for csvrow in csvread:
                    if len(csvrow) > 11:
                        reccount = reccount + 1

                        # Is it in our IOC List?
                        RowString = ' '.join(map(str, csvrow))
                        if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                            PreIOC = " <b><font color=red>"
                            PostIOC = "</font></b> "
                        else: 
                            PreIOC = " "
                            PostIOC = " "

                        outfile.write("<tr bgcolor=E0E0E0><td width=13%>" + PreIOC + csvrow[0] + PostIOC + "</td>\n")
                        outfile.write("<td width=5%>" + PreIOC + csvrow[2] + PostIOC + "</td>\n")
                        outfile.write("<td width=10%>" + PreIOC + csvrow[5] + PostIOC + "</td>\n")
                        outfile.write("<td width=5%>" + PreIOC + csvrow[3] + PostIOC + "</td>\n")
                        outfile.write("<td width=10%> <A href=https://www.virustotal.com/#/search/" + csvrow[8] + ">" + PreIOC + csvrow[8] + PostIOC + "</a> </td>\n")
                        outfile.write("<td width=5%>" + PreIOC + csvrow[6] + PostIOC + "</td>\n")
                        outfile.write("<td width=15%>" + PreIOC + csvrow[9] + PostIOC + "</td>\n")
                        outfile.write("<td width=7%>" + PreIOC + csvrow[10] + PostIOC + "</td>\n")
                        outfile.write("<td width=30%>" + PreIOC + csvrow[11] + PostIOC + "</td></tr>\n")

                        # Write out IP Address for Bulk Lookup 
                        ipsfileall.write(csvrow[8] + "\n")

            outfile.write("</tbody></table>\n")

            if reccount < 2:
                outfile.write("<p><b><font color = red> No CPortsData Found! </font></b></p>\n")
            else:
                outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
        else:
            print("[!] Bypassing IP Connections Information (No CPorts Input Data) ...")
            outfile.write("<p><b><font color = red> No CPorts Input Data Found! </font></b></p>\n")


        ###########################################################################
        # This section looks for the netstat-abno.dat file and reformats it.      #
        ###########################################################################
        reccount = 0
        filname = dirname + "\\sys\\netstat-abno.dat"

        if os.path.isfile(filname):
            print("[+] Reading netstat -abno Output File...")
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><th width=5%> Prot. (+/-)</th>\n")
            outfile.write("<th width=15%> Local IP (+/-)</th>\n")
            outfile.write("<th width=5%> Local Port (+/-)</th>\n")
            outfile.write("<th width=15%> Remote IP (+/-)</th>\n")
            outfile.write("<th width=5%> Remote Port (+/-)</th>\n")
            outfile.write("<th width=10%> State (+/-)</th>\n")
            outfile.write("<th width=5%> PID </th>\n")
            outfile.write("<th width=20%> Component </th>\n")
            outfile.write("<th width=20%> Process (+/-)</th></tr></thead><tbody>\n")

            innfile = open(filname, encoding='utf8', errors="replace")
            for innline in innfile:
                if innline.startswith("  TCP ") or innline.startswith("  UDP "):

                    # Is it in our IOC List?
                    if any(AnyIOC in innline.lower() for AnyIOC in IOCList):
                        PreIOC = " <b><font color=red>"
                        PostIOC = "</font></b> "
                    else: 
                        PreIOC = " "
                        PostIOC = " "

                    # Parse out individual pieces
                    ConnSplit = innline.split()
                    if len(ConnSplit) == 5:
                        if reccount > 0:
                            outfile.write("</tr>\n")

                        LocSplit = ConnSplit[1].rsplit(':',1)
                        RmtSplit = ConnSplit[2].rsplit(':',1)

                        outfile.write("<tr><td width=5%>" + PreIOC + ConnSplit[0] + PostIOC + "</td>\n")
                        outfile.write("<td width=15%>" + PreIOC + LocSplit[0] + PostIOC + "</td>\n")
                        outfile.write("<td width=5%>" + PreIOC + LocSplit[1] + PostIOC + "</td>\n")
                        outfile.write("<td width=15%> <A href=https://www.virustotal.com/#/search/" + RmtSplit[0] + ">" + PreIOC + RmtSplit[0] + PostIOC + "</a> </td>\n")
                        outfile.write("<td width=5%>" + PreIOC + RmtSplit[1] + PostIOC + "</td>\n")
                        outfile.write("<td width=10%>" + PreIOC + ConnSplit[3] + PostIOC +  "</td>\n")
                        outfile.write("<td width=5%>" + PreIOC + ConnSplit[4] + PostIOC +  "</td>\n")
                        reccount = reccount + 1

                    elif len(ConnSplit) == 4:
                        if reccount > 0:
                            outfile.write("</tr>\n")

                        LocSplit = ConnSplit[1].rsplit(':',1)
                        RmtSplit = ConnSplit[2].rsplit(':',1)

                        outfile.write("</tr><tr><td width=5%>" + PreIOC + ConnSplit[0] + PostIOC + "</td>\n")
                        outfile.write("<td width=15%>" + PreIOC + LocSplit[0] + PostIOC + "</td>\n")
                        outfile.write("<td width=5%>" + PreIOC + LocSplit[1] + PostIOC + "</td>\n")
                        outfile.write("<td width=15%>" + PreIOC + RmtSplit[0] + PostIOC + "</td>\n")
                        outfile.write("<td width=5%>" + PreIOC + RmtSplit[1] + PostIOC + "</td>\n")
                        outfile.write("<td width=10%>" + PreIOC + "-" + PostIOC + "</td>\n")
                        outfile.write("<td width=5%>" + PreIOC + ConnSplit[3] + PostIOC + "</td>\n")
                        reccount = reccount + 1
                else:
                    if reccount > 0:
                        outfile.write("<td width=20%>" + innline +  "</td>\n")

            outfile.write("</tr></tbody></table>\n")
            innfile.close()

        else:
            print("[!] Bypassing IP Connections Information (No netstat-abno Input Data) ...")
            outfile.write("<p><b><font color = red> No netstat-abno Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing IP Connections Information...")


    ###########################################################################
    # Write AmCache Entries                                                   #
    ###########################################################################
    if RunAllAll == 1 or RunAmCach == 1:
        print("[+] Generating AmCache Information...")
        outfile.write("<a name=AmCache></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id27\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id27\">\n")
        outfile.write("<H2>AmCache Hive Information</H2>\n")
        outfile.write("</label><div><hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
        outfile.write("the Windows AmCache Registry Hive. The AmCache Hive keys store information about \n")
        outfile.write("the execution of Windows programs. These files are forensically \n")
        outfile.write("interesting because they indicate that a program was excuted by a user, and the last \n")
        outfile.write("time it was executed.  This is normal behavior and does not in-itself indicate hostile behavior. \n")
        outfile.write("However, a quick look at the AmCache Hive is a good way to see if anything executed \n")
        outfile.write("appears to be suspicious.  Review this section to see if anything looks out of the \n")
        outfile.write("ordinary, or appears to be malicious.<font color=gray size=-1><br><br>Source: AmCache Registry Hive, Dates ending with a Z denote UTC Time Zone</font></font></i></p>\n")

        reccount = 0
        filname = "AmCache.dat"
        AmCName = " "
        AmCLast = " "

        if os.path.isfile(filname):
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")

            outfile.write("<thead><th width=10%> Last (+/-)</th>\n")
            outfile.write("<th width=60%> Name (+/-)</th>\n")
            outfile.write("<th width=30%> Hash (+/-)</th></tr></thead><tbody>\n")

            innfile = open(filname, encoding='utf8', errors="replace")
            for innline in innfile:
                reccount = reccount + 1

                # Is it in our IOC List?
                if any(AnyIOC in innline.lower() for AnyIOC in IOCList):
                    PreIOC = " <b><font color=red>"
                    PostIOC = "</font></b> "
                else: 
                    PreIOC = " "
                    PostIOC = " "

                strIndex = innline.find("LastWrite")
                if strIndex > 0:
                    AmCLast = innline[strIndex+10:]
                    AmCName = innline[0:strIndex]
                elif innline.startswith("Hash: "):
                    outfile.write("<tr><td width=10%>" + PreIOC + AmCLast + PostIOC + "</td>\n")
                    outfile.write("<td width=50%>" + PreIOC + AmCName + PostIOC + "</td>\n")

                    if len(innline) > 32:
                        outfile.write("<td width=30%> <A href=https://www.virustotal.com/#/search/" + innline[6:].strip() + ">" + PreIOC + innline[6:].strip() + PostIOC + "</a></td></tr>\n")
                        AmCName = " "
                        AmCLast = " "
                    else:
                        outfile.write("<td width=30%> Unknown</td></tr>\n")
                        AmCName = " "
                        AmCLast = " "

                    reccount = reccount + 1

                else:
                    if len(innline) > 1:
                        outfile.write("<td Colspan=\"3\" style=\"text-align:left\" width=100%>" + PreIOC + innline.strip() + PostIOC + "</td></tr>\n")
                        reccount = reccount + 1
                        AmCName = " "
                        AmCLast = " "

            outfile.write("</tbody></table>\n")
            innfile.close()
            os.remove(filname)

            if reccount < 1:
                outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
            else:
                outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

        else:
            print("[!] No AmCache Data Found (No Input Data)...")
            outfile.write("<p><i><font color=firebrick>AChoir was not able to parse\n")
            outfile.write("the endpoint AmCache Hive.</font></i></p>\n")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
        print("[+] Bypassing AmCache Hive (AmCache.hve) Information...")


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
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=13%> Modified Time (+/-)</th>\n")
            outfile.write("<th width=5%> Modified Count (+/-)</th>\n")
            outfile.write("<th width=30%> Item Name (+/-)</th></tr></thead><tbody>\n")

            with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
                csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                for csvrow in csvread:
                    if len(csvrow) > 3:
                        reccount = reccount + 1

                        # Is it in our IOC List?
                        RowString = ' '.join(map(str, csvrow))
                        if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                            PreIOC = " <b><font color=red>"
                            PostIOC = "</font></b> "
                        else: 
                            PreIOC = " "
                            PostIOC = " "

                        outfile.write("<tr bgcolor=E0E0E0><td width=15%>" + PreIOC + csvrow[3] + PostIOC + "</td>\n")
                        outfile.write("<td width=5%>" + PreIOC + csvrow[2] + PostIOC + "</td>\n")
                        outfile.write("<td width=30%>" + PreIOC + csvrow[0] + PostIOC + "</td></tr>\n")

            outfile.write("</tbody></table>\n")

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
        outfile.write("</label><div><font color=gray size=-1>Source: User Registry Hives, Dates ending with a Z denote UTC Time Zone</font><hr>\n")

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
                    # Is it in our IOC List?
                    if any(AnyIOC in innline.lower() for AnyIOC in IOCList):
                        PreIOC = " <b><font color=red>"
                        PostIOC = "</font></b> "
                    else: 
                        PreIOC = " "
                        PostIOC = " "

                    if innline.startswith("shellfolders "):
                        outfile.write("<h2>" + innline.strip()  + "</h2><br>\n")
                    elif innline.startswith("UserAssist"):
                        outfile.write("<hr><h2>" + innline.strip()  + "</h2><br>\n")
                    else:
                        outfile.write(PreIOC + innline.strip() + PostIOC + "<br>\n")
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
    # Write PowerShell Log Data (ConsoleHost_history.txt) for each profile    #
    ###########################################################################
    if RunAllAll == 1 or RunPwsLog == 1:
        print("[+] Generating PowerShell Log Information...")

        outfile.write("<a name=PShell></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id29\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id29\">\n")
        outfile.write("<H2>PowerShell Logs</H2>\n")
        outfile.write("</label><div><hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
        outfile.write("individual user PowerShell Logs. Powershell is often used legitimately by system \n")
        outfile.write("administrators. However, Hostile actors can, and do use Powershell for malicious \n")
        outfile.write("purposes.  Review the logs for any suspicious commands that might indicate hostile \n")
        outfile.write("intent.</font></i></p>\n")

        print("[+] Reading PowerShell Logs Multiple User Profiles...")
        filcount = 0

        curdir = dirname + "\\Psh"
        #lencurdir = len(curdir)
        for root, dirs, files in os.walk(curdir):
            for fname in files:
                fnameUpper = fname.upper()
                curfile = os.path.join(root, fname)

                if fnameUpper.startswith("CONSOLEHOST_HISTORY."):
                    filcount = filcount + 1
                    reccount = 0
                    outfile.write("<table border=1 cellpadding=5 width=100%>\n")
                    outfile.write("<tr><td style=\"text-align: left\">\n")
                    outfile.write("<h2> Powershell Log: " + curfile + "</h2><br>\n")

                    innfile = open(curfile, encoding='utf8', errors="replace")
                    for innline in innfile:
                        # Is it in our IOC List?
                        if any(AnyIOC in innline.lower() for AnyIOC in IOCList):
                            PreIOC = " <b><font color=red>"
                            PostIOC = "</font></b> "
                        else: 
                            PreIOC = " "
                            PostIOC = " "

                        outfile.write(PreIOC + innline.strip() + PostIOC + "<br>\n")
                        reccount = reccount + 1

                    innfile.close()
                    outfile.write("</td></tr></table>\n")

                    if reccount < 1:
                        outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
                    else:
                        outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

        if filcount < 1:
            print("[!] No User PowerShell Logs Found (No Input Data)...")
            outfile.write("<p><b><font color = red> No User PowerShell Logs Found! </font></b></p>\n")

        outfile.write("</div>\n")

    else:
      print("[+] ByPassing PowerShell Logs for Multiple User Profiles...")


    ###########################################################################
    # Parse Desktop and Recent Link Files                                     #
    ###########################################################################
    if RunAllAll == 1 or RunLnkPrs == 1:
        print("[+] Generating Desktop and Recent LNK Information...")

        outfile.write("<a name=LNKFiles></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id30\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id30\">\n")
        outfile.write("<H2>Desktop and Recent LNK Files</H2>\n")
        outfile.write("</label><div><hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed theLNK Files in \n")
        outfile.write("individual user Desktop and Recent Locations.  LNK files are not inherently hostile. \n")
        outfile.write("They are an artifact that indicates a program was run or an associated file was opened  \n")
        outfile.write("(the program associated with the file was run). Review these files and programs for \n")
        outfile.write("suspicious activity or unusual names that indicate hostile intent.<font color=gray size=-1><br><br>Source: Parsed LNK Files, TZ is in +hh:mm format</font></font></i></p>\n")

        print("[+] Checking for Eric Zimmerman LECmd Link Parser...")

        if os.path.isfile(".\\LECmd.exe") == False:
            print("[?] LECmd executable not found...  Would you like to Download it...")
            YesOrNo = input("[?] Y/N > ")

            if YesOrNo.upper() == "Y":
                print("[+] Downloading LECmd from Eric Zimmerman Web Site...")
                LECUrl = 'https://f001.backblazeb2.com/file/EricZimmermanTools/LECmd.zip'
                LECReq = requests.get(LECUrl, allow_redirects=True)
                open('LECmd.zip', 'wb').write(LECReq.content)

                print("[+] Unzipping LECmd...")
                with ZipFile('LECmd.zip', 'r') as zipObj:
                    # Extract all the contents of zip file in current directory
                    zipObj.extractall()
            else:
                print("[!] LECmd Download Bypassed...")


        exeName = ".\\LECmd.exe"
        if os.path.isfile(exeName):
            print("[+] LECmd executable found")
            print("[+] Parsing Desktop and Recent LNK Files from Multiple User Profiles...")

            curdir = dirname + "\\Lnk"
            filname = "LNKFiles.csv"
            cmdexec = exeName + " -q -d " + curdir + " --dt \"yyyy-MM-dd HH:mm:ss K\" --csv .\\ --csvf " + filname 
            returned_value = os.system(cmdexec)

            print("[+] Reading Desktop and Recent LNK Files from Multiple User Profiles...")

            reccount = 0

            if os.path.isfile(filname):
                outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
                with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
                    csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                    for csvrow in csvread:
                        if len(csvrow) > 18:
                            if reccount == 0:
                                tdtr = "th"
                                csvrow[1] = "Source<br>Create"
                                csvrow[2] = "Source<br>Modify"
                                csvrow[3] = "Source<br>Access"
                                csvrow[4] = "Target<br>Create"
                                csvrow[5] = "Target<br>Modify"
                                csvrow[6] = "Target<br>Access"
                            else:
                                tdtr = "td"

                            # Is it in our IOC List?
                            RowString = ' '.join(map(str, csvrow))
                            if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                PreIOC = " <b><font color=red>"
                                PostIOC = "</font></b> "
                            else: 
                                PreIOC = " "
                                PostIOC = " "

                            if reccount == 0:
                                outfile.write("<thead>\n")
                                PostIOC += " (+/-)"

                            outfile.write("<tr><" + tdtr + " width=25%>" + PreIOC + csvrow[0] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=23%>" + PreIOC + csvrow[15] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[18] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=7%>" + PreIOC + csvrow[1] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=7%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=7%>" + PreIOC + csvrow[3] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=7%>" + PreIOC + csvrow[4] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=7%>" + PreIOC + csvrow[5] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=7%>" + PreIOC + csvrow[6] + PostIOC + "</" + tdtr + "></tr>\n")

                            if reccount == 0:
                                outfile.write("</thead><tbody>\n")

                            reccount = reccount + 1

                outfile.write("</tbody></table>\n")
                os.remove(filname)

                if reccount < 2:
                    print("[!] No LNK File Data Found...")
                    outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
                else:
                    outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

            else:
                print("[!] No LNK Data Found...")
                outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")

            outfile.write("</div>\n")

        else:
            print("[!] LECmd Executable Not Found, Parsing Bypassed...")

    else:
      print("[+] ByPassing LECmd Parsing for Multiple User Profiles...")


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
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=10%> Time (+/-)</th>\n")
            outfile.write("<th width=30%> Entry Location  (+/-)</th>\n")
            outfile.write("<th width=10%> Entry  (+/-)</th>\n")
            outfile.write("<th width=30%> Image Path  (+/-)<hr> Launch String</th>\n")
            outfile.write("<th width=15%> MD5  (+/-)</th>\n")
            outfile.write("<th width=5%> Enabled  (+/-)</th></tr></thead><tbody>\n")

            with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
                csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                for csvrow in csvread:
                    if len(csvrow) > 10:
                        if "currentversion\\run" in csvrow[1].lower():

                            # Is it in our IOC List?
                            RowString = ' '.join(map(str, csvrow))
                            if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                PreIOC = " <b><font color=red>"
                                PostIOC = "</font></b> "
                            else: 
                                PreIOC = " "
                                PostIOC = " "

                            outfile.write("<tr><td width=10%>" + PreIOC + csvrow[0] + PostIOC + "</td>\n")
                            outfile.write("<td width=30%>" + PreIOC + csvrow[1] + PostIOC + "</td>\n")
                            outfile.write("<td width=10%>" + PreIOC + csvrow[2] + PostIOC + "</td>\n")
                            outfile.write("<td width=30%>" + PreIOC + csvrow[8] + PostIOC + "<hr>" + csvrow[10] + "</td>\n")
                            if len(csvrow) > 11:
                                outfile.write("<td width=15%> <A href=https://www.virustotal.com/#/search/" + csvrow[11] + ">" + PreIOC + csvrow[11] + PostIOC + "</a> </td>\n")
                            else:
                                outfile.write("<td width=15%> No MD5 Available </td>\n")
                            outfile.write("<td width=5%>" + PreIOC + csvrow[3] + PostIOC + "</td></tr>\n")

                            reccount = reccount + 1

            outfile.write("</tbody></table>\n")

            if reccount < 2:
                print("[!] No Run or RunOnce Information Found...")
                outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
            else:
                outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

        else:
            print("[!] Bypassing AutoRuns Run/RunOnce Information (No Input Data)...")
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
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
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

                        # Is it in our IOC List?
                        RowString = ' '.join(map(str, csvrow))
                        if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                            PreIOC = " <b><font color=red>"
                            PostIOC = "</font></b> "
                        else: 
                            PreIOC = " "
                            PostIOC = " "

                        if reccount == 0:
                            outfile.write("<thead>\n")
                            PostIOC += " (+/-)"


                        outfile.write("<tr><" + tdtr + " width=10%>" + PreIOC + csvrow[0] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=30%>" + PreIOC + csvrow[1] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=30%>" + PreIOC + csvrow[8] + "<hr>" + csvrow[10] + PostIOC + "</" + tdtr + ">\n")
                        if len(csvrow) > 11:
                            outfile.write("<" + tdtr + " width=15%> <A href=https://www.virustotal.com/#/search/" + csvrow[11] + ">" + PreIOC + csvrow[11] + PostIOC + "</a> </td>\n")

                            # Write out Hash for Bulk Lookup 
                            hshfileall.write(csvrow[11] + "\n")
                        else:
                            outfile.write("<" + tdtr + " width=15%> " + Hash + " </td>\n")

                        outfile.write("<" + tdtr + " width=5%>" + PreIOC + csvrow[3] + PostIOC + "</" + tdtr + "></tr>\n")

                        if reccount == 0:
                            outfile.write("</thead><tbody>\n")

                        reccount = reccount + 1

            outfile.write("</tbody></table>\n")

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
        outfile.write("which may indicate malicious intent.<font color=gray size=-1><br><br>Source: Parsed System Event Log, TZ is UTC</font></font></i></p>\n")

        reccount = 0
        filname = "SysEvt7045.csv"

        if os.path.isfile(filname):
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
                csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                for csvrow in csvread:
                    if len(csvrow) > 3:
                        if reccount == 0:
                            tdtr = "th"
                        else:
                            tdtr = "td"

                        # Is it in our IOC List?
                        RowString = ' '.join(map(str, csvrow))
                        if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                            PreIOC = " <b><font color=red>"
                            PostIOC = "</font></b> "
                        else: 
                            PreIOC = " "
                            PostIOC = " "

                        if reccount == 0:
                            outfile.write("<thead>\n")
                            PostIOC += " (+/-)"

                        outfile.write("<tr><" + tdtr + " width=15%>" + PreIOC + csvrow[0] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=30%>" + PreIOC + csvrow[1] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=45%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[3] + PostIOC + "</" + tdtr + "></tr>\n")

                        if reccount == 0:
                            outfile.write("</thead><tbody>\n")

                        reccount = reccount + 1

            outfile.write("</tbody></table>\n")
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
        outfile.write("which may indicate malicious intent.<font color=gray size=-1><br><br>Source: Parsed Security Event Log, TZ is UTC</font></font></i></p>\n")

        reccount = 0
        filname = "SecEvt4698.csv"

        if os.path.isfile(filname):
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            with open(filname, 'r', encoding='utf8', errors="replace") as csvfile:
                csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                for csvrow in csvread:
                    if len(csvrow) > 3:
                        if reccount == 0:
                            tdtr = "th"
                        else:
                            tdtr = "td"

                        # Is it in our IOC List?
                        RowString = ' '.join(map(str, csvrow))
                        if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                            PreIOC = " <b><font color=red>"
                            PostIOC = "</font></b> "
                        else: 
                            PreIOC = " "
                            PostIOC = " "

                        if reccount == 0:
                            outfile.write("<thead>\n")
                            PostIOC += " (+/-)"

                        outfile.write("<tr><" + tdtr + " width=15%>"+ PreIOC + csvrow[0] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=25%>"+ PreIOC + csvrow[1] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=30%>"+ PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                        outfile.write("<" + tdtr + " width=30%>"+ PreIOC + csvrow[3] + PostIOC + "</" + tdtr + "></tr>\n")

                        if reccount == 0:
                            outfile.write("</thead><tbody>\n")

                        reccount = reccount + 1

            outfile.write("</tbody></table>\n")
            os.remove(filname)

            if reccount < 2:
                outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
            else:
                outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")
        else:
            print("[!] No New Scheduled Tasks Found (No Input Data)...")
            outfile.write("<p><b><font color = red> No Input Data Found! </font></b></p>\n")


        ###########################################################################
        # Most Collections are going to run AutoRuns - But Just in case we want   #
        #  to collections the raw Scheduled Task XML File - This sectio will      #
        #  Parse them.                                                            #
        ###########################################################################
        print("[+] Parsing Sched Tasks XML...")
        outfile.write("<hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed information about \n")
        outfile.write("All Scheduled Task XML Files.  Scheduled Tasks are stored under c:\Windows\System32\Tasks \n")
        outfile.write("in Unicode XML Files.  This section simply parses the URI and Command Entries. Review \n")
        outfile.write("These for any suspicious scheduled tasks that could have hostile intent. </font></i></p>\n")

        reccount = 0
        curdir = dirname + "\\sch"
        curCdir = dirname + "\\C\\Windows\\System32\\Tasks"

        ###########################################################################
        # Check for alternate location of Sched Task Collection                   #
        ###########################################################################
        if os.path.isdir(curCdir):
            curdir = curCdir

        if os.path.isdir(curdir):
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=40%> URI (+/-)</th>\n")
            outfile.write("<th width=60%> Command (+/-)</th></tr></thead><tbody>\n")

            for root, dirs, files in os.walk(curdir):
                for fname in files:
                    fnameUpper = fname.upper()
                    curfile = os.path.join(root, fname)

                    task_URI = ""
                    task_Command = ""

                    innfile = open(curfile, encoding='utf16', errors="replace")
                    for innline in innfile:
                        strip_innline = innline.strip()

                        if strip_innline.startswith("<URI>"):
                            task_URI = strip_innline[5:]

                        elif strip_innline.startswith("<Command>"):
                            task_Command = strip_innline[9:]

                    innfile.close()

                    # Is it in our IOC List?
                    RowString = task_URI + task_Command 
                    if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                        PreIOC = " <b><font color=red>"
                        PostIOC = "</font></b> "
                    else: 
                        PreIOC = " "
                        PostIOC = " "

                    outfile.write("<tr><td style=\"text-align: left\" width=40%>" + PreIOC + task_URI + PostIOC + "</td>\n")
                    outfile.write("<td style=\"text-align: left\" width=60%>" + PreIOC + task_Command + PostIOC + "</td></tr>\n")

                    reccount = reccount + 1

            outfile.write("</tbody></table>\n")

            if reccount < 2:
                outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
            else:
                outfile.write("<p>XML Scheduled Tasks Found: " + str(reccount) + "</p>\n")


        else:
            outfile.write("<p><b><font color = red>No XML Scheduled Tasks Were Collected.</font></b></p>\n")

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
        RecType = "None"
        RecName = "None"
        LastRec = ""
        filname = dirname + "\\sys\\IPCfgDNS.dat"
        csvname = dirname + "\\sys\\DNSCache.csv"

        if os.path.isfile(filname):
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            outfile.write("<thead><tr><th width=25%> DNS Request (+/-)</th>\n")
            outfile.write("<th width=25%> Record Name (+/-)</th>\n")
            outfile.write("<th width=25%> Resolution (+/-)</th>\n")
            outfile.write("<th width=25%> Record Type (+/-)</th></tr></thead><tbody\n")

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

                # Is it in our IOC List?
                if any(AnyIOC in RecType.strip().lower() for AnyIOC in IOCList):
                    PreIOC = " <b><font color=red>"
                    PostIOC = "</font></b> "
                else: 
                    PreIOC = " "
                    PostIOC = " "

                if any(AnyIOC in RecName.strip().lower() for AnyIOC in IOCList):
                    PreIOC2 = " <b><font color=red>"
                    PostIOC2 = "</font></b> "
                else: 
                    PreIOC2 = " "
                    PostIOC2 = " "


                if writeRow > 0:
                    outfile.write("<tr><td width=25%>" + DNSRecName.strip() + "</td>\n")

                    if writeRow == 1:
                        outfile.write("<td width=25%>" + PreIOC2 + RecName.strip() + PostIOC2 + "</td>\n")
                        outfile.write("<td width=25%>" + PreIOC + RecType.strip() + PostIOC + "</td>\n")
                        outfile.write("<td width=25%> NA </td></tr>\n")
                    elif writeRow == 2:
                        outfile.write("<td width=25%> <A href=https://www.virustotal.com/#/search/" + RecName.strip().lower() + ">" + PreIOC2 + RecName.strip() + PostIOC2 + "</a> </td>\n")
                        outfile.write("<td width=25%> <A href=https://www.virustotal.com/#/search/" + RecType.strip() + ">" + PreIOC + RecType.strip() + PostIOC + "</a> </td>\n")
                        outfile.write("<td width=25%> A (Host) </td></tr>\n")

                        ipsfileall.write(RecType.strip() + "\n")

                        # Write out Domain for Bulk Lookup 
                        domfileall.write(RecName.strip() + "\n")
                    elif writeRow == 3:
                        outfile.write("<td width=25%>" + PreIOC2 + RecName.strip() + PostIOC2 + "</td>\n")
                        outfile.write("<td width=25%>" + PreIOC + RecType.strip() + PostIOC + "</td>\n")
                        outfile.write("<td width=25%> SRV Record </td></tr>\n")
                    elif writeRow == 4:
                        outfile.write("<td width=25%> <A href=https://www.virustotal.com/#/search/" + RecName.strip().lower() + ">" + PreIOC2 + RecName.strip() + PostIOC2 + "</a> </td>\n")
                        outfile.write("<td width=25%> <A href=https://www.virustotal.com/#/search/" + RecType.strip() + ">" + PreIOC + RecType.strip() + PostIOC + "</a> </td>\n")
                        outfile.write("<td width=25%> PTR Record </td></tr>\n")
                    else:
                        outfile.write("<td width=25%>" + PreIOC2 + RecName.strip() + PostIOC2 + "</td>\n")
                        outfile.write("<td width=25%>" + PreIOC + RecType.strip() + PostIOC + "</td>\n")
                        outfile.write("<td width=25%> Unknown </td></tr>\n")

                    RecName = ""                
                    RecType = ""                
                    writeRow = 0              

                LastRec = innline.strip()

            outfile.write("</tbody></table>\n")
            innfile.close()

        elif os.path.isfile(csvname):
            outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
            with open(csvname, 'r', encoding='utf8', errors="replace") as csvfile:
                csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                for csvrow in csvread:
                    if len(csvrow) > 4:
                        if reccount == 0:
                            tdtr = "th"
                        else:
                            tdtr = "td"

                        if reccount == 0:
                            outfile.write("<thead><tr><" + tdtr + " width=35%> " + csvrow[0] + " (+/-)</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%> " + csvrow[1] + " (+/-)</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%> " + csvrow[2] + " (+/-)</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%> " + csvrow[3] + " (+/-)</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=35%> " + csvrow[4] + " (+/-)</" + tdtr + "></tr></thead><tbody>\n")
                        else:
                            # Is it in our IOC List?
                            RowString = ' '.join(map(str, csvrow))
                            if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                PreIOC2 = " <b><font color=red>"
                                PostIOC2 = "</font></b> "
                            else: 
                                PreIOC2 = " "
                                PostIOC2 = " "

                            outfile.write("<tr><" + tdtr + " width=35%> <A href=https://www.virustotal.com/#/search/" + csvrow[0] + ">" + PreIOC2 + csvrow[0] + PostIOC2 + "</a> </" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%> " + PreIOC2 + csvrow[1] + PostIOC2 + " </" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%> " + PreIOC2 + csvrow[2] + PostIOC2 + " </" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%> " + PreIOC2 + csvrow[3] + PostIOC2 + " </" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=35%> <A href=https://www.virustotal.com/#/search/" + csvrow[4] + ">" + PreIOC2 + csvrow[4] + PostIOC2 + "</a> </" + tdtr + "></tr>\n")

                            # Write out Domain for Bulk Lookup 
                            domfileall.write(csvrow[0].strip() + "\n")

                            # Write out IP Address for Bulk Lookup 
                            ipsfileall.write(csvrow[4].strip() + "\n")

                        reccount = reccount + 1

            outfile.write("</tbody></table>\n")

            if reccount < 2:
                outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
            else:
                outfile.write("<p>Records Found: " + str(reccount) + "</p>\n")

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
            outfile.write("Please note: Some actors have been known to hide malware in the Recycle Bin. \n")
            outfile.write("<font color=gray size=-1><br><br>Source: Parsed Recycle Bin, TZ is in +hh:mm format</font></font></i></p>\n")

            outfile.write("<table border=1 cellpadding=5 width=100%>\n")

            innfile = open(filname, encoding='utf8', errors="replace")
            for innline in innfile:
                # Is it in our IOC List?
                if any(AnyIOC in innline.lower() for AnyIOC in IOCList):
                    PreIOC = " <b><font color=red>"
                    PostIOC = "</font></b> "
                else: 
                    PreIOC = " "
                    PostIOC = " "

                if innline.startswith("Source file: "):
                    outfile.write("<tr><td style=\"text-align: left\">\n")
                    outfile.write("<b>" + PreIOC + innline.strip() + PostIOC + "</b><br>\n")
                    reccount = reccount + 1

                elif innline.startswith("Version: "):
                    outfile.write(PreIOC + innline.strip() + PostIOC + "<br>\n")

                elif innline.startswith("File size: "):
                    outfile.write(PreIOC + innline.strip() + PostIOC + "<br>\n")

                elif innline.startswith("File name: "):
                    outfile.write(PreIOC + innline.strip() + PostIOC + "<br>\n")

                elif innline.startswith("Deleted on:"):
                    outfile.write(PreIOC + innline.strip() + PostIOC + "</td></tr>\n")

            outfile.write(PreIOC + innline.strip() + PostIOC + "</table>\n")

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
    # Run Eric Zimmermans Shell Bags Parser - Use -d to get all dirs          #
    ###########################################################################
    if (RunAllAll == 1 or RunShlBag == 1):
        print("[+] Checking for Eric Zimmerman SBECmd...")

        if os.path.isfile(".\\SBECmd\\SBECmd.exe") == False:
            print("[?] Shell Bags Explorer - SBECmd executable not found...  Would you like to Download it...")
            YesOrNo = input("[?] Y/N > ")

            if YesOrNo.upper() == "Y":
                print("[+] Downloading Eric Zimmerman Shell Bags Explorer...")

                if not os.path.exists('.\\SBECMD'):
                    os.makedirs('.\\SBECMD')

                ShlBUrl = 'https://f001.backblazeb2.com/file/EricZimmermanTools/SBECmd.zip'
                ShlBReq = requests.get(ShlBUrl, allow_redirects=True)
                open('.\\SBECmd\\SBECmd.zip', 'wb').write(ShlBReq.content)

                print("[+] Unzipping Shell Bags Explorer - SBECmd...")
                with ZipFile('.\\SBECMD\\SBECmd.zip', 'r') as zipObj:
                    # Extract all the contents of zip file in current directory
                    zipObj.extractall(path='.\\SBECmd')
            else:
                print("[!] Shell Bags Explorer Download Bypassed...")


        if os.path.isfile(".\\SBECmd\\SBECmd.exe"):
            print("[+] Shell Bags Explorer executable found")
            print("[+] Running Shell Bags Explorer against all Collection directories...")

            ShlBSubDir = ""

            ShlName = dirname
            cmdexec = ".\\SBECmd\\SBECmd.exe -d " + ShlName + " --csv .\ShellBags --nl --dt \"yyyy-MM-dd HH:mm:ss K\""
            returned_value = os.system(cmdexec)


            outfile.write("<a name=ShellBags></a>\n")
            outfile.write("<input class=\"collapse\" id=\"id31\" type=\"checkbox\" checked>\n")
            outfile.write("<label for=\"id31\">\n")
            outfile.write("<H2>Shell Bags Output</H2>\n")
            outfile.write("</label><div><hr>\n")

            outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed Eric Zimmermans \n")
            outfile.write("Shell Bags Explorer Data.  Shell Bags Explorer parses the Shell Bags Registry \n")
            outfile.write("entries in NTUSER.DAT and USRCLASS.DAT files.  Shell Bags are useful in identifying\n")
            outfile.write("directory accesses by each user/profile.<font color=gray size=-1><br><br>Source: Parsed Shellbags, TZ is in +hh:mm format</font></font></i></p>\n")

            ###########################################################################
            # Parse all SBECmd csv files                                              #
            ###########################################################################
            if os.path.isdir(".\\ShellBags"):
                for SBName in os.listdir(".\ShellBags"):

                    if SBName.endswith(".csv"):
                        outfile.write("<p><i><font color=firebrick>Processing: " + SBName + " </font></i></p>\n")
                        outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")

                        reccount = 0
                        with open(".\\ShellBags\\" + SBName, 'r', encoding='utf8', errors="replace") as csvfile:
                            csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                            for csvrow in csvread:
                                if len(csvrow) > 3:
                                    if reccount == 0:
                                        tdtr = "th"
                                    else:
                                        tdtr = "td"

                                    # Is it in our IOC List?
                                    RowString = ' '.join(map(str, csvrow))
                                    if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                        PreIOC = " <b><font color=red>"
                                        PostIOC = "</font></b> "
                                    else: 
                                        PreIOC = " "
                                        PostIOC = " "

                                    if reccount == 0:
                                        outfile.write("<thead>\n")
                                        PostIOC += " (+/-)"

                                    outfile.write("<tr><" + tdtr + " width=11%>" + PreIOC + csvrow[5] + "</" + tdtr + ">\n")
                                    outfile.write("<" + tdtr + " width=50%>" + PreIOC + csvrow[4] + PostIOC + "</" + tdtr + ">\n")
                                    outfile.write("<" + tdtr + " width=13%>" + PreIOC + csvrow[15] + PostIOC + "</" + tdtr + ">\n")
                                    outfile.write("<" + tdtr + " width=13%>" + PreIOC + csvrow[16] + PostIOC + "</" + tdtr + ">\n")
                                    outfile.write("<" + tdtr + " width=13%>" + PreIOC + csvrow[11] + PostIOC + "</" + tdtr + "></tr>\n")

                                    if reccount == 0:
                                        outfile.write("</thead><tbody>\n")

                                    reccount = reccount + 1

                        outfile.write("</tbody></table>\n")
                        os.remove(".\\ShellBags\\" + SBName)

                        if reccount < 2:
                            outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
                        else:
                            outfile.write("<p>Records Found: " + str(reccount) + "</p><hr>\n")


                outfile.write("</div>\n")

            else:
                print("[!] No Shell Bags Parsed!  Bypassing Shell Bags Processing...")

        else:
            print("[!] Shell Bags Explorer Executable not found!  Bypassing Shell Bags Processing...")

    else:
        print("[!] Bypassing Shell Bags Processing...")


    ###########################################################################
    # Run Countercept Chainsaw Program against all .EVTX Files                #
    # [+] audit_log_was_cleared.csv                                           #
    # [+] system_log_was_cleared.csv                                          #
    # [+] suspicious_process_creation.csv                                     #
    # [+] suspicious_registry_event.csv                                       #
    # [+] suspicious_file_creation.csv                                        #
    # [+] user_added_to_interesting_group.csv                                 #
    # [+] windows_defender_detections.csv                                     #
    # [+] 4624_logins.csv                                                     #
    ###########################################################################
    if (RunAllAll == 1 or RunChnSaw == 1) and SrcEvtx == 1:
        print("[+] Checking for F-Secure Countercept Chainsaw...")

        if os.path.isfile(".\\chainsaw\\chainsaw_x86_64-pc-windows-msvc.exe") == False:
            print("[?] Chainsaw executable not found...  Would you like to Download F-Secure Countercept...")
            YesOrNo = input("[?] Y/N > ")

            if YesOrNo.upper() == "Y":
                print("[+] Downloading F-Secure Countercept Chainsaw From Github...")
                ChSwUrl = 'https://github.com/WithSecureLabs/chainsaw/releases/download/v2.3.1/chainsaw_all_platforms+rules+examples.zip'
                ChSwReq = requests.get(ChSwUrl, allow_redirects=True)
                open('Chainsaw.zip', 'wb').write(ChSwReq.content)

                print("[+] Unzipping F-Secure Countercept Chainsaw...")
                with ZipFile('Chainsaw.zip', 'r') as zipObj:
                    # Extract all the contents of zip file in current directory
                    zipObj.extractall()
            else:
                print("[!] Chainsaw Download Bypassed...")


        if os.path.isfile(".\\chainsaw\\chainsaw_x86_64-pc-windows-msvc.exe"):
            print("[+] Chainsaw executable found")
            print("[+] Running F-Secure Countercept Chainsaw against all Event Logs...")

            ChSwSubDir = ""

            EvtName = dirname + "\\evt\\sys32\\"
            cmdexec = ".\\chainsaw\\chainsaw_x86_64-pc-windows-msvc.exe hunt --skip-errors --timezone UTC --full --csv --output .\\ChainCSV --mapping .\\chainsaw\\mappings\\sigma-event-logs-all.yml --rule .\\chainsaw\\rules --sigma .\\chainsaw\\sigma " + EvtName
            returned_value = os.system(cmdexec)

            outfile.write("<a name=ChainSaw></a>\n")
            outfile.write("<input class=\"collapse\" id=\"id28\" type=\"checkbox\" checked>\n")
            outfile.write("<label for=\"id28\">\n")
            outfile.write("<H2>ChainSaw Output</H2>\n")
            outfile.write("</label><div><hr>\n")

            outfile.write("<p><i><font color=firebrick>In this section, AChoir has parsed F-Secure Countercept\n")
            outfile.write("Chainsaw Data.  Chainsaw provides a powerful ‘first-response’ capability to quickly\n")
            outfile.write("identify threats within Windows event logs. It offers a generic and fast method of\n")
            outfile.write("searching through event logs for keywords, and by identifying threats using built-in\n")
            outfile.write("detection logic and via support for Sigma detection rules.<font color=gray size=-1><br><br>Source: Parsed Event Logs, TZ is in +hh:mm format</font></font></i></p>\n")


            ###########################################################################
            # Chainsaw: Log Tampering                                                 #
            ###########################################################################
            for ChName in glob.glob('.\\**\\log_tampering.csv', recursive=True):
                outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
                outfile.write("<p><i><font color=firebrick>Log Tampering:</font></i></p>\n")

                reccount = 0
                with open(ChName, 'r', encoding='utf8', errors="replace") as csvfile:
                    csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                    for csvrow in csvread:
                        if len(csvrow) > 3:
                            if reccount == 0:
                                tdtr = "th"
                            else:
                                tdtr = "td"

                            # Is it in our IOC List?
                            RowString = ' '.join(map(str, csvrow))
                            if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                PreIOC = " <b><font color=red>"
                                PostIOC = "</font></b> "
                            else: 
                                PreIOC = " "
                                PostIOC = " "

                            if reccount == 0:
                                outfile.write("<thead>\n")
                                PostIOC += " (+/-)"

                            outfile.write("<tr><" + tdtr + " width=20%>" + PreIOC + csvrow[0] + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=40%>" + PreIOC + csvrow[1] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[4] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=20%>" + PreIOC + csvrow[5] + PostIOC + "</" + tdtr + "></tr>\n")

                            if reccount == 0:
                                outfile.write("</thead><tbody>\n")

                            reccount = reccount + 1

                outfile.write("</tbody></table>\n")
                os.remove(ChName)

                if ChSwSubDir == "":
                    Path_File = os.path.split(ChName)
                    ChSwSubDir = Path_File[0]

                if reccount < 2:
                    outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
                else:
                    outfile.write("<p>Records Found: " + str(reccount) + "</p><hr>\n")


            ###########################################################################
            # Chainsaw: Account Tampering                                             #
            ###########################################################################
            for ChName in glob.glob('.\\**\\account_tampering.csv', recursive=True):
                outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
                outfile.write("<p><i><font color=firebrick>Account Tampering:</font></i></p>\n")

                reccount = 0
                with open(ChName, 'r', encoding='utf8', errors="replace") as csvfile:
                    csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                    for csvrow in csvread:
                        if len(csvrow) > 3:
                            if reccount == 0:
                                tdtr = "th"
                            else:
                                tdtr = "td"

                            # Is it in our IOC List?
                            RowString = ' '.join(map(str, csvrow))
                            if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                PreIOC = " <b><font color=red>"
                                PostIOC = "</font></b> "
                            else: 
                                PreIOC = " "
                                PostIOC = " "

                            if reccount == 0:
                                outfile.write("<thead>\n")
                                PostIOC += " (+/-)"

                            outfile.write("<tr><" + tdtr + " width=20%>" + PreIOC + csvrow[0] + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=30%>" + PreIOC + csvrow[1] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[4] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[5] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=20%>" + PreIOC + csvrow[7] + PostIOC + "</" + tdtr + "></tr>\n")

                            if reccount == 0:
                                outfile.write("</thead><tbody>\n")

                            reccount = reccount + 1

                outfile.write("</tbody></table>\n")
                os.remove(ChName)

                if ChSwSubDir == "":
                    Path_File = os.path.split(ChName)
                    ChSwSubDir = Path_File[0]

                if reccount < 2:
                    outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
                else:
                    outfile.write("<p>Records Found: " + str(reccount) + "</p><hr>\n")


            ###########################################################################
            # Chainsaw: Login Attacks                                                 #
            ###########################################################################
            for ChName in glob.glob('.\\**\\login_attacks.csv', recursive=True):
                outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
                outfile.write("<p><i><font color=firebrick>Login Attacks:</font></i></p>\n")

                reccount = 0
                with open(ChName, 'r', encoding='utf8', errors="replace") as csvfile:
                    csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                    for csvrow in csvread:
                        if len(csvrow) > 3:
                            if reccount == 0:
                                tdtr = "th"
                            else:
                                tdtr = "td"

                            # Is it in our IOC List?
                            RowString = ' '.join(map(str, csvrow))
                            if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                PreIOC = " <b><font color=red>"
                                PostIOC = "</font></b> "
                            else: 
                                PreIOC = " "
                                PostIOC = " "

                            if reccount == 0:
                                outfile.write("<thead>\n")
                                PostIOC += " (+/-)"

                            outfile.write("<tr><" + tdtr + " width=20%>" + PreIOC + csvrow[0] + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=40%>" + PreIOC + csvrow[1] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[3] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=20%>" + PreIOC + csvrow[4] + PostIOC + "</" + tdtr + "></tr>\n")

                            if reccount == 0:
                                outfile.write("</thead><tbody>\n")

                            reccount = reccount + 1

                outfile.write("</tbody></table>\n")
                os.remove(ChName)

                if ChSwSubDir == "":
                    Path_File = os.path.split(ChName)
                    ChSwSubDir = Path_File[0]

                if reccount < 2:
                    outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
                else:
                    outfile.write("<p>Records Found: " + str(reccount) + "</p><hr>\n")


            ###########################################################################
            # Chainsaw: Antivirus Detections                                          #
            ###########################################################################
            for ChName in glob.glob('.\\**\\antivirus.csv', recursive=True):
                outfile.write("<table class=\"sortable\" valign=top border=1 cellpadding=5 width=100%>\n")
                outfile.write("<p><i><font color=firebrick>Antivirus Detections:</font></i></p>\n")

                reccount = 0
                with open(ChName, 'r', encoding='utf8', errors="replace") as csvfile:
                    csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                    for csvrow in csvread:
                        if len(csvrow) > 5:
                            if reccount == 0:
                                tdtr = "th"
                            else:
                                tdtr = "td"

                            # Is it in our IOC List?
                            RowString = ' '.join(map(str, csvrow))
                            if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                PreIOC = " <b><font color=red>"
                                PostIOC = "</font></b> "
                            else: 
                                PreIOC = " "
                                PostIOC = " "

                            if reccount == 0:
                                outfile.write("<thead>\n")
                                PostIOC += " (+/-)"

                            outfile.write("<tr><" + tdtr + " valign=top width=15%>" + PreIOC + csvrow[0] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=15%>" + PreIOC + csvrow[1] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=5%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=10%>" + PreIOC + csvrow[4] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=10%>" + PreIOC + csvrow[5] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=10%>" + PreIOC + csvrow[6] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=10%>" + PreIOC + csvrow[7] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=15%>" + PreIOC + csvrow[8] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=10%>" + PreIOC + csvrow[9] + PostIOC + "</" + tdtr + "></tr>\n")

                            if reccount == 0:
                                outfile.write("</thead><tbody>\n")

                            reccount = reccount + 1
                outfile.write("</tbody></table>\n")
                os.remove(ChName)

                if ChSwSubDir == "":
                    Path_File = os.path.split(ChName)
                    ChSwSubDir = Path_File[0]

                if reccount < 2:
                    outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
                else:
                    outfile.write("<p>Records Found: " + str(reccount) + "</p><hr>\n")



            ###########################################################################
            # Chainsaw: Lateral Movement                                              #
            ###########################################################################
            for ChName in glob.glob('.\\**\\lateral_movement.csv', recursive=True):
                outfile.write("<table class=\"sortable\" valign=top border=1 cellpadding=5 width=100%>\n")
                outfile.write("<p><i><font color=firebrick>Lateral Movement Detections:</font></i></p>\n")

                reccount = 0
                with open(ChName, 'r', encoding='utf8', errors="replace") as csvfile:
                    csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                    for csvrow in csvread:
                        if len(csvrow) > 5:
                            if reccount == 0:
                                tdtr = "th"
                            else:
                                tdtr = "td"

                            # Is it in our IOC List?
                            RowString = ' '.join(map(str, csvrow))
                            if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                PreIOC = " <b><font color=red>"
                                PostIOC = "</font></b> "
                            else: 
                                PreIOC = " "
                                PostIOC = " "

                            if reccount == 0:
                                outfile.write("<thead>\n")
                                PostIOC += " (+/-)"

                            outfile.write("<tr><" + tdtr + " valign=top width=20%>" + PreIOC + csvrow[0] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=20%>" + PreIOC + csvrow[1] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=5%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=15%>" + PreIOC + csvrow[4] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=15%>" + PreIOC + csvrow[5] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=5%>" + PreIOC + csvrow[6] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " valign=top width=20%>" + PreIOC + csvrow[7] + PostIOC + "</" + tdtr + "></tr>\n")

                            if reccount == 0:
                                outfile.write("</thead><tbody>\n")

                            reccount = reccount + 1
                outfile.write("</tbody></table>\n")
                os.remove(ChName)

                if ChSwSubDir == "":
                    Path_File = os.path.split(ChName)
                    ChSwSubDir = Path_File[0]

                if reccount < 2:
                    outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
                else:
                    outfile.write("<p>Records Found: " + str(reccount) + "</p><hr>\n")


            ###########################################################################
            # Chainsaw: Sigma Detections                                              #
            ###########################################################################
            for ChName in glob.glob('.\\**\\sigma.csv', recursive=True):
                outfile.write("<table class=\"sortable\" border=1 cellpadding=5 width=100%>\n")
                outfile.write("<p><i><font color=firebrick>Sigma Rule(s) Detections:</font></i></p>\n")

                reccount = 0
                with open(ChName, 'r', encoding='utf8', errors="replace") as csvfile:
                    csvread = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',')
                    for csvrow in csvread:
                        if len(csvrow) > 3:
                            if reccount == 0:
                                tdtr = "th"
                            else:
                                tdtr = "td"

                            # Is it in our IOC List?
                            RowString = ' '.join(map(str, csvrow))
                            if any(AnyIOC in RowString.lower() for AnyIOC in IOCList):
                                PreIOC = " <b><font color=red>"
                                PostIOC = "</font></b> "
                            else: 
                                PreIOC = " "
                                PostIOC = " "

                            if reccount == 0:
                                outfile.write("<thead>\n")
                                PostIOC += " (+/-)"

                            outfile.write("<tr><" + tdtr + " width=20%>" + PreIOC + csvrow[0] + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=30%>" + PreIOC + csvrow[1] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=5%>" + PreIOC + csvrow[2] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=5%>" + PreIOC + csvrow[3] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=10%>" + PreIOC + csvrow[6] + PostIOC + "</" + tdtr + ">\n")
                            outfile.write("<" + tdtr + " width=30%>" + PreIOC + csvrow[7] + PostIOC + "</" + tdtr + "></tr>\n")

                            if reccount == 0:
                                outfile.write("</thead><tbody>\n")

                            reccount = reccount + 1

                outfile.write("</tbody></table>\n")
                os.remove(ChName)

                if ChSwSubDir == "":
                    Path_File = os.path.split(ChName)
                    ChSwSubDir = Path_File[0]

                if reccount < 2:
                    outfile.write("<p><b><font color = red> No Data Found! </font></b></p>\n")
                else:
                    outfile.write("<p>Records Found: " + str(reccount) + "</p><hr>\n")


            ###########################################################################
            # Chainsaw: See if we have any Unprocessed Files                          #
            ###########################################################################
            reccount = 0
            ChSwLeftOvers = ChSwSubDir + "\\**\*.csv"

            if ChSwSubDir != "":
                for ChName in glob.glob(ChSwLeftOvers, recursive=True):
                    print("[!] Unprocessed F-Secure Countercept Chainsaw File: " + ChName)
                    reccount = reccount + 1

            if reccount == 0:
                print("[+] No Unprocessed Chainsaw Files. Deleting ChainSaw Directory: " + ChSwSubDir)
                if ChSwSubDir != "":
                    shutil.rmtree(ChSwSubDir)
            else:
                print("[+] There are Unprocessed Chainsaw Files. So I WILL NOT Delete the ChainSaw Directory")
                print("[!] WARNING: Next Time AChReport Runs, IT WILL DELETE THESE FILES!")

        else:
            print("[!] Chainsaw Executable not found!  Bypassing Chainsaw Processing...")

    else:
        print("[!] Bypassing Chainsaw Processing...")


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
                    # Is it in our IOC List?
                    if any(AnyIOC in ipsline.lower() for AnyIOC in IOCList):
                        PreIOC = " <b><font color=red>"
                        PostIOC = "</font></b> "
                    else: 
                        PreIOC = " "
                        PostIOC = " "

                    outfile.write(PreIOC + ipsline + PostIOC + "<br>")

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
                    # Is it in our IOC List?
                    if any(AnyIOC in hshline.lower() for AnyIOC in IOCList):
                        PreIOC = " <b><font color=red>"
                        PostIOC = "</font></b> "
                    else: 
                        PreIOC = " "
                        PostIOC = " "

                    outfile.write(PreIOC + hshline + PostIOC + "<br>")

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
                    # Is it in our IOC List?
                    if any(AnyIOC in domline.lower() for AnyIOC in IOCList):
                        PreIOC = " <b><font color=red>"
                        PostIOC = "</font></b> "
                    else: 
                        PreIOC = " "
                        PostIOC = " "

                    outfile.write(PreIOC + domline + PostIOC + "<br>")

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
    # Write out the IOCs configured in the .cfg file                          #
    ###########################################################################
    if HasIOCs == 1:
        print("[+] Writing IOCs to Report...")

        outfile.write("<a name=IOCList></a>\n")
        outfile.write("<input class=\"collapse\" id=\"id32\" type=\"checkbox\" checked>\n")
        outfile.write("<label for=\"id32\">\n")
        outfile.write("<H2>IOCs to Search For</H2>\n")
        outfile.write("</label><div><hr>\n")

        outfile.write("<p><i><font color=firebrick>In this section, AChoir is listing the IOCs configured \n")
        outfile.write("in the " + cfgname + "configuration file used for this report. If these IOCs are  \n")
        outfile.write("found in the telemetry or artifacts, they will be higlighted in red in this report. \n")
        outfile.write("Using IOCs helps to make relevant data easier to find by making it stand out. \n")
        outfile.write("</b></font></i></p>\n")


        reccount = 0

        for thisIOC in IOCList:
            outfile.write(thisIOC + "<br>\n")
            reccount = reccount + 1

        if reccount < 1:
            outfile.write("<p><b><font color = red> No IOC Search Found! </font></b></p>\n")
        else:
            outfile.write("<p>Records Found: " + str(reccount) + "<br>\n")

        outfile.write("</div>\n")


    ###########################################################################
    #Write HTML Trailer Data                                                  #
    ###########################################################################
    outfile.write("<hr><h1><Center> * * * End Report * * * </Center></h1>\n")
    outfile.write("</body></html>\n")
    outfile.close() 

    print("[+] AChoir Report Processing Complete!\n")



if __name__ == "__main__":
    main()
