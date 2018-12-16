#!/usr/bin/env python3

import shlex
from subprocess import PIPE, Popen
from os import getpid, fork, wait, kill

from history import print_newest_history, write_history
from intekshell import Shell


def main():
    main_shell = Shell()
    handle_shell(main_shell)


def handle_shell(shell_obj):
    # run the REPL -- MAIN LOOP
    loop = True
    while loop:
        try:
            shell_obj.handle_signal()
            raw_input = input('\x1b[1m\033[92mintek-sh$\033[0m\x1b[1m\x1b[0m ')
            # pipe case ; 
            if '|' in raw_input and '||' not in raw_input:
                do_pipe_case(shell_obj, raw_input)
            # subshell case:
            elif raw_input.startswith('(') and raw_input.endswith(')'):
                do_subshell_case(shell_obj, raw_input)
            # normal case
            else:
                do_normal_case(shell_obj, raw_input)
        # catch EOFError when no input is prompted in
        except EOFError: 
            break
        # catch IndexError when nothing is input in (empty input list)
        except IndexError:
            pass
        except ValueError:
            pass
        except KeyboardInterrupt:
            shell_obj.exit_code = 130
            print('')
            pass
        except Exception:
            pass


def do_pipe_case(shell_obj, raw_input):
    print('pipe case')
    write_history('a', raw_input)
    pipe_inputs = raw_input.split('|')
    i = 0
    p = {}
    shell_obj.shell_stdout = PIPE
    shell_obj.shell_stderr = PIPE
    for command in pipe_inputs:
        shell_obj.raw_input = command
        shell_obj.user_input = shell_obj.handle_input()
        if i == 0:
            shell_obj.shell_stdin = None
            p[i] = shell_obj.execute_commands(shell_obj.user_input)
        else:
            shell_obj.shell_stdin = p[i-1].stdout
            p[i] = shell_obj.execute_commands(shell_obj.user_input)
        i = i + 1
    (output, _) = p[i - 1].communicate()
    print(output.decode().strip())
    

def do_normal_case(shell_obj, raw_input):
    print('normal case')
    # Setting Shell's inputs var
    shell_obj.raw_input = raw_input
    shell_obj.user_input = shell_obj.handle_input()
    # Setting streams
    shell_obj.shell_input = None
    shell_obj.shell_output = None
    shell_obj.shell_stderr = None
    # Execute
    shell_obj.execute_commands(shell_obj.user_input)
    # Why need this????
    print(shell_obj.process.communicate()[0].decode().strip())


def do_subshell_case(shell_obj, raw_input):
    print('subshell case')
    child = fork()
    if not child:
        print(getpid())
        print('in child')
        shell_obj.raw_input = raw_input[1:len(raw_input) - 1]
        shell_obj.user_input = shell_obj.handle_input()
        process = shell_obj.execute_commands(shell_obj.user_input)
        output = process.communicate()[0].decode().strip()
        print(output)
        kill(getpid(), 13)
    else:
        print(getpid())
        wait()



if __name__ == "__main__":
    main()
