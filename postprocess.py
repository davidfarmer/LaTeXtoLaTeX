
import re
import component


def put_lists_in_paragraphs(text):

    thetext = text

    thetext = re.sub(r"\s*</p>\s*<(ol|ul|dl)\b(.*?)</\1>",
                     "\n                  " + r"<\1" + r"\2" + "\n                  " + r"</\1>" + "\n                </p>", thetext, 0, re.DOTALL)
    # think about whether that needs to be done twice, when there are successive alternating blocks

    thetext = re.sub(r"\s*</p>\s*<(ol|ul|dl)\b(.*?)</\1>",
                     "\n                  " + r"<\1" + r"\2" + "\n                  " + r"</\1>" + "\n                </p>", thetext, 0, re.DOTALL)
    # note that this simple approach is confused by nested lists

    return thetext

##################

def tag_before_after(tag, startbefore, endbefore, startafter, endafter, text):

    thetag = "(" + tag + ")"
    thetext = text

    thetext = re.sub("\s*(<" + thetag + r"\b[^>]*?>)", startbefore + r"\1", thetext)
    thetext = re.sub("(<" + thetag + r"\b[^>]*?>)\s*", r"\1" + endbefore, thetext)
    thetext = re.sub("\s*(</" + thetag + r">)", startafter + r"\1", thetext)
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

