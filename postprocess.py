
import re

def put_lists_in_paragraphs(text):

    thetext = text

    thetext = re.sub(r"\s*</p>\s*<(ol|ul|dl)\b(.*?)</\1>",
                     "\n                  " + r"<\1" + r"\2" + "\n                  " + r"</\1>" + "\n                </p>", thetext, 0, re.DOTALL)
    # think about whether that needs to be done twice, when there are successive alternating blocks

    thetext = re.sub(r"\s*</p>\s*<(ol|ul|dl)\b(.*?)</\1>",
                     "\n                  " + r"<\1" + r"\2" + "\n                  " + r"</\1>" + "\n                </p>", thetext, 0, re.DOTALL)
    # note that this simple approach is confused by nested lists

    return thetext

##################


