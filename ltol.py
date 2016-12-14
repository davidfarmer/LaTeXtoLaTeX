#!/usr/bin/env python

import sys
import re
import os
import glob

import component
import transforms
import myoperations

#################################
# First use the command-line arguments to set up the
# input and output files.
#################################

if not len(sys.argv) == 4:
    print 'To convert a file to a different form, do either:'
    print './ltol.py filetype_plus inputfile outputfile'
    print 'to convert one file, or'
    print './ltol.py filetype_plus inputdirectory outputdirectory'
    print 'to convert all the "filetype" files in a directory.  The outputdirectory must already exist.'
    print 'Supported filetype_plus:  tex, mbx, mbx_pp, mbx_fix, mbx_strict_tex, mbx_strict_html, html'
    sys.exit()

component.filetype_plus = sys.argv[1]
component.inputname = sys.argv[2]
component.outputname = sys.argv[3]

if component.filetype_plus not in ["mbx", "mbx_pp", "mbx_fix", "mbx_strict_tex", "mbx_strict_html", "tex", "html"]:
    print "Filetype not recognized."
    print 'Supported filetype_plus are tex, mbx, mbx_pp, mbx_fix, mbx_strict_tex, mbx_strict_html, and html'
    sys.exit()

component.inputname = re.sub(r"/*$","",component.inputname)  # remove trailing slash
component.outputname = re.sub(r"/*$","",component.outputname)

if component.inputname == component.outputname:
    print "must have input distinct from output"
    print "try again"
    sys.exit()

if os.path.isfile(component.inputname) and not os.path.isdir(component.outputname):
    component.iofilepairs.append([component.inputname,component.outputname])
    print "converting one file:",component.inputname

elif os.path.isdir(component.inputname) and os.path.isdir(component.outputname):

    if component.filetype_plus in ["mbx_pp", "mbx_fix", "mbx_strict_tex", "mbx_strict_html"]:
        fileextension = "mbx"
    else:
        fileextension = component.filetype_plus

    inputdir = component.inputname
    outputdir = component.outputname
    outputdir = outputdir + "/"              # put slash back
    thefiles = glob.glob(inputdir + "/*." + fileextension)
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

# mostly for fcla and aata
component.bookidentifier = component.inputname
component.bookidentifier = re.sub(".*/", "", component.bookidentifier)
component.bookidentifier = re.sub("-.*", "", component.bookidentifier)

print component.iofilepairs

for inputfile, outputfile in component.iofilepairs:

    component.inputstub = inputfile
    component.inputstub = re.sub(".*/","",component.inputstub)
    component.inputstub = re.sub("\..*","",component.inputstub)
    print "file stub is ",component.inputstub

    with open(inputfile) as infile:
        component.onefile = infile.read()

#    print component.onefile[:100]

#    myoperations.setvariables(component.onefile)

    if component.filetype_plus == 'tex':
        component.onefile = myoperations.mytransform_tex(component.onefile)
    elif component.filetype_plus == 'html':
        component.onefile = myoperations.mytransform_html(component.onefile)
    elif component.filetype_plus == 'mbx':
        component.onefile = myoperations.mytransform_mbx(component.onefile)
    elif component.filetype_plus == 'mbx_pp':
        component.onefile = transforms.mbx_pp(component.onefile)
    elif component.filetype_plus in ["mbx_fix", "mbx_strict_tex", "mbx_strict_html"]:
        component.onefile = transforms.mbx_fix(component.onefile)
    else:
        print "doing nothing"

    if component.filetype_plus in ["mbx_strict_tex", "mbx_strict_html"]:
        component.onefile = transforms.mbx_strict(component.onefile)

    if component.filetype_plus == "mbx_strict_tex":
        component.onefile = transforms.mbx_strict_tex(component.onefile)
    elif component.filetype_plus == "mbx_strict_html":
        component.onefile = transforms.mbx_strict_html(component.onefile)

    with open(outputfile, 'w') as outfile:
        outfile.write(component.onefile)

#    print component.replaced_macros

sys.exit()

