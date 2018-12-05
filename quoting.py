import re
from globbing import globbing
from path_expansions import path_expans

def escape_backlash(inputs):
    _find_unsafe = re.compile(r'[^\w@%+=:,./-]', re.ASCII).search
    if inputs.startswith('\\'):
        pass
    pass

def singlequote(inputs):
    pass

def doublequote(inputs):
    pass

_find_unsafe = re.compile(r'[^\w@%+=:,./-]', re.ASCII).search

def quote(inputs):
    """Return a shell-escaped version of the string *s*."""
    if not inputs:
        return "''"
    if _find_unsafe(inputs) is None:
        return inputs
    inputs = globbing(path_expans(self.user_input))

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + inputs.replace("'", "'\"'\"'") + "'"