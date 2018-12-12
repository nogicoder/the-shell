import re
import os

_find_unsafe = re.compile(r'[a-zA-Z0-9_^@%+=:,./-]').search

def quote(s):
    if not s:
        return "''"

    if _find_unsafe(s) is None:
        return s
    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"

# string = '$HOME'
# string = "$HOME"

# print('No quote: ')
# os.system('echo %s' % (string))
# print('Quote: ')
# os.system('echo %s' % (quote(string)))


