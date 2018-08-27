
filetype_plus = ""
inputname = ""
outputname = ""

indent_num = 2
indentamount = indent_num*" "

iofilepairs = []
filestubs = []

error_messages = []
replaced_macros = []
defined_variables = {}
supplementary_variable_counter = 0
supplementary_variable_stub = "$tMvR"
supplementary_variables = {}

the_answers = []

ids = []

something_changed = False

substitution_counter = 0
generic_counter = 0

extra_macros = []

lipcounter = {}

sha1of = {}

# list these tags in order of importance/containment
document_global_structure = [
    'pretext', 'mathbook', 'book', 'part', 'article', 
    'docinfo', 'macros', 'latex-preamble', 'latex-image-preamble',
    'html', 'search', 'google', 'feedback', 'index',
    'frontmatter', 'backmatter', 
    'appendix', 'solutions', 'references',
    'titlepage', 'preface', 'abstract', 'colophon', 'shortlicense',
    'acknowledgement', 'credit', 'website', 'copyright',
    'author', 'institution','contributor', 'contributors' ]

document_sectioning = ['chapter', 'section', 'subsection', 'subsubsection',
                       'technology', 'worksheet',
                       'objectives', 'outcomes', 'paragraphs', 'task',
                       'sidebyside',
                       'introduction', 'conclusion', 'assemblage',
                       'prelude', 'postlude']

document_environments = ['proof',
                         'project',
                         'theorem', 'proposition', 'lemma', 'conjecture', 'corollary',
                         'definition', 'axiom', 'example', 'insight', 'exploration',
                         'problem', 'exercise', 'note', 'blockquote',
                         'activity', 'remark', 'warning', 'figure', 'table',
                         'subtask', 'notation', 'claim', 'biblio']


document_components = ['exercises', 'exercisegroup',
                       'statement', 'solution', 'answer', 'hint', 'case', 'aside']

document_pieces = ['title', 'cell', 'caption',
                   'address',
                   'personname', 'date', 'email', 'department', 'line',
                   'usage', 'description', 'journal', 'volume', 'number',
                   'mrow', 'inertext',
                   'webwork', 'setup', 'set', 'pg-code', 'pg-macros']

list_like = ['ol', 'ul', 'dl']

math_display = ['me', 'men', 'md', 'mdn']

footnote_like = ['fn']

nestable_tags = ["ul", "ol", "li", "p", "task"]

verbatim_tags = ['latex-image-preamble', 'latex-image',
                 'slate', 'sage', 'asymptote', 'macros']

