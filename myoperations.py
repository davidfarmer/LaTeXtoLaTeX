
import re

import utilities
import component
import postprocess

def setvariables(text):

    component.chapter_abbrev = utilities.argument_of_macro(text,"chap",2)


###################

def mytransform_mbx(text):

    thetext = text

    # put periods outside math mode
    # but be careful about ***\right.</m>
    thetext = re.sub(r"([^t])(\.|,) *</m>", r"\1</m>\2", thetext)

    for fcn in ["sin", "cos", "tan", "sec", "csc", "cot",
                "sinh", "cosh", "tanh", "sech", "csch", "coth",
                "ln", "log"]:
        component.something_changed = True
        while component.something_changed:
            component.something_changed = False
            # note that "cos\b" does not match ' cos1 '
            thetext = re.sub(r"\\(" + fcn + r")((\b|[0-9]).*)", wrap_in_parentheses,
                             thetext, 1, re.DOTALL)    # probably don't need the DOTALL
        thetext = re.sub(r"\\" + fcn + "XXXXXXXXXX", r"\\" + fcn, thetext)

    # no space at end of math mode
    thetext = re.sub(r"(\S) </m>", r"\1</m>", thetext)

#    if "xml ver" not in thetext:
#        thetext = '<?xml version="1.0" encoding="UTF-8" ?>' + '\n' + thetext
#
#    thetext = re.sub(r"(<pg-code>(.*?)</pg-code>)", replacepgcode, thetext, 0, re.DOTALL)

 #   for tag in ["p"]:
#    for tag in ["pg-code"]:
#        the_search = "(<" + tag + r"\b.*?</" + tag + ">)"
#        thetext = re.sub(the_search, replacetag, thetext, 0, re.DOTALL)

#    thetext = re.sub(r"\\ds\s*\\lim_", r"\\lim\\limits_", thetext)
#    thetext = re.sub(r"\\displaystyle\s*\\lim_", r"\\lim\\limits_", thetext)

#    for tag in ["cell","mrow","title","li"]:
#        the_search = "(<" + tag + r"\b.*?</" + tag + ">)"
#        thetext = re.sub(the_search, replacetag, thetext, 0, re.DOTALL)

#    for tag in ["mrow"]:
#        the_search = "(<" + tag + r"\b.*?</" + tag + ">)"
#        thetext = re.sub(the_search, replacetag, thetext, 0, re.DOTALL)

#    for tag in ["p"]:
#        the_search = "(<" + tag + r"\b.*?</" + tag + ">)"
#        thetext = re.sub(the_search, fixp, thetext, 0, re.DOTALL)

#    thetext = mytransform_mbx_figure(thetext)

#    thetext = process_fig_mult(thetext)

#    thetext = re.sub(r'<image xml:id="([^"]+)" >', deduplicate_id, thetext,0,re.DOTALL)

    return thetext

def wrap_in_parentheses(txt):

    the_function = "\\" + txt.group(1)
    everything_else = txt.group(2)

    the_function += "XXXXXXXXXX"
    component.something_changed = True

    everything_else = everything_else.lstrip()

    if everything_else.startswith("^"):
        the_function += "^"
        everything_else = everything_else[1:]
        if everything_else.startswith("{"):
            the_exponent, everything_else = utilities.first_bracketed_string(everything_else)
            the_function += the_exponent
        else:
            the_function += everything_else[0]
            everything_else = everything_else[1:]

    everything_else = everything_else.lstrip()

    # first case, the arcument is already in parentheses
    if everything_else.startswith(("(", "[", "\\big", "\\Big", "\\left")):
        return the_function + everything_else
    # second case, there is an argument not in parentheses, but that
    # could be x, or t, or \theta, or \varphi, or ...
#    elif everything_else.startswith(("\\theta", "\\var", "\\pi")):
#        the_argument = "\\"
#        everything_else = everything_else[1:]
#        print everything_else[:20]
#        nothing, the_letters, everything_else =  re.split('(\w+)', everything_else, 1)
#        the_argument += the_letters
#        everything_else = everything_else.lstrip()
#        return the_function + "(" + the_argument + ")" + " " + everything_else
    elif everything_else.startswith("{"):  # eg, \ln{x}  **why did someone write that?
        the_argument, everything_else = utilities.first_bracketed_string(everything_else)
        the_argument = utilities.strip_brackets(the_argument)
        everything_else = everything_else.lstrip()
        return the_function + "(" + the_argument + ")" + " " + everything_else
 #   elif everything_else.startswith(("\\", "}", "<")):  # eg, \ln \abs{t+1}
    elif everything_else.startswith(("}", "<")):  # eg, <m>\sin</m>
        return the_function + everything_else

###############
#
# If we get this far, we are now looking for an argument of the form
# (number) (variable) (exponent or subscript)
# or maybe something like 2 \pi t
#
####################

    the_argument = ""

    # numbers, which could be decimal, but not ending in a decimal point
    if everything_else[0].isdigit():
        nothing, the_numbers, everything_else =  re.split('([0-9.]*[0-9])', everything_else, 1)
        the_argument = the_numbers
 #       everything_else = everything_else.lstrip()
        # this needs to be fixed, and also not duplate the "else" code
 #       if everything_else.startswith("x"):
 #             the_argument += everything_else[0]
 #             everything_else = everything_else[1:]
#        everything_else = everything_else.lstrip()
#        return the_function + "(" + the_argument + ")" + " " + everything_else

    everything_else = everything_else.lstrip()
    # last case: there is just one character as the argument
    # except that it could be x^2 or t_0

    if everything_else.startswith(("\\theta", "\\var", "\\phi", "\\pi")):
        the_argument += "\\"
        everything_else = everything_else[1:]
        print everything_else[:40]
        nothing, the_letters, everything_else =  re.split('(\w+)', everything_else, 1)
        the_argument += the_letters
 #       return the_function + "(" + the_argument + ")" + " " + everything_else

    everything_else = everything_else.lstrip()

    if everything_else[:1].isalpha():
        if the_argument and everything_else[0] == 'd':
            #skip this case because it looks like \sin x dx
            pass
        else:
            the_argument += everything_else[0]
            everything_else = everything_else[1:]

    everything_else = everything_else.lstrip()

#    else:
#        if the_argument:
#            return the_function + "(" + the_argument + ")" + " " + everything_else
#        else:
#            return the_function +  everything_else

    if everything_else.startswith(("^", "_")):
       the_argument += everything_else[0]
       everything_else = everything_else[1:]
       everything_else = everything_else.lstrip()
       if everything_else.startswith("{"):
           the_arg, everything_else = utilities.first_bracketed_string(everything_else)
           the_argument += the_arg
       elif everything_else.startswith("\\"):
         # repeats code from above.  does not handle \frac correctly
            the_argument += "\\"
            everything_else = everything_else[1:]
            print "         exponent  :", everything_else[:40]
            nothing, the_letters, everything_else =  re.split('(\w+)', everything_else, 1)
            the_argument += the_letters
       else:
           the_argument += everything_else[0]
           everything_else = everything_else[1:]

    everything_else = everything_else.lstrip()

    if the_argument:
        return the_function + "(" + the_argument + ")" + " " + everything_else
    else:
        return the_function +  everything_else

def replacetag(txt):

    this_text = txt.group(1)

#    if "draw" in this_text:
#        return this_text

#    this_text = re.sub(r"\\parbox\[[^\]]*\]",r"\\parbox",this_text)
######    this_text = re.sub("\s*(<var [^<>]*/>)\s*", r" \1",this_text)

    if trimmed_text:
        print trimmed_text
    if "<var" in this_text:
        print this_text
#    this_text = utilities.replacemacro(this_text,r"\parbox",2,"#2")

#    this_text = re.sub(r"<answer>.*?</answer>\s*","",this_text,1,re.DOTALL)

#    while '$' in this_text:
#       # print "found $"
#        this_text = re.sub(r"\$","<m>",this_text,1)
#        this_text = re.sub(r"\$","</m>",this_text,1)

    return this_text

def fixp(txt):

    this_text = txt.group(1)

    if this_text.startswith(r"<p>\text{"):
        print "found starting text"
        this_text = this_text[8:]
        if not this_text.startswith("{"):
            print "missing bracket", this_text[:10]
        btext, the_remainder = utilities.first_bracketed_string(this_text)
        btext = btext[1:-1]   # remove { and }
        btext = btext.lstrip()
        btext = re.sub(r"\\\(","<m>",btext)
        btext = re.sub(r"\\\)","</m>",btext)
        this_text = "<p>" + btext + the_remainder

 #   if component.inputstub == 'sec_series':
 #       print this_text[:10]

    return this_text

def replacepgcode(txt):

    this_text = txt.group(1)

    trimmed_text = re.sub(r"<pg-code>(.*?)</pg-code>", r"\1", this_text, 0, re.DOTALL)
    if not trimmed_text.strip():
        return this_text
    print " "
    pglines = trimmed_text.split("\n")
    first_length = 0
    excess_length = 0
    spaces_to_delete = ""
    shortened_lines = []
    for line in pglines:
        if not line:
            print "blank line"
        else:
            starting_spaces = re.sub(r"( *)\S.*",r"\1",line)
    #        print(len(starting_spaces),"    ",line[:50])
            if not first_length:
                first_length = len(starting_spaces)
            elif not excess_length:
                excess_length = len(starting_spaces) - first_length
                spaces_to_delete = " " * excess_length
            line = re.sub("^" + spaces_to_delete, "", line)
            shortened_lines.append(line)
            print line

    the_answer = "<pg-code>\n" + "\n".join(shortened_lines) + "</pg-code>"

    return the_answer

def replaceabs(txt):

    this_math = txt.group(1)

    if "text" in this_math and "xref" in this_math:
        print this_math

    this_math = re.sub(r"\|\|([^\|]+)\|\|", r"\\norm{\1}",this_math)
    this_math = re.sub(r"\\big\|\\big\|([^\|]+)\\big\|\\big\|", r"\\norm{\1}",this_math)
    this_math = re.sub("\|\_","ZZZXCVBNM",this_math)
#    if "|" in this_math:
#        print this_math.count("|")

    this_math = re.sub(r"\\left\|(.*?)\\right\|",r"\\abs{" + r"\1" + "}",this_math, 0 ,re.DOTALL)
    this_math = re.sub(r"\\big\|(.*?)\\big\|",r"\\abs{" + r"\1" + "}",this_math, 0 ,re.DOTALL)
    this_math = re.sub(r"\|(.*?)\|",r"\\abs{" + r"\1" + "}",this_math, 0 ,re.DOTALL)

    if "|" in this_math:
        print this_math.count("|")

    this_math = re.sub("ZZZXCVBNM","|_",this_math)

    return this_math


###############

def mytransform_mbx_img_fig(text):

    thetext = text

#    thetext = re.sub(r"<cell(.*?)</cell>",cell_hack,thetext,0,re.DOTALL)
#
#    thetext = mytransform_mbx_figure(thetext)

#    thetext = process_fig_mult(thetext)

    thetext = re.sub(r'<image xml:id="([^"]+)" >', deduplicate_id, thetext,0,re.DOTALL)

    return thetext

def deduplicate_id(txt):

    this_id = txt.group(1)

    idcounter = 1
    if this_id in component.ids:
        print "found duplicate id:", this_id
        this_id = this_id + "X"
        if this_id in component.ids:
           while this_id + str(idcounter) in component.ids:
               idcounter += 1
           this_id = this_id + str(idcounter)

    component.ids.append(this_id)

    return '<image xml:id="' + this_id + '" >'

################
def mytransform_mbx_cell(text):

    thetext = text

#    thetext = re.sub(r"<sidebyside(.*?)</sidebyside>",sbs_hack,thetext,0,re.DOTALL)
    thetext = re.sub(r"<cell(.*?)</cell>",cell_hack,thetext,0,re.DOTALL)

    thetext = mytransform_mbx_figure(thetext)

    return thetext

##################

def cell_hack(txt):

    the_text = txt.group(1)

    if "<cell" in the_text:
        print "ERROR: nested cell"
        return "<cell" + the_text + "</cell>"

    the_text_stripped = the_text.strip()

    if the_text_stripped.startswith("><!--") and the_text_stripped.endswith("-->"):
        return "<cell>\n          <figure" + the_text + "</figure>\n          </cell>"
    else:
        return "<cell" + the_text + "</cell>"

##################

def sbs_hack(txt):

    the_text = txt.group(1)

    if "<sidebyside" in the_text:
        print "ERROR: nested sidebyside"
        return "<sidebyside" + the_text + "</sidebyside>"

    if "<image" in the_text and "<figure" not in the_text:
        print "bare image in sbs"
        the_text = process_fig_mult(the_text)
        return "<figure" + the_text + "</figure>"

#    print "processing a sidebyside:", the_text[:130]
    the_text = re.sub(r"<figure(.*?)</figure>",process_figure,the_text,0,re.DOTALL)

    return "<sidebyside" + the_text + "</sidebyside>"

##################

def mytransform_mbx_figure(text):

    thetext = text

    thetext = re.sub(r"<figure(.*?)</figure>",process_figure,thetext,0,re.DOTALL)

    return thetext

##################

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

    newtext = text
    newtext = re.sub(r"\s*{\s*(\\large)*\s*(\\bf)*\s*Exercises\s*-*\s*\\thesection\\*\s*}([^}]{2,60}\})",
                         r"\\begin{exercises}\3" + "\n\\end{exercises}",newtext,0, re.DOTALL)
    thetext = newtext

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

    elif the_text.startswith(">"):  # no xml:id, so look elsewhere
        if "START" in the_text and "<image>" in the_text:
            the_text = process_fig_mult(the_text)
        return "<figure" + the_text + "</figure>"

    # should start with the xml:id:
    try:
     #   the_xml_id = re.match('^ xml:id="fig_([^"]+)"',the_text).group(1)
        the_xml_id = re.match('^ xml:id="fig([^"]+)"',the_text).group(1)
    except AttributeError:
        print "figure should have an xml:id, but it doesn't",the_text[:200]
        return "<figure" + the_text + "</figure>"

    if the_xml_id.startswith("_"):
        the_xml_id = the_xml_id[1:]
    
    # should be only one contained image
    if the_text.count("<image>") > 1:
        print "more than one contained image in fig_" + the_xml_id
        the_text = process_fig_mult(the_text)
        return "<figure" + the_text + "</figure>" 

# should we skip this, because it was done in a previous iteration?
    # now put that id on the image
    the_text = re.sub("<image>",'<image xml:id="img_' + the_xml_id + '" >', the_text)

    return "<figure" + the_text + "</figure>" 

##################

def process_fig_mult(text):

    thetext = text

    text_parts = thetext.split("START")

    new_text = []

    for part in text_parts:
        try:
            this_id = re.search("figures/(.*?)\.(tex|asy)", part).group(1)
            print "found a possible image id:", this_id
            this_id = re.sub("fig_", "img_", this_id)
            this_id = re.sub("^fig", "img_", this_id)
            part = re.sub("<image>", '<image xml:id="' + this_id + '" >', part)
        except:
            print "can't find the figures filename",part[:10]
            pass
        new_text.append(part)

    new_text = "START".join(new_text) 
       
    return new_text

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
#    the_result += '      <answer>' + '\n'
#    the_result += '        ' + the_answer + '\n'
#    the_result += '      </answer>' + '\n'
    the_result += '      <solution>' + '\n'
    the_result += '        ' + the_answer + '\n'
    the_result += '      </solution>' + '\n'
    the_result += '    </webwork>' + '\n'
    the_result += '  </exercise>' + '\n'

    return the_result

