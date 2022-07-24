# AChReport
A Python based Report Writer for AChoir

I have had a difficult time finding a simple solution that can take the most common Windows artifacts and present them in a simple way, in order to get a quick, general idea of what has happened on a machine.

Since Live Response and Dead-Box analysis often look at the same artifacts, I wanted a simple report that could take the most common Windows artifacts (i.e. Registry, $MFT, Event Logs, etc...) and present their data in a way that a junior Incident Responder/Analyst could use and understand.  AChReport is meant as a tool to help Responders (junior or senior) to quickly identify obvious signs of compromise or attack, and quickly determine if deeper analysis is necessary.

The goals were to: Shorten the time it takes to get an overview of the machine, Allow junior or senior Responders to quickly understand what has happened on a machine, and Produce a standardized digital report that can be shared among responders to review a machine.  By standardizing the report I also hope it can be a tool for entry level Incident Responders to learn from.

I believe that this is likely to become increasingly important as laws begin to mandate things like 72 hour breach notification.  Senior level Responders and Forensicators are becoming harder to find, and the only way to meet the increased demand is to make the artifacts easier to consume and understand.

Since AChoir can already extract these common Windows artifacts (Live Response OR Dead-Box), it was simply a matter of writing a program to extract and present the most useful INFORMATION from these artifacts.  AChReport turns Artifacts into Information, by selecting only the most important information needed for a quick view, and presenting that Information in a simple to read, self contained HTML report.

AChReport IS NOT meant as a comprehensive reporting tool.  It's power is in extracting the most important information and presenting it in an easy to understand format.  AChReport IS NOT meant to replace your favorite forensics tool.  It is meant to meet the need for a quick, simple view of a machine.

As of AChReport v0.95 - You can select which Sections to generate in the report via the AChReport.cfg file

Use -c <ConfigFileName> for different report configurations.

IMPORTANT NOTE: AChReport reads the Artifacts extracted by AChoir, and requires AChoir to be installed to function.  AChReport DOES NOT extract the artifacts, it simply parses, filters and reports on those artifacts.

# Some Things to Know

1. AChReport requires Python to be installed
2. AChReport requires AChoir to be installed
3. AChReport requires that an AChoir extraction was performed (Live Response or Dead-Box)
4. AChReport requires a few additional components including: MS LogParser in the same directory as AChReport.py, and some RegRipper plugins in a subdirectory called "plugins"
5. AChReport is meant to run on Windows
6. AChReport now supports AChoir, and the Windows collections of AChoirX
7. As of v0.98 AChReport can now download and integrate F-secure Countecept Chainsaw
8. As of v0.99c AChReport can now download and integrate Eric Zimmerman's LECmd to parse LNK files
9. As of v0.99f AChReport can highlight IOCs (use the AChReport.cfg file to configure the IOCS ti highlight)

RegRipper can be found at:
 https://github.com/keydet89/RegRipper2.8
 https://github.com/keydet89/RegRipper3.0

Microsoft LogParser can be found at:
 https://www.microsoft.com/en-us/download/details.aspx?id=24659

F-Secure Countercept Chainsaw can be found at:
 https://github.com/countercept/chainsaw

Eric Zimmerman's LECmd can be found at:
 https://ericzimmerman.github.io/#!index.md


# Configuration

The AChReport.cfg file currently has two types of settings:

     Run:[The Report Section to run]

The Run: Option simply tells AChreport which sections to run (or not run).

     IOC:[Simple Text String to Highlight in RED]

The IOC: options allows the analyst to identify strings in the report to highlight in RED.
For instance, if the analyst knows that IP Address 1.2.3.4 is an Indicator, they can
add IOC:1.2.3.4 in the configuration file, and anywhere that AChReport encounters 
that string, it will highlight the entry in RED. The goal is to make known indicators easy
to identify in the report.


# Command Line Arguments

To run AChReport use the -d switch to point to the AChoir extract directory.  For Example:

     py Achreport.py -d c:\Achoir\ACQ-IR-PCName-20181116_1847

To run AChReport with an alternate configuration file use the -c option. For Example, to use a config file called Achreport-Alt.cfg:

     py Achreport.py -d c:\Achoir\ACQ-IR-PCName-20181116_1847 -c Achreport-Alt.cfg
