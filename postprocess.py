
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
        thetext = re.sub("\s*(<" + thetag + r"(>| [^/>]*>))", startbefore + r"\1", thetext)
    if not endbefore or endbefore.isspace():
        thetext = re.sub("(<" + thetag + r"(>| [^/>]*>))\s*", r"\1" + endbefore, thetext)
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
    findtag = "<(" + thetag + r")(>| [^/>]*>)(.*?)</\1>"
    thetext = re.sub(findtag, add_space_with, thetext, 0, re.DOTALL)

    return thetext

def add_space_with(txt):

    the_tag = txt.group(1)
    the_tag_attributes = txt.group(2)
    the_text_inside = txt.group(3)

    the_text = the_tag_attributes + the_text_inside

    # if we have nested lists, don't do anything
    if "<" + the_tag + ">" in the_text or "<" + the_tag + " " in the_text:
        print "problem with nested environment:", the_tag, the_text
        print "/////////////problem with nested environment"
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

    findtag = "<(" + thetag + ")>" + "(\n *)" + r"(.*?)</\1>"
    thetext = re.sub(findtag, add_line_fe, thetext, 0, re.DOTALL)

    # remove spaces after last attribute
    # this shoudl be somewhere else
    thetext = re.sub('"\s+>', '">', thetext)
    thetext = re.sub("'\s+>", "'>", thetext)

    return thetext

def add_line_fe(txt):

    the_tag = txt.group(1)
    the_space = txt.group(2)
    the_text = txt.group(3)

#    # since p can occur inside a p, only add line feeds in the innermost one
#    tag_stub = re.sub("[0-9]*$", "", the_tag)
#    if re.search("<" + tag_stub + r"[1-9]", the_text):
#        return "<" + the_tag + ">" + the_text + "</" + the_tag + ">"

    print "0101010101010101010", the_tag
    print re.sub("Practice visualizing vector addition", "Practice visualizing vector11addition", the_text)

#    # if it is a "just text" paragraph, throw away any formatting
    problematic_internal_tags = ("<p>", "<p ", "<li>", "<li ", "<md", "<me")
    if not any(s in the_text for s in problematic_internal_tags):
         the_text = re.sub(r"(\S) {2,}(\S)", r"\1 \2", the_text)
#        the_text = re.sub(r"\n +", "\n", the_text)
   #     the_text = re.sub(r"\s+", " ", the_text)
   #     the_text = re.sub(r"\s+$", the_space[:-1*component.indent_num], the_text)
    
    print "020202020202020202", the_tag
    print re.sub("Practice visualizing vector addition", "Practice visualizing vector22addition", the_text)
    the_text = the_space + the_text

    print "0303030303030303", the_tag
    print re.sub("Practice visualizing vector addition", "Practice visualizing vector22addition", the_text)
    the_text = the_space + the_text
    # traditional end of a sentence
    for _ in range(20):   # can be many sentences in one paragraph
        the_text = re.sub(the_space + r"(\S.*?[0-9a-z>\)]+(\.|\?|!)) +([A-Z]|<xref|<init)",
                          the_space + r"\1" + the_space + r"\3", the_text)
 #       the_text = re.sub(the_space + r"(\S.*?[0-9a-z>\)]+(\.|\?|!)) +([A-Z]|<xref)",
 #                         the_space + r"\1" + the_space + r"\3", the_text)

    print "11111111111111111111111", the_tag
    print re.sub("Practice visualizing vector addition", "Practice visualizing vector33addition", the_text)

    # put idx tags outside the sentence (if already at end of sentence).
    the_text = re.sub("(<idx>[^.]+</idx>)(\.|,)\s*", r"\2" + the_space + "    " + r"\1" + the_space, the_text)
    # and if in parentheses
    the_text = re.sub("(<idx>[^.]+</idx>)\)(\.|,)\s*", r")\2" + the_space + "    " + r"\1" + the_space, the_text)
    # and at the start of a line
    the_text = re.sub(the_space + "(<idx>[^.]+</idx>)\s+", the_space + "    " + r"\1" + the_space, the_text)
 #   the_text = re.sub(r"\s*" + "(<idx>[^.]+</idx>)\s*", the_space + "    " + r"\1" + the_space, the_text)
    the_text = re.sub(r"(\S|\S +)" + "(<idx>[^.]+</idx>)\s*", r"\1" + the_space + "    " + r"\2" + the_space, the_text)
    the_text = re.sub(the_space + " *(<idx>[^.]+</idx>) *([a-x])", the_space + r"\1" + the_space + r"\2", the_text)

    print "22222222222222222222", the_tag
    print re.sub("Practice visualizing vector addition", "Practice visualizing vector44addition", the_text)

    # colons and semicolons.  commas later
    the_text = re.sub(the_space + "(\S.{25,}[0-9a-z>\)](:)) +(([a-z]|<).{30,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{25,}[0-9a-z>\)](:|;)) +(([a-z]|<).{30,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)

    # put parentheses on their own line
    # parentheses that contain an entire sentence
   # the_text = re.sub("(\S[a-z>]\.) +(\([A-Z<][a-z][^\(\)]*?\.\)) +(\S)",
    the_text = re.sub(the_space + "(\S.*?[a-z>]\.) +(\([A-Z<][a-z][^\(\)]*?\.\)) +(\S)",
                          the_space + r"\1" + the_space + r"\2" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.*?[a-z>]\.) +(\([A-Z<][a-z][^\(\)]*?\.\)\s)",
                          the_space + r"\1" + the_space + r"\2", the_text)
    print "3333333333333333", the_tag
    print re.sub("being the other option", "being the other2option", the_text)

    # parentheses at the end of a sentence
    the_text = re.sub(the_space + "(\S.*?) +(\([<a-z]{2,}[^\(\)]*?\)\.\s)",
                          the_space + r"\1" + the_space + r"\2", the_text)
    print "444444444444444", the_tag
    print re.sub("being the other option", "being the other2option", the_text)

    # urls on their own line, if not punctuated
    the_text = re.sub(the_space + "(\S.*?[a-z>]) +(<url .*?</url>) +(\S)",
                          the_space + r"\1" + the_space + r"\2" + the_space + r"\3", the_text)
    # erls ending sentences
    the_text = re.sub(the_space + "(\S.*?[a-z>]) +(<url .*?</url>[.?!]+)",
                          the_space + r"\1" + the_space + r"\2", the_text)
    # erls ending sentences

    for n in range(3):
        the_text = re.sub(the_space + "(\S.{10,}) +(\([<a-z]{2,} [<a-zA-Z]+[^\(\)]*?\)) +(.*\n)",
                          the_space + r"\1" + the_space + r"\2" + the_space + r"\3", the_text)
        the_text = re.sub(the_space + "(\S.{10,}) +(\([<a-z]{2,} [<a-zA-Z]+[^\(\)]*?\)[.,;:!\?]+) +(.*\n)",
                          the_space + r"\1" + the_space + r"\2" + the_space + r"\3", the_text)

    print "55555555555555555", the_tag
    print re.sub("being the other option", "being the other3option", the_text)

    # commas
    the_text = re.sub(the_space + "(\S.{20,}[0-9a-z>\)]{2,}(:|;|,)) +(([a-z]|<).{50,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{20,}/>(:|;|,)) +(([a-z]|<).{50,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{20,}[0-9a-z>\)]{2,}(:|;|,)) +(([a-z]|<).{50,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{20,}[0-9a-z>\)]{2,}(:|;|,)) +(([a-z]|<).{60,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{25,}[0-9a-z>\)]{2,}(:|;|,)) +(([a-z]|<).{30,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{25,}[a-z>]{2,}(:|;|,)) +(([a-z]|<).{25,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{25,}[a-z>]{2,}(:|;|,)) +(([a-z]|<).{25,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{25,}[a-z>\)]{2,}(:|;|,)) +(([a-z]|<).{25,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)

    the_text = re.sub(the_space + "(\S.{25,}</(em|term|q)>) +(.{25,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{25,}</(em|term|q)>) +(.{25,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)

    the_text = re.sub(the_space + "(\S.{25,}</(xref|term|q|em)>) +(.{30,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{25,}</(xref|term|q|em)>) +(.{30,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{30,}) +(<(xref|term|q|em)>.{20,}\n)",
                      the_space + r"\1" + the_space + r"\2", the_text)

    the_text = re.sub(the_space + "(\S.{25,})" + " " + "(<m>[^<]{8,}</m>.{22,}\n)",
                      the_space + r"\1" + the_space + r"\2", the_text)
    the_text = re.sub(the_space + "(\S.{25,})" + " " + "(<m>[^<]{8,}</m>.{22,}\n)",
                      the_space + r"\1" + the_space + r"\2", the_text)

    the_text = re.sub(the_space + "(\S.{25,}[a-z>\)]{2,}(:|;|,)) +(([a-z]|<).{30,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{8,}[a-z>\)]{2,}(:|;|,)) +(([a-z]|<).{50,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)
    the_text = re.sub(the_space + "(\S.{50,}[a-z>\)]{2,}(:|;|,)) +(([a-z]|<).{8,}\n)",
                      the_space + r"\1" + the_space + r"\3", the_text)

    # idx at end of paragraph has two extra spaces
    the_text = re.sub("</idx>" + the_space + "$", "</idx>" + the_space[:-1*component.indent_num], the_text)

    the_text_trimmed = re.sub("^" + the_space, "", the_text)
    the_answer = "<" + the_tag + ">" + the_text_trimmed + "</" + the_tag + ">"

    print "rrrrrrrrrrrrrrrrr", the_tag
    print the_answer

    return(the_answer)

