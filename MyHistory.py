from shlex import split

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
                if inp == last_inp or inp.startswith('!'):
                    should_write = False
                    
            if should_write:
                history_file.write(str(num_line) + '\t' + inp + '\n')


def print_newest_history(n):
    try:
        with open('history.txt', 'r') as history_file:
            # get content of history file
            content = history_file.readlines()
            # print n newest lines 
            for line in content[-int(n):]:
                print('  ' + line.strip())
    except ValueError:
        print('intek-sh: history: %s: numeric argument required' % (n))
