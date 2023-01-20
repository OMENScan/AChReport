# AChReport is now TriageReport

A Python based Report Writer which was created for AChoir(X), but can now be used with other Triage Collection Data.

I have had a difficult time finding a simple solution that can take the most common Windows artifacts and present them in a simple way, in order to get a quick, general idea of what has happened on a machine.

Since Live Response and Dead-Box analysis often look at the same artifacts, I wanted a simple report that could take the most common Windows artifacts (i.e. Registry, $MFT, Event Logs, etc...) and present their data in a way that a junior Incident Responder/Analyst could use and understand.  TriageReport (AChReport) is meant as a tool to help Responders (junior or senior) to quickly identify obvious signs of compromise or attack, and quickly determine if deeper analysis is necessary.

The goals were to: Shorten the time it takes to get an overview of the machine, Allow junior or senior Responders to quickly understand what has happened on a machine, and Produce a standardized digital report that can be shared among responders to review a machine.  By standardizing the report I also hope it can be a tool for entry level Incident Responders to learn from.

I believe that this is likely to become increasingly important as laws begin to mandate things like 72 hour breach notification.  Senior level Responders and Forensicators are becoming harder to find, and the only way to meet the increased demand is to make the artifacts easier to consume and understand.

Since AChoir(X) can already extract these common Windows artifacts (Live Response OR Dead-Box), it was simply a matter of writing a program to extract and present the most useful INFORMATION from these artifacts.  AChReport turns Artifacts into Information, by selecting only the most important information needed for a quick view, and presenting that Information in a simple to read, self contained HTML report.

TriageReport (AChReport) IS NOT meant as a comprehensive reporting tool.  It's power is in extracting the most important information and presenting it in an easy to understand format.  TriageReport (AChReport) IS NOT meant to replace your favorite forensics tool.  It is meant to meet the need for a quick, simple view of a machine.

TriageReport (AChReport) can be configured to select which Sections to generate in the report via the AChReport.cfg file

Use -c <ConfigFileName> for different report configurations.

IMPORTANT NOTE: TriageReport (AChReport) reads the Artifacts extracted by AChoir(X), and other Triage collection programs. However, it REQUIRES AChoir(X) to be installed to function.  TriageReport (AChReport) DOES NOT extract the artifacts, it simply parses, filters and reports on those artifacts using many of the same forensics utilities installed with AChoir(X)..

# Some Things to Know

1. TriageReport (AChReport) requires Python to be installed
2. TriageReport (AChReport) requires AChoir(X) to be installed
3. TriageReport (AChReport) requires that an AChoir or other Triage extraction was performed (Live Response or Dead-Box)
4. TriageReport (AChReport) requires a few additional components including: MS LogParser in the same directory as AChReport.py, and some RegRipper plugins in a subdirectory called "plugins"
5. TriageReport (AChReport) is meant to run on Windows
6. TriageReport (AChReport) now supports AChoir, the Windows collections of AChoirX, and Velociraptor
7. TriageReport (AChReport) can now download and integrate F-secure Countercept Chainsaw
8. TriageReport (AChReport) can now download and integrate Eric Zimmerman's LECmd to parse LNK files
9. TriageReport (AChReport) can now download and integrate Eric Zimmerman's SBECmd to parse Shell Bags
10. TriageReport (AChReport) can highlight IOCs (use the AChReport.cfg file to configure the IOCS to highlight)

RegRipper can be found at:
 https://github.com/keydet89/RegRipper2.8
 https://github.com/keydet89/RegRipper3.0

Microsoft LogParser can be found at:
 https://www.microsoft.com/en-us/download/details.aspx?id=24659

F-Secure Countercept Chainsaw was originally here:
 https://github.com/countercept/chainsaw

Note: Chainsaw can now be found here:
 https://github.com/WithSecureLabs/chainsaw

Eric Zimmerman's LECmd, and SBECmd can be found at:
 https://ericzimmerman.github.io/#!index.md


# Configuration

The AChReport.cfg file has multiple configuration settings that make it extremely flexible:

     Run:[The Report Section to run]

     Brander:[Custom Header Text]
     PreConv:[Run a Pre-Conversion Proram against the data]
     Collect:[AChoir, or Velociraptor]
     MFTFile:[Subdirectory Location of the $MFT]
     RegSoft:[Subdirectory Location of the SOFTWARE Registry Hive]
     RegSyst:[Subdirectory Location of the SYSTEM Registry Hive]
     RegUser:[Subdirectory Location of the User Registry Hives]
     AmCache:[Subdirectory Location of the AmCache Hive]
     Prefetc:[Subdirectory Location of the Prefetch Files]
     EvtDir1:[Subdirectory Location of the Event Logs]
     EvtDir2:[Subdirectory Location of the Event Logs (Secondary Location)]
     Recycle:[Subdirectory Location of the Recycle Bin]
     Browser:[Subdirectory Location of the Collected Browser Data]
     IPConns:[Subdirectory Location of the Collected IP Connection Data]
     UsrAsst:[Subdirectory Location of the Collected User Assist Data]
     Powersh:[Subdirectory Location of the Collected User Powershell logs]
     LNKFile:[Subdirectory Location of the User LNK Files]
     AutoRun:[Subdirectory Location of the Collected Autoruns Data]
     SchTsk1:[Subdirectory Location of the Collected Scheduled Task Data]
     SchTsk2:[Subdirectory Location of the Collected Schedued Task XML Files]
     DNSIpcf:[Subdirectory Location of the DNS Data (ipconfig /displaydns)]
     DNSCach:[Subdirectory Location of the Collected DNS Cache Data]
     ShelBag:[Subdirectory Location of the User Shellbags Registry Hives]

     IOC:[Simple Text String to Highlight in RED]

The IOC: options allows the analyst to identify strings in the report to highlight in RED.
For instance, if the analyst knows that IP Address 1.2.3.4 is an Indicator, they can
add IOC:1.2.3.4 in the configuration file, and anywhere that TriageReport (AChReport) encounters 
that string, it will highlight the entry in RED. The goal is to make known indicators easy
to identify in the report.

# Table Sorting
Tables in the TriageReport (AChReport) are now sortable, using the most excellent sortable - a tiny, vanilla 
JS table sorter.  Which can be found here: https://github.com/tofsjonas/sortable

# Command Line Arguments

To run TriageReport (AChReport) use the -d switch to point to the AChoir extract directory.  For Example:

     py TriageReport.py -d c:\Achoir\ACQ-IR-PCName-20181116_1847

To run TriageReport (AChReport) with an alternate configuration file use the -c option. For Example, to use a config file called Achreport-Alt.cfg:

     py TriageReport.py -d c:\Achoir\ACQ-IR-PCName-20181116_1847 -c Achreport-Alt.cfg
