# LaTeXtoLaTeX

Do something like:

./ltol.py filetype full_path_to_original_directory full_path_to_new_directory

Typically the new_directory is temporary, and after running ltol.py you
copy files from the new_directory to the original_directory, replacing the
files you started with.  If you are working on a git branch, this should
be safe.

The transformations are done by the function

    mytransform_filetype

in the file

    myoperations.py

The supported filetypes are: tex, mbx, html


You may wish to comment out the print statements.

