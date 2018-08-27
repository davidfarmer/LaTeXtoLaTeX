
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
    'acknowledgement', 'credit', 'website', 'copyright'
    'author', 'institution','contributor', 'contributors' ]

document_sectioning = ['chapter', 'section', 'subsection', 'worksheet',
                       'objectives', 'paragraphs', 'sidebyside',
                       'introduction', 'conclusion', 'assemblage']

document_environments = ['proof',
                         'theorem', 'proposition', 'lemma', 'conjecture', 'corollary',
                         'definition', 'axiom', 'example', 'insight', 'exploration',
                         'problem', 'exercise',
                         'activity', 'remark', 'warning',
                         'task', 'subtask', 'notation', 'claim', 'biblio']

document_components = ['exercises', 'exercisegroup',
                       'statement', 'solution', 'answer', 'hint', 'case', 'aside']

document_pieces = ['title', 'cell', 'caption',
                   'personname', 'date', 'email', 'department', 'line',
                   'usage', 'description', 'journal', 'volume', 'number']

verbatim_tags = ['latex-image-preamble', 'latex-image',
                 'slate', 'sage', 'asymptote', 'macros']

