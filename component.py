
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
local_counter = {}

sha1of = {}

all_permid = []

permid_base = "dmoi"
permid_base_number = 1234567
permid_base_increment = 166469888
permid_base_mod = 380204032

# list these tags in order of importance/containment
document_global_structure = [
    'pretext', 'mathbook', 'book', 'part', 'article', 
    'docinfo', 'macros',
    'html', 'search', 'google', 'feedback', 'index',
    'frontmatter', 'backmatter', 
    'appendix', 'solutions', 'references', 'biography', 'dedication',
    'titlepage', 'preface', 'abstract', 'colophon', 'shortlicense',
    'acknowledgement', 'credit', 'website', 'copyright',
    'author', 'editor', 'contributor', 'contributors' ]

document_sectioning = ['chapter', 'section', 'subsection', 'subsubsection',
                       'technology', 'worksheet',
                       'objectives', 'outcomes', 'paragraphs', 'task',
                       'sbsgroup', 'stack',
                       'introduction', 'conclusion', 'assemblage',
                       'prelude', 'postlude']

document_environments = ['proof',
                         'project',
                         'theorem', 'proposition', 'lemma', 'conjecture',
                         'corollary', 'principle', 'algorithm',
                         'definition', 'axiom', 'example', 'insight', 'exploration',
                         'problem', 'exercise', 'question', 'note', 'blockquote',
                         'activity', 'remark', 'warning', 'table', 'tabular',
                         'list', 'listing', 'program', 'console', 'demonstration',
                         'image',
                         'subtask', 'notation', 'claim', 'biblio',
                         'poem', 'stanza']


document_components = ['exercises', 'exercisegroup', 'row', 'cd',
                       'statement', 'solution', 'answer', 'hint', 'case', 'aside',
                       'interactive', 'static', 'instructions', 'investigation']

document_pieces = ['title', 'subtitle', 'cell', 'caption',
                   'address', 'attribution', 'location', 'edition',
                   'personname', 'date', 'email', 'department', 'institution',
                   'line', 'cline',
                   'role', 'entity', 'year', 'minilicense', 'holder',
                   'usage', 'description', 'journal', 'volume', 'number',
                   'mrow', 'intertext', 'initialism',
                   'quantity',
                   'webwork', 'setup', 'set', 'pg-code', 'pg-macros']

# empty tags that shoudl be on their own line
document_pieces_empty = ['cell', 'col', 'notation-list', 'brandlogo',
                         'cross-references', 'input', 'video', 'slate',
                         'webwork']

list_like = ['ol', 'ul', 'dl']

math_display = ['me', 'men', 'md', 'mdn']

footnote_like = ['fn']

nestable_tags = ["ul", "ol", "li", "p", "task", "figure", "sidebyside"]

verbatim_tags = ['latex-image-preamble', 'latex-image', 'latex-preamble',
                 'slate', 'sage', 'sageplot', 'asymptote', 'macros',
                 'program', 'input', 'output', 'prompt', 'pre']

# these shoudl be listed from innermost to outermost

tags_by_level = [
         ['section', 'appendix',
             'book', 'chapter'],
         ['subsubsection', 'subsection', 'frontmatter', 'backmatter', 'preface',
             'exercises', 'paragraphs',
             'worksheet', 'assemblage', 'solutions'],
#         ['subsubsection', 'subsection', 'section', 'appendix',
#             'book', 'chapter'],
#         ['frontmatter', 'backmatter', 'preface',
#             'exercises', 'objectives',
#             'worksheet', 'example', 'assemblage', 'solutions'],
         ['objectives', 'theorem', 'proposition', 'lemma', 'definition',
             'conjecture', 'corollary', 'principle', 'algorithm',
             'axiom', 'example', 'insight',
             'sbsgroup', 'sidebyside', 'introduction', 'conclusion',
             'exercise', 'investigation', 'activity', 'exploration'],
         ['task', 'solution', 'answer', 'hint', 'proof', 'blockquote'],
         ['ul', 'ol', 'dl'],
         ['li'],
         ['p', 'figure'],
         ['me', 'men', 'md', 'mdn', 'image', 'table'] ]

abbreviation_of_tag = {
    'chapter': 'chap',
    'section': 'sec',
    'subsection': 'ssec',
    'subsec': 'ssec',
    'subsubsection': 'sssec',
    'frontmatter': 'frontm',
    'backmatter': 'backm',
    'preface': 'pref',
    'exercises': 'exers',
    'paragraphs': 'ps',
    'worksheet': 'wrk',
    'introduction': 'intr',
    'conclusion': 'conc',
    'objectives': 'ob',
    'outcomes': 'out',
    'sidebyside': 'sbs',
    'sbsgroup': 'sbsg',
    'proof': 'pf',
    'project': 'proj',
    'theorem': 't',
    'proposition': 'pr',
    'lemma': 'l',
    'conjecture': 'conj',
    'corollary': 'cor',
    'principle': 'prin',
    'algorithm': 'alg',
    'investigation': 'inv',
    'assemblage': 'asm',
    'definition': 'd',
    'axiom': 'ax',
    'example': 'ex',
    'insight': 'in',
    'exploration': 'expl',
    'problem': 'prob',
    'exercise': 'e_',
    'question': 'q',
    'note': 'n',
    'task': 'tk',
    'blockquote': 'bq',
    'activity': 'act',
    'remark': 'rem',
    'warning': 'warn',
    'table': 'tab',
    'tabular': 'tabu',
    'list': 'lst',
    'listing': 'lsti',
    'program': 'prog',
    'console': 'con',
    'demonstration': 'demo',
    'image': 'im',
    'answer': 'a',
    'solution': 's',
    'hint': 'h',
    'ul': 'ul',
    'ol': 'ol',
    'dl': 'dl',
    'dd': 'dd',
    'p': 'p',
    'li': 'l_'
}
