# -*- coding: utf-8 -*-


import re

import utilities
import component
import postprocess

def setvariables(text):

    component.chapter_abbrev = utilities.argument_of_macro(text,"chap",2)


###################

def fa_convert(txt):

# todo:  line 425 of sec_chainrule.mbx:
#        <mrow>\lz{y}{x} \amp = y'(u) \cdot u'(x)\amp\amp \text{XCXVXBXN(since } y=\fa{f}{u} \text{ and }u=\fa{g}{x}</mrow>
#  does <static>5\sec^2(5x)</static> count as math mode?
# \sum a_n(x-c)^n

    thetext = txt.group(0)

    thetext = re.sub(r"\\mathopen{}", "", thetext)
    thetext = re.sub(r"\\mathclose{}", "", thetext)

    # first we hide parentheses that definitely(?) are not the arguments of functions
    # anything of the form non_function(x) is not a function applied to x
    # replace ( by LPLPLPLP and ) by RPRPRP

    # but first, the edge case of half-open interval notation: (a,b]
    thetext = re.sub(r"\((\s*[0-9a-zA-Z/\-\\]+\s*),(\s*[0-9a-zA-Z/\-\\]+\s*)]",
                        r"LPLPLP\1,\1]", thetext)

    non_functions = [r">", "=", r"\\int", r"\+", r"-", r"/", r"\\cdots{0,1}", r"\\times", "!", "{", "RPRPRP"]
    separators = ["arrow", r"\\to", r"\\la", ",", r"\\ "]
             # the ">" should be a "^", except that the opening <m> is passed
             # can;t include "}" because of \sin^{23}(x)
             # should ) be here or later?
    all_non_functions = non_functions + separators
    non_functions_as_choice = "(" + "|".join(all_non_functions) + ")"
    utilities.something_changed = 1
    while utilities.something_changed:
        utilities.something_changed = 0
        thetext = re.sub(non_functions_as_choice + r"(|\^.|\^{[^{}]+}|\^\\[a-zA-Z]+)" +
                                               r"(\s*)((\\left|\\big|\\bigg|\\Big|\\Bigg)*\(.*)",
                           #  r"\\fa{\1\2}{\3}",
                             fa_nf_conv, thetext, 1, re.DOTALL)

    trig_functions = [r"\\sin",r"\\cos",r"\\tan",r"\\sec",r"\\csc",r"\\cot"]
    arc_trig_functions = [r"\\arcsin",r"\\arccos",r"\\arctan",r"\\arcsec",r"\\arccsc",r"\\arccot"]
    hyp_functions = [r"\\sinh",r"\\coth", r"\\tanh"]
    log_functions = [r"\\log",r"\\ln",r"\\exp"]
    generic_functions = [r"\\fp", "f", "g", "h", "p", "q", "F", "G", "P", "Q"]
    compound_functions = [r"\\vec [a-zA-Z]", r"\\vec [a-zA-Z]\\,", r"\\vec [a-zA-Z]\\,'"]
    occasionally_functions = ["v", r"\\ell"]

    all_functions = trig_functions + arc_trig_functions + hyp_functions + log_functions + generic_functions + compound_functions + occasionally_functions
    all_as_choice = "(" + "|".join(all_functions) + ")"

    utilities.something_changed = 1
    while utilities.something_changed:
        utilities.something_changed = 0
                       #  function             to a power
        thetext = re.sub("()" + all_as_choice + r"((|\^.|\^{[^{}]+}|\^\\[a-zA-Z]+|_.|_{[0-9xyzuvw]+})(|'|''|'''))" +
                                               # possibly resized         left paren
                                               r"\s*((\\left|\\big|\\Big)*\(.*)",
                           #  r"\\fa{\1\2}{\3}",
                             fa_conv, thetext, 1, re.DOTALL)

    # guess that <m>x(y)</m> is always the function x applied to the argument y
    thetext = re.sub(r"(<m>|<mrow>)(\ds |)([a-zA-Z]_*[LMRU0-9]*(\\,)*'*)\(([a-zA-Z0-9]_*[0-9ijmn]*)\)(</m>|</mrow>)", r"\1\2\\fa{\3}{\5}\6", thetext)
    thetext = re.sub(r"(<m>|<mrow>)(\\ds |)([a-zA-Z]_*[LMRU0-9]*(\\,)*'*)\(([a-zA-Z0-9]_*[0-9]*)\)(\s*=.*)(</m>|</mrow>)", r"\1\2\\fa{\3}{\5}\6\7", thetext)
    thetext = re.sub(r"(<m>|<mrow>)(\ds |)([a-zA-Z]\s*)=(\s*[a-zA-Z]_*[LMRU0-9]*(\\,)*'*)\(([a-zA-Z0-9]_*[0-9]*)\)(</m>|</mrow>)", r"\1\2\3=\\fa{\4}{\6}\7", thetext)
    thetext = re.sub(r"\b(y'*)\(([\-0-9]|x|t)\)", r"\\fa{\1}{\2}", thetext)
    thetext = re.sub(r"\b(r'*)\(([\-0-9]|x|y|z|t)\)", r"\\fa{\1}{\2}", thetext)

    thetext = re.sub(r"\b([a-zA-Z](\\,)*'+)\(([\-0-9]+|[a-zA-Z\\]+|[a-zA-A]_[0-9ijmn])\)", r"\\fa{\1}{\3}", thetext)
    thetext = re.sub(r"(\\kappa'*)\(([a-zA-Z0-9/\\]+_*[0-9ijmn]*)\)", r"\\fa{\1}{\2}", thetext)
    thetext = re.sub(r"(\\delta)\(([a-z, _\\]+)\)", r"\\fa{\1}{\2}", thetext)

    more_non_functions = [r"[0-9]", r"{", r"}", "\)", "k", "n", "m", r"\\pi", "RPRPRP"]
    letter_non_functions = ["x", "t"]
    more_non_functions_as_choice = "(" + "|".join(more_non_functions + letter_non_functions) + ")"
    utilities.something_changed = 1
    while utilities.something_changed:
        utilities.something_changed = 0
        thetext = re.sub(more_non_functions_as_choice + r"(|\^.|\^{[^{}]+}|\^\\[a-zA-Z]+)" +
                                               r"(\s*)((\\left|\\big|\\bigg|\\Big|\\Bigg)*\(.*)",
                           #  r"\\fa{\1\2}{\3}",
                             fa_nf_conv, thetext, 1, re.DOTALL)

    if "(" in thetext and "\\(" not in thetext:
        print thetext
        component.generic_counter += 1

    return thetext

###################

def fa_nf_conv(txt):

    the_function = txt.group(1)
    the_power = txt.group(2)
    the_space = txt.group(3)
    the_argument_plus = txt.group(4).lstrip()

    utilities.something_changed += 1

    hasleft = False
    the_left = ""

    if the_argument_plus.startswith(("\\left","\\big","\\Big")):
        hasleft = True
        the_left = re.sub(r"\(.*", "", the_argument_plus);
        the_argument_plus = re.sub(r"^.*?\(", "(", the_argument_plus)

    the_argument_orig, everything_else = utilities.first_bracketed_string(the_argument_plus, lbrack="(", rbrack=")")

    if the_argument_orig:
        the_argument = the_argument_orig[1:-1]
        if hasleft:  # then remove the \right
        #    the_argument = the_argument[:-6]
            if "\\" not in the_argument[-6:]:
                print "missing \\right or other size directive"
                print txt.group(0)
                print txt.group(1)
                print txt.group(2)
                print txt.group(3)
                print the_argument_orig
            the_argument = re.sub(r"\\.{0,5}$", "", the_argument)

        if "\\infty" in txt.group(0) and False:
                print "                  inftyoverline found"
                print "everything:",txt.group(0)
                print "the_function",txt.group(1)
                print "the_power", txt.group(2)
                print "original the_argument_plus", txt.group(3)
                print "the_argument_orig", the_argument_orig
                print "the_left", the_left
                print "the_argument", the_argument, "\n\n"

        #return the_function + the_power + the_left + "LPLPLP" + the_argument + "RPRPRP" + everything_else
        #return the_function + the_power + "LPLPLP" + the_argument + "RPRPRP" + everything_else
        return the_function + the_power + the_space + "LPLPLP" + the_argument + "RPRPRP" + everything_else
    else:
        return the_function + "XCXVXBXN" + the_argument_plus

###################

def fa_conv(txt):

    nothing = txt.group(1)
    the_function = txt.group(2)
    the_power = txt.group(3)  # includes ' or ''
    the_argument_plus = txt.group(6).lstrip()

    hasleft = False
    utilities.something_changed += 1
    if the_argument_plus.startswith(("\\left","\\big","\\Big")):
        hasleft = True
    #    the_argument_plus = the_argument_plus[5:]
        the_argument_plus = re.sub(r"^.*?\(", "(", the_argument_plus)
    the_argument_orig, everything_else = utilities.first_bracketed_string(the_argument_plus, lbrack="(", rbrack=")")
    if the_argument_orig:
        the_argument = the_argument_orig[1:-1]
        if hasleft:  # then remove the \right
        #    the_argument = the_argument[:-6]
            if "\\" not in the_argument[-6:]:
                print "missing \\right or other size directive"
                print txt.group(0)
                print txt.group(1)
                print txt.group(2)
                print txt.group(3)
                print the_argument_orig
    # next line should specificallt target \right, \big, \Big, etc
            the_argument = re.sub(r"\\[^\\]*$", "", the_argument)
            the_argument = the_argument
        return r"\fa{" + the_function + the_power + "}{" + the_argument + "}" + everything_else
    else:
        return the_function + "XCXVXBXN" + the_argument_plus

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

def mytransform_txt(text):

    thetext = text

    thetext = re.sub(r"^Hint for.*", "", thetext)
    thetext = re.sub(r".$", "", thetext,1,re.DOTALL)
    return thetext

###################

def mytransform_pfp(text):

    thetext = text
    theappslist = thetext.split("QWuiSs")
    
    the_answer = r"\documentclass[11pt]{amsart}" + "\n"
    the_answer += r"\usepackage{tgtermes}" + "\n"
    the_answer += r"\textwidth=6.5in" + "\n"
    the_answer += r" \hoffset=-.75in" + "\n"
    the_answer += r"\parskip 0.05in" + "\n"
    the_answer += r"\parindent 0in" + "\n"
    the_answer += r"\setlength{\textheight}{9.5 true in}" + "\n"
    the_answer += r"\setlength{\topmargin}{-.60in}" + "\n"

    the_answer += r"\begin{document}" + "\n\n"
    # assume the spreadsheet has everyone in the correct order
    component.numberof = 0
    for app in theappslist[1:]:
        this_person = ""
        app = app.strip()
        if not app:
            continue
        component.numberof += 1
        app = re.sub(r'\x0d',"\n\n",app)
        app = re.sub('\t'," ",app)
        app = re.sub(r' {2,}'," ",app)
        app = re.sub(r'(^|\s)\x5f',r"\1'",app)
        app = re.sub(r'\x5f(\s|$)',r"'\1",app)
        app = re.sub(r'\x5f(.{1,2})(\)|\.|,|\s|$)',r"'\1\2",app)
        app = re.sub(r'(\s|^)(.{1,2})\x5f',r"\1\2'",app)
        # \x5f can be an apostrophe or a dash
        app = re.sub(r'\x5f',r" -- ",app)
        app = re.sub(r'\x82',"\\'e",app)
        app = re.sub(r'\x8b','\\"{\\i}',app)
        app = re.sub(r'\x29',")",app)
        app = re.sub(r'\%',r"\\%",app)
        app = re.sub(r'&',r"\\&",app)
        app = re.sub(r'\$',r"\\$",app)
        app = re.sub(r'\#',r"\\#",app)
        app = re.sub(r'\\hum',r"hum",app)
        app = re.sub('\t'," ",app)
        app = re.sub(r'\x91',r"'",app)
        app = re.sub(r'\x92',r"'",app)

        thisapp = app.split("Brrrrk")
        the_name = r"{\large \textbf{" + str(component.numberof) + ". "
        the_name += thisapp[0].strip() + " "
        the_name += r"\textsc{" + thisapp[2].strip() + "}" + r"}}\\" + "\n"
        the_email_address = re.sub(r"_", "\\_", thisapp[3].strip())
        the_email = r"\textit{Email:} " + the_email_address + r"\\" + "\n\n"

        the_academics_text = thisapp[5].strip()
        the_academics_text = re.sub(r'^"',"",the_academics_text)
        the_academics_text = re.sub(r'"$',"",the_academics_text)
        the_academics_text = re.sub(r'""','"',the_academics_text)
        the_academics_text = re.sub(r'(^|\s)"(.+?)"(\s|$|,|\.)',r"\1``\2''\3",the_academics_text)
        the_academics_text = re.sub(r"(^|\s)'(.+?)'(\s|$|,|\.)",r"\1`\2'\3",the_academics_text)
        the_academics_text = re.sub('\n{2,}',"\n",the_academics_text)
        the_academics = r"\noindent\textit{Academic Interests:} " + the_academics_text + "\n\\vskip 0.1in\n"

        the_others_text = thisapp[6].strip()
        the_others_text = re.sub(r'^"',"",the_others_text)
        the_others_text = re.sub(r'"$',"",the_others_text)
        the_others_text = re.sub('\n{2,}',"\n",the_others_text)
        the_others = r"\noindent\textit{Other Interests:} " + the_others_text + "\n\\vskip 0.1in\n"

        essay_length = len(thisapp[4].strip().split())

        essay_text = thisapp[4].strip()
        essay_text = re.sub(r'^"',"",essay_text)
        essay_text = re.sub(r'"$',"",essay_text)
        essay_text = re.sub(r'""','"',essay_text)
        essay_text = re.sub(r'(^|\s)"(.+?)"(\s|$|,|\.)',r"\1``\2''\3",essay_text)
        essay_text = re.sub(r"(^|\s)'(.+?)'(\s|$|,|\.)",r"\1`\2'\3",essay_text)
        essay_text = re.sub(r'\x0d',"\n\n",essay_text)
        essay_text = re.sub(r'\x00\x90',r"\\'E",essay_text)
        essay_text = re.sub(r'\x00ff',r" ",essay_text)
        essay_text = re.sub(r'ÿ',r" ",essay_text)
        essay_text = re.sub(r'\x00d5',r"'",essay_text)
        essay_text = re.sub(r'Õ',r"'",essay_text)
#        essay_text = re.sub(r'\x0d',"\n\n",essay_text)

        the_essay = r"\noindent\textit{Essay:}\\" + "\n" + essay_text + r"\\" + "\n"
        the_essay += r"\phantom{x}\hfill " + "[" + str(essay_length) + "]"
        


        this_person = the_name + the_email + the_academics + the_others + the_essay
        this_person += "\n\n" + r"\newpage" + "\n\n"

        the_answer += this_person

#    thetext = re.sub(r"^Hint for.*", "", thetext)
#    thetext = re.sub(r".$", "", thetext,1,re.DOTALL)
    return the_answer + "\n\n" + r"\end{document}" + "\n\n"

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

#    thetext = re.sub(r"\\noindent\s*{\\bf\s+Example\s+[0-9.]+\s*}",r"\\begin{example}",thetext)
#    thetext = re.sub(r"\\hspace{\\fill}\s*\$\\blacksquare\$",r"\\end{example}",thetext)
#
#    # delete empty label arguments
#    thetext = re.sub(r"\\label{[a-zA-Z]+:[a-zA-Z]+:}","",thetext)
#
#    newtext = text
#    newtext = re.sub(r"\s*{\s*(\\large)*\s*(\\bf)*\s*Exercises\s*-*\s*\\thesection\\*\s*}([^}]{2,60}\})",
#                         r"\\begin{exercises}\3" + "\n\\end{exercises}",newtext,0, re.DOTALL)
#    thetext = newtext

    # from Bogart's IBL combinatorics book

    thetext = re.sub(r"\\bp\s(.*?)\\ep\s", myt_tex, thetext, 0, re.DOTALL)

    return thetext

#####################

def myt_tex(txt):

    thetext = txt.group(1)

    #\item is confusing when it is at the top level, so at least
    # catch it at the start of a problem
    thetext = re.sub(r"^\s*\\item\s+", r"\\itemx ", thetext)
    thetext = re.sub(r"(^|\n) *\\item(m|e|s|i|ei|es|esi|si|h|ih|x)\s", r"\nSPLIT\2DIVVV", thetext)

    problem_type = {'m':'motivation',
                    'e':'essential',
                    's':'summary',
                    'i':'interesting',
                    'ei':'essential and interesting',
                    'es':'essential for this or the next section',
                    'esi':'essential for this or the next section, and interesting',
                    'h':'difficult',
                    'ih':'interesting and difficult',
                    'x':'',
                    '':''}

    the_problems = thetext.split("SPLIT")
    the_answer = ""

    for problem in the_problems:
        problem = problem.strip()
        if not problem:
            continue
        try:
            the_type, the_statement = problem.split("DIVVV")
            this_problem_type = problem_type[the_type]
        except ValueError:
            if problem.startswith(r"\item "):
                the_statement = problem[:6]
                this_problem_type = ""
            else:
                print "WEIRD", problem
        #    print "the_type",the_type
                print "ERR:", problem[:50]
        the_answer += r"\begin{problem}"
        if this_problem_type:
            the_answer += r"(" + this_problem_type + ")" 
        the_answer += "\n"
        the_answer += the_statement + "\n"
        the_answer += r"\end{problem}" + "\n\n"

    return the_answer

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

#################

def wwmacros(text):

    thetext = text

    thetext = re.sub(".*loadMacros\(", "", thetext, 0, re.DOTALL)
    thetext = re.sub("\);", "", thetext, 0, re.DOTALL)
    thetext = thetext.strip()

    known_macros = ["PGstandard.pl"]

    the_macros = thetext.split(",")

    macros_in_mbx = "<pg-macros>" + "\n"

    for macro in the_macros:
        macro = macro.strip()
        if not macro:
            continue
        if macro.startswith("#"):
            continue
        macro = re.sub('"', '', macro)
        if macro not in known_macros:
            macros_in_mbx += "<macro-file>" + macro + "</macro-file>" + "\n"

    macros_in_mbx += "</pg-macros>" + "\n"

    return macros_in_mbx

################

def pgmarkup_to_mbx(text, the_answer_variables):
    """ Change one paragrapf from pg-style markup to mbx-style.

    """

    the_text = text.strip()

#    the_text = re.sub(r"\[``", "<me>", the_text)
#    the_text = re.sub(r"``\]", "</me>", the_text)
#    the_text = re.sub(r"\[`", "<m>", the_text)
#    the_text = re.sub(r"`\]", "</m>", the_text)

#    the_text = utilities.magic_character_convert(the_text, "text")

    the_text = re.sub(r"\[`(.*?)`\]", pg_math_environments, the_text, 0, re.DOTALL)

    the_text = re.sub(r">>\[\s*@\s*image\((.*?)\)\s*@\]\*<<", pg_image_environments, the_text, 0, re.DOTALL)

    the_text = re.sub(r"\[\s*(\$[a-zA-Z0-9_]+)\s*\]", r'<var name="\1" />', the_text)

#    if "_____" in the_text:
#        print "          found  ____________ ", the_text

    component.substitution_counter = 0
    the_text = re.sub(r"(\[_+\])((\{\$[a-zA-Z0-9_]*\}){0,1})", lambda match: pg_input_fields(match, the_answer_variables), the_text)

    # crude way to capture *emphasized words*.
    while "*" in the_text:
        the_text = re.sub(r"\*", "<em>", the_text, 1)
        the_text = re.sub(r"\*", "</em>", the_text, 1)

    return the_text

#------------------#

def pg_image_environments(txt):

    the_text = txt.group(1)
    the_text = the_text.strip()

    if not the_text.startswith("insertGraph"):
        print "ERROR: malformed image markup"
        return "<figure>" + "ERROR" + the_text + "</figure>"

    the_name = re.match(r"insertGraph\(([^)]+)\)", the_text).group(1).strip()
    the_width = re.search(r"width\s*=>\s*([^, ]+)(,| |\b)", the_text).group(1).strip()
    the_height = re.search(r"height\s*=>\s*([^, ]+)(,| |\b)", the_text).group(1).strip()
    the_tex_size = re.search(r"tex_size\s*=>\s*([^, ]+)(,| |\b)", the_text).group(1).strip()
    #is alt the right thing to grab for the description?
    the_alt = re.search(r"alt\s*=\s*([^, ]+)(,| |\b)", the_text).group(1).strip()
    the_alt = the_alt[1:-1]   # remove surrounding quotes

    the_image_short = '<image pg-name="' + the_name + '" />' + "\n"

    the_image_long = '<image pg-name="' + the_name + '" '
    the_image_long += 'width="' + the_width + '" '
    the_image_long += 'height="' + the_height + '" '
    the_image_long += 'tex_size="' + the_tex_size + '" '
    the_image_long += '>' + "\n"
    the_image_long += "<description>"
    the_image_long += '<var name="' + the_alt + '" />'
    the_image_long += "</description>" + "\n"
    the_image_long += "</image>" + "\n"

    the_answer = "<figure>" + "\n" + the_image_long + "</figure>" + "\n"

    return the_answer
#------------------#

def pg_math_environments(txt):
    """ Convert [`*`], [``*``], [``\begin{align}*``], etc to mbx markup.

    """

    the_text = txt.group(1)

    if not the_text.startswith("`"):
        return "<m>" + the_text + "</m>"

    # so it should start and end with `
    the_text = the_text[1:-1].strip()

    if not the_text.startswith("\\begin{aligned}"):
        return "<me>" + the_text + "</me>"

    # remove the begin and end align
    the_text = the_text[15:-13].strip()

#    print "xx"+the_text[:10]+"yy", the_text.startswith(r"[t]")

    if the_text.startswith(r"[t]"):
        the_text = the_text[3:].strip()

    the_output = "<md>" + "\n"
    the_mrows = the_text.split("\\\\")
    for row in the_mrows:
 #       print "row : ", row
        row = row.strip()
        row = utilities.magic_character_convert(row, "math")
        the_output += "<mrow>" + row + "</mrow>" + "\n"

    the_output += "</md>"

    return the_output
#------------------#

def pg_input_fields(txt, the_answer_variables):
    """ Convert [___________]  and [___________]{$foo} to mbx format.

    """

    the_text = txt.group(1)
    the_variable = txt.group(2)
    the_variable = the_variable[1:-1]

#    if len(the_answer_variables) > 1:
#        print "multiple answers", the_answer_variables
    # should add an error check that the_text is of the form [___________]

    width = len(the_text) - 2

    style = "externalvar"
    print "the_variable", the_variable, "and the_answer_variables", the_answer_variables
    if the_variable:
        this_variable = the_variable
        style = "internalvar"
    else:
        try:
            this_variable = the_answer_variables[component.substitution_counter]
        except IndexError:
            this_variable = "ERROR_VARIABLE_NOT_FOUND_IN_ORIGINAL_SOURCE"
            print "ERROR: name of variable not found"
    component.substitution_counter += 1
    the_answer = '<var name="' + this_variable + '" '
    if style == "externalvar":
        the_answer += 'evaluator="$ansevaluator" '
    elif this_variable in component.defined_variables:
        print "found", this_variable, "in", component.defined_variables
        the_answer += 'evaluator="' + component.defined_variables[this_variable] + '" '
    the_answer += 'width="' + str(width) + '" />'

    return the_answer

