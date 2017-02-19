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

conversion_options = ["mbx", "mbx_pp", "mbx_fix", "mbx_strict_tex", "mbx_strict_html", "mbx_fa",
                      "txt",
                      "tex",
                      "html",
                      "pgtombx"]

if not len(sys.argv) == 4:
    print 'To convert a file to a different form, do either:'
    print './ltol.py filetype_plus inputfile outputfile'
    print 'to convert one file, or'
    print './ltol.py filetype_plus inputdirectory outputdirectory'
    print 'to convert all the "filetype" files in a directory.  The outputdirectory must already exist.'
    print 'Supported filetype_plus: '
    print conversion_options
    sys.exit()

component.filetype_plus = sys.argv[1]
component.inputname = sys.argv[2]
component.outputname = sys.argv[3]

print component.inputname
print component.outputname

if component.filetype_plus not in conversion_options:
    print "Filetype not recognized."
    print 'Supported filetype_plus are:'
    print conversion_options
    sys.exit()

if component.inputname == component.outputname:
    print "must have input distinct from output"
    print "try again"
    sys.exit()

if os.path.isfile(component.inputname) and not os.path.isdir(component.outputname):
    component.iofilepairs.append([component.inputname,component.outputname])
    print "converting one file:",component.inputname

elif os.path.isdir(component.inputname) and os.path.isdir(component.outputname):

    if component.filetype_plus in ["mbx_pp", "mbx_fix", "mbx_strict_tex", "mbx_strict_html", "mbx_fa"]:
        fileextension_in = "mbx"
        fileextension_out = "mbx"
    elif component.filetype_plus in ["pgtombx"]:
        fileextension_in = "pg"
        fileextension_out = "mbx"
    else:
        fileextension_in = component.filetype_plus
        fileextension_out = component.filetype_plus

    inputdir = component.inputname
    inputdir = re.sub(r"/*$","",inputdir)  # remove trailing slash
    outputdir = component.outputname
    outputdir = re.sub(r"/*$","",outputdir)  # remove trailing slash
    outputdir = outputdir + "/"              # and then put it back
    thefiles = glob.glob(inputdir + "/*." + fileextension_in)
    for inputfilename in thefiles:
        outputfilename = re.sub(".*/([^/]+)", outputdir + r"\1", inputfilename)
        if fileextension_in != fileextension_out:
            outputfilename = re.sub(fileextension_in + "$", fileextension_out, outputfilename)
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

#    print component.onefile[:100]

#    myoperations.setvariables(component.onefile)

    if component.filetype_plus == 'tex':
        component.onefile = myoperations.mytransform_tex(component.onefile)
    elif component.filetype_plus == 'txt':
        component.onefile = myoperations.mytransform_txt(component.onefile)
    elif component.filetype_plus == 'html':
        component.onefile = myoperations.mytransform_html(component.onefile)
    elif component.filetype_plus == 'mbx':
        component.onefile = myoperations.mytransform_mbx(component.onefile)
    elif component.filetype_plus == 'mbx_pp':
        component.onefile = transforms.mbx_pp(component.onefile)
    elif component.filetype_plus in ["mbx_fix", "mbx_strict_tex", "mbx_strict_html"]:
        component.onefile = transforms.mbx_fix(component.onefile)
    else:
        pass
        # print "doing nothing"

    if component.filetype_plus in ["mbx_strict_tex", "mbx_strict_html"]:
        component.onefile = transforms.mbx_strict(component.onefile)

    if component.filetype_plus == "mbx_strict_tex":
        component.onefile = transforms.mbx_strict_tex(component.onefile)
    elif component.filetype_plus == "mbx_strict_html":
        component.onefile = transforms.mbx_strict_html(component.onefile)

    if component.filetype_plus == "mbx_fa":
        component.onefile = transforms.mbx_fa(component.onefile)

    if component.filetype_plus == "pgtombx":
        component.onefile = transforms.pgtombx(component.onefile)

    with open(outputfile, 'w') as outfile:
        outfile.write(component.onefile)

if component.generic_counter:
    print component.generic_counter
#    print component.replaced_macros

sys.exit()

