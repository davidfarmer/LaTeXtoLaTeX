#!/usr/bin/env python

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
                      "mbx_permid", "xml_permid", "ptx_permid",
                      "tex", "tex_ptx",
                      "html",
                      "pgtombx"]

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
    print 'For recursion target directory should NOT already exist'
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
    print 'Supported filetype_plus: '
    print conversion_options
    sys.exit()

component.filetype_plus = sys.argv[1]
component.inputname = sys.argv[2]
component.outputname = sys.argv[3]
dorecursive = False

if len(sys.argv) == 5:
    dorecursive = True    

print component.inputname
print component.outputname

component.permid_base_number = utilities.frombase52(component.permid_base)
print "component.permid_base_number", component.permid_base_number
junk=[]
rude_words = ["ass", "tit", "cum", "fuc", "fuk", "nig", "cnt", "sob", "fbi", "cia", "usa",
              "poo", "pee", "die", "sex", "bum", "ars", "cok", "dik", "jiz", "wtf", "lol",
              "fag", "kkk", "std", "lsd", "gay", "jew", "wop", "jap", "xxx", "pot", "pms",
              "god", "lay"]
rude_words_13 = [codecs.encode(x, 'rot_13') for x in rude_words]
print rude_words_13

for n in range(120000):
   this_pid = utilities.next_permid_encoded()
   print "next permid:", n, "ttt", this_pid, "sss"
#   new_permid_num = (component.permid_base_number + n*component.permid_base_increment) % component.permid_base_mod
#   print "new_permid_num", new_permid_num
#   new_permid_str = utilities.tobase52(new_permid_num)
#   print n, "           new_permid_str", new_permid_str
#   junk.append(new_permid_str)
#print "junk", junk


if component.filetype_plus not in conversion_options:
    print "Filetype not recognized."
    print 'Supported filetype_plus are:'
    print conversion_options
    sys.exit()

if component.inputname == component.outputname:
    print "must have input distinct from output"
    print "try again"
    sys.exit()

if component.filetype_plus in ["ptx_pp", "ptx_permid", "ptx_fix", "mbx_strict_tex", "mbx_strict_html", "mbx_fa"]:
    fileextension_in = "ptx"
    fileextension_out = "ptx"
elif component.filetype_plus in ["mbx_pp"]:
    fileextension_in = "mbx"
    fileextension_out = "mbx"
elif component.filetype_plus in ["xml", "xml_pp", "xml_permid"]:
    fileextension_in = "xml"
    fileextension_out = "xml"
elif component.filetype_plus in ["pgtombx"]:
    fileextension_in = "pg"
    fileextension_out = "mbx"
elif component.filetype_plus in ["tex_ptx"]:
    fileextension_in = "tex"
    fileextension_out = "ptx"
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

    if component.filetype_plus in ['mbx_permid', 'ptx_permid', 'xml_permid']:
        component.onefile = myoperations.add_permid_within_sections(component.onefile)
        if component.filetype_plus == 'mbx_permid':  # because we are changing file extensions
            component.onefile = re.sub("\.mbx", ".ptx", component.onefile)
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

        component.onefile = myoperations.mytransform_mbx_linefeeds(component.onefile)

        # put back verbatim environments
        for tag in component.verbatim_tags:
             component.onefile = re.sub(r"A(" + tag + ")B(.{40})ENDZ *",
                                        utilities.sha1undigest,component.onefile)
        component.onefile = re.sub(r" *ACOMMB(.{40})ENDZ *", utilities.sha1undigest,component.onefile)

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

        # there is not actually a subtask tag
    component.onefile = re.sub(r"<subtask\b", "<task", component.onefile)
    component.onefile = re.sub(r"subtask>", "task>", component.onefile)

    with open(outputfile, 'w') as outfile:
        outfile.write(component.onefile)

if component.filetype_plus in ['mbx_permid', 'ptx_permid', 'xml_permid'] and component.all_permid:
    component.all_permid.sort()
    with open(outputdir + 'allpermid.txt', 'w') as f:
        for permid in component.all_permid:
            f.write(permid + "\n")
print "permid~s", len(component.all_permid), "of which repeats:"
print [x for x in component.all_permid if component.all_permid.count(x) > 1]

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

