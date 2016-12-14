
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
    thejavascript += 'var dataurlbase = "http://books.aimath.org/' + component.bookidentifier + '/bbbb?";\n'

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

def new_sage_counter(txt, acro,new_counter):

    text = txt.group(1)

    component.something_changed = True

    new_text = text + acro + "-" + str(new_counter) + '"'

    return new_text
