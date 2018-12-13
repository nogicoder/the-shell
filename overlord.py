#!/usr/bin/env python3

from intekshell import Shell

def main():

    ShellObj = Shell()
    handle_shell(ShellObj)
    
    input = 'cat abc.txt | wc -l'
    if '|' in input:
        pipe_commands = input.split('|')
        shells = [Shell() for i in range(len(pipe_commands))]
        handle_shell(shells[0])
        for index, current_shell in enumerate(shells[1:]):
            current_shell.shell_input = shells[index - 1].shell_output
            handle_shell(current_shell)
            
def handle_shell(shell_obj):
    # run the REPL -- MAIN LOOP
    loop = True
    while loop:
        try:
            shell_obj.handle_signal()
            if not shell_obj.shell_input:
                shell_obj.user_input = shell_obj.handle_input()
                shell_obj.execute_commands(shell_obj.user_input)
                
            else:
                shell_obj.execute_commands(shell_obj.shell_input)
                loop = False
                return shell_obj.shell_output
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

if __name__ == "__main__":
    main()
