#!/usr/bin/env python

import sys
import re
import os
import glob
import shutil
import fnmatch

import component
import transforms
import myoperations

#################################
# First use the command-line arguments to set up the
# input and output files.
#################################

conversion_options = ["xml", "mbx", "ptx_pp", "xml_pp", "mbx_pp", "ptx_fix", "mbx_strict_tex", "mbx_strict_html", "mbx_fa",
                      "txt",
                      "tex", "tex_ptx",
                      "html",
                      "pgtombx"]
if sys.argv[1] == "-h":
    print 'To convert a file to a different form, do either:'
    print './ltol.py filetype_plus inputfile outputfile'
    print 'to convert one file, or'
    print './ltol.py filetype_plus inputdirectory outputdirectory'
    print 'to convert all the "filetype" files in a directory.  The outputdirectory must already exist.'
    print 'OR if you wish to convert an entire folder and subfolders'
    print './ltol.py filetype_plus inputrootdir outputrootdir R'
    print 'For recursion target directory should NOT already exist'
    print 'Supported filetype_plus: '
    print conversion_options
    sys.exit()


if not len(sys.argv) >= 4:
    print 'To convert a file to a different form, do either:'
    print './ltol.py filetype_plus inputfile outputfile'
    print 'to convert one file, or'
    print './ltol.py filetype_plus inputdirectory outputdirectory'
    print 'to convert all the "filetype" files in a directory.  The outputdirectory must already exist.'
    print 'Supported filetype_plus: '
    print conversion_options
    sys.exit()

if len(sys.argv) == 4:
    component.filetype_plus = sys.argv[1]
    component.inputname = sys.argv[2]
    component.outputname = sys.argv[3]
    dorecursive = False
else:
    component.filetype_plus = sys.argv[1]
    component.inputname = sys.argv[2]
    component.outputname = sys.argv[3]
    dorecursive = True    

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

elif os.path.isdir(component.inputname) and os.path.isdir(component.outputname) and not dorecursive:

    if component.filetype_plus in ["mbx_pp", "ptx_fix", "mbx_strict_tex", "mbx_strict_html", "mbx_fa"]:
        fileextension_in = "ptx"
        fileextension_out = "ptx"
    elif component.filetype_plus in ["ptx_pp"]:
        fileextension_in = "ptx"
        fileextension_out = "ptx"
    elif component.filetype_plus in ["xml_pp"]:
        fileextension_in = "xml"
        fileextension_out = "xml"
    elif component.filetype_plus in ["pgtombx"]:
        fileextension_in = "pg"
        fileextension_out = "mbx"
    elif component.filetype_plus in ["tex_ptx"]:
        fileextension_in = "tex"
        fileextension_out = "ptx"
    else:
        fileextension_in = component.filetype_plus
        fileextension_out = component.filetype_plus

    print "looking for", fileextension_in, "files in",  component.inputname
    print "Only looking in", component.inputname
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
  #  print thefiles
  #  print inputdir 
  #  print component.iofilepairs
#    sys.exit()
elif dorecursive and os.path.isdir(component.inputname) and not os.path.isdir(component.outputname):

    if component.filetype_plus in ["mbx_pp", "ptx_fix", "mbx_strict_tex", "mbx_strict_html", "mbx_fa"]:
        fileextension_in = "ptx"
        fileextension_out = "ptx"
    elif component.filetype_plus in ["ptx_pp"]:
        fileextension_in = "ptx"
        fileextension_out = "ptx"
    elif component.filetype_plus in ["pgtombx"]:
        fileextension_in = "pg"
        fileextension_out = "mbx"
    elif component.filetype_plus in ["tex_ptx"]:
        fileextension_in = "tex"
        fileextension_out = "ptx"
    else:
        fileextension_in = component.filetype_plus
        fileextension_out = component.filetype_plus

    print "looking for", fileextension_in, "files in",  component.inputname
    
    #First copy the entire src directory to the new destination.
    shutil.copytree(component.inputname, component.outputname)
    thefiles = []
    #Two loops below walk entire sub-structure and adds full path to 
    #each file to be converted. Conversion is done in-place (in = out).
    for root, dirnames, filenames in os.walk(component.outputname):
        for filename in fnmatch.filter(filenames,'*.'+fileextension_in):
            thefiles.append(os.path.join(root,filename))
        
    print "thefiles", thefiles

    component.iofilepairs = []
    for filepath in thefiles:
        component.iofilepairs.append([filepath, filepath])

else:
    print "Not proper input.  Does target directory exist?"
    sys.exit()

# print component.iofilepairs

print "about to loop over files:", component.iofilepairs

for inputfile, outputfile in component.iofilepairs:

    #By using os.path.join, the paths SHOULD match the operating systems' 
    #correct syntax. Regardless of windows or linux. Thank you compiler!
    if not dorecursive:
        # hack for windows
        inputfile = re.sub(r"\\\\", "/", inputfile)
        inputfile = re.sub(r"\\", "/", inputfile)
        outputfile = re.sub(r"\\\\", "/", outputfile)
        outputfile = re.sub(r"\\", "/", outputfile)

    component.extra_macros = []

    component.inputstub = inputfile
    component.inputstub = re.sub(".*/","",component.inputstub)
    component.inputstub = re.sub("\..*","",component.inputstub)
    print "file stub is ",component.inputstub
    component.filestubs.append(component.inputstub)

    with open(inputfile) as infile:
        component.onefile = infile.read()

#    print component.onefile[:100]

#    myoperations.setvariables(component.onefile)

    if component.filetype_plus == 'tex':
        component.onefile = myoperations.mytransform_tex(component.onefile)
    if component.filetype_plus == 'tex_ptx':
        component.onefile = myoperations.mytransform_tex_ptx(component.onefile)
    elif component.filetype_plus == 'txt':
        component.onefile = myoperations.mytransform_txt(component.onefile)
    elif component.filetype_plus == 'html':
        component.onefile = myoperations.mytransform_html(component.onefile)
    elif component.filetype_plus in ['ptx', 'mbx', 'xml']:
        component.onefile = myoperations.mytransform_mbx(component.onefile)
 #       component.onefile = transforms.mbx_pp(component.onefile)
    elif component.filetype_plus in ['mbx_pp', 'ptx_pp', 'xml_pp']:
        component.onefile = transforms.mbx_pp(component.onefile)
    elif component.filetype_plus in ["ptx_fix", "mbx_strict_tex", "mbx_strict_html"]:
        component.onefile = myoperations.mbx_fix(component.onefile)
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

    if component.filetype_plus == "tex_ptx":
        component.onefile = transforms.mbx_pp(component.onefile)

    with open(outputfile, 'w') as outfile:
        outfile.write(component.onefile)

tmpcount=0
if component.filetype_plus == "pgtombx":
    with open(outputdir + 'compilation.mbx', 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" ?>\n\n')
        f.write('<mathbook xmlns:xi="http://www.w3.org/2001/XInclude" xml:lang="en-US">\n')
        f.write('<docinfo>\n')
        f.write('</docinfo>\n')
        f.write('<article>\n')
        f.write('  <section>\n')
        f.write('    <exercises>\n')
        for stub in component.filestubs:
     #       if tmpcount > 30: continue
            tmpcount += 1
            f.write('      <xi:include href="./' + stub + '.mbx' + '" />' + '\n\n')
        f.write('    </exercises>\n')
        f.write('  </section>\n')
        f.write('</article>\n')
        f.write('</mathbook>\n')

if component.generic_counter:
    print component.generic_counter
#    print component.replaced_macros

if component.extra_macros:
    print "component.extra_macros", component.extra_macros
sys.exit()

