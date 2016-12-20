
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

def add_utmost_tracking(text):

    the_text = text

    # javascript at end
    thejavascript = """
<script>
var topsection = document.getElementsByTagName('section')[0];
var thefocus = topsection.id;

var recenthistory = '';

var onpage = false;
var timecounter = 0;
"""
    thejavascript += 'var dataurlbase = "http://books.aimath.org/' + component.bookidentifier + '/cccc?";\n'

    thejavascript += 'dataurlbase = dataurlbase.concat("' + component.bookidentifier + '").concat("&");\n'
#dataurlbase = dataurlbase.concat("book=aata").concat("&");

    thejavascript += """
function timeTracker() {
  if (onpage) {
    timecounter++;
    recenthistory = recenthistory.concat(thefocus).concat('.');
    if (timecounter % 10 == 0) {
        dataurl = dataurlbase.concat(recenthistory.slice(0, -1));  //trailing "."
        $.get(dataurl);
        recenthistory = '';
    }
  }
}

theTimer = setInterval(timeTracker, 1000);

$('body').focusout(function() {
    onpage = false;
    if (recenthistory != '') {
      dataurl = dataurlbase.concat(recenthistory.slice(0, -1));  //trailing "."
      $.get(dataurl);
      recenthistory = '';
    }
    timecounter = 0;
});
$('body').focusin(function() {
    onpage = true;
});
</script>

<script>
// the hidden proof knowls have knowl="", which is like the a does not have knowl as an attribute
$('a').on('click', function() {
  if(this.classList.contains('active')) {
    thefocus = this.closest('section').id;
  } else if ($(this).attr("knowl")) {
           if($(this).attr("id")) {
             thefocus = this.id
           }
           else if (kid = this.getAttribute('knowl-id')) {
                  thefocus = kid
                }
           else {
                  thefocus = 'Unknown'
           }
    } else if ($(this).attr("id")) {
             thefocus = this.id;
  };
  recenthistory = recenthistory.concat('click-').concat(thefocus).concat('.');
});
</script>

<script>
setTimeout(function(){
    $('body').attr('tabindex',-1).focus()},
100);
</script>

<script>
// instead of waiting 2 seconds, it would be better to trigger on sage cell completing setup
setTimeout(function(){
  var allbuttons = document.getElementsByTagName('button');
  $('button.sagecell_evalButton').on('click', function() {
     article_id = this.closest('div.sagecell-sage').id;
     thefocus = article_id;
     recenthistory = recenthistory.concat('click-').concat(article_id).concat('.');
     });
},
2000);
</script>
"""

#    # add assistive link
#    the_text = re.sub(r"(<body[^>]*>)\s*",
#                   r'\1' + '\n<a class="assistive" href="#content">Skip to main content</a>\n', the_text)

    the_text = re.sub("</body>", thejavascript + "</body>", the_text)

#    counterdisplay = '\n' + '<p id="sagecounter" style="font-size: 80%;"></p>\n<p id="countertimer" style="font-size: 70%;"></p>\n'
    counterdisplay = ""

#    # temporary location for the counters
#    if '<section class="chapter"' in the_text:
#        the_text = re.sub(r'(permalink</a>\s*</h1></header>)',
#                           r'\1' + counterdisplay, the_text)
#    else:
#        the_text = re.sub(r'(<div id="content"[^>]+>\s*<section class="section"[^>]+>)',
#                            r'\1' + counterdisplay, the_text)

    knowlcounter = 1
    while 'knowl-id="' in the_text:
        the_text = re.sub('knowl-id="([^"]+)"',
                          r'id="\1' + "-" + str(knowlcounter) + '" ' + r'knowlid="\1"',
                          the_text, 1)
        knowlcounter += 1

    the_text = re.sub('knowlid', 'knowl-id', the_text)

    # rearrange the buttons
# only needed for "old style" buttons
#    the_text = re.sub(r'(<a class="previous-button toolbar-item button" href="[^"]+">Prev</a>)(<a class="up-button button toolbar-item" href="[^"]+">Up</a>)(<a class="next-button button toolbar-item" href="[^"]+">Next</a>)',
#                    r'\3\2\1', the_text)

    return the_text

################

def make_better_ids(text):

    thetext = text

    # add ids to those that have none
    for tag in ["ol", "ul", "dl"]:
        thetext = re.sub(r'<' + tag + r'\b', lambda match: rename_sequentially_according_to(tag, tag, "", "", match), thetext)

    thetext = re.sub(r'<li>', lambda match: rename_sequentially_according_to("li", "li", "", ">", match), thetext)

    # very crude way to make better ids for things like id="subsection-89"
    try:
        this_section_id = re.search(r'<section class="section" id="([^"]+)"', thetext).group(1)
        component.tag_number["subsection"] = 1
        for n in range(20):
            thetext = re.sub(r'(<section class="subsection" id="subsection)-[0-9]+"',           
                             r'\1' + '-' + str(component.tag_number["subsection"]) + '-' + this_section_id + '"', thetext, 1)
            component.tag_number["subsection"] += 1

        component.tag_number["theorem"] = 1
        for n in range(20):
            thetext = re.sub(r'(<article class="theorem-like" id="theorem)-[0-9]+"',
                             r'\1' + '-' + str(component.tag_number["theorem"]) + '-' + this_section_id + '"', thetext, 1)
  # nasty python issue: r'\1' + '0' looks for the 10th captured group, hence the "-" not in \1
            component.tag_number["theorem"] += 1
        component.tag_number["proposition"] = 1
        for n in range(20):
            thetext = re.sub(r'(<article class="theorem-like" id="proposition)-[0-9]+"',
                             r'\1' + '-' + str(component.tag_number["proposition"]) + '-' + this_section_id + '"', thetext, 1)
            component.tag_number["proposition"] += 1


        component.tag_number["sage"] = 1
        for n in range(20):
            thetext = re.sub(r'(<div class="sagecell-sage" id="sage)-[0-9]+"',
                             r'\1' + '-' + str(component.tag_number["sage"]) + '-' + this_section_id + '"', thetext, 1)
            component.tag_number["sage"] += 1

    except AttributeError:
        print "file with no section id"

# sloppy: combine with the above
      
    try:
        this_section_id = re.search(r'<section class="exercises" id="([^"]+)"', thetext).group(1)

        component.tag_number["sage"] = 1
        for n in range(20):
            thetext = re.sub(r'(<div class="sagecell-sage" id="sage)-[0-9]+"',
                             r'\1' + '-' + str(component.tag_number["sage"]) + '-' + this_section_id + '"', thetext, 1)
            component.tag_number["sage"] += 1
    except AttributeError:
        print "file with no section id"

# need to rename proof ids and sage-365


    # since exercises/exercisegroups can have introductions,
    # rename them bfore renaming the introductions
    thetext = re.sub('(<section class="exercises" id="(readingquestions-[^"]+)">.*?</section>)',
                     renameexercisegroup_intro, thetext, 1, re.DOTALL)
    thetext = re.sub('(<section class="exercises" id="(exercises-[^"]+)">.*?</section>)',
                     renameexercisegroup_intro, thetext, 1, re.DOTALL)

    thetext = re.sub("IDIDID", "id", thetext)

    # hack to partially deal with nested sections: XXSECTION
    thetext = re.sub(r'(<section)( class="introduction" id="([^"]+)")(.*?)(</section>)',
                        lambda match: rename_exercises(match, new_start="<XXSECTION", new_end="</XXSECTION>"), thetext, 0, re.DOTALL)
    thetext = re.sub(r'(<section)( class="exercises" id="(readingquestions-[^"]+)")(.*?)(</section>)',
                        lambda match: rename_exercises(match, new_start="<XXSECTION", new_end="</XXSECTION>"), thetext, 0, re.DOTALL)
    thetext = re.sub(r'(<section)( class="exercises" id="([^"]+)")(.*?)(</section>)',
                        lambda match: rename_exercises(match, new_start="<XXSECTION", new_end="</XXSECTION>"), thetext, 0, re.DOTALL)
    thetext = re.sub(r'XXSECTION', 'section', thetext)


    component.something_changed = True
    while component.something_changed:
        component.something_changed = False
        thetext = re.sub(r'(.{1000})(<section class="introduction") id="introduction-([0-9]+)"', renamesectionintro, thetext, 1, re.DOTALL)
    component.something_changed = True
    while component.something_changed:
        component.something_changed = False
        thetext = re.sub(r'(.{1000})(<article class="introduction") id="introduction-([0-9]+)"', renamesectionintro, thetext, 1, re.DOTALL)

    thetext = re.sub("IDIDID", "id", thetext)

# rename proof ids

    separated_by_theorems = thetext.split('<article class="theorem-like" id="')

    the_text_revised = separated_by_theorems.pop(0)
    print "number of theorems:", len(separated_by_theorems)
    for this_segment in separated_by_theorems:
        the_text_revised  += '<article class="theorem-like" id="'
        the_proofs = re.findall('id="proof-', this_segment)
        print "----------",this_segment[:10]
        if len(the_proofs) == 1:
            theorem_id = re.sub('".*', "", this_segment, 1, re.DOTALL) 
            print "theorem_id", theorem_id
            this_segment = re.sub('(id="proof)-[0-9]+"', r'\1' + '-1-' + theorem_id + '"', this_segment)
        the_text_revised += this_segment

    thetext = the_text_revised

    # re-id ol/ul/dl in articles
    for tag in ["ol", "ul", "dl"]:
        thetext = re.sub(r'(<article class="[^"]+" id="([^"]+)")(.*?)(</article>)', lambda match: rename_children_of(tag, match), thetext, 0, re.DOTALL)
    # and in sections
    for s in ["subsub", "sub", ""]:
        for tag in ["ol", "ul", "dl"]:
            thetext = re.sub(r'(<section class="' + s + '[^"]+" id="([^"]+)")(.*?)(</section>)', lambda match: rename_children_of(tag, match), thetext, 0, re.DOTALL)
    # re-id paragraphs
    thetext = re.sub(r'(<dl id="([^"]+)")(.*?)(</dl>)', lambda match: rename_children_of("p", match), thetext, 0, re.DOTALL)
    thetext = re.sub(r'(<article class="[^"]+" id="([^"]+)")(.*?)(</article>)', lambda match: rename_children_of("p", match), thetext, 0, re.DOTALL)
    # don't use the 'hk-' par of hidden knowl ids.
    # possible problem with nested divs
    thetext = re.sub(r'(<div id="hk-([^"]+)")(.*?)(</div>)', lambda match: rename_children_of("p", match), thetext, 0, re.DOTALL)
    for s in ["intro", "subsub", "sub", ""]:
        thetext = re.sub(r'(<section class="' + s + '[^"]+" id="([^"]+)")(.*?)(</section>)', lambda match: rename_children_of("p", match), thetext, 0, re.DOTALL)

    thetext = re.sub(r'(<ol id="([^"]+)")(.*?)(</ol>)', lambda match: rename_children_of("li", match), thetext, 0, re.DOTALL)

    
    return thetext

#################

def rename_exercises(txt, new_start="", new_end=""):

    the_start_part1 = txt.group(1)
    if new_start:
        the_start_part1 = new_start
    the_start = the_start_part1 + txt.group(2)
    the_parent_id = txt.group(3)
    the_middle = txt.group(4)
    the_end = txt.group(5)
    if new_end:
        the_end = new_end

    tag = 'article class="exercise-like"'
    component.tag_number[tag] = 1

    the_middle = re.sub(r'<article class="exercise-like"' + ' id="exercise-[0-9]+"', 
                           lambda match: rename_sequentially_according_to(tag, "exercise", the_parent_id, "", match), the_middle)

    print "matched", component.tag_number[tag], tag + "s"

    return the_start + the_middle + the_end

#################

def rename_children_of(tag, txt):

    the_start = txt.group(1)
    the_parent_id = txt.group(2)
    the_middle = txt.group(3)
    the_end = txt.group(4)

#    print "matched", component.tag_number["p"], "paragraphs"
    component.tag_number[tag] = 1
    the_middle = re.sub(r'<' + tag + ' id="' + tag + '-[0-9]+"', lambda match: rename_sequentially_according_to(tag, tag, the_parent_id, "", match), the_middle)

#    print "matched", component.tag_number[tag], tag + "s"

    return the_start + the_middle + the_end

#################

def rename_sequentially_according_to(the_tag, new_id_start, the_parent_id, text_after, txt):

    new_tag_id = new_id_start + '-' + str(component.tag_number[the_tag])
    if the_parent_id:
        new_tag_id += '-' + the_parent_id

    component.tag_number[the_tag] += 1

    return '<' + the_tag + ' id="' + new_tag_id + '"' + text_after

#################

def renameexercisegroup_intro(txt):

    the_text = txt.group(1)
    the_parent_id = txt.group(2)

    exercisecounter = 1
    while r'<div class="exercisegroup" id="exercisegroup-' in the_text:
        the_text = re.sub(r'<div class="exercisegroup" id="exercisegroup-[0-9]+">',
                          '<div class="exercisegroup" IDIDID="exercisegroup-' + str(exercisecounter) + '-' + the_parent_id + '">',
                          the_text, 1)
        exercisecounter += 1

    return the_text

#################

def renamesectionintro(txt):

    text_before = txt.group(1)
    intro_start = txt.group(2)
    old_number = txt.group(3)

    print "found old_number", old_number, "in", intro_start

#    print "looking for section id in ", text_before[-400:]
#    findparentsection = r'<section class="appendix" id="(appendix-A)"'
#    findparentsection = r'<section class="appendix" id="(appendix-[^"]+)"'
    try:
        findparentsection = r'<section class="(section|exercises|appendix|chapter|conclusion)" id="([^"]+)"'
        theparent = re.search(findparentsection,text_before).group(2)
    except AttributeError:
        findparentobject = r'<div class="(exercisegroup)" id="([^"]+)"'
        theparent = re.search(findparentobject,text_before).group(2)

    component.something_changed = True
    print "found theparent", theparent

    revised_text = text_before + intro_start + ' IDIDID="introduction-' + theparent + '"'

    return revised_text
