# -*- coding: utf-8 -*-

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

html_to_latex_pairs = [
    [r"&#xc1;",r"\\'A"],
    [r"&#xc4;",r'\\"A'],
    [r"&#xc8;",r"\\`E"],
    [r"&#xc9;",r"\\'E"],
    [r"&#xd6;",r'\\"O'],
    [r"&#xe1;",r"\\'a"],
    [r"&#xe4;",r'\\"a'],
    [r"&#xe8;",r"\\`e"],
    [r"&#xe9;",r"\\'e"],
    [r"&#xf3;",r"\\'o"],
    [r"&#xf8;",r"{\\o}"],
    [r"&#xfa;",r"\\'u"],
    [r"&#xfc;",r'\\"u'],
    [r"&#xf1;",r'\\~n'],
    [r"&#355;",r'\\c{t}'],
    [r"&#169;",r'\\~u'],
    [r"&#259;",r'\\u{a}'],
    [r"&#287;",r'\\u{g}'],
    [r"&#281;",r'\\c{e}'],
    [r"&#301;",r'\\u{\\i}'],
    [r"&#350;",r'\\c{S}'],
    [r"&#351;",r'\\c{s}'],
    [r"&#x107;",r"\\'c"],
    [r"&#x10c;",r"\\v{C}"],
    [r"&#x10d;",r"\\v{c}"],
    [r"&#x11a;",r"\\v{E}"],
    [r"&#x11b;",r"\\v{e}"],
    [r"&#x141;",r"\\L"],
    [r"&#x160;",r'\\v{S}'],
    [r"&#x161;",r'\\v{s}'],
    [r"&#x27;",r"'"],
    [r"&iuml;",r'\\"{\\i}'],
    [r"&szlig;",r'{\\ss}'],
    [r"&ndash;",r'--'],
    [r"&quot;",r'"']
    ]


def html_to_latex_alphabet(text):

    thetext = text

    for ht,la in html_to_latex_pairs:
        thetext = re.sub(ht,la,thetext)

    thetext = re.sub(r"&#34;",r'"',thetext)
    thetext = re.sub(r"&#39;",r"'",thetext)

    thetext = re.sub(r"&(.)uml;",r'\\"\1',thetext)
    thetext = re.sub(r"&iacute;",r"\\'{\\i}",thetext)
    thetext = re.sub(r"&(.)acute;",r"\\'\1",thetext)
    thetext = re.sub(r"&(.)grave;",r"\\`\1",thetext)
    thetext = re.sub(r"&(.)tilde;",r"\\~\1",thetext)
    thetext = re.sub(r"&(.)caron;",r"\\v{\1}",thetext)
    thetext = re.sub(r"&(.)cedil;",r"\\c{\1}",thetext)
    thetext = re.sub(r"&(o|O)slash;",r"{\\\1}",thetext)


    return thetext

def other_alphabets_to_latex(text):  # including Word characters

    thetext = text

    # maybe use str.replace instead of a regular expression

    thetext = re.sub('−',r"-",thetext)
    thetext = re.sub('’',r"'",thetext)
    thetext = re.sub('“',r"``",thetext)
    thetext = re.sub('”',r"''",thetext)

    thetext = re.sub('\xc3\xb3',r"\'o",thetext)
    thetext = re.sub('\xc3\xa1',r"\'a",thetext)
    thetext = re.sub('\xc5\x9f',r"\c{a}",thetext)
    thetext = re.sub('\xc3\xb1',r"\~n",thetext)

    thetext = re.sub('\xe2\x80\x22',r'-',thetext)   # not sure why that worked, but the clue was
                                                    # looking at the html file.  That character is
                                                    # the windows 0x2013 en dash

    thetext = re.sub('\x91',r"'",thetext)
    thetext = re.sub('\x92',r"'",thetext)
    thetext = re.sub('\x93',r'"',thetext)
    thetext = re.sub('\x94',r'"',thetext)
    thetext = re.sub('\x96',r'-',thetext)
    thetext = re.sub('\x97',r' - ',thetext)

    thetext = re.sub('\x85',r' - ',thetext)
    thetext = re.sub('\x8a',r'\\"a',thetext)
    thetext = re.sub('\x9a',r'\\"o',thetext)
    thetext = re.sub('\x96',r"-",thetext)
    thetext = re.sub('\x9f',r'\\"u',thetext)
    thetext = re.sub('\xa0'," ",thetext)
    thetext = re.sub('\xb1',r"\\pm",thetext)
    thetext = re.sub('\xb4',r"'",thetext)
    thetext = re.sub('\xc2'," ",thetext)
    thetext = re.sub('\xd5',r"'",thetext)
    thetext = re.sub('\xdf',r"{\\ss}",thetext)
    thetext = re.sub('ł',r"{\\l}",thetext)
    thetext = re.sub('ồ',r"\\^o",thetext)   # note: not the correct translation
    thetext = re.sub('á',r"\\'a",thetext)
    thetext = re.sub('à',r"\\`a",thetext)
    thetext = re.sub('ä',r'\\"a',thetext)
    thetext = re.sub('ã',r'\\~a',thetext)
    thetext = re.sub('é',r"\\'e",thetext)
    thetext = re.sub('è',r"\\`e",thetext)
    thetext = re.sub('É',r"\\'E",thetext)
    thetext = re.sub('\xe0',r"\\`a",thetext)
    thetext = re.sub('\xe1',r"\\'a",thetext)
    thetext = re.sub('\xe9',r"\\'e",thetext)
    thetext = re.sub('í',r"\\'{\\i}",thetext)
    thetext = re.sub('\xed',r"\\'{\\i}",thetext)
    thetext = re.sub('\xee',r"\\^{\\i}",thetext)
    thetext = re.sub('Á',r"\\'{A}",thetext)
    thetext = re.sub('Å',r"\\c{A}",thetext)
    thetext = re.sub('ń',r"\\'n",thetext)
    thetext = re.sub('ñ',r"\\~n",thetext)
    thetext = re.sub('ó',r"\\'o",thetext)
    thetext = re.sub('ú',r"\\'u",thetext)
    thetext = re.sub('ü',r'\\"u',thetext)
    thetext = re.sub('\xf1',r"\\~n",thetext)
    thetext = re.sub('\xf3',r"\\'o",thetext)
    thetext = re.sub('\xf6',r'\\"o',thetext)
    thetext = re.sub('ö',r'\\"o',thetext)
    thetext = re.sub('š',r'\\v{s}',thetext)
    thetext = re.sub('ş',r'\\c{s}',thetext)
    thetext = re.sub('ç',r'\\c{c}',thetext)
    thetext = re.sub('č',r'\\v{c}',thetext)
    thetext = re.sub("ć",r"\\'c",thetext)
    thetext = re.sub('ř',r'\\v{r}',thetext)
    thetext = re.sub('\xfc',r'\\"u',thetext)
    thetext = re.sub('\xe8',r'\\`e',thetext)
    thetext = re.sub('Ã ',r'\\`a',thetext)
    thetext = re.sub('—',r'--',thetext)

    return thetext

def latex_to_ascii(text):

    thetext = text

    # these convert like \alpha -> alpha
    latex_to_ascii_greek = ["alpha","beta","gamma","delta","epsilon"
"zeta","eta","theta","mu","nu","tau","rho","sigma","xi","kappa",
"iota","lambda","upsilon","omicron","phi","chi","omega","psi","pi"]

    for letter in latex_to_ascii_greek:
        the_sub =  "\\\\" + "(" + letter + ")" + r"\b"
        thetext = re.sub(the_sub,r"\1",thetext,re.I)  # case insensitive

    latex_to_ascii_symbol = [["ge",">="],["geq",">="],["le","<="],["leq","<="]]
    for pair in latex_to_ascii_symbol:
        the_sub =  "\\\\" + "(" + pair[0] + ")" + r"(\b|[0-9])"
        the_target = " " + pair[1] + " "
        thetext = re.sub(the_sub,the_target+r"\2",thetext,re.I)  # case insensitive

    thetext = re.sub(r"\s*\\times\s*"," x ",thetext)

    thetext = re.sub(r"\\tfrac",r"\\frac",thetext)
    thetext = re.sub(r"\\widehat",r"\\hat",thetext)
    thetext = re.sub(r"\\widetilde",r"\\tilde",thetext)
    thetext = re.sub(r"\\widecheck",r"\\check",thetext)
    thetext = re.sub(r"\\bar\b",r"\\overline",thetext)

    thetext = re.sub(r"\\[\^\'\`\"\~\-\=]\s*","",thetext)  # remove latex accents

    # in TeX, \\i is an i (without a dot), but usually \\. is a diacritical mark

    # shuld put these into a list in mapping.py
    thetext = re.sub(r"\\varphi","phi",thetext)
    thetext = re.sub(r"\\varrho","rho",thetext)
    thetext = re.sub(r"\\pm\b","+-",thetext)
    thetext = re.sub(r"\\ell(\b|\s+)","l",thetext)
    thetext = re.sub(r"{\\i}","i",thetext)
    thetext = re.sub(r"\\i ([A-Z])",r"i \1",thetext)
    thetext = re.sub(r"\\i\b","i",thetext)
    thetext = re.sub(r"{\\l}","l",thetext)
    thetext = re.sub(r"\\l ([A-Z])",r"l \1",thetext)
    thetext = re.sub(r"\\l ","l",thetext)
    thetext = re.sub(r"\\l\b","l",thetext)
    thetext = re.sub(r"\\L ","L",thetext)
    thetext = re.sub(r"{\\L}","L",thetext)
    thetext = re.sub(r"{\\o}","oe",thetext)
    thetext = re.sub(r"\\o\b","oe",thetext)
    thetext = re.sub(r"{\\oe}","oe",thetext)
    thetext = re.sub(r"{\\ss}","ss",thetext)
    thetext = re.sub(r"\\ss\b","ss",thetext)
    thetext = re.sub(r"\\H o","o",thetext)
    thetext = re.sub(r"\\H{o}","o",thetext)

    thetext = re.sub(r"\s*\\cprime\s*","'",thetext)
    thetext = re.sub(r"\s*\\vert\b\s*","|",thetext)

    thetext = re.sub(r"\s*\\left\b\s*","",thetext)
    thetext = re.sub(r"\s*\\right\b\s*","",thetext)

    latex_to_delete_from_ascii = ["rm","it","sl","bf","tt","em","emph",
                       "Bbb","mathbb","bold",
                       "scr",
                       "roman",
                       "Cal","cal","mathcal",
                       "mathrm","mathit","mathsl","mathbf","mathsf","mathtt",
                       "germ","frak", "mathfrak"]

    for macro in latex_to_delete_from_ascii:
        the_sub =  "\\\\" + macro + r"\b"
        thetext = re.sub(the_sub,"",thetext)

    other_latex_markup = ["v","u","c"]     # as in Nata\v sa or Altu\u{g} or Ho{\c{s}}ten/

    for macro in other_latex_markup:
        the_sub =  "\\\\" + "(" + macro + ")" + r"\s*{([a-zA-Z])}"
        thetext = re.sub(the_sub,r"\2",thetext)
        the_sub =  "\\\\" + "(" + macro + ")" + r"\b\s*"
        thetext = re.sub(the_sub,"",thetext)

    thetext = re.sub(r"{([^}])}",r"\1",thetext)  #  {.} --> .
    thetext = re.sub(r"{([^}])}",r"\1",thetext)  #  {.} --> .  # Twice, because of {\v{S}}emrl

    thetext = re.sub(r"\s+"," ",thetext)

    return thetext


def to_ascii(text):

    thetext = text

    thetext = html_to_latex_alphabet(thetext)
    thetext = other_alphabets_to_latex(thetext)
    thetext = latex_to_ascii(thetext)

    return thetext

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
