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

if not len(sys.argv) == 4:
    print 'To convert a LaTeX file to a different form, do either:'
    print './ltol.py filetype inputfile outputfile'
    print 'to convert one file, or'
    print './ltol.py filetype inputdirectory outputdirectory'
    print 'to convert all the "filetype" files in a directory.  The outputdirectory must already exist.'
    print 'Supported filetypes:  tex, mbx, html'
    sys.exit()

component.filetype = sys.argv[1]
component.inputname = sys.argv[2]
component.outputname = sys.argv[3]

if component.filetype not in ["mbx", "tex", "html"]:
    print "Filetype not recognized."
    print 'Supported filetypes are tex, mbx, and html'
    sys.exit()

if component.inputname == component.outputname:
    print "must have input distinct from output"
    print "try again"
    sys.exit()

if os.path.isfile(component.inputname) and not os.path.isdir(component.outputname):
    component.iofilepairs.append([component.inputname,component.outputname])
    print "converting one file:",component.inputname

elif os.path.isdir(component.inputname) and os.path.isdir(component.outputname):
    inputdir = component.inputname
    inputdir = re.sub(r"/*$","",inputdir)  # remove trailing slash
    outputdir = component.outputname
    outputdir = re.sub(r"/*$","",outputdir)  # remove trailing slash
    outputdir = outputdir + "/"              # and then put it back
    thefiles = glob.glob(inputdir + "/*." + component.filetype)
    for inputfilename in thefiles:
        outputfilename = re.sub(".*/([^/]+)", outputdir + r"\1", inputfilename)
        if inputfilename == outputfilename:
            print "big problem, quitting"
        component.iofilepairs.append([inputfilename, outputfilename])
    print thefiles
    print inputdir 
    print component.iofilepairs
#    sys.exit()

else:
    print "Not proper input.  Does target directory exist?"
    sys.exit()

print component.iofilepairs

for inputfile, outputfile in component.iofilepairs:

    component.inputstub = inputfile
    component.inputstub = re.sub(".*/","",component.inputstub)
    component.inputstub = re.sub("\..*","",component.inputstub)
    print "file stub is ",component.inputstub

    with open(inputfile) as infile:
        component.onefile = infile.read()

    print component.onefile[:100]

#    myoperations.setvariables(component.onefile)

    if component.filetype == 'tex':
        component.onefile = myoperations.mytransform_tex(component.onefile)
    elif component.filetype == 'mbx':
        component.onefile = myoperations.mytransform_mbx(component.onefile)
    elif component.filetype == 'html':
        component.onefile = myoperations.mytransform_html(component.onefile)
    else:
        print "doing nothing"


    with open(outputfile, 'w') as outfile:
        outfile.write(component.onefile)

#    print component.replaced_macros

sys.exit()

