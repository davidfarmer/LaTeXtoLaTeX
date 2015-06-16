
import re

import utilities
import component

def setvariables(text):

    component.chapter_abbrev = utilities.argument_of_macro(text,"chap",2)


###################

def mytransform(text):

    thetext = text

    # replace \begin{prop}{the_label} by
    # \begin{prop}\label{proposition:chaptername:the_label}
    thetext = utilities.replacemacro(thetext,r"\begin{prop}",1,
                         r"\begin{prop}\label{proposition:"+component.chapter_abbrev+":#1}")

    # and similarly for example and exercise (yes, this can be in a loop)
    thetext = utilities.replacemacro(thetext,r"\begin{example}",1,
                         r"\begin{example}\label{example:"+component.chapter_abbrev+":#1}")
    thetext = utilities.replacemacro(thetext,r"\begin{exercise}",1,
                         r"\begin{exercise}\label{exercise:"+component.chapter_abbrev+":#1}")

    # in actions.tex and crypt.tex many examples start with something like
    # \noindent {\bf Example 2.}
    # and end with
    # \hspace{\fill} $\blacksquare$
    # so we convert these to \begin{example} \end{example}.
    # Labels and references need to be added by hand.

    thetext = re.sub(r"\\noindent{\\bf Example [0-9]+\.}",r"\\begin{example}",thetext)
    thetext = re.sub(r"\hspace{\\fill} \$\blacksquare\$",r"\\end{example}",thetext)

    # delete empty label arguments
    thetext = re.sub(r"\\label{[a-zA-Z]+:[a-zA-Z]+:}","",thetext)

    return thetext

