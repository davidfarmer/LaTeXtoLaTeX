
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
    'docinfo', 'macros',
    'html', 'search', 'google', 'feedback', 'index',
    'frontmatter', 'backmatter', 
    'appendix', 'solutions', 'references',
    'titlepage', 'preface', 'abstract', 'colophon', 'shortlicense',
    'acknowledgement', 'credit', 'website', 'copyright',
    'author', 'institution','contributor', 'contributors' ]

document_sectioning = ['chapter', 'section', 'subsection', 'subsubsection',
                       'technology', 'worksheet',
                       'objectives', 'outcomes', 'paragraphs', 'task',
                       'sbsgroup', 'stack',
                       'introduction', 'conclusion', 'assemblage',
                       'prelude', 'postlude']

document_environments = ['proof',
                         'project',
                         'theorem', 'proposition', 'lemma', 'conjecture',
                         'corollary', 'principle',
                         'definition', 'axiom', 'example', 'insight', 'exploration',
                         'problem', 'exercise', 'question', 'note', 'blockquote',
                         'activity', 'remark', 'warning', 'table', 'tabular',
                         'listing', 'program', 'console', 'demonstration',
                         'image',
                         'subtask', 'notation', 'claim', 'biblio',
                         'poem', 'stanza']


document_components = ['exercises', 'exercisegroup', 'row', 'cd',
                       'statement', 'solution', 'answer', 'hint', 'case', 'aside']

document_pieces = ['title', 'cell', 'caption',
                   'address',
                   'personname', 'date', 'email', 'department', 'line', 'cline',
                   'usage', 'description', 'journal', 'volume', 'number',
                   'mrow', 'intertext',
                   'webwork', 'setup', 'set', 'pg-code', 'pg-macros']

# empty tags that shoudl be on their own line
document_pieces_empty = ['cell', 'col']

list_like = ['ol', 'ul', 'dl']

math_display = ['me', 'men', 'md', 'mdn']

footnote_like = ['fn']

nestable_tags = ["ul", "ol", "li", "p", "task", "figure", "sidebyside"]

verbatim_tags = ['latex-image-preamble', 'latex-image',
                 'slate', 'sage', 'sageplot', 'asymptote', 'macros',
                 'program', 'input', 'output', 'prompt', 'pre']

