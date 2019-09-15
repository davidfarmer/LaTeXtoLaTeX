
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
    thetext = re.sub("</m>\s*([,:;.!?\-\)'\"]+)\s+<m>", r"\\text{\1}</m><nbsp /><m>", thetext)
    thetext = re.sub("</m>\s*([,:;.!?\-\)'\"]+)", r"\\text{\1}</m>", thetext)

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

    # first hide comments
    thetext = re.sub("--> +\n", "-->\n",thetext)
    thetext = re.sub("--> +", "-->UVUSpACeVUV",thetext)
    thetext = re.sub(r"(\s*(<!--)(.*?)(-->))",
                     lambda match: utilities.sha1hide(match, "comment"),
                     thetext, 0, re.DOTALL)

    # some tags can have punctuation after them
    for tag in component.punctuatable_tags:
        thetext = re.sub(r"(</" + tag + ">)" + r"(\S)", r"\1UVUnooooSpACeVUV\2", thetext)
        thetext = re.sub(r"(</" + tag + ">)" + r" ", r"\1UVUSpACeVUV", thetext)

    # then hide verbatim content
    for tag in component.verbatim_tags:
        thetext = re.sub(r"(\s*(<" + tag + "(>| [^/>]*>))(.*?)(</" + tag + ">))",
                         lambda match: utilities.sha1hide(match, tag),
                         thetext, 0, re.DOTALL)

    # empty tags that should be on their own line
    for tag in component.document_pieces_empty:
        thetext = re.sub(r"\s*(<" + tag + r"[^>]*/>)", "\n" + r"\1", thetext)

    # sort-of a hack to handle tags that can occur within themselves (like li and p)
    for lip_tag in component.nestable_tags:
        component.lipcounter[lip_tag] = 0
        thetext = utilities.tag_to_numbered_tag(lip_tag, thetext)

        print "found", component.lipcounter
        for n in range(component.lipcounter[lip_tag]):
            if lip_tag == "li":  # note: now the same as the else case!
                thetext = postprocess.tag_before_after(lip_tag + str(n), "\n\n", "\n", "\n", "\n\n", thetext)
            else:
                thetext = postprocess.tag_before_after(lip_tag + str(n), "\n\n", "\n", "\n", "\n\n", thetext)
        thetext = postprocess.tag_before_after(lip_tag, "\n\n", "\n", "\n", "\n\n", thetext)

    # delete all leading spaces!
    thetext = re.sub(r"\n +", "\n", thetext)

    # first remove extraneous spaces and put in appropriate carriage returns

    thetext = postprocess.tag_before_after("dt", "\n\n", "", "", "\n", thetext)
    thetext = postprocess.tag_before_after("dd", "\n", "", "", "\n\n", thetext)

    component.document_global_structure.reverse()
    component.document_sectioning.reverse()

    for tag in component.math_display:
        thetext = postprocess.tag_before_after(tag, "\n", "\n", "\n", "\n", thetext)
    for tag in component.document_components:
        thetext = postprocess.tag_before_after(tag, "\n", "\n", "\n", "\n", thetext)
    for tag in component.list_like:
        thetext = postprocess.tag_before_after(tag, "\n", "\n", "\n", "\n", thetext)
    for tag in component.document_environments:
        thetext = postprocess.tag_before_after(tag, "\n\n", "\n", "\n", "\n\n", thetext)
    for tag in component.document_sectioning:
        thetext = postprocess.tag_before_after(tag, "\n\n", "\n", "\n", "\n\n", thetext)
    for tag in component.document_global_structure:
        thetext = postprocess.tag_before_after(tag, "\n\n", "\n", "\n", "\n\n", thetext)
    for tag in component.document_pieces:
        thetext = postprocess.tag_before_after(tag, "\n", "", "", "\n", thetext)
    for tag in component.footnote_like:
        thetext = postprocess.tag_before_after(tag, "", "\n", "\n", "", thetext)

#    thetext = re.sub(r"(\s)UVUSpACeVUV", r"\1", thetext)
#    thetext = re.sub(r"UVUSpACeVUV(\s)", r"\1", thetext)
#    thetext = re.sub(r"UVUSpACeVUV", " ", thetext)
#    thetext = re.sub(r"\s*UVUnooooSpACeVUV\s*(.)", r"\1", thetext)

    # sort-of hack for spacing after punctuation after display math
    thetext = re.sub(r"(</(md|mdn|me|men)>)\s*(;|:|,)\s*", r"\1\3" + "\n", thetext)
    thetext = re.sub(r"(</(md|mdn|me|men)>)\s*((\?|!|\.)+)\s*", r"\1\3" + "\n", thetext)

    # sort-of hack for spacing after footnotes that do not end a sentence
    thetext = re.sub(r"(</fn>)([a-zA-Z])", r"\1 \2", thetext)

    # space around pagebreak
    thetext = re.sub(r"\s*<pagebreak\s*/>\s*", "\n\n<pagebreak />\n\n", thetext)

    # sort-of hack for cells containing p paragraphs
    thetext = re.sub(r"(<cell>)(<p[0-9]*>)", r"\1" + "\n" + r"\2", thetext)
    thetext = re.sub(r"(</p[0-9]*>)(</cell>)", r"\1" + "\n" + r"\2", thetext)

    # title and idx should not be immediately next to non-pubctuation
    for tag in ["title", "idx"]:
        search_string = "(</" + tag + ">)([a-zA-Z]|<)"
        thetext = re.sub(search_string, r"\1" + "\n" + r"\2", thetext)

    for lip_tag in component.nestable_tags:
        for n in range(component.lipcounter[lip_tag]):
            thetext = postprocess.add_space_within(lip_tag + str(n), thetext)

    for tag in component.document_global_structure:
        thetext = postprocess.add_space_within(tag, thetext)
    for tag in component.document_sectioning:
        thetext = postprocess.add_space_within(tag, thetext)
    for tag in component.document_environments:
        thetext = postprocess.add_space_within(tag, thetext)
    for tag in component.document_components:
        thetext = postprocess.add_space_within(tag, thetext)
    for tag in component.list_like:
        thetext = postprocess.add_space_within(tag, thetext)
    for tag in component.math_display:
        thetext = postprocess.add_space_within(tag, thetext)

    # since cd is in document_pieces, it does not get spaces inside.
    # but a cline inside a cd should get spaces in front of it
    thetext = re.sub("<cline>", "  <cline>", thetext)

    thetext = postprocess.add_space_within("cell", thetext)

    # now put back the li and p
    for lip_tag in component.nestable_tags:
        for n in range(component.lipcounter[lip_tag]):
            thetext = re.sub(r"<" + lip_tag + str(n) + r"( |>)", "<" + lip_tag + r"\1", thetext)
            thetext = re.sub(r"</" + lip_tag + str(n) + ">", "</" + lip_tag + ">", thetext)

    # special case of p inside li
    thetext = re.sub(r"(<li>\n)\n( *<p>)", r"\1\2", thetext)
    thetext = re.sub(r"(</p>\n)\n( *</li>)", r"\1\2", thetext)

    # no blank line after ul or before /ul
    thetext = re.sub(r"(<(ul|ol|dl)(>| [^>]+>)\n)\n", r"\1", thetext)
    thetext = re.sub(r"\n(\n *</(ul|ol|dl)>)", r"\1", thetext)

    # special case of punctuation after a closing display math tag
    thetext = re.sub(r"(</(me|men)>)\s*((\?|!|;|:|,|\.)+) *?", r"\1\3", thetext)
    # and punctuation after /line
    thetext = re.sub(r"(</line>)\s*((\?|!|;|:|,|\.|\)|</)+) *?", r"\1\2", thetext)

#    print thetext
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

def text_to_p_ul_ol(the_statement, the_answer_variables, wrapper):

    the_statement = the_statement.strip()
#    if the_statement.startswith("a)"):
#        print "found it:", the_statement
    the_statement_p = the_statement.split("\n")
#    else:
#        the_statement_p = the_statement.split("\n\n")
    current_par = ""
    previous_par = ""
    ulol_mode = ""
    in_list = False
    the_statement_p_mbx = []
    for par in the_statement_p:
     #   print "THIS par", par
        par = par.strip()
        if not par:
            if current_par == "p":
                the_statement_p_mbx[-1] += "</p>"
                current_par = ""
                previous_par = ""
            elif current_par == "li":
                the_statement_p_mbx[-1] += "</p></li>\n"
      #          the_statement_p_mbx[-1] += "</" + ulol_mode + ">\n"
                current_par = ""
                previous_par = "li"
              #  the_statement_p_mbx[-1] += "\n</ul>\n</p>"
               # the_statement_p_mbx[-1] += "\n</" + ulol_mode + ">\n</p>"
             #   pass  # because we don't know yet if the ol/ul has finished
            continue

        elif par.startswith("* "):
            ulol_mode = "ul"
            in_list = True
            par = "<li><p>" + par[2:].strip() 
            if current_par == "p":
                par = "</p>" + "<p>\n<ul>" + "\n" + par
                current_par = "li"
                previous_par = "p"
            elif current_par == "li":
                par = "</p>\n</li>" + "\n" + par
                current_par = "li"
                previous_par = "li"
            elif previous_par != "li":
                par =  '<p>\n<ul>' + '\n' + par
                current_par = "li"
                previous_par = ""
            else:
                current_par = "li"

        elif par[1] == ")":   # as in    a) .... or b)..., for a list
            ulol_mode = "ol"
            in_list = True
            par = "<li><p>" + par[2:].strip() # + "</p></li>"
            if current_par == "p":
                par = '</p>' + '<p>\n<ol label="a">' + '\n' + par
                current_par = "li"
                previous_par = "p"
            elif current_par == "li":
                par = "</p>\n</li>" + "\n" + par
                current_par = "li"
                previous_par = "li"
            elif previous_par != "li":
                par =  '<p>\n<ol label="a">' + '\n' + par
                current_par = "li"
                previous_par = ""
            else:
                current_par = "li"

        elif current_par == "p":  # this line is a continuation of the previous paragraph
            pass # do nothing, because we are just processing another ine in the current paragraph
     #       par = "</p>\n<p>" + par
        elif current_par == "li":
            pass
        else: # starting a new p?
            par = "<p>" + par
            if previous_par == "li":  # then end the previous list
                par = "\n</" + ulol_mode + ">\n</p>" + par
            current_par = "p"
            previous_par = ""
       
        the_statement_p_mbx.append(par)

    if current_par == "li":   # unfinished list to be completed
        the_statement_p_mbx[-1] += "\n</p></li>\n</" + ulol_mode + ">\n</p>"
    elif current_par == "p":
        the_statement_p_mbx[-1] += "</p>" + "\n"

    the_statement_mbx = "<" + wrapper + ">" + "\n"
    the_statement_mbx += "\n".join(the_statement_p_mbx)
    the_statement_mbx += "\n</" + wrapper + ">" + "\n"
  
    return the_statement_mbx

