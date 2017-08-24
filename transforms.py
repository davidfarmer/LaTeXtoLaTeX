
import re

import utilities
import component
import postprocess
import myoperations
import mapping


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

#    # first a hack to handle 2-level lists.
#    thetext = re.sub(r"<li>\s*<p>", "<lip>", thetext)
#    thetext = re.sub(r"</p>\s*</li>", "</lip>", thetext)
    
    # sort-of a hack to handle tags that can occur withing themselves (like li and p)
    # (does not handle the case of opening tag with parameters)
    for lip_tag in ["li", "p"]:
        component.lipcounter[lip_tag] = 0
        this_tag_start = "<" + lip_tag + ">"
        this_tag_end = "</" + lip_tag + ">"
        the_search_string = this_tag_start + "(.*?)" + this_tag_end
        component.something_changed = True
        while component.something_changed:
            component.something_changed = False
            thetext = re.sub(the_search_string, lambda match: liprename(match, lip_tag), thetext, 0, re.DOTALL)

#    print "found", component.lipcounter, "li/p pairs"
        for n in range(component.lipcounter[lip_tag]):
            if lip_tag == "li":
                thetext = postprocess.tag_before_after(lip_tag + str(n), "\n\n", "", "", "\n\n", thetext)
            else:
                thetext = postprocess.tag_before_after(lip_tag + str(n), "\n\n", "\n", "\n", "\n\n", thetext)
        thetext = postprocess.tag_before_after(lip_tag, "\n\n", "\n", "\n", "\n\n", thetext)

    # first remove extraneous spaces and put in appropriate carriage returns

#    thetext = postprocess.tag_before_after("p", "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("row|tabular|image|latex-image-code|asymptote", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("me|men|md|mdn", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("exercises|exercisegroup|exercise", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("webwork|setup|set|pg-code|pg-macros", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("mrow|intertext", "\n", "", "", "\n", thetext)
    thetext = postprocess.tag_before_after("dt", "\n\n", "", "", "\n", thetext)
    thetext = postprocess.tag_before_after("dd", "\n", "", "", "\n\n", thetext)

    thetext = postprocess.tag_before_after("sage", "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("input", "\n", "", "", "\n", thetext)
    thetext = postprocess.tag_before_after("output", "\n", "", "", "\n", thetext)

    thetext = postprocess.tag_before_after("fn", "", "", "", "", thetext)

#    thetext = postprocess.tag_before_after("li", "\n\n", "", "", "\n\n", thetext)
    thetext = postprocess.tag_before_after("ul|ol|dl", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("theorem|proposition|lemma|conjecture|corollary",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("algorithm",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("objectives",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("definition|axiom|example|insight|exploration|activity|remark|warning|proof",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("problem", "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("figure|table",
                                           "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("paragraphs|sidebyside|aside", "\n\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("introduction|statement|solution|answer|hint|objectives|task", "\n", "\n", "\n", "\n", thetext)
    thetext = postprocess.tag_before_after("subsection", "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("chapter|section", "\n\n", "\n", "\n", "\n\n", thetext)
    thetext = postprocess.tag_before_after("title|cell|caption", "\n", "", "", "\n", thetext)

# now shove everything else to the left
# need to be more clever, because sometimes the author spacing should be preserved
###########    thetext = re.sub("\n +", "\n", thetext)

    for lip_tag in ["li", "p"]:
        for n in range(component.lipcounter[lip_tag]):
            thetext = postprocess.add_space_within(lip_tag + str(n), thetext)
      #      thetext = postprocess.add_space_within(lip_tag + str(n), thetext)  # twice, because we will separate into li and p

    thetext = postprocess.add_space_within("chapter", thetext)
    thetext = postprocess.add_space_within("section", thetext)
    thetext = postprocess.add_space_within("subsection", thetext)
    thetext = postprocess.add_space_within("introduction", thetext)
    thetext = postprocess.add_space_within("objectives", thetext)
    thetext = postprocess.add_space_within("figure", thetext)
    thetext = postprocess.add_space_within("image", thetext)
    thetext = postprocess.add_space_within("sage", thetext)
    thetext = postprocess.add_space_within("asymptote", thetext)
    thetext = postprocess.add_space_within("sidebyside", thetext)
    thetext = postprocess.add_space_within("aside", thetext)
    thetext = postprocess.add_space_within("latex-image-code", thetext)
    for tag in ["theorem", "definition", "axiom", "proposition", "lemma", "conjecture", "corollary"]:
        thetext = postprocess.add_space_within(tag, thetext)
    for tag in ["example", "insight", "exploration", "activity", "remark", "warning", "algorithm", "objectives"]:
        thetext = postprocess.add_space_within(tag, thetext)
    thetext = postprocess.add_space_within("task", thetext)
    thetext = postprocess.add_space_within("statement|solution|answer|hint|proof", thetext)
#    thetext = postprocess.add_space_within("p", thetext)
    thetext = postprocess.add_space_within("paragraphs", thetext)
    thetext = postprocess.add_space_within("ul", thetext)
    thetext = postprocess.add_space_within("ol", thetext)
    thetext = postprocess.add_space_within("dl", thetext)
#    thetext = postprocess.add_space_within("li", thetext)
    thetext = postprocess.add_space_within("me|men|md|mdn", thetext)
    thetext = postprocess.add_space_within("exercises", thetext)
    thetext = postprocess.add_space_within("exercisegroup", thetext)
    thetext = postprocess.add_space_within("exercise", thetext)
    thetext = postprocess.add_space_within("problem", thetext)
    thetext = postprocess.add_space_within("webwork", thetext)
    thetext = postprocess.add_space_within("setup", thetext)
 #   thetext = postprocess.add_space_within("var", thetext)
    thetext = postprocess.add_space_within("set", thetext)
    thetext = postprocess.add_space_within("pg-code", thetext)
    thetext = postprocess.add_space_within("pg-macros", thetext)
    thetext = postprocess.add_space_within("table", thetext)
    thetext = postprocess.add_space_within("tabular", thetext)
    thetext = postprocess.add_space_within("row", thetext)
    thetext = postprocess.add_space_within("pre", thetext)

    # now put back the li and p
    for lip_tag in ["li", "p"]:
        for n in range(component.lipcounter[lip_tag]):
   #     thetext = re.sub(r"(\n *)<" + lip_tag + str(n) + ">",r"\1<" + lip_tag + ">", thetext)
   #     thetext = re.sub(r"(\n *)</" + lip_tag + str(n) + ">",r"\1</" + lip_tag + ">", thetext)
            thetext = re.sub(r"<" + lip_tag + str(n) + ">", "<" + lip_tag + ">", thetext)
            thetext = re.sub(r"</" + lip_tag + str(n) + ">", "</" + lip_tag + ">", thetext)
#    # for some reason there can be extra </lip>.  Not sure why.
#    thetext = re.sub(r"(\n *)</lip>",r"\1  </p>\1</li>", thetext)

    # special case of p inside li
    thetext = re.sub(r"(<li>\n)\n( *<p>)", r"\1\2", thetext)
    thetext = re.sub(r"(</p>\n)\n( *</li>)", r"\1\2", thetext)

    return thetext

##################

def liprename(txt, tag="lip"):

    the_inside = txt.group(1)

    component.something_changed = True
    current_counter = component.lipcounter[tag]
    component.lipcounter[tag] += 1

    the_tag = "<" + tag + ">"
    the_ta = "<" + tag 
    the_ag = "</" + tag 

    if the_tag in the_inside:  # replace the last <lip> by <lipN>
        the_inside_start, the_inside_end = the_inside.rsplit(the_tag, 1)
        the_inside = the_inside_start + the_ta + str(current_counter) + ">" + the_inside_end
        return the_tag + the_inside + the_ag + str(current_counter) + ">"
    else:
        return the_ta + str(current_counter) + ">" + the_inside + the_ag + str(current_counter) + ">"

#    if "<lip>" in the_inside:  # replace the last <lip> by <lipN>
#        the_inside_start, the_inside_end = the_inside.rsplit("<lip>", 1)
#        the_inside = the_inside_start + "<lip" + str(current_counter) + ">" + the_inside_end
#        return "<lip>" + the_inside + "</lip" + str(current_counter) + ">"
#    else:
#        return "<lip" + str(current_counter) + ">" + the_inside + "</lip" + str(current_counter) + ">"

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

def pgtombx(text):

    thetext = text

    component.supplementary_variable_counter = 0
    component.supplementary_variables = {}
    component.the_answers = []
    thetext = myoperations.pgpreprocess(thetext)
# to do:
# HINTs
# multiple solutions: BasicAlgebra/SystemsOfLinearEquations/SystemEquation40.pg

    ERROR_MESSAGE = ""

    # find the defined variables, for later interpreting [________]{$var}
    predefined_variables = re.findall(r"(\$[a-zA-Z0-9_]+\s*=\s*\$[a-zA-Z0-9_]+)\s*->\s*cmp", thetext)
    # print "predefined_variables", predefined_variables
    for varpair in predefined_variables:
        var, evaluator = varpair.split("=")
        var = var.strip()
        evaluator = evaluator.strip()
        component.defined_variables[var] = evaluator
    # need to do the same for PopUp and RadioButtons

    # extract the metadata
    the_metadata, everything_else = thetext.split("\nDOCUMENT();")

    the_metadata = re.sub("#{5,}", "", the_metadata)
    the_metadata = the_metadata.strip()

    the_metadata = utilities.magic_character_convert(the_metadata, "text")

    # extract the macros
    the_macros = re.sub("#{5,}.*", "", everything_else, 0, re.DOTALL)
    everything_else = re.sub(".*?#{5,}", "", everything_else, 1, re.DOTALL)

    the_macros_mbx = myoperations.wwmacros(the_macros)

    # kill commented out lines that are not in the metadata section.
    everything_else = re.sub("\n#.*", "", everything_else)

    # find the ANSwers and save them in component.the_answers
    while "ANS(" in everything_else:
        everything_else = re.sub(r"ANS\((.*)", myoperations.extract_ans, everything_else, 1, re.DOTALL)
 #   re_ANS = "\nANS\((.*?)\);"  # wrong: could be complicated, so use first bracketed string
 #   the_answers = re.findall(re_ANS, everything_else, re.DOTALL)
 #   the_answers = [answer.strip() for answer in the_answers]
    try:
        the_answer_variables = [re.search(r"(\$[a-zA-Z0-9_]+)", answer).group(1) for answer in component.the_answers]
    except AttributeError:
        print "no variables in", component.the_answers

 #   everything_else = re.sub(re_ANS, "", everything_else, 0, re.DOTALL)
    the_answer_mbx = ""
    for answer in component.the_answers:
        answer = utilities.magic_character_convert(answer, "code")
        the_answer_mbx += "$ansevaluator = " + answer + ";\n"

    # extract the problem statement
#    re_statement = "BEGIN_PGML\s(.*)END_PGML\n"
    re_statement = r"BEGIN_(PGML|TEXT)\s(.*?)END_\1" + "\n"
    the_statement = ""
    try:
        the_statement_parts = re.findall(re_statement, everything_else, re.DOTALL)
        everything_else = re.sub(re_statement, "", everything_else, 0, re.DOTALL)
        for part in the_statement_parts:
            this_part = part[1]
 #           this_part = re.sub(" *\$PAR *\n", "", this_part)
            # here is where to convert DataTable, as in AdditionSubtractionApplications30
            the_statement += this_part
   #     the_statement = re.search(re_statement, everything_else, re.DOTALL).group(1)
   #     everything_else = re.sub(re_statement, "", everything_else, 0, re.DOTALL)
   #     print "the_statement is", the_statement[:30]
    except AttributeError:
        the_statement = "STATEMENT_NOT_PARSED_CORRECTLY"
        ERROR_MESSAGE += "ERROR: file does not contain a statement\n"
        print "file does not contain a statement"
        print the_statement_parts

            # extract the variables in the statement
    vars_in_statement = re.findall(r"(\$[a-zA-Z0-9_]+)", the_statement)
    vars_in_statement = list(set(vars_in_statement))  # remove duplicates
    vars_in_statement.sort()

    the_statement_p = text_to_p_ul_ol(the_statement, the_answer_variables, "statement")
    the_statement_mbx = myoperations.pgmarkup_to_mbx(the_statement_p, the_answer_variables)

    # extract the solution
    re_solution = "BEGIN_PGML_SOLUTION(.*)END_PGML_SOLUTION"
    try:
        the_solution = re.search(re_solution, everything_else, re.DOTALL).group(1)
        everything_else = re.sub(re_solution, "", everything_else, 0, re.DOTALL)
    except AttributeError:
        re_solution = "BEGIN_SOLUTION(.*)END_SOLUTION"
        try:
            the_solution = re.search(re_solution, everything_else, re.DOTALL).group(1)
     #       the_solution = re.sub(" *\$PAR *\n", "", the_solution)
            everything_else = re.sub(re_solution, "", everything_else, 0, re.DOTALL)

        except AttributeError:
            the_solution = "SOLUTION_NOT_PARSED_CORRECTLY"
            ERROR_MESSAGE += "ERROR: file does not contain a solution\n"
            print "file does not contain a solution\n"

    the_solution = the_solution.strip()

    if "BEGIN_HINT" in everything_else:
        ERROR_MESSAGE += "ERROR: HINTs not implemented properly\n"
        print "file contains non-PGML HINTs, which are not implemented yet"
    if "BEGIN_TEXT" in everything_else:
        ERROR_MESSAGE += "ERROR: TEXT not implemented properly\n"
        print "file contains non-PGML TEXT, which is not implemented yet"
    if "BEGIN_SOLUTION" in everything_else:
        ERROR_MESSAGE += "ERROR: SOLUTION not implemented properly\n"
        print "file contains non-PGML SOLUTION, which is not implemented yet"

        # extract the variables in the solution
    vars_in_solution = re.findall(r"(\$[a-zA-Z0-9_]+)", the_solution)
#    print "vars2: ", vars_in_solution
    vars_in_solution = list(set(vars_in_solution))  # remove duplicates
#    print "vars: ", vars_in_solution

    the_solution_mbx = myoperations.pgmarkup_to_mbx(the_solution, the_answer_variables)
    the_solution_mbx = text_to_p_ul_ol(the_solution_mbx, the_answer_variables, "solution")

    #throw away things that are not needed in the mbx version
    things_to_throw_away = [
           r"TEXT\(beginproblem\(\)\);",
           r"ENDDOCUMENT\(\);",
           r"#{5,}"
           ]
    for junk in things_to_throw_away:
        everything_else = re.sub("\s*" + junk + "\s*", "\n", everything_else)

    for str in mapping.pg_macro_files:
        if str in everything_else:
            if mapping.pg_macro_files[str] not in component.extra_macros:
                component.extra_macros.append(mapping.pg_macro_files[str])

    everything_else = utilities.magic_character_convert(everything_else, "text")

    all_vars = list(set(vars_in_statement + vars_in_solution))
    all_vars.sort()

    the_pgcode_mbx = "<pg-code>" + "\n"
    the_pgcode_mbx += everything_else.strip()
    the_pgcode_mbx += "\n\n" + the_answer_mbx
    the_pgcode_mbx += "if($envir{problemSeed}==10) {\n"
    for var in all_vars:
        the_pgcode_mbx += "  " + var + "=1;" + "\n"
    for pre_var in component.supplementary_variables:
        new_var = component.supplementary_variables[pre_var]
        the_pgcode_mbx += "  " + new_var + "=" + pre_var + "1;" + "\n"
    the_pgcode_mbx += "}\n"
    the_pgcode_mbx += "\n" + "</pg-code>" + "\n"

    the_setup_mbx = "<setup>" + "\n"
    for var in all_vars:
        the_setup_mbx += '<var name="' + var + '">' + "\n"
        the_setup_mbx += '  <static></static>' + "\n"
        the_setup_mbx += '</var>' + "\n"
    for pre_var in component.supplementary_variables:
        new_var = component.supplementary_variables[pre_var]
        the_setup_mbx += '<var name="' + new_var + '">' + "\n"
        the_setup_mbx += '  <static>' + pre_var + '</static>' + "\n"
        the_setup_mbx += '</var>' + "\n"

    the_setup_mbx += the_pgcode_mbx
    the_setup_mbx += "</setup>" + "\n"
#    print the_macros_mbx
#    print the_statement_mbx
#    print the_answer_mbx
#    print the_solution_mbx
#    print the_setup_mbx

#    print "----------------"
#    print everything_else
#    print "----------------"

 #   the_output = ERROR_MESSAGE
    the_output = ""
    the_output += '<?xml version="1.0" encoding="UTF-8" ?>' + "\n"
    the_output += "\n" + "<exercise>" + "\n"
    the_output += "<original-metadata>" + "\n"
    the_output += "<original-file>" + component.inputstub + "</original-file>" + "\n"
    the_output += the_metadata
    the_output += "\n" + "</original-metadata>" + "\n"
    the_output += "\n"
    the_output += '<webwork seed="1">' + "\n"
    the_output += the_macros_mbx
    the_output += "\n"
    the_output += the_setup_mbx
    the_output += "\n"
    the_output += the_statement_mbx
    the_output += "\n"
    the_output += the_solution_mbx
    the_output += "\n" + "</webwork>" + "\n"
    the_output += "</exercise>" + "\n"

    component.indentamount = "    "
    the_output = mbx_pp(the_output)

    return the_output

#######################

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

