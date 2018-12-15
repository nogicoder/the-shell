from subprocess import Popen, PIPE, run, TimeoutExpired
from shlex import split


def handle_backquotes(item, result=''):
    i = 0
    while i < len(item):
        if item[i] != '`':
            result += item[i]
            i += 1
        elif item[i] == '`':
            temp = ''
            i += 1
            while item[i] != '`':
                temp += item[i]
                i += 1
            result += execute_cmd(temp)
            i += 1
    return item

def execute_cmd(item):
    item = split(['./intek-sh.py'], posix=True)
    child = Popen(item, stdin=PIPE, stdout=PIPE,
            stderr=PIPE)
    try:
        out, err = child.communicate(timeout=3)
        print(out.decode())
        print('--')
        print(err.decode())
    except TimeoutExpired:
        child.kill()
        out, err = child.communicate()
        print(out.decode())
        print('--')
        print(err.decode())
        if not child.returncode:
            return out.decode()
        else:
            return err.decode()


print(execute_cmd('echo ef'))
