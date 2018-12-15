#!/usr/bin/env python3

from intekshell import Shell
from subprocess import PIPE
    
def handle_shell(shell_obj):
    # run the REPL -- MAIN LOOP
    loop = True
    while loop:
        try:
            # raw_input = input('\x1b[1m\033[92mintek-sh$\033[0m\x1b[1m\x1b[0m ')
            # shell_obj.raw_input = raw_input
            # shell_obj.handle_signal()
            # shell_obj.user_input = shell_obj.handle_input()
            # shell_obj.execute_commands(shell_obj.user_input)

            shell_obj.handle_signal()
            raw_input = input('\x1b[1m\033[92mintek-sh$\033[0m\x1b[1m\x1b[0m ')
            # pipe case
            if '|' in raw_input:
                inputs = raw_input.split('|')
                for index, command in enumerate(inputs):
                    # Setting Shell's inputs var
                    shell_obj.raw_input = command.strip()
                    shell_obj.user_input = shell_obj.handle_input()
                    # Setting streams
                    shell_obj.shell_input = shell_obj.shell_output if index != 0 else None
                    shell_obj.shell_output = PIPE if index != len(inputs) - 1 else None
                    # Execute 
                    shell_obj.execute_commands(shell_obj.user_input)
            # normal case
            else:
                # Setting Shell's inputs var
                shell_obj.raw_input = raw_input
                shell_obj.user_input = shell_obj.handle_input()
                # Setting streams
                shell_obj.shell_input = None
                shell_obj.shell_output = None
                # Execute
                shell_obj.execute_commands(shell_obj.user_input)
                

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

def main():
    
    main_shell = Shell()
    handle_shell(main_shell)

if __name__ == "__main__":
    main()
