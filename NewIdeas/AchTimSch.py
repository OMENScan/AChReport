#!/usr/bin/env python
####################################################################### 
# Version: v0.1 (Python 3.x)                                          #
# Author.: David Porco                                                #
# Release: 12/29/2019                                                 #
#                                                                     #
#   Read the artifacts output by AChoir and create a plaso timeline   #
#   - This Python Proram is essentially the same as Plaso.Acq         #
####################################################################### 
import fnmatch
import msvcrt
import os
import sys
import csv
import time 
import argparse
import ctypes


###########################################################################
# Parse Configuration Options
###########################################################################
parser = argparse.ArgumentParser(description="Format AChoir Output Telemetry into a Report")
parser.add_argument("-d", dest="dirname", help="Specify AChReport Directory - Must Contain the AChoir, AChInput, and AchOutput Subdirs")
args = parser.parse_args()


###########################################################################
# Main 
###########################################################################
def main():
    #######################################################################
    # Specify all AchReport Directories
    #######################################################################
    dirname = str(args.dirname)
    achname = dirname + "\\AChoir"
    srcname = dirname + "\\AChInput"
    dstname = dirname + "\\AChOutput"
    plsname = dirname + "\\AChoir\\Plaso"

    if dirname == "None":
        dirname = "C:\AChReport"    

    if os.path.exists(dirname):
        print("[+] Valid AChReport Root Directory Found.")
    else:
        print("[!] No Valid AChReport Root Directory Found.")
        sys.exit(1)

    if os.path.exists(plsname):
        print("[+] Valid AChReport/Plaso Root Directory Found.")
    else:
        print("[!] No Valid AChReport/Plaso Root Directory Found.")
        sys.exit(1)

    if os.path.exists(achname):
        print("[+] Valid AChoir Software Directory Found.")
    else:
        print("[!] No Valid AChoir Software Directory Found.")
        sys.exit(1)

    if os.path.exists(srcname):
        print("[+] Valid AChoir Input Telemetry / Collection Directory Found.")
    else:
        print("[!] No Valid AChoir Input Telemetry / Collection Directory Found.")
        sys.exit(1)

    if os.path.exists(dstname):
        print("[+] Valid AChReport Output Directory Found.")
    else:
        print("[!] No Valid AChReport Output Directory Found.")
        sys.exit(1)


    ###########################################################################
    # Checking Input Directory for Telemetry to Process
    ###########################################################################
    for roox, dirx, filex in os.walk(srcname):
        for dname in dirx:
            srcfull = srcname + "\\" + dname
            bdyname = dstname + "\\" + dname + ".body"
            csvname = dstname + "\\" + dname + ".csv"

            print ("[+] Found Achoir Telemetry Directory: " + dname)
            if os.path.isfile(csvname):
                print("[+] AChreport: " + csvname + " Already Processed, Bypassing...\n\n")
                continue


            ###########################################################################
            # Checking to see if the Collection is growing (Still in progress)
            ###########################################################################
            print("[+] Sanity Checks in Progress...")
            oldcount = 0
            newcount = 0
            evtflag = 0
            regflag = 0
            arnflag = 0
            mftflag = 0

            for root, dirs, files in os.walk(srcfull):
                for fname in files:
                    fnamelc = fname.lower()

                    if fnamelc == "application.evtx":
                        evtflag = evtflag + 1
                    if fnamelc == "software":
                        regflag = regflag + 1
                    if fnamelc == "autorun.dat":
                        arnflag = arnflag + 1
                    if fnamelc == "$mft":
                        mftflag = mftflag + 1

                    oldcount = oldcount + 1

            time.sleep(60)

            for root, dirs, files in os.walk(srcfull):
                for fname in files:
                    newcount = newcount + 1
  
            if newcount == oldcount:
                print("    [+] Collection is stable at: " + str(newcount) + " Files")
            else:
                print("    [+] Collection is still growing...  Bypassing...\n\n")
                continue

            if arnflag == 0:
                print("[+] Sanity Check Failed - Missing Autoruns File...")
                continue
            if regflag == 0:
                print("[+] Sanity Check Failed - Missing Registry File...")
                continue
            if mftflag == 0:
                print("[+] Sanity Check Failed - Missing $MFT File...")
                continue
            if evtflag == 0:
                print("[+] Sanity Check Failed - Missing Event Log File...")
                continue


            ###########################################################################
            # Fell Through, Now Process the files and extract data for report
            #  Starting with $MFT Files
            ###########################################################################
            print("[+] Now Timelining MFT Files...")

            reccount = 0
            curdir = srcfull + "\\RawData"

            for root, dirs, files in os.walk(curdir):
                for fname in fnmatch.filter(files, '$MFT*'):
                    curfile = os.path.join(root, fname)

                    cmdexec = achname + "\\Plaso\\Log2TimeLine.exe -z \"UTC\" --parsers \"win7_slow\" --status_view \"none\" --quiet --logfile " + dstname + "\\Temp.Log" + " " + bdyname + " \"" + curfile + "\""
                    returned_value = os.system(cmdexec)

                    reccount = reccount + 1

            print("[+] $MFT Files Timelined: " + str(reccount))


            ###########################################################################
            # Now Process Event Viewer Logs
            ###########################################################################
            print("[+] Now Timelining Event Viewer Log Files...")

            reccount = 0
            curdir = srcfull + "\\Evt"

            for root, dirs, files in os.walk(curdir):
                for fname in fnmatch.filter(files, '*.evtx'):
                    curfile = os.path.join(root, fname)

                    cmdexec = achname + "\\Plaso\\Log2TimeLine.exe -z \"UTC\" --parsers \"win7_slow\" --status_view \"none\" --quiet --logfile " + dstname + "\\Temp.Log" + " " + bdyname + " \"" + curfile + "\""
                    returned_value = os.system(cmdexec)

                    reccount = reccount + 1

            print("[+] Event Log Files Timelined: " + str(reccount))


            ###########################################################################
            # Now Process Prefetch
            ###########################################################################
            print("[+] Now Timelining Prefetch Files...")

            reccount = 0
            curdir = srcfull + "\\Prf"

            for root, dirs, files in os.walk(curdir):
                for fname in files:
                    curfile = os.path.join(root, fname)

                    cmdexec = achname + "\\Plaso\\Log2TimeLine.exe -z \"UTC\" --parsers \"win7_slow\" --status_view \"none\" --quiet --logfile " + dstname + "\\Temp.Log" + " " + bdyname + " \"" + curfile + "\""
                    returned_value = os.system(cmdexec)

                    reccount = reccount + 1

            print("[+] Prefetch Files Timelined: " + str(reccount))


            ###########################################################################
            # Now Process Registry Files 
            ###########################################################################
            print("[+] Now Timelining Registry Files...")

            reccount = 0
            curdir = srcfull + "\\Reg"

            for root, dirs, files in os.walk(curdir):
                for fname in files:
                    curfile = os.path.join(root, fname)

                    cmdexec = achname + "\\Plaso\\Log2TimeLine.exe -z \"UTC\" --parsers \"win7_slow\" --status_view \"none\" --quiet --logfile " + dstname + "\\Temp.Log" + " " + bdyname + " \"" + curfile + "\""
                    returned_value = os.system(cmdexec)

                    reccount = reccount + 1

            print("[+] Event Log Files Timelined: " + str(reccount))


            ###########################################################################
            # Now Convert BodyFile to CSV  
            ###########################################################################
            print("[+] Now Convering BodyFile to CSV Format...")

            cmdexec = achname + "\\Plaso\\psort.exe -z \"UTC\" -o l2tcsv -w " + csvname + " " + bdyname
            returned_value = os.system(cmdexec)

            print("[+] BodyFile Coverted to CSV for post Processing")


            print("[+] Processing Completed for: " + dname + "\n\n")

        ###########################################################################
        # del dirx[:] - This is to prevent recursion - we just want one Dir Level #
        ###########################################################################
        del dirx[:] # or a break here. does the same thing.


    print("[+] AChoir Plaso Timeline Processing Complete!\n")



if __name__ == "__main__":
    main()
