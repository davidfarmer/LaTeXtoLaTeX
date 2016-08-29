
import re

import utilities
import component
import postprocess

def setvariables(text):

    component.chapter_abbrev = utilities.argument_of_macro(text,"chap",2)


###################

def mytransform_mbx(text):

    thetext = text

    # start and end paragraphs on the same line, with a blank line above and below.
    # and similarly for caption, cell, title (except for space above and below)
    thetext = re.sub(r"\s*<(p)>\s*","\n\n<" + r"\1" + ">",thetext)
    thetext = re.sub(r"\s*</(p)>\s*","</" + r"\1" + ">\n\n",thetext)
    thetext = re.sub(r"\s*<(cell|caption|title)>\s*","\n<" + r"\1" + ">",thetext)
    thetext = re.sub(r"\s*</(cell|caption|title)>\s*","</" + r"\1" + ">\n",thetext)

    # do what Alex wanted with <latex-image-code><![CDATA[ 
    # and other image things
    thetext = re.sub(r"\s*<image>\s*<latex-image-code><!\[CDATA\[\s*","\n<image>\n<description></description>\n<latex-image-code><![CDATA[\n",thetext)
    thetext = re.sub(r"</image>\s*","</image>\n",thetext)
    
    thetext = re.sub(r"<figure(.*?)</figure>",process_figure,thetext,0,re.DOTALL)
    thetext = re.sub(r"<exercise(.*?)</exercise>",process_exercise,thetext,0,re.DOTALL)
    
    return thetext


def old_mytransform_mbx(text):

    thetext = text

    thetext = postprocess.put_lists_in_paragraphs(thetext)

    # if statement starts and ends with  list, wrap it in p

    thetext = re.sub(r"\s*<statement>\s*<(ol|ul|dl)>(.*?)\s*</\1>\s*</statement>",
                     "\n        <statement>\n            <p>\n               <" + r"\1" + ">" + r"\2" +
                     "\n               </" + r"\1" + ">\n            </p>\n        </statement>",thetext, 0, re.DOTALL)

    # same for "hint".  Exercise: make one substitution which does both statement and hint
    thetext = re.sub(r"\s*<hint>\s*<(ol|ul|dl)>(.*?)\s*</\1>\s*</hint>",
                     "\n        <hint>\n            <p>\n               <" + r"\1" + ">" + r"\2" +
                     "\n               </" + r"\1" + ">\n            </p>\n        </hint>",thetext, 0, re.DOTALL)

    return thetext

###################

def mytransform_html(text):

    thetext = text

    # the white space before the end of an h5 makes a space before the "." added by CSS
    thetext = re.sub(r"\s+</h5>", "</h5>", thetext)

    return thetext

###################

def mytransform_tex(text):

    thetext = text

    # replace \begin{prop}{the_label} by
    # \begin{prop}\label{proposition:chaptername:the_label}
#    thetext = utilities.replacemacro(thetext,r"\begin{prop}",1,
#                         r"\begin{prop}\label{proposition:"+component.chapter_abbrev+":#1}")

    # and similarly for example and exercise (yes, this can be in a loop)
#    thetext = utilities.replacemacro(thetext,r"\begin{example}",1,
#                         r"\begin{example}\label{example:"+component.chapter_abbrev+":#1}")
#    thetext = utilities.replacemacro(thetext,r"\begin{exercise}",1,
#                         r"\begin{exercise}\label{exercise:"+component.chapter_abbrev+":#1}")

    # in actions.tex and crypt.tex many examples start with something like
    # \noindent {\bf Example 2.}
    # and end with
    # \hspace{\fill} $\blacksquare$
    # so we convert these to \begin{example} \end{example}.
    # Labels and references still need to be added by hand.

    thetext = re.sub(r"\\noindent\s*{\\bf\s+Example\s+[0-9.]+\s*}",r"\\begin{example}",thetext)
    thetext = re.sub(r"\\hspace{\\fill}\s*\$\\blacksquare\$",r"\\end{example}",thetext)

    # delete empty label arguments
    thetext = re.sub(r"\\label{[a-zA-Z]+:[a-zA-Z]+:}","",thetext)

    return thetext

#####################
#####################

def process_figure(txt):

    """We are given <figure***</figure> and we want to do something with the ***
       Currently: transfer the fig_id to the contined image

    """

    the_text = txt.group(1)

    # check that we have only one figure
    if "<figure" in the_text:
        return "<figure" + the_text + "<figure>"

    elif the_text.startswith(">"):  # no xml:id, so nothing to do
        return "<figure" + the_text + "<figure>"

    # should start with the xml:id:
    try:
        the_xml_id = re.match('^ xml:id="fig_([^"]+)"',the_text).group(1)
    except AttributeError:
        print "figure should have an xml:id, but it doesn't",the_text[:200]
        return "<figure" + the_text + "<figure>"
    
    # should be only one contained image
    if the_text.count("<image>") != 1:
        print "Error: more than one contained image in fig_" + the_xml_id
        return "<figure" + the_text + "<figure>" 

    # now put that id on the image
    the_text = re.sub("<image>",'<image xml:id="img_' + the_xml_id + '" >', the_text)

    return "<figure xml:id=" + the_text + "<figure>" 

###################

def process_exercise(txt):
    """We are given <exercise***</exercise> and we want to do something with the ***
       Currently: wrap everything in a blank webwork exercise

    """

    the_text = txt.group(1)

    # check that we have only one exercise
    if "<exercise" in the_text:
        return "<exercise" + the_text + "<exercise>"

    if the_text.count("<answer>") > 1:
        print "More than one answer in this exercise:", the_text[:200]
        return "<exercise" + the_text + "<exercise>"

    if "<answer>" in the_text:
        the_answer = re.search('<answer>(.*?)</answer>',the_text,re.DOTALL).group(1)
    else:
        the_answer = ""
    the_answer = the_answer.strip()

    if the_text.count("<statement>") != 1:
        print "No (or more than one) statement in this exercise:", the_text[:200]
        return "<exercise" + the_text + "<exercise>"

    the_statement = re.search('<statement>(.*?)</statement>',the_text,re.DOTALL).group(1)
    the_statement = the_statement.strip()

    # exrtract the xml:id, so we can do nice spacing
    end_of_opening_tag = re.match('([^>]*>)',the_text).group(1)
    the_text = re.sub('^([^>]*>)\s*', '', the_text)

    the_result = '  <exercise' + end_of_opening_tag + '\n'
    the_result += '    <webwork seed="1">' + '\n'
    the_result += '      <setup>' + '\n'
    the_result += '        <var name="">' + '\n'
    the_result += '          <static></static>' + '\n'
    the_result += '        </var>' + '\n'
    the_result += '        <pg-code>' + '\n'
    the_result += '        </pg-code>' + '\n'
    the_result += '      </setup>' + '\n'
    the_result += '      <statement>' + '\n'
    the_result += '        ' + the_statement + '\n'
    the_result += '      </statement>' + '\n'
    the_result += '      <answer>' + '\n'
    the_result += '        ' + the_answer + '\n'
    the_result += '      </answer>' + '\n'
    the_result += '      <solution>' + '\n'
    the_result += '        ' + the_answer + '\n'
    the_result += '      </solution>' + '\n'
    the_result += '    </webwork>' + '\n'
    the_result += '  </exercise>'

    return the_result
