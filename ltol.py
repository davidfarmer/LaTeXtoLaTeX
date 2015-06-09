#!/usr/bin/env python

import sys
import re
import os
import glob

import component
import myoperations

#################################
# First use the command-line arguments to set up the
# input and output files.
#################################

if not len(sys.argv) == 3:
    print 'To convert a LaTeX file to a different form, do one of:'
    print './ltol.py inputfile outputfile'
    print 'or'
    print './ltol.py inputdirectory outputdirectory\n'
    sys.exit()

component.inputname = sys.argv[1]
component.outputname = sys.argv[2]

if component.inputname == component.outputname:
    print "must have input distinct from output"
    print "try again"
    sys.exit()

if os.path.isfile(component.inputname) and os.path.isfile(component.outputname):
    print "converting one file:",component.inputname
    component.inputstub = component.inputname
    component.inputstub = re.sub(".*/","",component.inputstub)
    component.inputstub = re.sub("\..*","",component.inputstub)
    print "file stub is ",component.inputstub

with open(component.inputname) as infile:
    component.onefile = infile.read()

print component.onefile[:100]

myoperations.setvariables(component.onefile)

component.onefile = myoperations.mytransform(component.onefile)

with open(component.outputname, 'w') as outfile:
    outfile.write(component.onefile)

print component.replaced_macros

sys.exit()

latexfiles = glob.glob(latexfiledir + "/*.tex")
if nonsense == xxx:
        print "found these LaTeX files:",latexfiles
        if len(latexfiles) == 1:
            junk.allworks[work_key]['latexfile'] = latexfiles[0]
        else:
            print "Warning, multiple latex files:",latexfiles
            for file in latexfiles:
                with open(file) as f:
                    filecontents = f.read()
                    if "begin{document}" in filecontents:
                         junk.allworks[work_key]['latexfile'] = file
                         break

