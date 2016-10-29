
import re
import component

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
##        print "ERROR?: replacing macro", macroname, "in empty string"
        return ""

##    print "in replacemacro, macroname",macroname
##    print text[:150]
##    print "------------------"

    thetext = text
    global a_macro_changed

    a_macro_changed = 1
    component.replaced_macros = []

    the_macroname = re.sub(r"\\",r"\\\\",macroname)

    while a_macro_changed:   # change to:  while "\\"+macroname in text:

        a_macro_changed = 0

  #      thetext = re.sub(r"\\("+macroname+r")\**(([0-9]|\b|{)+.*)",
        thetext = re.sub("(" + the_macroname + r")\**(([0-9]|\b|{)+.*)",
                         lambda match: replacemac(match,numargs,replacementtext),
                         thetext,1,re.DOTALL)

    for idx, val in enumerate(component.replaced_macros):
        the_val = re.sub(r"\\",r"\\\\",val)
        print "substituting number"+str(idx) + "for" + the_val
        print r"xxxx" + str(idx) + r"yyyy"
        thetext = re.sub(r"xxxx" + str(idx) + r"yyyy", the_val, thetext)

    return thetext

##############

def replacemac(txt,numargs,replacementtext):

    this_macro = txt.group(1)
 #   text_after = txt.group(2).strip()   # not sure why we strip the text after?
    text_after = txt.group(2)

    if numargs:
        text_after = text_after.lstrip()

    if text_after.startswith("["):
        print "found square group" #  of type",replacementtext
        squaregroup, text_after = first_bracketed_string(text_after,0,"[","]")
        text_after = text_after.lstrip()
        # Currently we ignore the squaregroup.  What should we do with it?

     # first a hack to handle some oddly formed macro calls
    try:
        first_character = text_after[0]
    except IndexError:
        first_character = ""

 #   if numargs and not text_after.startswith("{"):
    if numargs and first_character  not in ["{","\\"] and first_character not in r"0123456789":
        print "found", this_macro, "but it has no argument",text_after[:50]
        return text_after

    if first_character in "0123456789":   # wrap it in {} and proceed normally
        print "found that the argument is a number"
        text_after = re.sub("^([0-9])",r"{\1}",text_after,1)
        print "now the text after starts:",text_after[:20]

    if first_character == r"\\":   # wrap the argument in {} and proceed normally
        print "found that the argument is another macro"
        text_after = re.sub(r"^\\([a-zA-Z]+)",r"{\\\1}",text_after,1)

    global a_macro_changed
    a_macro_changed += 1

##    print "\n   found",this_macro, "with nurmags",numargs,"to replace:", text_after[:50]
##
##    print "\nXXXXX replacing it by",replacementtext,"XXXXX"
#    print "\nYYYYYYYY\n"
    arglis=[""]      # put a throw-away element 0 so that it is less confusing
                     # when we assign to the LaTeX "#N" argmuments


    for _ in range(numargs):
            try:
                theitem, text_after = first_bracketed_string(text_after)
            except ValueError:
                print "ERROR, no text_after in replacemac",text_after[:100]
                theitem = ""
                # below is to fail gracefully when there is an error.
                # need to come up with a better way
            if not theitem:  # probably missing close bracket
                print "was scanning argument",_
                print "missing brace?  guess to stop at end of line"
             #  arglis.append(text_after)
                if "\n" in text_after:
                    theitem, text_after = text_after.split("\n",1)
                else:
                    theitem = ""
          #      text_after = ""
          #      continue
            theitem = strip_brackets(theitem)
            theitem = re.sub(r"\\",r"\\\\",theitem)  # This is tricky.  We are using the extracted LaTeX
                                                   # in a substitution, so we should think of it as code.
                                                   # Therefore we need to excape the backslashes.
      #      theitem = re.sub(r"\b",r"\\b",theitem)  # because \b is special?
     #       theitem = re.escape(theitem)  # This is tricky.  We are using the extracted LaTeX
     #                                              # in a substitution, so we should think of it as code.
     #                                              # Therefore we need to excape the backslashes.
            arglis.append(theitem)

###    macroexpanded = replacementtext
    macroexpanded = re.sub(r"\\",r"\\\\",replacementtext)
#    print "macroexpanded",macroexpanded

    for arg in range(1,numargs+1):
        mysubstitution = "#"+str(arg)
 #       print "About to do re.sub("
 #       print mysubstitution
 #       print "1111111"
 #       print arglis[arg]
 #       print "22222222"
 #       print macroexpanded
 #       print "33333333"
        macroexpanded = re.sub(mysubstitution,arglis[arg],macroexpanded)
 #       print "4444444"

#    print "At end of replacemac, the macroexpanded is",macroexpanded
#    print "And the text_after starts",text_after[:120]

    macro_index = len(component.replaced_macros)
    component.replaced_macros.append(macroexpanded)

    return "xxxx" + str(macro_index) + "yyyy" + text_after
#    return macroexpanded + text_after

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


