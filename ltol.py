#!/usr/bin/env python2.7

import sys
import re
import os
import glob
import shutil
import fnmatch
import codecs

import component
import utilities
import transforms
import myoperations

#################################
# First use the command-line arguments to set up the
# input and output files.
#################################

conversion_options = ["xml", "mbx", "ptx_pp", "xml_pp", "mbx_pp", "ptx_fix", "mbx_strict_tex", "mbx_strict_html", "mbx_fa",
                      "txt",
                      "svg",
                      "iso",
                      "ptx",
                      "ldata",
                      "html_ptx",
                      "html_matrix",
                      "xml_semantic", "ptx_semantic",
                      "mbx_permid", "xml_permid", "ptx_permid",
                      "tex", "tex_ptx",
                      "html"]

if len(sys.argv) == 1 or sys.argv[1] == "-h":
    print ''
    print 'To convert a file to a different form, do either:'
    print '    ./ltol.py filetype_plus inputfile outputfile'
    print 'to convert one file, or'
    print '    ./ltol.py filetype_plus inputdirectory outputdirectory'
    print 'to convert all the "filetype" files in a directory.  The outputdirectory must already exist.'
    print ''
    print 'OR if you wish to convert an entire folder and subfolders, do'
    print '    ./ltol.py filetype_plus inputrootdir outputrootdir R'
#    print 'For recursion target directory should NOT already exist'
    print ''
    print 'Supported filetype_plus: '
    print conversion_options
    print ''
    sys.exit()

if not len(sys.argv) >= 4:
    print 'To convert a file to a different form, do either:'
    print './ltol.py filetype_plus inputfile outputfile'
    print 'to convert one file, or'
    print './ltol.py filetype_plus inputdirectory outputdirectory'
    print 'to convert all the "filetype" files in a directory.  The outputdirectory must already exist.'
    print 'Or'
    print './ltol.py filetype_plus inputdirectory outputdirectory R'
    print 'to convert all the "filetype" files in a directory and its subdirectories.'
    print 'Supported filetype_plus: '
    print conversion_options
    sys.exit()

component.filetype_plus = sys.argv[1]
component.inputname = sys.argv[2]
component.outputname = sys.argv[3]
dorecursive = False

if len(sys.argv) == 5 and sys.argv[4] == 'R':
    dorecursive = True    

print component.inputname
print component.outputname

print "component.current_permid", component.current_permid
junk=[]

if component.filetype_plus not in conversion_options:
    print "Filetype not recognized."
    print 'Supported filetype_plus are:'
    print conversion_options
    sys.exit()

if component.inputname == component.outputname:
    print "must have input distinct from output"
    print "try again"
    sys.exit()

if component.filetype_plus in ["ptx", "ptx_pp", "ptx_permid", "ptx_fix", "ptx_semantic", "mbx_strict_tex", "mbx_strict_html", "mbx_fa"]:
    fileextension_in = "ptx"
    fileextension_out = "ptx"
elif component.filetype_plus in ["mbx_pp"]:
    fileextension_in = "mbx"
    fileextension_out = "ptx"
elif component.filetype_plus in ["xml", "xml_pp", "xml_permid"]:
    fileextension_out = "mbx"
elif component.filetype_plus in ["xml", "xml_pp", "xml_permid", "xml_semantic"]:
    fileextension_in = "xml"
    fileextension_out = "xml"
elif component.filetype_plus in ["tex_ptx"]:
    fileextension_in = "tex"
    fileextension_out = "ptx"
elif component.filetype_plus in ["html_ptx"]:
    fileextension_in = "html"
    fileextension_out = "ptx"
elif component.filetype_plus in ["html_matrix"]:
    fileextension_in = "html"
    fileextension_out = "txt"
elif component.filetype_plus in ["svg"]:
    fileextension_in = "src"
    fileextension_out = "svg"
elif component.filetype_plus in ["ldata"]:
    fileextension_in = ""
    fileextension_out = ""
elif component.filetype_plus in ["iso"]:
    fileextension_in = "iso"
    fileextension_out = "html"
elif component.filetype_plus in ["mbx_permid"]:
    fileextension_in = "mbx"
    fileextension_out = "ptx"
else:
    fileextension_in = component.filetype_plus
    fileextension_out = component.filetype_plus

if os.path.isfile(component.inputname) and not os.path.isdir(component.outputname):
    component.iofilepairs.append([component.inputname,component.outputname])
    print "converting one file:",component.inputname

elif os.path.isdir(component.inputname) and os.path.isdir(component.outputname) and not dorecursive:

    print "looking for", fileextension_in, "files in",  component.inputname
    print "Only looking in", component.inputname
    inputdir = component.inputname
    inputdir = re.sub(r"/*$","",inputdir)  # remove trailing slash
    outputdir = component.outputname
    outputdir = re.sub(r"/*$","",outputdir)  # remove trailing slash
    outputdir = outputdir + "/"              # and then put it back
    if fileextension_in:
        thefiles = glob.glob(inputdir + "/*." + fileextension_in)
    else:
        thefiles = glob.glob(inputdir + "/*")

    for component.inputfilename in thefiles:
        if component.filetype_plus == "ldata":
            outputfilename = outputdir + "summart.txt"
        else:
            outputfilename = re.sub(".*/([^/]+)", outputdir + r"\1", component.inputfilename)
        if fileextension_in and fileextension_in != fileextension_out:
            outputfilename = re.sub(fileextension_in + "$", fileextension_out, outputfilename)
        if component.inputfilename == outputfilename:
            print "big problem, quitting"
        component.iofilepairs.append([component.inputfilename, outputfilename])
  #  print thefiles
  #  print inputdir 
  #  print component.iofilepairs
#    sys.exit()
elif dorecursive and os.path.isdir(component.inputname) and not os.path.isdir(component.outputname):

    print "looking for", fileextension_in, "files in",  component.inputname
    
    #First copy the entire src directory to the new destination.
    shutil.copytree(component.inputname, component.outputname)
    thefiles = []
    #Two loops below walk entire sub-structure and adds full path to 
    #each file to be converted. Conversion is done in-place (in = out).
    for root, dirnames, filenames in os.walk(component.outputname):
        for filename in fnmatch.filter(filenames,'*.'+fileextension_in):
            thefiles.append(os.path.join(root,filename))
        
#    print "thefiles", thefiles

    component.iofilepairs = []
    for filepath in thefiles:
        component.iofilepairs.append([filepath, filepath])

else:
    print "Not proper input.  Does target directory exist?"
    sys.exit()

# print component.iofilepairs

listofpermids = []

# if adding permids, need to find old permids
if component.filetype_plus in ['mbx_permid', 'ptx_permid', 'xml_permid']:
    for inputfile, outputfile in component.iofilepairs:
        with open(inputfile) as infile:
            thisfile = infile.read()
        tmp_ct = 0
        while 'permid=' in thisfile and tmp_ct < 100000:
            this_permid = re.search(r'permid="([^"]+)"', thisfile).group(1)
            thisfile = re.sub(r'permid="([^"]+)"', r'PERMID="\1"', thisfile, 1)
            component.all_permid.append(this_permid)
            listofpermids.append(utilities.tobase52(component.current_permid))
            utilities.next_permid_encoded()
        thisfile = re.sub(r'PERMID=', r'permid=', thisfile)

    component.permid_base_number = len(component.all_permid) + 123
    component.current_permid = component.permid_base_number
    print "starting permid:", component.current_permid

#listofpermids.sort()
#component.all_permid.sort()
#
#print listofpermids
#print component.all_permid
#
#print len(listofpermids)
#print len(component.all_permid)

#print listofpermids == component.all_permid

#for nn in range(70,100):
#    print nn, listofpermids[nn], component.all_permid[nn]

#for count, theid in enumerate(listofpermids):
#    print count, theid == component.all_permid[count]

#die()

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
    component.inputfilename = component.inputstub
    component.inputstub = re.sub("\..*","",component.inputstub)
    print "file is ",inputfile
    component.filestubs.append(component.inputstub)

    with open(inputfile) as infile:
        component.onefile = infile.read()

#    print component.onefile[:100]

#    myoperations.setvariables(component.onefile)

    if component.filetype_plus in ['mbx_permid', 'ptx_permid', 'xml_permid']:
        component.onefile = myoperations.add_permid_within_sections(component.onefile)
        if component.filetype_plus == 'mbx_permid':  # because we are changing file extensions
            component.onefile = re.sub("\.mbx", ".ptx", component.onefile)
    if component.filetype_plus == 'tex':
        component.onefile = myoperations.mytransform_tex(component.onefile)
    if component.filetype_plus == 'tex_ptx':
        component.onefile = myoperations.mytransform_tex_ptx(component.onefile)
    if component.filetype_plus == 'html_ptx':
        component.onefile = myoperations.mytransform_html_ptx(component.onefile)
    if component.filetype_plus == 'html_matrix':
        component.onefile = myoperations.mytransform_html_matrix(component.onefile)
    if component.filetype_plus in ['xml_semantic', 'ptx_semantic']:
        component.onefile = myoperations.mytransform_to_semantic(component.onefile)
    elif component.filetype_plus == 'txt':
        component.onefile = myoperations.mytransform_txt(component.onefile)
    elif component.filetype_plus == 'html':
        component.onefile = myoperations.mytransform_html(component.onefile)
    elif component.filetype_plus in ['ptx']:
        component.onefile = myoperations.mytransform_ptx(component.onefile)
    elif component.filetype_plus in ['svg']:
        component.onefile = myoperations.mytransform_svg(component.onefile)
    elif component.filetype_plus in ['ldata']:
        component.onefile = myoperations.mytransform_ldata(component.onefile)
    elif component.filetype_plus in ['iso']:
        component.onefile = myoperations.mytransform_iso(component.onefile)
    elif component.filetype_plus in ['mbx', 'xml']:
        component.onefile = myoperations.mytransform_mbx(component.onefile)

    if component.filetype_plus in ['mbx_pp', 'ptx_pp', 'xml_pp', 'tex_ptx']:

        if component.filetype_plus in ['mbx_pp']:
            component.onefile = re.sub(r'\.mbx"', '.ptx"', component.onefile)

    if component.filetype_plus in ['mbx_pp', 'ptx_pp', 'xml_pp', 'tex_ptx', 'html_ptx']:

        component.onefile = myoperations.mytransform_mbx_remove_linefeeds(component.onefile)

        component.onefile = transforms.mbx_pp(component.onefile)

        component.onefile = myoperations.mytransform_mbx_linefeeds(component.onefile)

        # no space in self-closing tag
        component.onefile = re.sub(r" +/>", "/>", component.onefile)

        # put back verbatim environments
        for tag in component.verbatim_tags:
             component.onefile = re.sub(r"A(" + tag + ")B(.{40})ENDZ *",
                                        utilities.sha1undigest,component.onefile)
        component.onefile = re.sub(r" *ACOMMB(.{40})ENDZ *", utilities.sha1undigest,component.onefile)

        component.onefile = re.sub(r" UVUSpACeVUV", " ", component.onefile)
        component.onefile = re.sub(r"UVUSpACeVUV ", " ", component.onefile)
        component.onefile = re.sub(r"UVUSpACeVUV", " ", component.onefile)
        component.onefile = re.sub(r" *UVUnooooSpACeVUV *", "", component.onefile)

        # special case of punctuation after quantity
        component.onefile = re.sub(r"(</quantity>)\s*((\?|!|;|:|,|\.|\)|</)+) *?", r"\1\2", component.onefile)
        # and parentheses or other markup before quantity
        component.onefile = re.sub(r"(\(|>)\s*(<quantity>)", r"\1\2", component.onefile)

        # quote at end of sentence
        component.onefile = re.sub(r"(</q>)\s+(!|\.|,|\?|:|;)", r"\1\2", component.onefile)

        # special case for <c> in the middle of a sentence
        # this should not be needed, but there is a bug somewhere.
        component.onefile = re.sub(r"(</c>)([a-z])", r"\1 \2", component.onefile)

        # fix lines that only contain spaces
        component.onefile = re.sub(r"\n +\n", "\n\n", component.onefile)
        component.onefile = re.sub(r"\n +\n", "\n\n", component.onefile)
        # fix extra white space around comments
        component.onefile = re.sub(r"\n+( *<!--)", "\n" + r"\1", component.onefile)
        component.onefile = re.sub(r"-->\n+", "-->\n", component.onefile)
        # no need for more than one blank line
        component.onefile = re.sub(r"\n{3,}", "\n\n", component.onefile)
        # put short li on one line
        component.onefile = re.sub("(<li>)\s+(.{,50})\s+(</li>)", r"\1\2\3", component.onefile)
        for _ in range(10):
            component.onefile = re.sub("(\n +)(<idx>.*?</idx>) *(<idx>)",
                                       r"\1\2\1\3", component.onefile)
        component.onefile = re.sub("(\n +)(    <idx>.*?</idx>) *([A-Z])",
                                   r"\1\2\1\3", component.onefile)

        # somehow periods after a quote or url were ending up on the next line
        component.onefile = re.sub(r">\n *(\)*(\.|,)) *\n", r">\1" + "\n", component.onefile)
        component.onefile = re.sub(r">\n( *)(\)*(\.|,)) +", r">\2" + "\n" + r"\1", component.onefile)
        # and line feeds before a closing url
        component.onefile = re.sub(r"\s+</url>", "</url>", component.onefile)
        # and sometimes spaces at end of line  (often from idx)
        component.onefile = re.sub(r"\s+\n", "\n", component.onefile)

        # there should not be a blank line at the start or end of a file
        component.onefile = re.sub(r"^\n+", "", component.onefile)
        component.onefile = re.sub(r"\n+$", "", component.onefile)

    # temporary, delete when you see this
        component.onefile = re.sub(r"\n *<p>\n *(OLDNUMBER [0-9]+\.[0-9]+\.[0-9]+) *\n *</p>",
                                   "\n\n\n" + r"\1" + "\n", component.onefile)
        component.onefile = re.sub(r"(\n *<p>\n) *(OLDNUMBER [0-9]+\.[0-9]+\.[0-9]+) *\n( *<ol)",
                                   "\n\n\n" + r"\2" + "\n" + r"\1" + r"\3", component.onefile)
        component.onefile = re.sub(r'type="labelalph"', 'label="(a)"', component.onefile)

    if component.filetype_plus in ["ptx_fix", "mbx_strict_tex", "mbx_strict_html"]:
        component.onefile = myoperations.mbx_fix(component.onefile)

    if component.filetype_plus in ["mbx_strict_tex", "mbx_strict_html"]:
        component.onefile = transforms.mbx_strict(component.onefile)

    if component.filetype_plus == "mbx_strict_tex":
        component.onefile = transforms.mbx_strict_tex(component.onefile)
    elif component.filetype_plus == "mbx_strict_html":
        component.onefile = transforms.mbx_strict_html(component.onefile)

    if component.filetype_plus == "mbx_fa":
        component.onefile = transforms.mbx_fa(component.onefile)

    if "ptx" in component.filetype_plus:
        # there is not actually a subtask tag
        component.onefile = re.sub(r"<subtask\b", "<task", component.onefile)
        component.onefile = re.sub(r"subtask>", "task>", component.onefile)

    if component.onefile and component.filetype_plus == 'html_matrix':
        this_matrix = component.onefile
        this_matrix_formatted = "[\n"
        for row in this_matrix:
            this_row = "["
            for elt in row:
                this_row += str(elt) + ","
            this_row = this_row[:-1]   # was extra comma at end
            this_matrix_formatted += this_row + '],\n'
        this_matrix_formatted = this_matrix_formatted[:-2]  # delete comma and \n
        this_matrix_formatted += '\n]\n'
        with open(outputfile, 'w') as outfile:
            outfile.write(this_matrix_formatted)
                
    elif component.onefile and component.filetype_plus != "ldata":
        with open(outputfile, 'w') as outfile:
            outfile.write(component.onefile)

    elif component.filetype_plus == "ldata":
        print "the file starts", component.onefile[:150]

component.foundvalues.sort()
if component.filetype_plus == "ldata":
    with open(outputfile, 'w') as outfile:
        for lam1lam2 in component.foundvalues:
            outfile.write(lam1lam2 + ",\n")

if component.filetype_plus in ['mbx_permid', 'ptx_permid', 'xml_permid'] and component.all_permid:
    component.all_permid.sort()
#    with open(outputdir + 'allpermid.txt', 'w') as f:
#        for permid in component.all_permid:
#            f.write(permid + "\n")
    print "Total number of permid~s:", len(component.all_permid), ", of which repeats:"
    print [x for x in component.all_permid if component.all_permid.count(x) > 1]

    print "component.current_permid", component.current_permid

if component.generic_counter:
    print component.generic_counter
#    print component.replaced_macros

if component.extra_macros:
    print "component.extra_macros", component.extra_macros

print "need to start again at",  component.startagain

print "all found values"
for j in range(20):
    print component.foundvalues[j]

print "done"

sys.exit()

