
import re

import utilities
import component
import postprocess

def setvariables(text):

    component.chapter_abbrev = utilities.argument_of_macro(text,"chap",2)


###################

def mytransform_mbxpp(text):

    thetext = text

    # first remove extraneous spaces and put in appropriate carriage returns

    thetext = postprocess.tag_before_after("p", "\n\n", "", "", "\n\n", thetext)
    thetext = postprocess.tag_before_after("row|tabular|image|latex-image-code|asymptote", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("me|men|md|mdn", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("exercises|exercisegroup|exercise", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("webwork|setup|var|set|pg-code", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("mrow|intertext", "\n", "", "", "\n", thetext)
    thetext = postprocess.tag_before_after("dt", "\n\n", "", "", "\n", thetext)
    thetext = postprocess.tag_before_after("dd", "\n", "", "", "\n\n", thetext)
    thetext = postprocess.tag_before_after("li", "\n\n", "", "", "\n\n", thetext)
    thetext = postprocess.tag_before_after("ul|ol|dl", "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("title|cell|caption", "\n", "", "", "\n", thetext)
    thetext = postprocess.tag_before_after("theorem|proposition|lemma|conjecture|corollary",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("definition|example|insight|remark|proof",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("figure|table",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("paragraphs|sidebyside|aside", "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("introduction|statement|solution|answer", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("subsection", "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("chapter|section", "\n", "\n", "\n", "\n", thetext)

#    # first remove all the spaces at the beginning of a line
#    thetext = re.sub("\n +", "\n", thetext)

    # then put it back
    thetext = postprocess.add_space_within("chapter", thetext)
    thetext = postprocess.add_space_within("section", thetext)
    thetext = postprocess.add_space_within("subsection", thetext)
    thetext = postprocess.add_space_within("introduction", thetext)
    thetext = postprocess.add_space_within("figure", thetext)
    thetext = postprocess.add_space_within("image", thetext)
    thetext = postprocess.add_space_within("asymptote", thetext)
    thetext = postprocess.add_space_within("sidebyside", thetext)
    thetext = postprocess.add_space_within("aside", thetext)
    thetext = postprocess.add_space_within("latex-image-code", thetext)
    thetext = postprocess.add_space_within("definition|theorem|example|insight", thetext)
    thetext = postprocess.add_space_within("proposition|lemma|remark|conjecture|corollary", thetext)
    thetext = postprocess.add_space_within("statement|solution|answer|proof", thetext)
    thetext = postprocess.add_space_within("p", thetext)
    thetext = postprocess.add_space_within("paragraphs", thetext)
    thetext = postprocess.add_space_within("ul", thetext)
    thetext = postprocess.add_space_within("ol", thetext)
    thetext = postprocess.add_space_within("dl", thetext)
    thetext = postprocess.add_space_within("li", thetext)
    thetext = postprocess.add_space_within("me|men|md|mdn", thetext)
    thetext = postprocess.add_space_within("exercises", thetext)
    thetext = postprocess.add_space_within("exercisegroup", thetext)
    thetext = postprocess.add_space_within("exercise", thetext)
    thetext = postprocess.add_space_within("webwork", thetext)
    thetext = postprocess.add_space_within("setup", thetext)
    thetext = postprocess.add_space_within("var", thetext)
    thetext = postprocess.add_space_within("set", thetext)
    thetext = postprocess.add_space_within("pg-code", thetext)
    thetext = postprocess.add_space_within("table", thetext)
    thetext = postprocess.add_space_within("tabular", thetext)
    thetext = postprocess.add_space_within("row", thetext)

    return thetext

def old_mytransform_mbx2(text):

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
    
    thetext = re.sub(r"></image>\s*",">\n</image>\n",thetext)

    thetext = re.sub(r"<figure(.*?)</figure>",process_figure,thetext,0,re.DOTALL)

    # temporarily hide exercises tag
    thetext = re.sub(r"<exercises", "<EXERCISES",thetext)
    thetext = re.sub(r"<exercisegroup", "<EXERCISEGROUP",thetext)
    # because of how we are handling exercises with xml:ids
    thetext = re.sub(r"\s*<exercise(.*?)</exercise>\s*",process_exercise,thetext,0,re.DOTALL)
    # then put it back
    thetext = re.sub(r"<EXERCISES", "<exercises",thetext)
    thetext = re.sub(r"<EXERCISEGROUP", "<exercisegroup",thetext)
    
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
        return "<figure" + the_text + "</figure>"

    elif the_text.startswith(">"):  # no xml:id, so nothing to do
        return "<figure" + the_text + "</figure>"

    # should start with the xml:id:
    try:
        the_xml_id = re.match('^ xml:id="fig_([^"]+)"',the_text).group(1)
    except AttributeError:
        print "figure should have an xml:id, but it doesn't",the_text[:200]
        return "<figure" + the_text + "</figure>"
    
    # should be only one contained image
    if the_text.count("<image>") != 1:
        print "Error: more than one contained image in fig_" + the_xml_id
        return "<figure" + the_text + "</figure>" 

    # now put that id on the image
    the_text = re.sub("<image>",'<image xml:id="img_' + the_xml_id + '" >', the_text)

    return "<figure" + the_text + "</figure>" 

###################

def process_exercise(txt):
    """We are given <exercise***</exercise> and we want to do something with the ***
       Currently: wrap everything in a blank webwork exercise

    """

    the_text = txt.group(1)

    # check that we have only one exercise
    if "<exercise" in the_text:
        print "Error: exercise within an exercise", the_text[:200]
        return '\n' + "<exercise" + the_text + "</exercise>" + '\n'

    if the_text.count("<answer") > 1:
        print "More than one answer in this exercise:", the_text[:200]
        return '\n' + "<exercise" + the_text + "</exercise>" + '\n'

    if "<answer>" in the_text:
        the_answer = re.search('<answer>(.*?)</answer>',the_text,re.DOTALL).group(1)
    else:
        the_answer = ""
    the_answer = the_answer.strip()

    if the_text.count("<statement>") != 1:
        print "No (or more than one) statement in this exercise:", the_text[:200]
        return '\n' + "<exercise" + the_text + "</exercise>" + '\n'

    the_statement = re.search('<statement>(.*?)</statement>',the_text,re.DOTALL).group(1)
    the_statement = the_statement.strip()

    # exrtract the xml:id, so we can do nice spacing
    end_of_opening_tag = re.match('([^>]*>)',the_text).group(1)
    the_text = re.sub('^([^>]*>)\s*', '', the_text)

    the_result = '\n' + '  <exercise' + end_of_opening_tag + '\n'
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
    the_result += '  </exercise>' + '\n'

    return the_result
