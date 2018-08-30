
import re

import utilities
import component
import postprocess
import transforms

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

#def mytransform_mbx(text):   # schmidt calc 3 temporary
def mbx_fix(text):   # schmidt calc 3 temporary


    thetext = text
    print "in mbx_fix"

    thetext = re.sub(r"\\G\b", r"\\mathcal{G}", thetext)
    thetext = re.sub(r"\\fatr\b", r"\\R", thetext)
    thetext = re.sub(r"\\fatz\b", r"\\Z", thetext)
    thetext = re.sub(r"\\fatq\b", r"\\Q", thetext)
    thetext = re.sub(r"\\fatc\b", r"\\C", thetext)
    thetext = re.sub(r"\\fatn\b", r"\\N", thetext)

#    thetext = re.sub(r"EXTRA\s*<fn>(.*?)</fn>\s*", r"\\extrafn{\1}", thetext, 0, re.DOTALL)
#
#    for mac in ["bmw", "valpo", "valposhort","marginparbmw"]:
#         thetext = utilities.replacemacro(thetext,mac,1,"\n<insight><p>\n#1\n</p></insight>\n")
#
##    for mac in ["extrafn", "instructor"]:
#    for mac in ["note"]:
#        thetext = utilities.replacemacro(thetext, mac,1,"<!-- \XX" + mac + "{#1} -->")
#        thetext = re.sub("XX" + mac, mac, thetext)
#
#    thetext = re.sub(r"<p>\s*\\section{([^}]+)}",r"\\section{\1}<p>",thetext)
#    thetext = utilities.replacemacro(thetext,"section",1,"<title>#1</title>\n")
#
#    thetext = utilities.replacemacro(thetext,"item",0,"</p></li>\n<li><p>\n")
#    thetext = re.sub(r"\\begin{itemize}\s*</p>\s*</li>","<ul>",thetext)
#    thetext = re.sub(r"\\end{itemize}","</p></li></ul>",thetext)
    
    return thetext

def mytransform_mbx_linefeeds(text):

    thetext = text

#    print "should be deleting existing formatting, but check!"
# kill existing formatting.
# need to rethink this!

#    # temporary for apex
#    thetext = re.sub(r'(\s+)<table xml:id="([^" ]+)"\s*>\s+(<caption>.{,200}</caption>)\s*<tabular>\s*<row>\s*<cell>(.{,200})</cell>\s*</row>\s*</tabular>\s*</table>',
#            r'\1<figure xml:id="\2">\1  \3\1    \4\1</figure>', thetext)

#    thetext = re.sub("\n +", "\n", thetext)

    thetext = fix_ptx_math_punctuation(thetext)
#    thetext = transforms.mbx_pp(thetext)

    #  now we make all the p tags separate
    for lip_tag in ["p"]:
        component.lipcounter[lip_tag] = 0
        thetext = utilities.tag_to_numbered_tag(lip_tag, thetext)

        print "counted", component.lipcounter[lip_tag], "of", lip_tag

    print re.sub("Practice visualizing vector addition", "Practice visualizing vector1addition", thetext)
    # before we put line feeds in p's, there could be some leaf li's
    # that just contain one big p that is not marked as a p.
    # So we arrange for that to have line breaks
    thetext = re.sub(r"(\n +)<li>([a-zA-Z].{50,}?)</li>", r"\1<li>\1  \2\1</li>",
                     thetext, 0, re.DOTALL)
    thetext = postprocess.add_line_feeds("li", thetext)
    print re.sub("Practice visualizing vector addition", "Practice visualizing vector2addition", thetext)

    for lip_tag in ["p"]:
        for n in range(component.lipcounter[lip_tag]):
            thetext = postprocess.add_line_feeds(lip_tag + str(n), thetext)

    print re.sub("Practice visualizing vector addition", "Practice visualizing vector3addition", thetext)
    # now put back the original p tags
    for lip_tag in ["p"]:
        for n in range(component.lipcounter[lip_tag]):
   #     thetext = re.sub(r"(\n *)<" + lip_tag + str(n) + ">",r"\1<" + lip_tag + ">", thetext)
   #     thetext = re.sub(r"(\n *)</" + lip_tag + str(n) + ">",r"\1</" + lip_tag + ">", thetext)
            thetext = re.sub(r"<" + lip_tag + str(n) + "( |>)", "<" + lip_tag + r"\1", thetext)
            thetext = re.sub(r"</" + lip_tag + str(n) + ">", "</" + lip_tag + ">", thetext)

    return thetext

 # ----------- #

    thetext = re.sub(r"<task\b(.*?)</task>", 
          lambda match: mytransform_mbx_tag(match, "task", "statement", "conclusion", ["hint", "answer", "solution"]),
          thetext,0, re.DOTALL)

    # if an exploration contains a task or hint,
    # then the introduction and conclusion needs to be wrapped
    thetext = re.sub(r"<exploration\b(.*?)</exploration>", 
          lambda match: mytransform_mbx_tag(match, "exploration", "introduction", "conclusion", ["task", "hint"]),
          thetext,0, re.DOTALL)

    thetext = re.sub(r"<example\b(.*?)</example>", 
          lambda match: mytransform_mbx_tag(match, "example", "statement", "conclusion", ["hint", "answer", "solution"]),
          thetext,0, re.DOTALL)

    return thetext

def mytransform_mbx_tag(txt, outertag, introtag, conclusiontag, innertags):

    the_text = txt.group(1)

    # If the intro tag (statement, introduction, etc) is in the environment,
    # then assume everything is okay.
    if "<" + introtag + ">" in the_text:
        return "<" + outertag + the_text + "</" + outertag + ">"

    if "<!--" in the_text:   # comments mess things up
        return "<" + outertag + the_text + "</" + outertag + ">"

    # If none of the innertags are in the environment, then there is no
    # need to use the introtag.
    has_inner_tag = False
    for tag in innertags:
        if "<" + tag + ">" in the_text: 
            has_inner_tag = True

    if not has_inner_tag:
        return "<" + outertag + the_text + "</" + outertag + ">"

    # We have determined there there are inner tags, but no intro tag,
    # so we need to pull things apart and then reassemble using the inner tag.

    # pull out the xml_id (which may be empty)
    the_id = re.sub("(.*?>)(.*)", r"\1", the_text, 1, re.DOTALL)
    the_text = re.sub("(.*?>)(.*)", r"\2", the_text, 1, re.DOTALL)

    # separate the title and index entries
    the_env = {}
    for tag in ["title", "idx"]:
        the_env[tag] = ""
        if "<" + tag in the_text:
            search_string = "^(.*?)(<" + tag + ">.*</" + tag + ">)(.*?)$"
            # pull out this tag and save it
            the_env[tag] = re.sub(search_string, r"\2", the_text, 1, re.DOTALL)
            # and then remove it from the_text
            the_text = re.sub(search_string, r"\1\3", the_text, 1, re.DOTALL)
        
    # presumably the only thing left in the_text is:
    # statement/intro/whatever goes first, then the selected tags, then the conclusion.
    innertags_re = "|".join(innertags)

    search_string = "^(.*?)(<(" + innertags_re + ").*$)"
    the_intro = re.sub(search_string, r"\1", the_text, 1, re.DOTALL)
    the_text = re.sub(search_string, r"\2", the_text, 1, re.DOTALL)

    search_string = "^(.*</(" + innertags_re + ")>)(.*?$)"
    the_conclusion = re.sub(search_string, r"\3", the_text, 1, re.DOTALL)
    the_text = re.sub(search_string, r"\1", the_text, 1, re.DOTALL)

    # the_text should now contain only the inner tags

    if the_intro.strip():
        the_env[introtag] = "<" + introtag + ">" + the_intro + "</" + introtag + ">"
    else:
        the_env[introtag] = ""
    if the_conclusion.strip():
        the_env[conclusiontag] = "<" + conclusiontag + ">" + the_conclusion + "</" + conclusiontag + ">"
    else:
        the_env[conclusiontag] = ""

    # now put the pieces back togetther again
    the_answer = "<" + outertag + the_id
    for tag in ["title", "idx"]:
        the_answer += the_env[tag]
    the_answer += the_env[introtag]
    the_answer += the_text
    the_answer += the_env[conclusiontag]
    the_answer += "</" + outertag + ">"

    return the_answer

def mytransform_mbx_act(txt):

    the_text = txt.group(1)

    the_start = re.sub("^([^<>]*>)(.*)", r"\1", the_text, 1, re.DOTALL)
    the_text = re.sub("^([^<>]*>)(.*)", r"\2", the_text, 1, re.DOTALL)

    the_text = the_text.strip()

#    if the_start:
#        print the_start
#        print the_text[:30]

#    the_text = re.sub("<statement>\s*", "", the_text)
#    the_text = re.sub("</statement>\s*", "", the_text)
    the_text = re.sub("<ol>\s*", "", the_text)
    the_text = re.sub("</ol>\s*", "", the_text)
    the_text = re.sub("<ul>\s*", "", the_text)
    the_text = re.sub("</ul>\s*", "", the_text)
    the_text = re.sub("<li>", "<task>", the_text)
    the_text = re.sub("<li ([^>]+)>", r"<task \1>", the_text)
    the_text = re.sub("</li>", "</task>", the_text)

    the_text = re.sub("(<task>\n) *<p>\n", r"\1", the_text)
    the_text = re.sub(" *</p>\n(\s*</task>\s*)", r"\1", the_text)

    the_text = re.sub(r"<task>(\s*)(.*?)<solution>",
                      r"<task>\1<statement><p>\2\1</p>\1</statement>\1<solution>",
                      the_text, 0, re.DOTALL)

    # may be too aggressive?
    the_text = re.sub(r"</solution>\s*<p>\s*\\item (.*?)</p>\s*<solution>",
                      r"</solution><task><statement><p>\1</p></statement></task><solution>",the_text,0,re.DOTALL)

    # the statement and solution should both be inside the task
    the_text = re.sub(r"</task>\s*<solution>(.*?)</solution>",
                      r"<solution>\1</solution></task>",the_text,0,re.DOTALL)

    # maybe first taskis not wrapped in task
    the_text = re.sub(r"<statement>(.*?)</solution>\s*<task>",
                      r"<task><statement>\1</solution></task><task>",the_text,0,re.DOTALL)

    the_text = re.sub(r"<p>\s*<p>","<p>", the_text)
    the_text = re.sub(r"</solution>\s*</p>","</solution>", the_text)

    if the_text.startswith("<statement") and the_text.endswith("statement>") and "<task>" in the_text:
        the_text = the_text[11:-12]
        the_text = the_text.strip()
    #    print "ggggg" + the_text[:20]
    #    print "uuuuu" + the_text[-20:]

        if the_text.startswith("<p>") and the_text.endswith("</p>"):
            the_text = the_text[3:-4]
            the_text = the_text.strip()
            the_text = re.sub("^(.*?)<task", r"<p>\1</p><task", the_text, 1, re.DOTALL)

    if the_text.startswith("<statement") and the_text.endswith("solution>") and "<task>" in the_text:

        the_text_part1 = re.sub("^(.*)</statement>(.*?)$", r"\1", the_text, 1, re.DOTALL)
        the_text_part2 = re.sub("^(.*)</statement>(.*?)$", r"\2", the_text, 1, re.DOTALL)
        the_text_part1 = the_text_part1[11:].strip()
        print "ggggg" + the_text_part1[:40]
        print "uuuuu" + the_text_part1[-40:]

        if the_text_part1.startswith("<p>") and the_text_part1.endswith("</p>"):
            print "the_text_part1" + the_text_part1[:33]
            the_text_part1 = the_text_part1[3:-4]
            the_text_part1 = the_text_part1.strip()
            the_text_part1 = re.sub("^(.*?)<task", r"<p>\1</p><task", the_text_part1, 1, re.DOTALL)
        the_text = the_text_part1 + the_text_part2

    the_text = re.sub(r"</task>\s*</p>","</task>", the_text)

    return "<activity" + the_start + the_text + "</activity>"

def mytransform_mbx_parentheses(text):

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

    lines = thetext.split("\n")

    url_stub = "http://linear.ups.edu/fcla/section-"
    this_section = "WILA"
    this_subsection = "LA"
    the_answer = ""

    for line in lines:
        if line.startswith("\\sec"):
            this_section = re.sub(" .*", "", line[5:])
        #    print "xxx"+sec_abbr+"yyy"
        elif line.startswith("\\ssec"):
            this_subsection = re.sub(" .*", "", line[6:])
        elif "::" in line:
            try:
                type_name, these_ids = line.split(" :: ")
            except:
                print "cccc", line, "dddd"
            id_lis = these_ids.strip().split(",")
            try:
                this_type, this_name = type_name.split(" ")
            except:
                print "aaaa", type_name, "bbbb" 
            for this_id in id_lis:
                this_id = this_id.strip()
                if not this_id:
                    next
                this_link = this_id
                this_link += " "
                this_link += url_stub
                this_link += this_section
                this_link += ".html" + "#"
                if this_type in ["Definition", "Theorem", "Example"]:
                    this_link += this_type.lower()
                    this_link += "-"
                    this_link += this_name
                else:
                    this_link += "subsection"
                    this_link += "-"
                    this_link += this_section
                    this_link += "-"
                    this_link += this_subsection
                the_answer += this_link + "\n"
        elif line:
            print "skipping", line

#    thetext = re.sub(r"^Hint for.*", "", thetext)
#    thetext = re.sub(r".$", "", thetext,1,re.DOTALL)
#
#    thetext = "<hint>\n  <p>\n" + thetext.strip() + "\n  </p>\n</hint>\n"

    return the_answer

###################

def mytransform_tex_ptx(text):

    thetext = text

    # first let's throw away stuff we can't use
    thetext = re.sub(r"\\def\\labelenumi.*", "", thetext)
    thetext = re.sub(r"[%].*", "", thetext)
    # delete backslash followed by white space
    thetext = re.sub(r"\\\s+", "", thetext)

    # 3 or more \n should just be 2 of them
    thetext = re.sub("\n{3,}", "\n\n", thetext)

    # convert the math delimiters
    # note that this substitution also puts one space befre and after
    # inline math, because that seemed to be consistently wrong in the source
    thetext = re.sub(r"\s*\\\(\s*", " <m>", thetext)
    thetext = re.sub(r"\s*\\\)\s*", "</m> ", thetext)

    # would need to me more clever if there were multiline displays,
    # but there doesnt seem to be any
    thetext = re.sub(r"\\\[", "<md>", thetext)
    thetext = re.sub(r"\\\]", "</md>", thetext)

    # obviously it would be eassy  to fix the \title{...} by hand,
    # but I wanted to show you how replacemacro works
    thetext = utilities.replacemacro(thetext, "title", 1,
           "<title>#1</title>")

    # Convert enumerate to ol
    # This approach is a bit sloppy, but works in many cases
    thetext = re.sub(r"\s*\\begin{enumerate}\s*", "\n\n<ol>\n<li>", thetext)
    thetext = re.sub(r"\s*\\end{enumerate}\s*", "</li>\n</ol>\n\n", thetext)
    thetext = re.sub(r"\s*\\item\s*", "</li>\n<li>", thetext)

    # see line 2608.  A good example of doing things in the right order
    thetext = re.sub(r"\\emph{\\\\\s+", r"\\emph{", thetext)
    # Hope that theorems contain no blank lines
    thetext = re.sub(r"\\emph{THEOREM[^{}]*}(.*?)\n\n",
                     r"<theorem><statement><p>\1</p></statement></theorem>",
                     thetext, 0, re.DOTALL)

    # guess that things in all caps are section titles
    thetext = re.sub(r"\n\n([A-Z]{2,} [A-Z]+)\n\n",
                     "</p></section>\n\n<section><title>" + r"\1" + r"</title>\n\n<p>",
                     thetext)
    # but now there is an extra </p></section> at the beginning, and a missing one at the end
    thetext = re.sub(r"</p></section>", "", thetext, 1)
    thetext = thetext + "</section>"

    # feeble attempt at paragraph markup
    thetext = re.sub(r"\.\n\n([A-Z][a-z ])", r"</p><p>\1", thetext)

    thetext = re.sub(r"``(.+)''", r"<q>\1</q>", thetext)

    # delete some garbage
    # empty li
    thetext = re.sub(r"<li>\s*</li>", "", thetext)


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

#    # from Bogart's IBL combinatorics book
#
#    thetext = re.sub(r"\\bp\s(.*?)\\ep\s", myt_tex, thetext, 0, re.DOTALL)

#    thetext = re.sub(r".*\\section\*", r"\\section", thetext, 0, re.DOTALL)
#    thetext = re.sub(r"\\begin{ex}", r"\\begin{example}", thetext)
#    thetext = re.sub(r"\\end{ex}", r"\\end{example}", thetext)
#    thetext = re.sub(r"\\begin{framed}", r"\\begin{aside}", thetext)
#    thetext = re.sub(r"\\end{framed}", r"\\end{aside}", thetext)
    thetext = re.sub(r".*\\input table", "", thetext, 0, re.DOTALL)
    thetext = re.sub(r"\\end{document}.*", "", thetext, 0, re.DOTALL)

    thetext = "\n\n" + r"\begin{solution}" + "\n" + thetext.strip() + "\n" + r"\end{solution}" + "\n\n"

    thetext = re.sub("\r\n", "\n", thetext, 0, re.DOTALL)

#    thetext = re.sub(r"\s*\\\\\s*~\\\\\s*", "\n\n", thetext, 0, re.DOTALL)
#    thetext = re.sub(r"\\\\\n\n", "\n\n", thetext, 0, re.DOTALL)
    # incorrect use of ``smart quotes"
    # don't try to make this perfect
#    thetext = re.sub(r'``([^`\'"\n]{,50})"', r"``\1''", thetext)

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

    known_macros = ["PGstandard.pl", "MathObjects.pl", "PGML.pl", "PGcourse.pl"]

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
    for macro in component.extra_macros:
        if macro not in the_macros:
            macros_in_mbx += "<macro-file>" + macro + "</macro-file>" + "\n"
    macros_in_mbx += "</pg-macros>" + "\n"

    return macros_in_mbx

################

def pgmarkup_to_mbx(text, the_answer_variables=[]):
    """ Change one paragrapf from pg-style markup to mbx-style.

    """

    the_text = text.strip()

#    for TAG in ["$PAR", "$BCENTER", "$ECENTER"]:
#        the_text = re.sub(" *\$" + TAG + " *", "", the_text)

    # one blank line to indicate a paragraph break
    the_text = re.sub("\n{3,}", "\n\n", the_text)

    # convert all [complicated math stuff] to [$something]
    the_text = re.sub(r"\[([^_@\$\'\"\[\]]*\$[^\[\]]+)\]", lambda match: rename_vars(match, the_answer_variables), the_text)

    the_text = re.sub(r"\[`(.*?)`\]", pg_math_environments, the_text, 0, re.DOTALL)

    the_text = re.sub(r">>\s*\[\s*@\s*image\((.*?)\)\s*@\]\*\s*<<", pg_image_environments, the_text, 0, re.DOTALL)
    the_text = re.sub(r"\\{\s*image\((.*?)\)\s*\\}", pg_image_environments, the_text, 0, re.DOTALL)

    the_text = re.sub(r"\\{\s*DataTable\((.*?)\);\s*\\}", pg_table_environments, the_text, 0, re.DOTALL)

    # can this happen, or is it already done by pg_math_environments ?
    the_text = re.sub(r"\[\s*(\$[a-zA-Z0-9_]+)\s*\]", r'<var name="\1" />', the_text)

#    if "_____" in the_text:
#        print "          found  ____________ ", the_text

    component.substitution_counter = 0
    the_text = re.sub(r"(\[_+\])((\{\$[a-zA-Z0-9_]*\}){0,1})", lambda match: pg_input_fields(match, the_answer_variables), the_text)

    # crude way to capture *emphasized words*.
 #   while "*" in the_text:
 #       the_text = re.sub(r"\*", "<em>", the_text, 1)
 #       the_text = re.sub(r"\*", "</em>", the_text, 1)
    the_text = re.sub(r"\*([a-zA-Z :]+)\*", r"<em>\1</em>", the_text)
    # also can have *mi/hr*
    the_text = re.sub(r"\*([a-zA-Z]+/[a-zA-Z]+)\*", r"<em>\1</em>", the_text)

    the_text = re.sub(" PERLmultiplicationPERL ", "*", the_text)

    return the_text

#------------------#

def rename_vars(txt, the_answer_variables):

    the_var = txt.group(1)
    # next line should be handled earlier?
    the_var = re.sub(" PERLmultiplicationPERL ", "*", the_var)
    the_var = the_var.strip()

    if not re.match(r"\$[a-zA-Z0-9\-]+$", the_var):
        if the_var in component.supplementary_variables:
            the_var = component.supplementary_variables[the_var]
            print "     re-used ", the_var
        else:
            new_var = component.supplementary_variable_stub + str(component.supplementary_variable_counter)
            component.supplementary_variable_counter += 1
            component.supplementary_variables[the_var] = new_var
            print "made the new var:",new_var, "=", the_var
            the_var = new_var

    return "[" + the_var + "]"

#------------------#

def extract_ans(txt):

    the_text = txt.group(1)

    this_ans, what_remains = utilities.first_bracketed_string(the_text, depth=1, lbrack="(", rbrack=")")

    this_ans = this_ans[:-1]  # take off the ) at the end
    this_ans = this_ans.strip()
    if not this_ans:
        print "no answer before", what_remains
    component.the_answers.append(this_ans)

    return what_remains

#------------------#

def pg_table_environments(txt):

    the_text = txt.group(1)
    the_text = the_text.strip()

    # here is where to process the_text and then return it inside table tags

    # as a placeholder, just return the original
    the_answer = "\{\n"
    the_answer += "DataTable("
    the_answer += the_text
    the_answer += ");\n"

    return the_answer

#-----------------#

def pg_image_environments(txt):

    the_text = txt.group(1)
    the_text = the_text.strip()

    if not the_text.startswith("insertGraph"):
        print "ERROR: malformed image markup"
        return "<figure>" + "ERROR" + the_text + "</figure>"
#    else:
#        print "processing pg_image_environments", the_text[:20]

    the_name = re.match(r"insertGraph\(([^)]+)\)", the_text).group(1).strip()
    the_width = re.search(r"width\s*=>\s*([^, ]+)(,| |\b)", the_text).group(1).strip()
    the_height = re.search(r"height\s*=>\s*([^, ]+)(,| |\b)", the_text).group(1).strip()
    the_tex_size = re.search(r"tex_size\s*=>\s*([^, ]+)(,| |\b)", the_text).group(1).strip()
    #is alt the right thing to grab for the description?
    try:
        the_alt = re.search(r'alt\s*=\s*(\"|\')([^\"\']*)\1', the_text).group(2).strip()
    except AttributeError:
        the_alt = re.search(r'alt\s*=\s*(\"|\')(.*?)\1\s*(,|$)', the_text, re.DOTALL).group(2).strip()

    the_image_short = '<image pg-name="' + the_name + '" />' + "\n"

    the_image_long = '<image pg-name="' + the_name + '" '
    the_image_long += 'width="' + the_width + '" '
    the_image_long += 'height="' + the_height + '" '
    the_image_long += 'tex_size="' + the_tex_size + '" '
    the_image_long += '>' + "\n"
    the_image_long += "<description>"
    the_alt = re.sub(r"(\$[a-zA-Z0-9_]+)", r'<var name="\1" />', the_alt)
    the_image_long += the_alt
    the_image_long += "</description>" + "\n"
    the_image_long += "</image>" + "\n"

    the_answer = "<figure>" + "\n" + the_image_long + "</figure>" + "\n"

    return the_answer
#------------------#

def pg_math_environments(txt):
    """ Convert [`*`], [``*``], [``\begin{align}*``], etc to mbx markup.

    """

    the_text = txt.group(1)
    the_text = the_text.strip()

    the_text = re.sub(r"\*", " PERLmultiplicationPERL ", the_text)

    the_text = re.sub(r"\[\s*(\$[a-zA-Z0-9_]+)\s*]", r'<var name="\1" />', the_text)

    
    if not the_text.startswith("`"):
        if "align" in the_text:
            print "What we found:", the_text[:30]
        return "<m>" + the_text + "</m>"

    # so it should start and end with `
    the_text = the_text[1:-1].strip()

    if not the_text.startswith("\\begin{aligned}"):
     #   return "<me>" + the_text + "</me>"
        return "<m>" + "\\displaystyle{" + the_text + "}</m>"
      #  return "<m>" + the_text + "</m>"

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

    # delete empty mrows  (alternative is to skip empty rows in previous loop)
    the_output = re.sub("<mrow>\s*</mrow>\s*", "", the_output)

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
 #   print "the_variable", the_variable, "and the_answer_variables", the_answer_variables
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
 #       print "found", this_variable, "in", component.defined_variables
        the_answer += 'evaluator="' + component.defined_variables[this_variable] + '" '
    the_answer += 'width="' + str(width) + '" />'

    return the_answer

########################

def pgpreprocess(text):

# fix some anomalies

    thetext = text

    for TAG in [r"\$PAR", r"\$BCENTER", r"\$ECENTER"]:
        thetext = re.sub(" *" + TAG + " *", "", thetext)

    thetext = re.sub(r"\[`\s*\\begin{aligned", r"[``\\begin{aligned", thetext)
    thetext = re.sub(r"\\end{aligned}\s*`\]", r"\\end{aligned}``]", thetext)
    
    return thetext

########################

def fix_ptx_math_punctuation(text):

# punctuation should come after the closing display math tag

    thetext = text

    thetext = re.sub(r"(\.|,)(\s*)(</me>|</men>|</mrow>\s*</md>|</mrow>\s*</mdn>)", r"\2\3\1", thetext)

# and also after the closing inline math tag
    thetext = re.sub(r"(\.|,)(\s*)(</m>)", r"\3\1", thetext)

    return thetext

