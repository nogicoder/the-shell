#!/usr/bin/env python3

import shlex
from subprocess import PIPE, Popen

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
            # pipe case
            if '|' in raw_input:
                do_pipe_case(raw_input)
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


def do_pipe_case(raw_input):
    write_history('a', raw_input)
    inputs = raw_input.split('|')
    i = 0
    p = {}
    for command in inputs:
        command = shlex.split(command.strip())
        if i == 0:
            p[i] = Popen(command, stdin=None, stdout=PIPE, stderr=PIPE)
        else:
            p[i] = Popen(command, stdin=p[i-1].stdout, stdout=PIPE, stderr=PIPE)
        i = i + 1
    (output, _) = p[i - 1].communicate()
    print(output.decode().strip())


def do_normal_case(shell_obj, raw_input):
    # Setting Shell's inputs var
    shell_obj.raw_input = raw_input
    shell_obj.user_input = shell_obj.handle_input()
    # Setting streams
    shell_obj.shell_input = None
    shell_obj.shell_output = None
    # Execute
    shell_obj.execute_commands(shell_obj.user_input)
    # print(shell_obj.process.communicate()[0].decode())


if __name__ == "__main__":
    main()
