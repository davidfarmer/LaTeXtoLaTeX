
import re
import math

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

def mytransform_ldata(text):

    thetext = text.strip()

    refineddata = True

    if "Take" in thetext:
        return ""
    if "Null" in thetext:
        return ""

    thetext = re.sub(r" +", "", thetext)

    # hack becaise of different runs
    thetext = re.sub(r'"cR', '"R', thetext)
    thetext = re.sub(r'retry', '', thetext)
    thetext = re.sub(r'HRmoreB', '', thetext)
    thetext = re.sub(r'HRmore', '', thetext)
    thetext = re.sub(r'HR', '', thetext)

    if not thetext.startswith('itemtosave={"R') and not thetext.startswith('itemtosave={"ckappa'):
        print "starts with", thetext[:50]
        print "data file starts wrong, quitting"
        die()

    if thetext.startswith('itemtosave={"R0_R1_R1",'):

      thetext = re.sub(r"\\\s+", "", thetext)
      thetext = re.sub("\s", "", thetext)
      thetext = re.sub("`[0-9]+\.[0-9]+", "", thetext)

      thetext = re.sub('^itemtosave *= *{"R0_R1_R1", *', "", thetext)
      startval, thetext = utilities.first_bracketed_string(thetext)
      thetext = re.sub("^\s*,*", "", thetext)
      print thetext[:50]

      if len(startval) > 40:  # startval is actually lamset
          lamset = startval
          startval = "{999, 999}"
      else:
          lamset, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)
          print thetext[:50]

      func_eq, thetext = utilities.first_bracketed_string(thetext)
      thetext = re.sub("^\s*,*", "", thetext)
      euler_prod, thetext = utilities.first_bracketed_string(thetext)
      thetext = re.sub("^\s*,*", "", thetext)
      coefficients_set, thetext = utilities.first_bracketed_string(thetext)
      thetext = re.sub("^\s*,*", "", thetext)
      search_params, thetext = utilities.first_bracketed_string(thetext)
      thetext = re.sub("^\s*,*", "", thetext)
      eig_precision, thetext = utilities.first_bracketed_string(thetext)
      thetext = re.sub("^\s*,*", "", thetext)
      coeff_precision, thetext = utilities.first_bracketed_string(thetext)
      thetext = re.sub("^\s*,*", "", thetext)
      print "lamset", lamset, "coefficients_set", coefficients_set[:20]

      if not (eig_precision.startswith("{0.0") or eig_precision.startswith("{0``")) and "*^-" not in eig_precision:
          component.maybe_bad += 1
          print component.maybe_bad, "LOW PRECISION?", eig_precision
          component.startagain += startval
      #    return ""

      else:
          this_value = "{" + lamset + "," + coefficients_set + "," + eig_precision + "," + coeff_precision + "," + search_params + "}"

          component.foundvalues.append(this_value)

  #    if "Null" in text:
  #        print "             Null:  NEED TO TRY AGAIN AT", startval
  #        component.startagain += startval

      thetext = thetext[1:]

      if thetext:
          thetext = mytransform_ldata(thetext)

      return thetext

    else:

        thetext = re.sub(r"\\\s+", "", thetext)
        thetext = re.sub("\s", "", thetext)
        thetext = re.sub("`[0-9]+\.[0-9]+", "", thetext)
  
        if refineddata:
   #     thesortofweight = re.search(r'^itemtosave *= *{"R[0,1]_C([0-9]+)",', thetext).group(1)
          thesortofweight = re.search(r'^itemtosave *= *{"ckappa_rdelta_([0-9]+)",', thetext).group(1)
          print "found thesortofweight", thesortofweight
   #     thetext = re.sub('^itemtosave *= *{"R[0,1]_C([0-9]+)", *', "", thetext)
          thetext = re.sub('^itemtosave *= *{"R[0,1]_C([0-9]+)[^"]+", *', "", thetext)
  
          # save version
          version = re.search('^([^,]+),', thetext).group(1)
          thetext = re.sub('^([^,]+),', "", thetext)
  
          # save equationlist
          equationlist = re.search('^([^,]+),', thetext).group(1)
          thetext = re.sub('^([^,]+),', "", thetext)
  
          thedata, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)
  
          errormeasures, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)
  
          searchparameters, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)
  
          parameterchanges, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)
  
          startingvalues, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)

          this_value = "{" + thesortofweight + "," + thedata + "}"

          component.foundvalues.append(this_value)
    
          thetext = thetext[1:]

          if thetext:
              thetext = mytransform_ldata(thetext)

          return thetext

        else:

          thesortofweight = re.search(r'^itemtosave *= *{"R[0,1]_C([0-9]+)",', thetext).group(1)
          print "found thesortofweight", thesortofweight
          thetext = re.sub('^itemtosave *= *{"R[0,1]_C([0-9]+)", *', "", thetext)

  
          startval, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)
          print thetext[:50]
  
          if len(startval) > 40:  # startval is actually lamset
              lamset = startval
              startval = "{999, 999}"
          else:
              lamset, thetext = utilities.first_bracketed_string(thetext)
              thetext = re.sub("^\s*,*", "", thetext)
              print thetext[:50]
  
          lamset = re.sub(r"^{", "{" + thesortofweight + ",", lamset)
  
          func_eq, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)
          euler_prod, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)
          coefficients_set, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)
          search_params, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)
          eig_precision, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)
          coeff_precision, thetext = utilities.first_bracketed_string(thetext)
          thetext = re.sub("^\s*,*", "", thetext)
          print "lamset", lamset, "coefficients_set", coefficients_set[:20]
  
          if not (eig_precision.startswith("{0.0") or eig_precision.startswith("{0``")) and "*^-" not in eig_precision:
      #  if not eig_precision.startswith("{0.0") and "*^-" not in eig_precision:
              component.maybe_bad += 1
              print component.maybe_bad, "LOW PRECISION?", eig_precision
              component.startagain += startval
      #      return ""
  
          else:
              this_value = "{" + lamset + "," + coefficients_set + "," + eig_precision + "," + coeff_precision + "," + search_params + "}"
  
              component.foundvalues.append(this_value)
  
    #    if "Null" in text:
    #        print "             Null:  NEED TO TRY AGAIN AT", startval
    #        component.startagain += startval
  
          thetext = thetext[1:]
  
          if thetext:
              thetext = mytransform_ldata(thetext)
  
          return thetext
  
#########3


def mytransform_mbx(text):   # schmidt calc 3 temporary
#def mbx_fix(text):   # schmidt calc 3 temporary


    thetext = text

    thetext = re.sub(r"</c>([a-z])", r"</c> \1", thetext)

#    thetext = re.sub(r"\\G\b", r"\\mathcal{G}", thetext)
#    thetext = re.sub(r"\\fatr\b", r"\\R", thetext)
#    thetext = re.sub(r"\\fatz\b", r"\\Z", thetext)
#    thetext = re.sub(r"\\fatq\b", r"\\Q", thetext)
#    thetext = re.sub(r"\\fatc\b", r"\\C", thetext)
#    thetext = re.sub(r"\\fatn\b", r"\\N", thetext)

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

def mytransform_mbx_remove_linefeeds(text):

    thetext = text

#    print "should be deleting existing formatting, but check!"
# kill existing formatting.
# need to rethink this!

    thetext = re.sub("\n +", "\n", thetext)

#    thetext = fix_ptx_math_punctuation(thetext)

    #  now we make all the p tags separate
    for lip_tag in ["p", "li"]:
        component.lipcounter[lip_tag] = 0
        thetext = utilities.tag_to_numbered_tag(lip_tag, thetext)

        print "counted", component.lipcounter[lip_tag], "of", lip_tag

    for lip_tag in ["p", "li"]:
        for n in range(component.lipcounter[lip_tag]):
            thetext = re.sub(r"(<" + lip_tag + str(n) + "( |>))" +
                                 r"(.*?)" + r"(</" + lip_tag + str(n) + ">)",
                             postprocess.remove_line_feeds,
                             thetext, 1, re.DOTALL)

    # now put back the original p tags
    for lip_tag in ["p", "li"]:
        for n in range(component.lipcounter[lip_tag]):
            thetext = re.sub(r"<" + lip_tag + str(n) + "( |>)", "<" + lip_tag + r"\1", thetext)
            thetext = re.sub(r"</" + lip_tag + str(n) + ">", "</" + lip_tag + ">", thetext)

    return thetext

##################

def mytransform_mbx_linefeeds(text):

    thetext = text

#    print "should be deleting existing formatting, but check!"
# kill existing formatting.
# need to rethink this!

#    thetext = re.sub("\n +", "\n", thetext)

    thetext = fix_ptx_math_punctuation(thetext)

    #  now we make all the p tags separate
    for lip_tag in ["p", "li"]:
        component.lipcounter[lip_tag] = 0
        thetext = utilities.tag_to_numbered_tag(lip_tag, thetext)

        print "counted", component.lipcounter[lip_tag], "of", lip_tag

    for lip_tag in ["p", "li"]:
        for n in range(component.lipcounter[lip_tag]):
            thetext = postprocess.add_line_feeds(lip_tag + str(n), thetext)

    # now put back the original p tags
    for lip_tag in ["p", "li"]:
        for n in range(component.lipcounter[lip_tag]):
            thetext = re.sub(r"<" + lip_tag + str(n) + "( |>)", "<" + lip_tag + r"\1", thetext)
            thetext = re.sub(r"</" + lip_tag + str(n) + ">", "</" + lip_tag + ">", thetext)

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

        if the_text_part1.startswith("<p>") and the_text_part1.endswith("</p>"):
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

    if trimmed_text:
        print trimmed_text
    if "<var" in this_text:
        print this_text

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

    return this_text

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

def mytransform_fixptx(text):

    taglevel = {
        "chapter": 1,
        "section": 2,
        "theorem": 3,
        "statement": 4,
        "li": 8,
        "p": 8
    }

    thetext = text

    level = 0

    theanswer = ""
    sawleft = False
    inopeningtag = False
    inclosingtag = False
    thistag = ""
    activetags = []
    prevch = ""

    for ch in thetext:
      if ch == "<":
        sawleft = True
      elif ch == "/":
        sawleft = False
        if prevch == "<":
           inclosingtag = True
      elif ch == " ":
        if prevch == "<":
          sawleft = False
        elif inopeningtag:  # space before attributes
          sawleft = False
          activetags.append(thistag)
          inopeningtag = False
          thistag = ""
      elif ch == ">":  # ended an openingn or closing tag
        if prevch == "/":   # self-closing tag
          if not inopeningtag:  # then pop the tag which was already saved
            print "removing self-closing tag", activetags, "thistag", thistag, "so far",theanswer[-50:] 
            activetags.pop()
          else:
            print "tag so far", thistag, "activetags", activetags
            inopeningtag = False
          if inclosingtag:
            print theanswer[-120:]
            print "error tracking tags"
          inopeningtag = False
          thistag = ""
        elif inopeningtag:
          activetags.append(thistag)
          inopeningtag = False
          thistag = ""
        elif inclosingtag:
          inclosingtag = False
          if thistag != activetags[-1]:
            print theanswer[-120:]
            print "thistag", thistag, "activetags", activetags
            print "tag error", activetags[-1], "closed by", thistag
            if taglevel[thistag] > taglevel[activetags[-1]]:
                print "minor tag", thistag, "closed major tag", activetags[-1]
            else:
                print "minor tag", thistag, "failed to close"
            die
          else:
            activetags.pop()
            thistag = ""
        elif True:
          pass
        else:
          print theanswer[-120:]
          print "thistag", thistag, "activetags", activetags
          print "tag out of place", thistag
          die
      else:
        if sawleft:
          inopeningtag = True
          thistag = ch
        elif inopeningtag or inclosingtag:
          thistag += ch
        sawleft = False

      if thistag == "times":
        print "found times", activetags, theanswer[-120:]
      theanswer += ch
      prevch = ch

    return theanswer

#############

def mytransform_ptx(text):

    thetext = text

    thetext = re.sub(r"<li>\s*<p>\s*<em>(.*?)</em>\s*</p>",
                     r"<li><title>\1</title>", thetext)

    thetext = re.sub(r"\.</title>", "</title>", thetext)

    return thetext

# below is old and will not be reached

    # first hide comments
    thetext = re.sub(r"(\s*(<!--)(.*?)(-->))",
                     lambda match: utilities.sha1hide(match, "comment"),
                     thetext, 0, re.DOTALL)

    # hide verbatim content
    for tag in component.verbatim_tags:
        thetext = re.sub(r"(\s*(<" + tag + "(>| [^/>]*>))(.*?)(</" + tag + ">))",
                         lambda match: utilities.sha1hide(match, tag),
                         thetext, 0, re.DOTALL)

    opening_tags = re.findall(r"(<[a-z]([^<>]+[^/]|)>)", thetext)

    for tag in opening_tags:
        the_tag = tag[0]
        if "permid" not in the_tag:
            tag_name = the_tag[1:]
            if tag_name.startswith("o"): print "XXXXXXXXXXXXXXXXXXX  tag", tag
            tag_name = re.sub(" .*","",tag_name)
            tag_name = re.sub(">$","",tag_name)
            
            if tag_name not in component.generic_list:
                component.generic_list.append(tag_name)

    component.generic_list.sort()
    print component.generic_list

def mytransform_html(text):

    thetext = text

    # the white space before the end of an h5 makes a space before the "." added by CSS
#    thetext = re.sub(r"\s+</h5>", "</h5>", thetext)

  #  # this is for scraping the Stanford math dept email addresses
  #  thetext = re.sub(r'mini-row-link">(.*?)</a>.*?mailto:(.*?)"', mytransform_ht, thetext, 0, re.DOTALL)
    # and for the SJSU math dept
  #  thetext = re.sub(".*he following are a list", "", thetext, 1, re.DOTALL)
  #  thetext = re.sub("<h3>Information for</h3>.*", "", thetext, 1, re.DOTALL)
  #  print "first alt"
  #  thetext = re.sub(r'alt="([^"]+)".*?<br>([a-z\-\.]{,30}\@sjsu.edu)', mytransform_ht, thetext, 0, re.DOTALL)
  #  print "then title"
  #  thetext = re.sub(r'<a title="(.*?)" hre.*?<br>([a-z\-\.]{,30}\@\S*?)(\s|<strong)', mytransform_ht, thetext, 0, re.DOTALL)
  #  print "then strong"
  #  thetext = re.sub(r'<strong>(.*?)</strong>.*?<br>([a-z\-\.]{,30}\@\S*?)(\s|<strong)', mytransform_ht, thetext, 0, re.DOTALL)

  #  print thetext

    # UCSC math
    thetext = re.sub(r'class="p-name">([^<>]+)</span>.*?mailto:([^"]+)"', mytransform_ht, thetext, 0, re.DOTALL)

    for _ in component.people_list:
        print _

    print "found", len(component.people_list), "people"
    return thetext

###################

def mytransform_ht(txt):

    this_name = txt.group(1)
    this_email = txt.group(2)
    print "this_name", this_name
    if " " not in this_name:
        return txt.group(0)
    this_name = re.sub(" [A-Z] ", " ", this_name)

#    this_ln, this_fn = this_name.split(", ")
    this_fn, this_ln = this_name.split(" ",1)

    if this_email:
        the_ans = this_fn+";"+this_ln+";"+this_email
        component.people_list.append(the_ans)

    return ""
###################

def mytransform_svg(text):

    thetext = text

    the_output = '<?xml version="1.0" standalone="no" ?>'
    the_output += '\n'
    the_output += '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
    the_output += '\n'
    the_output += '\n'
    the_output += '<svg viewBox="0 0 1600 950" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">'
    the_output += '\n'
    the_output += '\n'

    blobparams = {
        "blobx1" : 650,
        "bloby1" : 550,
        "blobsideheight1" : "200",
        "blobsidewidth1" : "400",
        "TheTitle1a" : "Primitive degree 2",
        "TheTitle1b" : "L-functions",
        "TheTitle1A" : "Gamma_C(s + nu)",
        "TheTitle1B1" : "Gamma_C(s+1/2), chi=1, rational",
        "TheTitle1B2" : "(not used)",
        "blobbordercolor1" : "#ff8c00",
        "blobfillcolor1" : "#fff6f6",
        "blobx2" : 1315,
        "bloby2" : 1020,
        "blobsideheight2" : "80",
        "blobsidewidth2" : "300",
        "TheTitle2" : "Elliptic curves/Q",
        "blobbordercolor2" : "#00aa00",
        "blobfillcolor2" : "#f6fff6",
        "blobx3" : 45,
        "bloby3" : 950,
        "blobsideheight3" : "140",
        "blobsidewidth3" : "350",
        "TheTitle3a" : "GL(2)/Q cusp forms",
        "TheTitle3A" : "holomorphic",
        "TheTitle3B" : "k=2, chi=1, rational",
        "blobbordercolor3" : "#0000aa",
        "blobfillcolor3" : "#f6f6ff",
        "blobx4" : 1270,
        "bloby4" : 300,
        "blobsideheight4" : "140",
        "blobsidewidth4" : "350",
        "TheTitle4a" : "Compatible systems of",
        "TheTitle4b" : "odd 2-dim irred geometric",
        "TheTitle4c" : "ell-adic Galois repns",
        "TheTitle4B1" : "H-T weight [0, 1],",
	"TheTitle4B2" : "det=w, rational",
        "blobbordercolor4" : "#0000aa",
        "blobfillcolor4" : "#ccc",
        "blobx5" : 600,
        "bloby5" : 1100,
        "blobsideheight5" : "20",
        "blobsidewidth5" : "250",
        "TheTitle5" : "isogeny class 112.c",
        "blobbordercolor5" : "#f00",
        "blobfillcolor5" : "none",
        "blobx6" : 10,
        "bloby6" : 300,
        "blobsideheight6" : "200",
        "blobsidewidth6" : "400",
        "TheTitle6a" : "Cuspidal automorphic",
        "TheTitle6b" : "representation of GL(2)/Q",
        "TheTitle6A" : "pi_oo is (limit of) discrete series",
        "TheTitle6B1" : "pi_oo has weight 2,",
	"TheTitle6B2" : "chi_pi=1, rational",
 #       "blobbordercolor6" : "#ff8c00",
 #       "blobfillcolor6" : "#fff6f6",
        "inneroffset2" : "translate(23,27)",
        "inneroffset3" : "translate(47,52)",
        "innerfontsize" : "24",
        "titlex0" : "50",
        "titley0" : "-66",
        "titlex1" : "50",
        "titley1" : "-33",
        "titlex2" : "50",
        "titley2" : "0",
        "titlex3" : "45",
        "titley3" : "18",
        "titlefontsize" : "30",
        "blobcornerheight" : "40",
        "blobcornerwidth" : "40",
        "objectxoffset" : "80",
        "objectyoffset" : "85",
        "linkcolor" : "black"
    }

    for key in blobparams:
        the_key_val = blobparams[key]

        thetext = re.sub(key, str(the_key_val), thetext)

    thetext = re.sub(r"lline\((.*?),(.*?)\)",
             r'<path d="M \1 L \2" stroke="black" stroke-width="2"/>',
             thetext)

    iso_vertices = [
        {
         "title": "112.c1",
         "sha_tamagawa" : "1.4",
         "torsion" : [2],
         "degree" : 144,
         "optimal": False
        },
        {
         "title": "112.c3",
         "sha_tamagawa" : "1.4",
         "torsion" : [2],
         "degree" : 48
        },
        {
         "title": "112.c4",
         "sha_tamagawa" : "1.4",
         "torsion" : [2],
         "degree" : 16,
         "optimal": False
        },
        {
         "title": "112.c6",
         "sha_tamagawa" : "1.4",
         "torsion" : [2],
         "degree" : 24
        },
        {
         "title": "112.c2",
         "sha_tamagawa" : "1.4",
         "torsion" : [2],
         "degree" : 72
        },
        {
         "title": "112.c5",
         "sha_tamagawa" : "1.4",
         "torsion" : [2],
         "degree" : 8,
         "optimal": True
        }
    ]

    iso_vertices = [
        {
         "title": "21.a1",
         "sha_tamagawa" : "1.4",
         "torsion" : 2,
         "degree" : 4,
         "optimal": False
        },
        {
         "title": "21.a3",
         "sha_tamagawa" : "1.4",
         "torsion" : 8,
         "degree" : 2
        },
        {
         "title": "21.a2",
         "sha_tamagawa" : "1.4",
         "torsion" : 4,
         "degree" : 2,
         "optimal": False
        },
        {
         "title": "21.a5",
         "sha_tamagawa" : "1.4",
         "torsion" : 8,
         "degree" : 1,
         "optimal": True
        },
        {
         "title": "21.a4",
         "sha_tamagawa" : "1.4",
         "torsion" : 2,
         "degree" : 4
        },
        {
         "title": "21.a6",
         "sha_tamagawa" : "1.4",
         "torsion" : 4,
         "degree" : 2,
        }
    ]


    iso_graph_window = {}
    iso_graph_window["h"] = [[0,0], [1200, 950]]
    iso_graph_layout = {}
    graph_layout = "g"
    graph_layout = "h"

    iso_graph_layout["g"] = [
              [[200, 125], [800, 125], [1400, 125], [200, 625], [800, 625], [1400, 625]],
              [
              {"ends": [0,1], "label": "3"},
              {"ends": [0,3], "label": "2"},
              {"ends": [1,2], "label": "3"},
              {"ends": [1,4], "label": "2"},
              {"ends": [2,5], "label": "2"},
              {"ends": [3,4], "label": "3"},
              {"ends": [4,5], "label": "3"}
              ]
    ]
    iso_graph_layout["h"] = [
              [[200, 125], [1400, 125], [500, 475], [1100, 475], [200, 825], [1400, 825]],
       #       [[200, 125], [800, 125], [1400, 125], [200, 625], [800, 625], [1400, 625]],
              [
              {"ends": [0,2], "label": "2"},
              {"ends": [2,3], "label": "2"},
              {"ends": [3,1], "label": "2"},
              {"ends": [4,2], "label": "2"},
              {"ends": [3,5], "label": "2"}
              ]
    ]

#    iso_edges["g"] = [
#        {"ends": [0,1], "label": "3"},
#        {"ends": [0,3], "label": "2"},
#        {"ends": [1,2], "label": "3"},
#        {"ends": [1,4], "label": "2"},
#        {"ends": [2,5], "label": "2"},
#        {"ends": [3,4], "label": "3"},
#        {"ends": [4,5], "label": "3"}
#        ]
#    iso_vertices["g"] = [[200, 125], [800, 125], [1400, 125], [200, 625], [800, 625], [1400, 625]]

    siz = [[300,150], [21,15,15], [1,-1], [0.3,0.4], 5]
    scal = [1,2]
    cont = [ ["This is title", ""], "", ["ab", "bc", "cd", "de"], "not optimal" ]
    colo = ["#900", "#fff", "#6d6", "#000", "#999"]



#    thetext = re.sub("SUB_HERE",
#               utilities.business_card(c_loc, siz, scal, cont, colo),
#               thetext)

    these_cards = {}

    c_loc = iso_graph_layout[graph_layout][0]
    for j, dat in enumerate(iso_vertices):
        this_location = c_loc[j]
        this_data = [ [dat['title'], ""], "" ]
        this_data.append([str(dat["degree"]), "", dat["sha_tamagawa"], str(dat["torsion"])])
        if "optimal" in dat and dat["optimal"]:
            this_data.append("optimal")
        else:
            this_data.append("")
        these_cards[j] = utilities.business_card(this_location, siz, scal, this_data, colo)

    these_edges = {}
    iso_edges = iso_graph_layout[graph_layout][1]
    for j, edge in enumerate(iso_edges):
        start_v, end_v = edge["ends"]
        start_pt = these_cards[start_v][1]
        end_pt = these_cards[end_v][1]
        this_edge = '<path d="'
        this_edge += 'M ' + str(start_pt[0]) + ' ' + str(start_pt[1]) + ' '
        this_edge += 'L ' + str(end_pt[0]) + ' ' + str(end_pt[1]) + ' '
        this_edge += '" '

        this_edge += 'stroke="' + '#3d8' + '" '
        this_edge += 'stroke-width="' + '9' + '"'

        this_edge += '/>'

        label_offset = 30
        label_font_size = 40
        font = "font-family:verdana"
        if "label" in edge:
            this_label = str(edge["label"])
            line_mid_pt_x = (start_pt[0] + end_pt[0])/2.0
            line_mid_pt_y = (start_pt[1] + end_pt[1])/2.0
            x_offset = y_offset = 0
            if start_pt[0] == end_pt[0]:
                if math.copysign(1, end_pt[1] - start_pt[1]) > 0:
                    x_offset += label_offset
                    this_text_anchor = "start"
                else:
                    x_offset -= label_offset
                    this_text_anchor = "end"
            elif start_pt[1] == end_pt[1]:
                if math.copysign(1, end_pt[0] - start_pt[0]) > 0:
                    y_offset -= label_offset
                    this_text_anchor = "middle"
                else:
                    y_offset += label_offset + label_font_size
                    this_text_anchor = "middle"
            else:  # can make this more sophisticated and take the slope into account
                if math.copysign(1, end_pt[1] - start_pt[1]) > 0:
                    x_offset += 0.7 * label_offset
                    y_offset -= 0.7 * label_offset
                    this_text_anchor = "start"
                else:
                    x_offset -= 0.7 * label_offset
                    this_text_anchor = "end"
                if math.copysign(1, end_pt[0] - start_pt[0]) > 0:
                    y_offset -= 0.7 * label_offset
                else:
                    y_offset += 0.7 * (label_offset + label_font_size)

            this_label_text = '<text '
            this_label_text += 'x="' + str(line_mid_pt_x + x_offset) + '" '
            this_label_text += 'y="' + str(line_mid_pt_y + y_offset) + '" '
            this_label_text += 'text-anchor="' + this_text_anchor + '" '
            this_label_text += 'fill="' + '#d0d' + '" '
            this_label_text += 'style="' + font + ';font-size:' + str(label_font_size) + '" '
            this_label_text += '>'
            this_label_text += this_label
            this_label_text += '</text>'
        else:
            this_label_text = ''

        print "this_edge", this_edge
        these_edges[j] = this_edge
        these_edges[j] += this_label_text

    the_output += '<svg viewBox="'
    the_window = iso_graph_window[graph_layout]
    the_output += the_window[0][0] + ' ' + the_window[0][0] + ' ' + the_window[0][0] + ' ' + the_window[0][0]

    the_output += '0 0 1600 950" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">'
    the_output += '\n'
    the_output += '\n'
    for j in these_edges:
    #    the_output += utilities.business_card(this_location, siz, scal, this_data, colo)
        print "j",j,"these_edges[j]", these_edges[j]
        the_output += these_edges[j]

    for j in these_cards:
    #    the_output += utilities.business_card(this_location, siz, scal, this_data, colo)
        print "j",j,"these_cards[j]", these_cards[j][0]
        the_output += these_cards[j][0]

    the_output += '\n'
    the_output += '</svg>'
    the_output += '\n'

    return the_output

###################

def mytransform_txt(text):

    thetext = text

    workshop_range = [55, 61, 96, 93, 94, 95, 64, 73, 82, 90, 91, 87, 89, 88, 98, 99,
100, 101, 102, 103, 106, 107, 108, 109, 110, 111, 112, 113, 114,
115, 116, 117, 118, 119, 120, 121, 122, 123, 130, 131, 134, 136,
142, 141, 143, 144, 147, 148, 150, 151, 152, 153, 154, 155, 156,
157, 158, 159, 160, 161, 162, 174, 178, 182, 183, 184, 212, 185,
186, 187, 188, 189, 190, 191, 192, 200, 202, 201, 203, 204, 205,
206, 207, 208, 221, 218, 219, 222, 223, 229, 230, 231, 232, 233,
234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 305, 246,
247, 248, 249, 250, 251, 265, 266, 267, 277, 275, 278, 279, 280,
281, 302, 303, 304, 245, 306, 307, 308, 309, 310, 311, 312, 313,
314, 315, 316, 317, 318, 319, 320, 326, 332, 343, 344, 353, 354,
355, 356, 357, 358, 359, 360, 361, 362, 363, 380, 391, 392, 393,
394, 398, 399, 400, 401, 402, 403, 405, 406, 407, 408, 409, 410,
411, 412, 413, 431, 439, 449, 476, 477, 478, 479, 480, 481, 482,
483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 497, 520,
554, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567,
568, 569, 570, 571, 572, 573, 574, 575, 578, 579, 588, 635, 636,
637, 638, 639, 640, 641, 642, 643, 644]

    workshop_range += [j for j in range(500,999)]

    totalpapers = 0
    the_answer = ""

    papers_per_workshop = {}
    authors_per_workshop = {}

    thetext = re.sub("\nVolume.*", "", thetext)
    thetext = re.sub("\n{3,}", "\n\n", thetext)

    lines = thetext.split("\n\n")
    print len(lines), "lines"
#    print "part of thetext", thetext[:1000]
    for line in lines:
        totalpapers += 1
        if "(Workshop " not in line and "(workshop " not in line:
            continue
        this_paper = line.split("\n")

        try:
            this_workshop = re.search("orkshop\s+([0-9]+)", this_paper[4]).group(1)
        except:
            this_workshop = 999

        if int(this_workshop) not in workshop_range:
            print "Workshop not in range", this_workshop
            continue
        these_authors = this_paper[3]
        these_authors = re.sub(",* and ", ", ", these_authors)
        these_authors = re.sub("[^a-zA-Z, .\-]", "", these_authors)
        author_list = these_authors.split(", ")
        
        if this_workshop in papers_per_workshop:
        #    papers_per_workshop[this_workshop].append(author_list)
            authors_per_workshop[this_workshop] += author_list
            papers_per_workshop[this_workshop] += 1
        else:
            authors_per_workshop[this_workshop] = author_list
            papers_per_workshop[this_workshop] = 1


    all_papers = 0
    all_authors = 0
    print "totalpapers", totalpapers
    found_workshops = papers_per_workshop.keys()
    found_workshops.sort()
    for w in found_workshops:
        all_papers += papers_per_workshop[w]
        all_authors += len(authors_per_workshop[w])
        print w, len(set(authors_per_workshop[w])), "from total", len(authors_per_workshop[w]), "on", papers_per_workshop[w], "papers"
        print authors_per_workshop[w]
        print "possible workshops", len(workshop_range)
        print "actual workshops", len(found_workshops)
        print ""

    print "all_papers", all_papers, "all_authors", all_authors
    return the_answer

###################


def mytransform_html_matrix(text):
#
#  a relevant line in the hat map looks like
# <rect x="257385" y="710.0" width="5"  height="18.0" fill="rgb(0,98,221)" stroke-width="2.0" stroke="none" class="who51102821 "><title>tBU 17:57 51102821</title></rect>
#
# The x-coordinate is in absolute minutes multiplied by 5.
# The y-coordinate is relative position in the viewed item, offset by -10
#    and multiplied by 30.
# The digits after "who" is the id of the person
#
# Other relevant lines include
# <text class="chapteritem" x="251910" y="1145.0" fill="rgb(20,20,20)" text-anchor="middle" ><a href="http://books.aimath.org/fcla/section-LDS.html?#wYd">ssec-Linearly D..Spans</a></text>
# which indicates an item was viewed.
# We will count "chapteritem" to know how many lines are in the map.
# The line
# <g id="level3" transform="translate(-251820 150)" >
# tells you the x-coordinate offset.

    thetext = text

    this_person = component.person_id
    this_person_identifier = "who" + this_person

    num_columns = 24*60   # one day of data, one column per minute

    num_rows = thetext.count("chapteritem")
    print "we have", num_rows, "rows"
    print "and", num_columns, "columns"
    x_offset = int(re.search("translate\(-([0-9]+) ", thetext).group(1))/5

    the_matrix = [[0 for x in range(num_columns)] for y in range(num_rows)]

    lines = thetext.split("\n")

    for line in lines:
        if line.startswith("<rect "):
            if this_person_identifier in line:
                x_coord = re.search(' x="([^"]+)"', line).group(1)
                x_coord_index = int(x_coord)/5 - x_offset
                y_coord = re.search(' y="([^"]+)"', line).group(1)
                y_coord_index = (int(float(y_coord)) + 10)/30
  #              print "x_coord_index, y_coord_index", x_coord_index, y_coord_index
                the_matrix[y_coord_index][x_coord_index] = 1

    return the_matrix

###################

def mytransform_html_ptx(text):

    thetext = text

    if "<p>" in thetext and "</p>" not in thetext:  # p tags not properly closed
        pass  # this needs to be implemented

    thetext = re.sub('<span style="color:[^"]+">([^<]+)</span>',
                     r"<alert>\1</alert>", thetext, 0, re.DOTALL)
    thetext = re.sub('&quot;([^<]+)&quot;',
                     r"<q>\1</q>", thetext, 0, re.DOTALL)
    thetext = re.sub("&nbsp;", "<nbsp/>", thetext)
    thetext = re.sub("&hellip;", "<ellipsis/>", thetext)
    thetext = re.sub("&ldquo;", "<lq/>", thetext)
    thetext = re.sub("&rdquo;", "<rq/>", thetext)
    thetext = re.sub("&radic;", "<m>\sqrt{}</m>", thetext)
    thetext = re.sub("&#39;", "'", thetext)
    thetext = re.sub("&#123;", "<lbrace/>", thetext)
    thetext = re.sub("&#125;", "<rbrace/>", thetext)
    thetext = re.sub("&lt;", "<less/>", thetext)
    thetext = re.sub("&gt;", "<greater/>", thetext)
    thetext = re.sub("<br(|/)>", "</p>\n<p>", thetext)
    thetext = re.sub("<br(| )(|/)>", "\n", thetext)
    thetext = re.sub("<span .*?>","", thetext, re.DOTALL)
    thetext = re.sub("</span>","", thetext)
    thetext = re.sub("<strong>", "<alert>", thetext)
    thetext = re.sub("</strong>", "</alert>", thetext)
    thetext = re.sub("<(|/)h[1-4]>", "", thetext)

    # delete empty paragraphs
    thetext = re.sub("<p>\s*</p>", "", thetext)

    return thetext

###################

def mytransform_to_semantic(text):

    thetext = text

    if "\\(" in thetext or "\\[" in thetext:
        thetext = re.sub(r"(\\\(\s*)(.*?)(\s*\\\))",
            utilities.to_semantic_math, thetext, 0, re.DOTALL)
        thetext = re.sub(r"(\\\[\s*)(.*?)(\s*\\\])",
            utilities.to_semantic_math, thetext, 0, re.DOTALL)
        thetext = re.sub(r"(\\begin{equation\**})(.*?)(\s*\\end{equation\**})",
            utilities.to_semantic_math, thetext, 0, re.DOTALL)
        return thetext

    thetext = re.sub(r"(<m>\s*)(.*?)(\s*</m>)",
            utilities.to_semantic_math, thetext, 0, re.DOTALL)
    thetext = re.sub(r"(<mrow>\s*)(.*?)(\s*</mrow>)",
            utilities.to_semantic_math, thetext, 0, re.DOTALL)
    thetext = re.sub(r"(<me>\s*)(.*?)(\s*</me>)",   # if no permid
            utilities.to_semantic_math, thetext, 0, re.DOTALL)
    thetext = re.sub(r"(<me [^<>]+>\s*)(.*?)(\s*</me>)",
            utilities.to_semantic_math, thetext, 0, re.DOTALL)
    thetext = re.sub(r"(<men>\s*)(.*?)(\s*</men>)",   # if no permid
            utilities.to_semantic_math, thetext, 0, re.DOTALL)
    thetext = re.sub(r"(<men [^<>]+>\s*)(.*?)(\s*</men>)",
            utilities.to_semantic_math, thetext, 0, re.DOTALL)

    return thetext

###################

def mytransform_tex_ptx(text):

    thetext = text

    thetext = re.sub(r"\\noindent *", "", thetext, 0, re.DOTALL)
    thetext = re.sub(r"\~*\\\\\[[^\[\]]+\] *", "", thetext, 0, re.DOTALL)

    thetext = re.sub(r".*\{(Reading Questions|Questions)\}\s*(.*?)\\begin\{(enumerate|itemize)\}",
                     "\n<reading-questions>\n<introduction>\n<p>\n" +
                    r"\2" +
                     "</p>\n</introduction>\n",
                      thetext, 1, re.DOTALL)

    thetext = re.sub(r"\\item", "</p></exercise>\n<exercise><p>", thetext)
    thetext = re.sub("</p></exercise>\n", "", thetext, 1)

    thetext = re.sub(r"\\end{(enumerate|itemize)}(.*)", "\n</p></exercise>\n" + r"XXXX\2YYYY", thetext, 1, re.DOTALL)

    the_end = re.sub(".*XXXX", "", thetext, 1, re.DOTALL)
    if "enumerate" in the_end or "itemize" in the_end:
        print "the_end", the_end
    else:
        thetext = re.sub("XXXX.*", "", thetext, 1, re.DOTALL)

    thetext = thetext + "\n" + "</reading-questions>" + "\n"

    thetext = "\n" + re.sub(".*/", "", component.inputfilename) + "\n\n" + thetext

    thetext = re.sub(r"\\par", "</p>\n<p>", thetext, 1)
    
    while "$" in thetext:
        thetext = re.sub("\$", "<m>", thetext, 1)
        thetext = re.sub("\$", "</m>", thetext, 1)

    thetext = re.sub(r"\\\[", "<me>", thetext)
    thetext = re.sub(r"\\\]", "</me>", thetext)

    thetext = re.sub(r"``(.*?)''", r"<q>\1</q>", thetext)
    thetext = re.sub(r"\\verb\|(.*?)\|", r"<c>\1</c>", thetext)
    thetext = re.sub(r"\\#", r"#", thetext)

    thetext = re.sub("\%.*", "", thetext)

    thetext = utilities.replacemacro(thetext,"emph",1,"<emph>#1</emph>")
    thetext = utilities.replacemacro(thetext,"textbf",1,"<emph>#1</emph>")
    thetext = utilities.replacemacro(thetext,"url",1,'<url href="#1"/>')

    return thetext + "\n\n<!--  - - - - - - - - - - - - - - - - - -->"

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

########################

def fix_ptx_math_punctuation(text):

# punctuation should come after the closing display math tag

    thetext = text

    # a spacing command at the end of math makes no sense, so delete it
    thetext = re.sub(r"\\,\s*</m>", "</m>", thetext)

    # hide \right.
    thetext = re.sub(r"\\right\.", "xxRIGHTDOTxx", thetext)

    thetext = re.sub(r"(\.|,)(\s*)(</me>|</men>|</mrow>\s*</md>|</mrow>\s*</mdn>)", r"\2\3\1", thetext)

# and also after the closing inline math tag
    thetext = re.sub(r"(\.|,)(\s*)(</m>)", r"\3\1", thetext)

    # unhide \right.
    thetext = re.sub("xxRIGHTDOTxx", r"\\right.", thetext)

    return thetext

########################

def add_permid_within_sections(text):

    thetext = text

    # first hide comments
    thetext = re.sub(r"(\s*(<!--)(.*?)(-->))",
                     lambda match: utilities.sha1hide(match, "comment"),
                     thetext, 0, re.DOTALL)

    # then hide verbatim content
    for tag in component.verbatim_tags:
        thetext = re.sub(r"(\s*(<" + tag + "(>| [^/>]*>))(.*?)(</" + tag + ">))",
                         lambda match: utilities.sha1hide(match, tag),
                         thetext, 0, re.DOTALL)

    for tag in component.tags_by_level[0]:

        if '<' + tag + ' ' not in thetext and '<' + tag + '>' not in thetext:  
                 # space, because xml:id is required, but may be missing
            continue

        component.local_counter[tag] = 0

        thetext = re.sub(r"<" + tag + r"( [^>]*|)>(.*?</" + tag + ">)",
            lambda match: add_permid_on(match, tag), thetext, 0, re.DOTALL)

        thetext = re.sub(r"(<" + tag + r"( [^>]*|)>)(.*?)(</" + tag + ">)",
            lambda match: add_permid_within(match, tag, 1), thetext, 0, re.DOTALL)

    for tag in component.tags_by_level[1] + component.tags_by_level[0]:
        thetext = re.sub(r"(<" + tag + r"( [^>]*|)>)(.*?)(</" + tag + ">)",
            lambda match: add_permid_within(match, tag, 2), thetext, 0, re.DOTALL)

    for tag in component.tags_by_level[2] + component.tags_by_level[1] + component.tags_by_level[0]:
        thetext = re.sub(r"(<" + tag + r"( [^>]*|)>)(.*?)(</" + tag + ">)",
            lambda match: add_permid_within(match, tag, 3), thetext, 0, re.DOTALL)

    for lev in range(3, -1, -1):
      for tag in component.tags_by_level[lev]:
        thetext = re.sub(r"(<" + tag + r"( [^>]*|)>)(.*?)(</" + tag + ">)",
            lambda match: add_permid_within(match, tag, 4), thetext, 0, re.DOTALL)

    for lev in range(4, -1, -1):
      for tag in component.tags_by_level[lev]:
        thetext = re.sub(r"(<" + tag + r"( [^>]*|)>)(.*?)(</" + tag + ">)",
            lambda match: add_permid_within(match, tag, 5), thetext, 0, re.DOTALL)

    for lev in range(5, -1, -1):
      for tag in component.tags_by_level[lev]:
        thetext = re.sub(r"(<" + tag + r"( [^>]*|)>)(.*?)(</" + tag + ">)",
            lambda match: add_permid_within(match, tag, 6), thetext, 0, re.DOTALL)

    for lev in range(6, -1, -1):
      for tag in component.tags_by_level[lev]:
        thetext = re.sub(r"(<" + tag + r"( [^>]*|)>)(.*?)(</" + tag + ">)",
            lambda match: add_permid_within(match, tag, 7), thetext, 0, re.DOTALL)

    for lev in range(7, -1, -1):
      for tag in component.tags_by_level[lev]:
        thetext = re.sub(r"(<" + tag + r"( [^>]*|)>)(.*?)(</" + tag + ">)",
            lambda match: add_permid_within(match, tag, 7), thetext, 0, re.DOTALL)

    # now we put permid "on" everything.  If there already is a permid,
    # then it should not change.  But if we missed somethign, now we catch it.
    print "looking for missing permid",len(component.all_permid)
    for lev in range(8, -1, -1):
      for tag in component.tags_by_level[lev]:
        component.local_counter[tag] = 0
   #     print "BBB",lev,tag
        thetext = re.sub(r"<" + tag + r"( [^>]*|)>(.*?</" + tag + ">)",
            lambda match: add_permid_on(match, tag), thetext, 0, re.DOTALL)
    print "done looking for missing permid",len(component.all_permid)

    print "again looking for missing permid",len(component.all_permid)
    for lev in range(8, -1, -1):
      for tag in component.tags_by_level[lev]:
        component.local_counter[tag] = 0
   #     print "BBB",lev,tag
        thetext = re.sub(r"<(" + tag + ")>",
            naive_add_permid_on, thetext, 0, re.DOTALL)
        thetext = re.sub(r"<(" + tag + " [^<>/]+)>",
            naive_add_permid_on, thetext, 0, re.DOTALL)
    print "done looking for missing permid",len(component.all_permid)


        # put back verbatim environments
#    print "put back verbatim environments"
    for tag in component.verbatim_tags:
         thetext = re.sub(r"A(" + tag + ")B(.{40})ENDZ *",
                                    utilities.sha1undigest,thetext)
    thetext = re.sub(r" *ACOMMB(.{40})ENDZ *", utilities.sha1undigest,thetext)

    # sage is verbatim, but it also needs a permid
    for tag in ['sage']:
        component.local_counter[tag] = 0
        thetext = re.sub(r"<(" + tag + " [^<>/]+)>",
            naive_add_permid_on, thetext, 0, re.DOTALL)
        thetext = re.sub(r"<(" + tag + ")>",
            naive_add_permid_on, thetext, 0, re.DOTALL)

    # put permid as the last attribute
    thetext = re.sub(r'( permid="[^\"]+")([^>]*[^/])>', r"\2\1>", thetext)

    return thetext

#-------------#

def add_permid_within(txt, parent_tag, level):

    the_opening_tag = txt.group(1)   
    the_attributes = txt.group(2)
    the_text = txt.group(3)
    the_closing_tag = txt.group(4)

    try:
        parent_permid = re.search(' permid="([^"]+)"', the_attributes).group(1)
    except AttributeError:
        print "ERROR: parent with no permid:", the_opening_tag, "aaa", the_text[:30]
        parent_permid = "ERROR"
#        try:
#            parent_id = re.search('xml:id="([^"]+)"', the_attributes).group(1)
#    #        parent_id = re.sub("-[0-9]", "", parent_id)
#        except AttributeError:
#            print "the_attributes", the_attributes
#            print "Error, no xml:id on",parent_tag,"of",the_text[:40]
#            the_title = re.search("<title>\s*(.*?)\s*</title>", the_text, re.DOTALL).group(1)
#            print "found the title", the_title, "pppp"
#            parent_id = the_title.lower()
#
#        parent_permid = shorten(parent_id)

    for tag in component.tags_by_level[level]:
        component.local_counter[tag] = 0
        the_text = re.sub(r"<" + tag + r"( [^>]*|)>(.*?</" + tag + ">)",
            lambda match: add_permid_on(match, tag, parent_permid), the_text, 0, re.DOTALL)

    return the_opening_tag + the_text + the_closing_tag

#-------------#

def shorten(permid):

    the_permid = permid

    the_permid = re.sub(r"[\'\",\.\(\)]", "", the_permid)
    the_permid = re.sub(r"\W", "-", the_permid).lower()

    for tag in component.abbreviation_of_tag:
        the_permid = re.sub(r"(^|[_\- \"\'])" + tag + r"($|[_\- \"\'])",
                               r"\1" + component.abbreviation_of_tag[tag] + r"\2",
                               the_permid)
    for tag in ['and', 'of', 'the', "m"]:
        the_permid = re.sub("-" + tag + "-", "-", the_permid)

    the_permid = re.sub("-{2,}", "-", the_permid)
    the_permid = re.sub("^-+", "", the_permid)
    the_permid = re.sub("-+$", "", the_permid)
    the_permid = re.sub("_-", "_", the_permid)

    return the_permid

#-------------#

def naive_add_permid_on(txt):

    tag = txt.group(1)

    if " permid" in tag:
        return "<" + tag + ">"

    the_permid = utilities.next_permid_encoded()

    permid_attribute = 'permid="'
    permid_attribute += the_permid
    permid_attribute += '"'

    component.all_permid.append("+" + the_permid)

    return "<" + tag + " " + permid_attribute + ">"

def add_permid_on(txt, tag, parent_permid=""):

    the_attribute = txt.group(1)
    everything_else = txt.group(2)

#    if tag == "activity":
#        print "ACTIVITY", the_attribute, everything_else[:30]
    if 'permid="' in the_attribute:  # don;t change an existing permid
        return "<" + tag + the_attribute + ">" + everything_else

#    if 'xml:id="' in the_attribute:  #use the xml:id if it exists
#        this_id = re.search('xml:id="([^"]+)"', the_attribute).group(1)
#  #      this_id = re.sub("-[0-9]", "", this_id)
#        this_permid = shorten(this_id)
#        permid_attribute = 'permid="' + this_permid + '"'
#        return "<" + tag + " " + permid_attribute + the_attribute + ">" + everything_else

# the next several lines are irrelevant
    component.local_counter[tag] += 1

    tag_counter = str(component.local_counter[tag])
    if tag == "exercise":
        tag_counter = utilities.two_letter_number(50+component.local_counter[tag])
    elif tag == "li":
        tag_counter = utilities.two_letter_number(component.local_counter[tag])

    needs_number = True

    try:
        this_id = re.search('xml:id="([^"]+)"', the_attribute).group(1)
  #      this_id = re.sub("-[0-9]", "", this_id)
        this_permid = this_id.lower()
        needs_number = False
    except AttributeError:
#        try:
#            the_title = re.search('^\s*<title>\s*(.*?)\s*</title>', everything_else, re.DOTALL).group(1)
#            this_permid = tag + "-" + the_title
#            needs_number = False
#        except AttributeError:
            this_permid = tag

    this_permid = shorten(this_permid)

    full_permid = this_permid
    if parent_permid:
        full_permid = parent_permid + "-" + this_permid

    if needs_number:
        full_permid += tag_counter

# above several lines are irrelevant

    the_permid = utilities.next_permid_encoded()

    permid_attribute = 'permid="'
    permid_attribute += the_permid
    permid_attribute += '"'

    component.all_permid.append(parent_permid + "-" + the_permid)

    return "<" + tag + " " + permid_attribute + the_attribute + ">" + everything_else

    
