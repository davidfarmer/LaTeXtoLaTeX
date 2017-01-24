
import re

import utilities
import component
import postprocess
import myoperations


###################

def mbx_fix(text):
    """ Correct some authoring shortcuts.

    """

    thetext = text

    # allow the user to omit the <main> in an index entry,
    # and to use LaTeX-style <index>theorem!three color</index>
    thetext = re.sub(r"<index>(.*?)</index>", index_fix, thetext, 0, re.DOTALL)

    return thetext

###################

def mbx_strict(text):
    """ Remove white space that confuses xslt.

    """

    # need a big comment explaining the general ideas, pluse one for each case

    thetext = text

    thetext = postprocess.tag_before_after("mrow|intertext", "\n", "", "", "\n", thetext)

    # do p and li separately, and in this order, because of p in li
    thetext = postprocess.tag_before_after("p", "x", "", "", "\n", thetext)
    thetext = postprocess.tag_before_after("li", "x", "", "", "\n", thetext)

    # no white space arounf me, md, etc
    thetext = postprocess.tag_before_after("md|mdn", "", "x", "x", "", thetext)
    thetext = postprocess.tag_before_after("me|men", "", "", "", "", thetext)

    return thetext

###################

def mbx_strict_tex(text):
    # Nothing here yet

    # need to worry about things like white space in paragraphs

    thetext = text

    return thetext

###################

def mbx_strict_html(text):
    """ Rewrite some markup that confuses HTML/MathJax.

    """

    thetext = text

    # mathjax can cause a line feed between math and punctuation
    thetext = re.sub("</m>\s*([,:;.!?\-\)]+)\s+<m>", r"\\text{\1}</m><nbsp /><m>", thetext)
    thetext = re.sub("</m>\s*([,:;.!?\-\)]+)", r"\\text{\1}</m>", thetext)

    # there can also be puntuation before math: (<m> x = 9 </m>)

    # where do we rearrange the punctuation for multi-line math?

    return thetext

###################

def mbx_fa(text):
    """ replace f(x) by \fa{f}{x}.

    """

    thetext = text

    # first process all of the inline math 
    thetext = re.sub(r"<m>.*?</m>", myoperations.fa_convert, thetext, 0, re.DOTALL)
    # and then the simple display math
    thetext = re.sub(r"<me>.*?</me>", myoperations.fa_convert, thetext, 0, re.DOTALL)
    thetext = re.sub(r"<men[^>]*>.*?</men>", myoperations.fa_convert, thetext, 0, re.DOTALL)
    # a row of a multiline
    thetext = re.sub(r"<mrow>.*?</mrow>", myoperations.fa_convert, thetext, 0, re.DOTALL)

    return thetext

###################

def mbx_pp(text):
    """ Pretty-print MBX source.

    """

    thetext = text

    # first remove extraneous spaces and put in appropriate carriage returns

    thetext = postprocess.tag_before_after("p", "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("row|tabular|image|latex-image-code|asymptote", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("me|men|md|mdn", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("exercises|exercisegroup|exercise", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("webwork|setup|set|pg-code", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("mrow|intertext", "\n", "", "", "\n", thetext)
    thetext = postprocess.tag_before_after("dt", "\n\n", "", "", "\n", thetext)
    thetext = postprocess.tag_before_after("dd", "\n", "", "", "\n\n", thetext)
    thetext = postprocess.tag_before_after("li", "\n\n", "", "", "\n\n", thetext)
    thetext = postprocess.tag_before_after("ul|ol|dl", "\n\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("theorem|proposition|lemma|conjecture|corollary",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("algorithm",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("objectives",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("definition|example|insight|exploration|activity|remark|proof",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("figure|table",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("paragraphs|sidebyside|aside", "\n\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("introduction|statement|solution|answer|hint|objectives", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("subsection", "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("chapter|section", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("title|cell|caption", "\n", "", "", "\n", thetext)

#    # first remove all the spaces at the beginning of a line
#    thetext = re.sub("\n +", "\n", thetext)

    # then put it back
    thetext = postprocess.add_space_within("chapter", thetext)
    thetext = postprocess.add_space_within("section", thetext)
    thetext = postprocess.add_space_within("subsection", thetext)
    thetext = postprocess.add_space_within("introduction", thetext)
    thetext = postprocess.add_space_within("objectives", thetext)
    thetext = postprocess.add_space_within("figure", thetext)
    thetext = postprocess.add_space_within("image", thetext)
    thetext = postprocess.add_space_within("asymptote", thetext)
    thetext = postprocess.add_space_within("sidebyside", thetext)
    thetext = postprocess.add_space_within("aside", thetext)
    thetext = postprocess.add_space_within("latex-image-code", thetext)
    thetext = postprocess.add_space_within("definition|theorem|example|insight|exploration|activity", thetext)
    thetext = postprocess.add_space_within("algorithm|objectives", thetext)
    thetext = postprocess.add_space_within("proposition|lemma|remark|conjecture|corollary", thetext)
    thetext = postprocess.add_space_within("statement|solution|answer|hint|proof", thetext)
    thetext = postprocess.add_space_within("p", thetext)
    thetext = postprocess.add_space_within("paragraphs", thetext)
    thetext = postprocess.add_space_within("ul", thetext)
    thetext = postprocess.add_space_within("ol", thetext)
    thetext = postprocess.add_space_within("dl", thetext)
    thetext = postprocess.add_space_within("li", thetext)
    thetext = postprocess.add_space_within("me|men|md|mdn", thetext)
    thetext = postprocess.add_space_within("exercises", thetext)
    thetext = postprocess.add_space_within("exercisegroup", thetext)
    thetext = postprocess.add_space_within("exercise", thetext)
    thetext = postprocess.add_space_within("webwork", thetext)
    thetext = postprocess.add_space_within("setup", thetext)
 #   thetext = postprocess.add_space_within("var", thetext)
    thetext = postprocess.add_space_within("set", thetext)
    thetext = postprocess.add_space_within("pg-code", thetext)
    thetext = postprocess.add_space_within("table", thetext)
    thetext = postprocess.add_space_within("tabular", thetext)
    thetext = postprocess.add_space_within("row", thetext)
    thetext = postprocess.add_space_within("pre", thetext)

    return thetext

##################

def index_fix(txt):

    the_text = txt.group(1)

    if the_text.startswith("<main>"):
        return "<index>" + the_text + "</index>"

    elif "!" not in the_text:
        return "<index><main>" + the_text + "</main></index>"

    elif "<m>" in the_text:   # poor hack to handle factorial
        return "<index><main>" + the_text + "</main></index>"

    else:
        this_entry = the_text.split("!")
        the_answer = "<main>" + this_entry.pop(0) + "</main>"
        for sub in this_entry:
            the_answer += "<sub>" + this_entry.pop(0) + "</sub>"

    return "<index>" + the_answer + "</index>"
  

##################

