# LaTeXtoLaTeX

Do something like:

./ltol.py filetype_plus full_path_to_original_directory full_path_to_new_directory

Typically the new_directory is temporary, and after running ltol.py you
do whatever you wish with the new files.  If you are working on a git branch,
this should be safe.

The supported filetype_plus are: tex, mbx, mbx_pp, mbx_fix, mbx_strict_tex, mbx_strict_html, html, and more


You may wish to comment out the print statements.

-------------

For prettyprinting PreTeXt documents, 
assuming the files to be
converted are in the "src" directory:

0) Get on a branch, of course.

1) Copy the PTX files into src_orig for posible reuse later
(this step not strictly necessary if you are a git guru).

2) Make two new directories:  src1 and src2.

3) If the file extension is "ptx", do:

./ltol.py ptx_pp path_to_src path_to_src1

(If the file extension is xml or mbx, replace ptx_pp
by xml_pp or mbx_pp, and similarly in the next command.)

-------------

4) If you also want to add permids, do

./ltol.py ptx_permid path_to_src1 path_to_src2

Both of those may print out a possibly annoying number of
useless messages.

5) Check if the files in src1 or src2 are okay, depending on whether you
wanted to add permids.  If they are, copy into src.

The reason I save the src_orig files is that when I need to
make a change after doing step 5), I want to start over with
the original files.  I find it easier to use the files I saved in
src_orig instead of switching branches or doing some other git thing.

-------------

To convert all the files in a directory *and its subdirectories* then
append 'R' to the command, as in

./ltol.py ptx_permid path_to_src1 path_to_src2 R

