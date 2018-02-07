
import re
import component

##################

def wrap_li_content_in_p(text):

    the_text = text

    the_text = re.sub(r"<li\b([^<>]*)>(.*?)(</li>|<ul\b[^>]*>|<ol\b[^>]*>)",
                        fix_li,the_text,0,re.DOTALL)

    return the_text


def fix_li(txt):

    the_param = txt.group(1)
    the_text = txt.group(2)
    the_ending_tag = txt.group(3)

    the_text = the_text.strip()

    if not the_text:
        pass   # nothing to do, except return the enclosing tags
    elif the_text.startswith("<p>") or the_text.endswith("</p>"):
        pass     # already in <p> so don't do anything
    else:
        the_text = "<p>" + the_text + "</p>\n"

    return "<li" + the_param + ">" + the_text + the_ending_tag

##################

def tag_before_after(tag, startbefore, endbefore, startafter, endafter, text):
    """ Replace the white space around starting and ending tags
        by the given white space (or by nothing).

        If the "new" text is not white space, then the text is not changed.

    """

    thetag = "(" + tag + ")"
    thetext = text

    if not startbefore or startbefore.isspace():
        thetext = re.sub("\s*(<" + thetag + r"\b[^>]*?>)", startbefore + r"\1", thetext)
    if not endbefore or endbefore.isspace():
        thetext = re.sub("(<" + thetag + r"\b[^>]*?>)\s*", r"\1" + endbefore, thetext)
    if not startafter or startafter.isspace():
        thetext = re.sub("\s*(</" + thetag + r">)", startafter + r"\1", thetext)
    if not endafter or endafter.isspace():
        thetext = re.sub("(</" + thetag + r">)\s*", r"\1" + endafter, thetext)

    return thetext

##################

def add_space_within(tag,text):

   # thetag = re.sub("-",r"\-",tag)
    thetag = tag
    thetext = text

    # note the work-around for self-closing tags
    findtag = "<(" + thetag + r")\b([^>]*[^/]?>.*?)</\1>"
    thetext = re.sub(findtag, add_space_with, thetext, 0, re.DOTALL)

    return thetext

def add_space_with(txt):

    the_tag = txt.group(1)
    the_text = txt.group(2)

    # if we have nested lists, don't do anything
    if "<" + the_tag + ">" in the_text or "<" + the_tag + " " in the_text:
        print "problem with nested environment:", the_tag, the_text[:20]
        closing_tag = "</" + the_tag + ">"
        the_text = add_space_within(the_tag, the_text + closing_tag)
        the_text = re.sub(closing_tag + "$", "", the_text)
    else:
        # don't add more space at the beginning of every line,
        # just those that contain a non-white-space character
        the_text = re.sub("\n( *\S)","\n" + component.indentamount + r"\1", the_text)

    the_text = "<" + the_tag + the_text + "</" + the_tag + ">"

    return(the_text)

##################

def add_line_feeds(tag,text):

   # assumes tag is followed by line feed 

   # thetag = re.sub("-",r"\-",tag)
    thetag = tag
    thetext = text

    # note the work-around for self-closing tags
    findtag = "<(" + thetag + ")>" + "(\n *)" + r"(.*?)</\1>"
    thetext = re.sub(findtag, add_line_fe, thetext, 0, re.DOTALL)

    return thetext

def add_line_fe(txt):

    the_tag = txt.group(1)
    the_space = txt.group(2)
    the_text = txt.group(3)

    # traditional end of a sentence
    the_text = re.sub(r"([a-z>\)]+(\.|\?|!)) +([A-Z]|<xref)",
                      r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(r"([a-z>\)]+(\.|\?|!)) +([A-Z]|<xref)",
                      r"\1" + the_space + r"\3", the_text)
    # put idx tags outside the sentence (if already at end of sentence).
    the_text = re.sub("(<idx>[^.]+</idx>)\.", "." + the_space + "    " + r"\1", the_text)
    # and if in parentheses
    the_text = re.sub("(<idx>[^.]+</idx>)\)\.", ")." + the_space + "    " + r"\1", the_text)

    the_text = re.sub(the_space + "(.{20,}[a-z>\)](:|;|,)) +(([a-z]|<m|<xref).{50,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub("(^|" + the_space + ")" + "(.{20,}[a-z>\)](:|;|,)) +(([a-z]|<m|<xref).{50,}\n)",
                      r"\1" + r"\2" + the_space + r"\4", the_text)
    the_text = re.sub(the_space + "(.{20,}[a-z>\)](:|;|,)) +(([a-z]|<m|<xref).{60,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(.{25,}[a-z>\)](:|;|,)) +(([a-z]|<m|<xref).{30,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub("(^|" + the_space + ")" + "(.{25,}[a-z>](:|;|,)) +(([a-z]|<m|<xref).{25,}\n)",
                      r"\1" + r"\2" + the_space + r"\4", the_text)
    the_text = re.sub("(^|" + the_space + ")" + "(.{25,}[a-z>](:|;|,)) +(([a-z]|<m|<xref).{25,}\n)",
                      r"\1" + r"\2" + the_space + r"\4", the_text)
    the_text = re.sub("(^|" + the_space + ")" + "(.{25,}[a-z>\)](:|;|,)) +(([a-z]|<m|<xref).{25,}\n)",
                      r"\1" + r"\2" + the_space + r"\4", the_text)
    the_text = re.sub("(.{25,}</(xref|term)>) +(.{30,}\n)",
                      r"\1" + the_space + r"\3", the_text)
    the_text = re.sub("(.{25,}</(xref|term)>) +(.{30,}\n)",
                      r"\1" + the_space + r"\3", the_text)
    the_text = re.sub("(^|" + the_space + ")" + "(.{25,}</(m|em)>) +(.{30,}\n)",
                      r"\1" + r"\2" + the_space + r"\4", the_text)
    the_text = re.sub("(^|" + the_space + ")" + "(.{25,}</(m|em)>) +(.{30,}\n)",
                      r"\1" + r"\2" + the_space + r"\4", the_text)
    the_text = re.sub("(^|" + the_space + ")" + "(.{30,}) +(<(m|em)>.{20,}\n)",
                      r"\1" + r"\2" + the_space + r"\3", the_text)
    the_text = re.sub("(^|" + the_space + ")" + "(.{25,}</(q|m|em|term|xref)>\)) +(.{30,}\n)",
                      r"\1" + r"\2" + the_space + r"\4", the_text)
    the_text = re.sub("(^|" + the_space + ")" + "(.{25,}</(q|m|em|term|xref)>\)) +(.{30,}\n)",
                      r"\1" + r"\2" + the_space + r"\4", the_text)
    the_text = re.sub("(^|" + the_space + ")" + "(.{25,})" + " " + "(<(q|m|em|term|xref)>.{30,}\n)",
                      r"\1" + r"\2" + the_space + r"\3", the_text)

#    the_text_lines = the_text.split("\n")
#
#    for ct,line in enumerate(the_text_lines):
# #       if len(line) > 50:
#            line = re.sub(r"([a-z>\)](:|;|,)) +(([a-z]|<m|<xref).{20,})",
#                      r"\1" + the_space + r"\3", line)
#            the_text_lines[ct] = line
#
#    the_text = "\n".join(the_text_lines)

#    # colon, semicolon or comma
#    the_text = re.sub(r"([a-z>\)](:|;|,)) +([a-z]|<m|<xref)",
#                      r"\1" + the_space + r"\3", the_text)

    the_answer = "<" + the_tag + ">" + the_space + the_text + "</" + the_tag + ">"

    return(the_answer)



