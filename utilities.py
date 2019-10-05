
import logging
import hashlib
import re
import math
import codecs

import component

#################

def sha1hexdigest(text):
    """Return the sha1 hash of text, in hexadecimal."""

    the_text = text
    sha1 = hashlib.sha1()

    try:
        sha1.update(the_text.encode('utf-8', errors="ignore"))
    except UnicodeDecodeError:
        sha1.update(the_text)

    this_sha1 = sha1.hexdigest()

    component.sha1of[this_sha1] = {'original_text' : the_text}

    return(this_sha1)

#################

def sha1hide(txt, tag, keeptags=False):

    thetext = txt.group(1)
    the_hash = sha1hexdigest(thetext)

    if keeptags:
        theopeningtag = txt.group(1)
        theinnertext = txt.group(4)
        theclosingtag = txt.group(5)

        the_hash = sha1hexdigest(theinnertext)

        return theopeningtag + "A" + tag + "B" + the_hash + "ENDZ" + theclosingtag

    if tag == "comment":
        return "ACOMMB" + the_hash + "ENDZ"
    else:
        return "A" + tag + "B" + the_hash + "ENDZ"
        
#################

def sha1undigest(txt):

    try:
        the_tag = txt.group(1)
        the_sha1key = txt.group(2)
    #    return "<" + the_tag + component.sha1of[the_sha1key]['original_text'] + "</" + the_tag + ">"
   #     return component.sha1of[the_sha1key]['original_text']

    except (AttributeError, IndexError) as e:
        the_sha1key = txt.group(1)
#    print "unsha1 of", the_sha1key
    #    return component.sha1of[the_sha1key]['original_text']

    orig_text = component.sha1of[the_sha1key]['original_text']
    orig_text_trimmed = delete_leading_block(orig_text)

    return orig_text_trimmed

#################

def strip_brackets(text,lbrack="{",rbrack="}",depth=0):
    """Convert {{text}}} to text}.

    """

    thetext = text
    current_depth = 0

    if not thetext:
        return ""

    while thetext and thetext[0] == lbrack and thetext[-1] == rbrack:
        current_depth += 1
        firstpart,secondpart = first_bracketed_string(thetext,0,lbrack,rbrack)
        firstpart = firstpart[1:-1]
        if not firstpart:
            return secondpart
        elif depth and current_depth >= depth:
            return firstpart
        thetext = firstpart + secondpart

    return thetext

###################

def first_bracketed_string(text, depth=0, lbrack="{", rbrack="}"):
    """If text is of the form {A}B, return {A},B.

    Otherwise, return "",text.

    """

    thetext = text.lstrip()

    if not thetext:
        print "Error: no text"
        component.error_messages.append("empty string sent to first_bracketed_string()")
        return ""

    previouschar = ""
       # we need to keep track of the previous character becaause \{ does not
       # count as a bracket

    if depth == 0 and thetext[0] != lbrack:
        return "",thetext

    elif depth == 0:
        firstpart = lbrack
        depth = 1
        thetext = thetext[1:]
    else:
        firstpart = ""   # should be some number of brackets?

    while depth > 0 and thetext:
        currentchar = thetext[0]
        if currentchar == lbrack and previouschar != "\\":
            depth += 1
        elif currentchar == rbrack and previouschar != "\\":
            depth -= 1
        firstpart += currentchar
        if previouschar == "\\" and currentchar == "\\":
            previouschar = "\n"
        else:
            previouschar = currentchar

        thetext = thetext[1:]

    if depth == 0:
        return firstpart, thetext
    else:
        print "Error: no matching bracket",lbrack,"in",thetext,"XX"
  #      return "",thetext
        print "returning",firstpart[1:100], "\nPLUS MORE\n"
        return "",firstpart[1:]   # firstpart should be everything
                                  # but take away the bracket that doesn't match


#################

def replacemacro(text,macroname,numargs,replacementtext):
    """Expand a LaTeX macro in text.

    """

    if text == "":
        logging.debug("replacing macro %s in an empty string", macroname)
        return ""

    if "\\"+macroname not in text:
        return text

    # there is a tricky situation when a macro is being replaced by nothing.  if it is
    # alone on a line, then you just introduced a paragraph break.  it seems we must
    # treat that as a special case


    thetext = text
    global a_macro_changed

    a_macro_changed = 1

    while a_macro_changed:   # maybe change to:  while "\\"+macroname in text:

        # first, the special case described above, which we are not really handling right
        if not replacementtext:
            while a_macro_changed:
                logging.debug("replacing macro %s by nothing in: %s", macroname, re.sub("\s{2,}","\n",thetext.strip())[:30])
                a_macro_changed = 0
                thetext = re.sub(r"\n\\("+macroname+r")\s*({[^{}]*})\s",
                                 lambda match: replacemac(match,numargs,"\n"),thetext,1,re.DOTALL)
        a_macro_changed = 0

        thetext = re.sub(r"\\("+macroname+r")\**(([0-9]|\b)+.*)",lambda match: replacemac(match,numargs,replacementtext),thetext,1,re.DOTALL)

    return thetext

##############

def replacemac(txt,numargs,replacementtext):

    this_macro = txt.group(1)
    text_after = txt.group(2)

    if numargs:
        text_after = text_after.lstrip()

    if text_after.startswith("["):
        logging.debug("found square group")
        squaregroup, text_after = first_bracketed_string(text_after,0,"[","]")
        text_after = text_after.lstrip()
        # Currently we ignore the squaregroup.  What should we do with it?

     # first a hack to handle some oddly formed macro calls
    try:
        first_character = text_after[0]
    except IndexError:
        first_character = ""

    if numargs and first_character  not in ["{","\\"] and first_character not in r"0123456789":
        logging.debug("found %s but it has no argument %s", this_macro, text_after[:50])
        return text_after

    if first_character in "0123456789":   # wrap it in {} and proceed normally
        logging.debug("found that the argument is a number")
        text_after = re.sub("^([0-9])",r"{\1}",text_after,1)
        logging.debug("now the text after starts: %s", text_after[:20])

    if first_character == r"\\":   # wrap the argument in {} and proceed normally
        logging.debug("found that the argument is another macro")
        text_after = re.sub(r"^\\([a-zA-Z]+)",r"{\\\1}",text_after,1)

    global a_macro_changed
    a_macro_changed += 1

    arglis=[""]      # put a throw-away element 0 so that it is less confusing
                     # when we assign to the LaTeX "#N" argmuments

    for ar in range(numargs):
            try:
                theitem, text_after = first_bracketed_string(text_after)
            except ValueError:
                logging.error("no text_after in replacemac for argument %s of %s", ar, this_macro)
                logging.error("text_after begins %s", text_after[:40])
                if ar:
                    logging.error("arglis so far is %s", arglis)
                theitem = ""
                # below is to fail gracefully when there is an error.
                # need to come up with a better way
            if not theitem:  # probably missing close bracket
                logging.error("was scanning argument %s of %s before text_after %s", ar, this_macro, text_after[:20])
                logging.error("missing brace?  guess to stop at end of line")
                if "\n" in text_after:
                    theitem, text_after = text_after.split("\n",1)
                else:
                    theitem = ""
            theitem = strip_brackets(theitem)
            theitem = re.sub(r"\\",r"\\\\",theitem)  # This is tricky.  We are using the extracted LaTeX
                                                   # in a substitution, so we should think of it as code.
                                                   # Therefore we need to excape the backslashes.
            arglis.append(theitem)

# confused about which of the next two lines is correct
    macroexpanded = replacementtext
#    macroexpanded = re.sub(r"\\",r"\\\\",replacementtext)

    for arg in range(1,numargs+1):
        mysubstitution = "#"+str(arg)
        macroexpanded = re.sub(mysubstitution,arglis[arg],macroexpanded)

    return macroexpanded + text_after


#################

def text_before(text, target):
    """If text is of the form *target*, return (*,target*).
    Otherwise, return ("",text)
    Note that target can be a tuple.
    """

    thetext = text
    thetarget = target

    if isinstance(thetarget, str):
        thetarget = [thetarget]
    thetarget = tuple(thetarget)

    firstpart = ""

    while thetext and not thetext.startswith(thetarget):
        firstpart += thetext[0]
        thetext = thetext[1:]

    if thetext:
        return (firstpart,thetext)
    else:
        return("",text)

#################

def argument_of_macro(text,mac,argnum=1):
    """Return the argument (without brackets) of the argnum
       argument of the first appearance of the macro \mac
       in text.

    """

    searchstring = r".*?" + r"\\" + mac + r"\b" + r"(.*)"
    # the ? means non-greedy, so it matches the first appearance of \\mac\b

    try:
        text_after = re.match(searchstring,text,re.DOTALL).group(1)
    except AttributeError:
        print "Error: macro " + mac + " not in text"
        return ""

    for _ in range(argnum):
        the_argument, text_after = first_bracketed_string(text_after)

    the_argument = strip_brackets(the_argument)

    return the_argument

#################

def magic_character_convert(text, mode):
    """ replace & and < by 
        &amp; or \amp or <ampersand /> or TMPAMPAMP 
            and 
        &lt; or \lt or <less /> or TMPLESSLESS
            depending on whether mode is
        code or math or text or hide

    """

 ### need "hide" as a 3rd parameter, so we can get TMPmathAMPAMP for example
 ### that way we can hide math first, and then do text that includes math

    the_text = text

    the_text = re.sub(r"&", "TMPhideAMPAMP", the_text)
    the_text = re.sub(r"<", "TMPhideLESSLESS", the_text)

    if mode == "code":
        the_text = re.sub("TMPhideAMPAMP", r"<ampersand />", the_text)
        the_text = re.sub("TMPhideLESSLESS", r"<less />", the_text)
    elif mode == "math":
        the_text = re.sub("TMPhideAMPAMP", r"\\amp", the_text)
        the_text = re.sub("TMPhideLESSLESSvar", r"<var", the_text)
        the_text = re.sub("TMPhideLESSLESS", r"\\le", the_text)
    elif mode == "text":
        the_text = re.sub("TMPhideAMPAMP", r"&amp;", the_text)
        the_text = re.sub("TMPhideLESSLESS", r"&lt;", the_text)
        
# also need an "unhide" mode

    return the_text

###############

def tag_to_numbered_tag(tag, text):

    # turn each instance of <tag>...</tag> into <tagN>...</tagN> where N
    # increments from 1 to the number of times that tag appears
    # tags are counted by component.lipcounter

    # be careful of tags that can also be self-closing

    the_text = text

    find_start_tag = r"(<" + tag + ")"
    find_start_tag += "(>| [^/>]*>)"
    find_end_tag = r"(</" + tag + ")>"

    component.something_changed = True
    while component.something_changed:
        component.something_changed = False
        the_text = re.sub(find_start_tag + "(.*?)" + find_end_tag,
                          lambda match: tag_to_numbered_t(tag, match),
                          the_text, 0, re.DOTALL)

    return the_text

#-------------#

def tag_to_numbered_t(tag, txt):

    the_tag = tag
    the_start1 = txt.group(1)
    the_start2 = txt.group(2)
    the_text = txt.group(3)
    the_end = txt.group(4)

    component.something_changed = True

    if "<" + the_tag + " " in the_text or "<" + the_tag + ">" in the_text:
        the_text = tag_to_numbered_tag(the_tag, the_text + the_end + ">")

        # this is necessary, but not obviously so
        component.something_changed = True

        return the_start1 + the_start2 + the_text  #+ the_end + ">"

    else:
        this_N = component.lipcounter[the_tag]
        component.lipcounter[the_tag] += 1
        
        return the_start1 + str(this_N) + the_start2  + the_text + the_end + str(this_N) + ">"

#############

def delete_leading_block(text):

    """If a block of text has white space at the beginning
       of every line, delete the common white space."""

    the_text = text

    # do we need to ensure there are at least 2 lines?
    the_text_plus = the_text + "\n"
    the_lines_plus = the_text_plus.split("\n")

    min_leading_space = 9999999
    for line in the_lines_plus:
        if line:  # there might be empty lines, such as at the end
            leading_space = re.match("( *)", line).group(1)
            num_leading_space = len(leading_space)
            min_leading_space = min(min_leading_space, num_leading_space)

    if min_leading_space > 10:
        the_answer = re.sub("\n {" + str(min_leading_space) + "}", "\n" + " "*12, the_text)
    else:
        the_answer = the_text
    
    return the_answer

#############

def two_letter_number(num):

    if num < 26:
 #       print "nun", num, "eee"
        num_mod = 35*num % 26
        ans = chr(ord('a') + num_mod)

    else:
 #       print "bignum", num, "www"
        num_mod = 35*num % (26*26)
 #       print "num_mod", num_mod, "www", num_mod % 26, "zzz", num_mod/26, math.floor(num_mod/26), int(math.floor(num_mod/26))
        ans = two_letter_number(num_mod % 26) + two_letter_number(int(math.floor(num_mod/26)))

    return ans

##############

def frombase52(string):

    string_backward = string[::-1]

    ans = 0
    base = 52
    base_ct = ord('a')
    for i, char in enumerate(string_backward):
        this_num = ord(char)
        if this_num >= 97:
            num_normalized = this_num - 97
        else:
            num_normalized = this_num - 65
        ans += base**i * num_normalized

    return ans

#-----------#

def tobase52(num, chars=3):

    the_num = num
    base = 52
    base_ct = ord('a')
    base_CT = ord('A')

    ans = ""
    for place in range(chars):
#        print "                   the_num", the_num, "this_place_num", the_num % base
        this_place_num = the_num % base
        if this_place_num < 26:
            this_place_num += base_ct
        else:
            this_place_num += base_CT - 26
#        print "BASE_CT", base_ct, "hhh", place, "this_place_num", this_place_num, "ggg", the_num, "ooo", base
        this_place_char = chr(this_place_num)
#        print "this_place_char", this_place_char
        ans = this_place_char + ans
        the_num = int(math.floor(the_num/base))
#        print "the_num = math.floor...", the_num, "ans=", ans

    return ans

################

def next_permid_encoded():

    component.generic_counter += 1

    component.current_permid = (component.current_permid + component.permid_base_increment) % component.permid_base_mod

#    print "component.current_permid", component.current_permid
    current_permid_encoded = tobase52(component.current_permid)
    current_permid_encoded_lc_13 = codecs.encode(current_permid_encoded.lower(), 'rot_13')
    if not any(s in current_permid_encoded_lc_13 for s in component.prohibited_13):
        if component.generic_counter < 10:
            print "permid",component.generic_counter,"is",current_permid_encoded,"encoded from",component.current_permid
        return current_permid_encoded
    else:
     #   print "prohibited:", current_permid_encoded
        return next_permid_encoded()

###################

def to_semantic_math(txt):

    theopeningtag = txt.group(1)
    thetext = txt.group(2)
    theclosingtag = txt.group(3)

    thetext = to_semantic_ma(thetext)

    return theopeningtag + thetext + theclosingtag

#--------------#

def to_semantic_ma(text):

    thetext = text

    # hide all teh relations
#    the_relations = r'(=|\\lt\b|\\le\b|\\ne\b|\\gt\b|\\ge\b|\\approx\b)'
    the_relations = [r'=',
                     r'\\lt\b',
                     r'\\le\b',
                     r'\\leq\b',
                     r'\\ne\b',
                     r'\\gt\b',
                     r'\\ge\b',
                     r'\\geq\b',
                     r'\\pm\b',
                     r'\\mp\b',
                     r'\\amp\b',   # not a relation, but serves as a divider
                     r'\\approx\b']
#    thetext = re.sub(r"(=|\\lt\b|\\le\b|\\ne\b|\\gt\b|\\ge\b|\\approx\b)", r"@$\1$@", thetext)
    for this_relation in the_relations:
        thetext = re.sub(r"(" + this_relation + ")", r"@$\1$@", thetext)
    thetext = re.sub(r"(\\geq) ", r"@$\1$@ ", thetext)

    # fix some common anomalies
    thetext = re.sub(r"([0-9])(-|\+)([0-9])", r"\1 \2 \3", thetext)  # as in x^3-4x^2+8
    thetext = re.sub(r"([0-9])\\", r"\1 \\", thetext)  # as in 2\sqrt{x} or 2\\left(
    thetext = re.sub(r"(\s|^)uv(\s|$)", r"\1u v\2", thetext)
    thetext = re.sub(r"([a-zA-Z0-9])(\\(sin|cos|tan|sec|csc|cot|ln|log)\b)", r"\1 \2", thetext)
    thetext = re.sub(r"([0-9a-zA-Z}\)+])(\\frac{[^{}]+}{[^{}]+})", r"\1 \2", thetext)
    thetext = re.sub(r"([0-9])([a-zA-Z])", r"\1 \2", thetext)
    thetext = re.sub(r"(\\frac{[^{}]+}{[^{}]+})([0-9a-zA-Z\(+\-])", r"\1 \2", thetext)
    thetext = re.sub(r"(\S) {2,}", r"\1 ", thetext)

#    thetext = re.sub(r"\\frac",
#                     r"\\xfrac", thetext)

    # base of the natural log
    thetext = re.sub(r"\be\^", r"\\eulerE^", thetext)
    # the \pi which is approximately 3.14159
    thetext = re.sub(r"\\pi\b", r"\\circlePi", thetext)

    # roots
    thetext = re.sub(r"\\sqrt\[([^\[\]]+)\]{([^{}]+)}",
                     r"\\nthRoot{\1}{\2}", thetext)

    # factorial
    thetext = re.sub(r"(\b[a-zA-Z]|[0-9]+)\!",
                     r"\\factorial{\1}", thetext)

    #Delta in the sense of a small width
    thetext = re.sub(r"\\Delta +(\S+)", r"\\deltaWidth{\1}", thetext)

    # function application
    thetext = re.sub(r"((\b[a-zA-Z]'*|\\[a-zA-Z]+'*)\(([^\(\)]+)\))",
                     r"\\functionApply{\2}{\3}", thetext)
    thetext = re.sub(r"{([^{}]+)'''}", r"{\\thirdDerivative{\1}}", thetext)
    thetext = re.sub(r"{([^{}]+)''}", r"{\\secondDerivative{\1}}", thetext)
    thetext = re.sub(r"{([^{}]+)'}", r"{\\firstDerivative{\1}}", thetext)
    thetext = re.sub(r"(\b[a-zA-Z]+)'''", r"\\thirdDerivative{\1}", thetext)
    thetext = re.sub(r"(\b[a-zA-Z]+)''", r"\\secondDerivative{\1}", thetext)
    thetext = re.sub(r"(\b[a-zA-Z]+)'", r"\\firstDerivative{\1}", thetext)

    # large parentheses
    thetext = re.sub(r"\\left(\()(.*?)\\right\)",
                     to_paren_group, thetext, 0, re.DOTALL)
    thetext = re.sub(r"\\left(\[)(.*?)\\right\]",
                     to_paren_group, thetext, 0, re.DOTALL)

    # intervals 
    thetext = re.sub(r"\[ *([0-9\.a-zA-Z\-+\\_{}]+) *, *([0-9\.a-zA-Z\-+\\_{}]+) *\]",
                     r"\\ccInterval{\1}{\2}", thetext)
    thetext = re.sub(r"\( *([0-9\.a-zA-Z\-+\\_{}]+) *, *([0-9\.a-zA-Z\-+\\_{}]+) *\]",
                     r"\\ocInterval{\1}{\2}", thetext)
    thetext = re.sub(r"\[ *([0-9\.a-zA-Z\-+\\_{}]+) *, *([0-9\.a-zA-Z\-+\\_{}]+) *\)",
                     r"\\coInterval{\1}{\2}", thetext)
    # in AC, (a,b) usuall means a point in the plane
 #   thetext = re.sub(r"\( *([0-9\.a-zA-Z\-+\\_{}]+) *, *([0-9\.a-zA-Z\-+\\_{}]+) *\)",
 #                    r"\\ooInterval{\1}{\2}", thetext)
    thetext = re.sub(r"\( *([0-9\.a-zA-Z\-+\\_{}]+) *, *([0-9\.a-zA-Z\-+\\_{}]+) *\)",
                     r"\\cartesianPoint{\1}{\2}", thetext)

    # absolute value
    thetext = re.sub(r"\| *([0-9\.a-zA-Z\-+\\_{}\^\(\) ]+?) *\|",
                     r"\\abs{\1}", thetext)

    # limits
    thetext = re.sub(r"\\lim_\{([^{}]) *\\to *([^{}]+) *\} *(\S+)",
                     to_semantic_limit, thetext)
    thetext = re.sub(r" *([0-9\.a-zA-Z\-+\\_{}]+) *\\to *([0-9\.a-zA-Z\-+\\_{}]+)",
                     r"\\goesTo{\1}{\2}", thetext)

    # derivatives
    thetext = re.sub(r"\\frac{d}{d(\\?[a-z]+)} *([^ ]+)",
                     r"\\functionapply{\\dderivativewrt{\1}}{\2}", thetext)
    thetext = re.sub(r"\\frac{d(\\?[a-z]+)}{d(\\?[a-z]+)}",
                     r"\\dderivative{\1}{\2}", thetext)

#    # integrals
#    thetext = re.sub(r"(\\int(.*?[^\\])(d([a-zA-Z]|\\[a-z]+)\b))",
#                     to_semantic_integral, thetext, 0, re.DOTALL)
#
#    # sumations
#    thetext = re.sub(r"\\sum_\{([^{}]+)\}\^\{([^{}]+)\} *([0-9\.a-zA-Z\\\(\)^_\-+ ]+)",
#                    to_semantic_summation, thetext, 0, re.DOTALL)

    # differentials
    thetext = re.sub(r"( |\)|^)d([a-z]'*|\\[a-z]+)",
                     r"\1\\differential{\2}", thetext)

    # implied multiplication from thinspace
    thetext = re.sub(r"([^ ]+) *\\, *([^ ]+)",
                     r"\\impliedMultiplication{\1}{\2}", thetext)
    # should do it multiple times because of several products.
    # or make a function with an arbitrary number of arguments?
    thetext = re.sub(r"([^ ]+) *\\, *([^ ]+)",
                     r"\\impliedMultiplication{\1}{\2}", thetext)

    #  multiplication with a dot (note that this is just for calculus)
    thetext = re.sub(r"([^ ]+) \\cdot ([^ ]+)",
                     r"\\dotMultiplication{\1}{\2}", thetext)
    thetext = re.sub(r"([^ ]+) \\cdot ([^ ]+)",
                     r"\\dotMultiplication{\1}{\2}", thetext)
    #  multiplication with a times (note that this is just for calculus)
    thetext = re.sub(r"([^ ]+) \\times ([^ ]+)",
                     r"\\timesMultiplication{\1}{\2}", thetext)
    thetext = re.sub(r"([^ ]+) \\times ([^ ]+)",
                     r"\\timesMultiplication{\1}{\2}", thetext)

    # number implicit times something
    thetext = re.sub(r"( |^)([0-9]+) *(\(?\\?[a-zA-Z][0-9a-zA-Z\\\(\){}^_]*)( |$)",
                     r"\1\\impliedMultiplication{\2}{\3}\4", thetext)

    # integrals
    thetext = re.sub(r"(\\int(.*?[^\\])(d([a-zA-Z]|\\[a-z]+)\b))",
                     to_semantic_integral, thetext, 0, re.DOTALL)

    # sumations
    thetext = re.sub(r"\\sum_\{([^{}]+)\}\^\{([^{}]+)\} *([0-9\.a-zA-Z\\\(\){}^_\-+ ]+)",
                    to_semantic_summation, thetext, 0, re.DOTALL)
    thetext = re.sub(r"\\sum_\{([^{}]+)\}\^(\\infty|[a-zA-Z]) +([0-9\.a-zA-Z\\\(\){}^_\-+ ]+)",
                    to_semantic_summation, thetext, 0, re.DOTALL)
    # no upper limit
    thetext = re.sub(r"\\sum_\{([^{}]+)\}() +([0-9\.a-zA-Z\\\(\){}^_\-+ ]+)",
                    to_semantic_summation, thetext, 0, re.DOTALL)

    if "400" in thetext or "geq" in thetext:
        print "found 400", thetext

    thetext = re.sub(r"( |{|^)(\-?[0-9\.]+) +(\\?[0-9\.a-zA-Z][0-9\.a-zA-Z\\^_]*)( |}|$)",
                     r"\1\\impliedMultiplication{\2}{\3}\4", thetext)
    if "400" in thetext or "geq" in thetext:
        print "0 found 400", thetext
    # tricky case is "backslash space"
    thetext = re.sub(r"( |^)(\(?\\?[0-9a-zA-Z][0-9a-zA-Z\\\(\)^_]*) +(\(?\\?[0-9a-zA-Z][0-9\.a-zA-Z\\\(\)^_\-+]*)( |$)",
                     r"\1\\impliedMultiplication{\2}{\3}\4", thetext)
    if "400" in thetext or "geq" in thetext:
        print "1 found 400", thetext
    thetext = re.sub(r"( |^)(\(?\\?[0-9a-zA-Z][0-9a-zA-Z\\\(\){}^_]*) +(\(?\\?[0-9a-zA-Z][0-9\.a-zA-Z\\\(\){}^_]*)( |$)",
                     r"\1\\impliedMultiplication{\2}{\3}\4", thetext)
    if "400" in thetext or "geq" in thetext:
        print "2 found 400", thetext
    thetext = re.sub(r"({)(\(?\\?[0-9a-zA-Z][0-9a-zA-Z\\\(\){}^_]*) +(\(?\\?[0-9a-zA-Z][0-9\.a-zA-Z\\\(\){}^_]*)(})",
                     r"\1\\impliedMultiplication{\2}{\3}\4", thetext)
    if "400" in thetext or "geq" in thetext:
        print "3 found 400", thetext
    thetext = re.sub(r"( |^)(\(?\\?[0-9a-zA-Z][0-9a-zA-Z\\\(\){}^_]*) +(\(?\\?[0-9a-zA-Z][0-9\.a-zA-Z\\\(\){}^_]*)( |$)",
                     r"\1\\impliedMultiplication{\2}{\3}\4", thetext)

    if "400" in thetext:
        print "4 again found 400", thetext

    #unhide all the relations
 #   thetext = re.sub(r"@\$(=|\\lt|\\le|\\ne|\\gt|\\ge|\\approx)\$@", r"\1", thetext)
    for this_relation in the_relations:
        thetext = re.sub(r"@\$(" + this_relation + ")\$@", r"\1", thetext)

    thetext = re.sub("ONESPACE", " ", thetext)

    thetext = re.sub(r"(\s|{|^)ar\^([a-z])", r"\1\\impliedMultiplication{a}{r^\2}", thetext)

    return thetext

#------------#

def to_paren_group(txt):

    thebracket = txt.group(1)
    inside_parens = txt.group(2)

    inside_parens = inside_parens.strip()

#    print "inside_parens was", inside_parens
    inside_parens = to_semantic_ma(inside_parens)
#    print "inside_parens is ", inside_parens

    inside_parens = re.sub(" ", "ONESPACE", inside_parens)

    if thebracket == "(":
        theanswer = "\\parenGroup"
    elif thebracket == "[":
        theanswer = "\\bracketGroup"
    else:
        theanswer = "\\ERROR"

    theanswer += "{" + inside_parens + "}"

    return theanswer

#------------#

def to_semantic_limit(txt):

    thevariable = txt.group(1).strip()
    thegoal = txt.group(2).strip()
    thefunction = txt.group(3).strip()

#    print "thegoal", thegoal+ "ttt"

    if thegoal.endswith("^-"):
        thegoal = thegoal[:-2]
        the_answer = r"\limitLeft"
    elif thegoal.endswith("^+"):
        thegoal = thegoal[:-2]
        the_answer = r"\limitRight"
    else:
        the_answer = r"\limitBoth"

    the_answer += "{" + thevariable + "}"
    the_answer += "{" + thegoal + "}"
    the_answer += "{" + thefunction + "}"

#    print "     the_answer", the_answer

    return the_answer

def to_semantic_summation(txt):

    lowerlimit_raw = txt.group(1).strip()
    upperlimit = txt.group(2)
    summand = txt.group(3)

    print "summand", summand

#    if "@$" in lowerlimit_raw:
#        lowerlimit_raw = re.sub("(@|\$)", "", lowerlimit_raw)
    if "=" in lowerlimit_raw:
        lowerlimit_raw = re.sub("(@|\$)", "", lowerlimit_raw)
        print 'lowerlimit_raw.split("=")', lowerlimit_raw.split("=")
        thevariable, lowerlimit = lowerlimit_raw.split("=")
        thevariable = thevariable.strip()
        lowerlimit = lowerlimit.strip()
    else:
        lowerlimit = lowerlimit_raw   # wrong: need to do more than that
        thevariable = lowerlimit_raw[0]

    if upperlimit:
        the_answer = r"\summationLimits"
        the_answer += "{" + lowerlimit + "}"
        the_answer += "{" + upperlimit + "}"
    else:
        the_answer = r"\summationSet"
        the_answer += "{" + lowerlimit + "}"

    the_answer += "{" + summand + "}"
    the_answer += "{" + thevariable + "}"

    return the_answer

def to_semantic_integral(txt):

    lowerlimit = ""
    upperlimit = ""

    theintegrand = txt.group(2)
    theintegrationvariable = txt.group(4)

    if theintegrand.startswith("_"):
        theintegrand = theintegrand[1:]   # remove the _
        if theintegrand.startswith("{"):
            lowerlimit, theintegrand = first_bracketed_string(theintegrand,0,"{","}")
        else:  # in tex, one character lower limit
            lowerlimit = "{" + theintegrand[0] + "}"
            theintegrand = theintegrand[1:]

    if theintegrand.startswith("^"):
        theintegrand = theintegrand[1:]
        if theintegrand.startswith("{"):
            upperlimit, theintegrand = first_bracketed_string(theintegrand,0,"{","}")
        else:  # in tex, one character lower limit
            upperlimit = "{" + theintegrand[0] + "}"
            theintegrand = theintegrand[1:]
    

    theintegrand = theintegrand.strip()
    # remove the spacing before dx in the source
    theintegrand = re.sub(r" *\\(,|;|$)$", "", theintegrand)

    if "[" in theintegrand:
         print "theintegrand", theintegrand
    theintegrand = to_semantic_ma(theintegrand)

    if lowerlimit and upperlimit:
        theanswer = r"\definiteIntegralLimits"
        theanswer += lowerlimit # the limits already are contained in brackets
        theanswer += upperlimit
        theanswer += "{" + theintegrand + "}"
        theanswer += "{" + theintegrationvariable + "}"
    elif lowerlimit and not upperlimit:
        theanswer = r"\definiteIntegralSet"
        theanswer += lowerlimit
        theanswer += "{" + theintegrand + "}"
        theanswer += "{" + theintegrationvariable + "}"
    else:
        theanswer = r"\indefiniteIntegral"
        theanswer += "{" + theintegrand + "}"
        theanswer += "{" + theintegrationvariable + "}"

    return theanswer

###################

def business_card(c_location, size, scale, contents, colors):
    """
    c_location: [center_x, center_y]
    size: [[height, width], [title_font, corner_font, sig_font],
           [title_y_offset, subtitle_y_offset],
           [corner_offset_x, corner_offset_y], edge_width ]
    scale: [overall, font]
    contents: [[title, subtitle], url, [ur, ul, ll, lr], sig]
    colors: [border, fill, title, corners, sig]
    """

    center_x, center_y = c_location
    width, height = size[0]
    aspect_ratio = float(height)/float(width)
    overall_scale = scale[0]
    half_width = overall_scale * width / 2
    half_height = overall_scale * height / 2

    left_x = center_x - half_width
    left_x_str = str(left_x)
    right_x = center_x + half_width
    right_x_str = str(right_x)
    top_y = center_y - half_height
    top_y_str = str(top_y)
    bottom_y = center_y + half_height
    bottom_y_str = str(bottom_y)

    border_color, fill_color, title_color, corner_color, sig_color = colors
    print "border_color", border_color, "border_color"
    print "fill_color", fill_color, "fill_color"
    edge_width = size[4]

    enclosing_rectangle = '<path d="'
    enclosing_rectangle += 'M ' + left_x_str + ' ' + top_y_str + ' ' 
    enclosing_rectangle += 'L ' + left_x_str + ' ' + bottom_y_str + ' ' 
    enclosing_rectangle += 'L ' + right_x_str + ' ' + bottom_y_str + ' ' 
    enclosing_rectangle += 'L ' + right_x_str + ' ' + top_y_str + ' ' 
    enclosing_rectangle += 'L ' + left_x_str + ' ' + top_y_str + ' ' 
    enclosing_rectangle += '" '

    enclosing_rectangle += 'stroke="' + border_color + '" '
    enclosing_rectangle += 'fill="' + fill_color + '" '
    enclosing_rectangle += 'stroke-width="' + str(edge_width) + '" '

    enclosing_rectangle += '/>'
    enclosing_rectangle += '\n'

    # title
    font = "font-family:verdana"
    title, subtitle = contents[0]
    title_font, corner_font, sig_font = size[1]
    font_scale = scale[1]
    title_font_size = font_scale * title_font
    title_y_offset, subtitle_y_offset = size[2]

    title1 = ""
    title2 = ""

    title1 = '<text '
    title1 += 'x="' + str(center_x) + '" '
    if subtitle:  # subtitle
        title1 += 'y="' + str(center_y + title_y_offset*title_font_size) + '" '
    else:
        title1 += 'y="' + str(center_y + title_font_size/4) + '" '
   #     title1 += 'alignment-baseline="center" '
    title1 += 'text-anchor="middle" '
    title1 += 'fill="' + title_color + '" '
    title1 += 'style="' + font + ';font-size:' + str(title_font_size) + '" '
    title1 += '>'

    title1 += title

    title1 += '</text>'
    title1 += '\n'

    # corners
    corner_offset_x, corner_offset_y = size[3]
    corner_font_size = font_scale * corner_font
    ur_content, ul_content, ll_content, lr_content = contents[2]

    ul_corner = ll_corner = lr_corner = ur_corner = ''
    # would it be better to have a loop instead of 4 similar constructions?
    if ul_content:
        ul_corner = '<text '
        ul_corner += 'x="' + str(left_x + corner_offset_x*corner_font_size) + '" '
        ul_corner += 'y="' + str(top_y + (0.6 + corner_offset_y)*corner_font_size) + '" '
        ul_corner += 'text-anchor="start" '
        ul_corner += 'fill="' + corner_color + '" '
        ul_corner += 'style="' + font + ';font-size:' + str(corner_font_size) + '" '
        ul_corner += '>'
        ul_corner += ul_content
        ul_corner += '</text>'
        ul_corner += '\n'

    if ll_content:
        ll_corner = '<text '
        ll_corner += 'x="' + str(left_x + corner_offset_x*corner_font_size) + '" '
        ll_corner += 'y="' + str(bottom_y - corner_offset_y*corner_font_size) + '" '
        ll_corner += 'text-anchor="start" '
        ll_corner += 'fill="' + corner_color + '" '
        ll_corner += 'style="' + font + ';font-size:' + str(corner_font_size) + '" '
        ll_corner += '>'
        ll_corner += ll_content
        ll_corner += '</text>'
        ll_corner += '\n'

    if lr_content:
        lr_corner = '<text '
        lr_corner += 'x="' + str(right_x - corner_offset_x*corner_font_size) + '" '
        lr_corner += 'y="' + str(bottom_y - corner_offset_y*corner_font_size) + '" '
        lr_corner += 'text-anchor="end" '
        lr_corner += 'fill="' + corner_color + '" '
        lr_corner += 'style="' + font + ';font-size:' + str(corner_font_size) + '" '
        lr_corner += '>'
        lr_corner += lr_content
        lr_corner += '</text>'
        lr_corner += '\n'

    if ur_content:
        ur_corner = '<text '
        ur_corner += 'x="' + str(right_x - corner_offset_x*corner_font_size) + '" '
        ur_corner += 'y="' + str(top_y + (0.6 + corner_offset_y)*corner_font_size) + '" '
        ur_corner += 'text-anchor="end" '
        ur_corner += 'fill="' + corner_color + '" '
        ur_corner += 'style="' + font + ';font-size:' + str(corner_font_size) + '" '
        ur_corner += '>'
        ur_corner += ur_content
        ur_corner += '</text>'
        ur_corner += '\n'

    # sig refers to words that are below and to the right
    the_sig = contents[3]
    if the_sig:
        sig_text = '<text '
        sig_text += 'x="' + str(right_x - corner_offset_x*corner_font_size) + '" '
        sig_text += 'y="' + str(bottom_y + (0.6 + corner_offset_y)*corner_font_size) + '" '
        sig_text += 'text-anchor="end" '
        sig_text += 'fill="' + corner_color + '" '
        sig_text += 'style="' + font + ';font-size:' + str(corner_font_size) + '" '
        sig_text += '>'
        sig_text += the_sig
        sig_text += '</text>'
        sig_text += '\n'
    else:
         sig_text = ''

    the_object = enclosing_rectangle + title1 + title2 + ul_corner + ll_corner + lr_corner + ur_corner + sig_text


    return [the_object, [center_x, center_y], [left_x, right_x, top_y, bottom_y], aspect_ratio]
