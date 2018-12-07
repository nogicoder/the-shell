from shlex import split
from os import stat


def write_history(inp):
    if inp is not '':
        with open("history.txt", 'a+') as history_file:
            should_write = True
            # get line number
            history_file.seek(0)
            num_line = sum(1 for line in history_file) + 1
            # get content of history file
            history_file.seek(0)
            content = history_file.readlines()
            # check if history file is not empty
            if num_line > 1:
                last_line = content[-1].split('\t')
                last_inp = last_line[1].strip()
                # input duplicate, should not write
                if inp == last_inp:
                    should_write = False
            if inp.startswith('!') and not inp is '!':
                should_write = False

            if should_write:
                history_file.write(str(num_line) + '\t' + inp + '\n')
    

def print_newest_history(n):
    try:
        with open('history.txt', 'r') as history_file:
            # get content of history file
            content = history_file.readlines()
            # 'history 0' - do nothing
            if int(n) is 0:
                pass
            # 'history n' with n < 0 - print error 
            elif int(n) < 0:
                print('intek-sh: history: %s: invalid option' % (n))
            # print n newest lines
            else:
                for line in content[-int(n):]:
                    print('  ' + line.strip())
    except ValueError:
        print('intek-sh: history: %s: numeric argument required' % (n))
