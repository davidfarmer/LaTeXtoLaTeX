# LaTeXtoLaTeX

Do something like:

./ltol.py filetype_plus full_path_to_original_directory full_path_to_new_directory

Typically the new_directory is temporary, and after running ltol.py you
do whatever you wish with the new files.  If you are working on a git branch,
this should be safe.

The supported filetype_plus are: tex, mbx, mbx_pp, mbx_fix, mbx_strict_tex, mbx_strict_html, html


You may wish to comment out the print statements.

