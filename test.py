#!/usr/bin/env python3

from os import chdir, environ, getcwd
from os.path import dirname, exists
from shlex import split, quote
from subprocess import run
from string import ascii_lowercase
from string import ascii_uppercase
from globbing import *
from path_expansions import *
from signal_handling import handle_signal
from MyHistory import write_history, print_newest_history


'''----------------------Create a Shell Object-----------------------------'''


class Shell:
    # Initialize Shell
    def __init__(self):
        self.ascii_list = ascii_lowercase + ascii_uppercase
        # list of built-in features
        self.builtins = ('exit', 'printenv', 'export', 'unset', 'cd', 'history')
        self.exit_code = 0
        # run the REPL -- MAIN LOOP
        loop = True
        while loop:
            try:
                handle_signal()
                self.handle_input()
                self.execute_commands(self.user_input)
            # catch EOFError when no input is prompted in
            except EOFError:
                break
            # catch IndexError when nothing is input in (empty input list)
            except IndexError:
                pass
            except ValueError:
                pass
            except KeyboardInterrupt:
                self.exit_code = 130
                print('')
                pass
    # Handling input to match each feature's requirement
    def handle_input(self):
        # raw input
        self.inputs = input('\x1b[1m\033[92mintek-sh$\033[0m\x1b[1m\x1b[0m ')
        user_input = split(self.inputs, posix=True)
        self.handle_exit_code(user_input)
        # list of inputs
        self.user_input = globbing(path_expans(user_input)) 

    # convert $? to exit code
    def handle_exit_code(self, user_input):
        if '$?' in user_input:
            pos = user_input.index('$?')
            user_input[pos] = str(self.exit_code)
        if '${?}' in user_input:
            pos = user_input.index('${?}')
            user_input[pos] = str(self.exit_code)    

    def execute_commands(self, commands):
        raw_commands = ' '.join(commands)
        write_history(raw_commands)
        if commands:
            # handle && and || separately
            if '&&' in commands or '||' in commands:
                self.logical_operator(raw_commands)
            else:
                command = commands[0]
                # check if command is a built-in
                if command in self.builtins:
                    self.do_builtin(command)
                # check if command is '!*'
                elif command.startswith('!') and len(command) > 1:
                    self.do_exclamation(command)
                    self.should_write_history = False
                # if command is not a built-in
                else:
                    # Only this function use 'commands'
                    self.do_external(command, commands)
    
    # logical operator handling feature
    def logical_operator(self, inputs):
        # base case for recursion - if no logical operator in inputs
        if '&&' not in inputs and '||' not in inputs:
            self.user_input = split(inputs, posix=True)
            command = self.user_input[0]
            if command in self.builtins:
                self.do_builtin(command)
            else:
                self.do_external(command, self.user_input)
            return self.exit_code
        # if logical operator in inputs
        else:
            # if both in inputs
            if '&&' in inputs and '||' in inputs:
                pos1 = inputs.index('&&', 1)
                pos2 = inputs.index('||', 1)
                # if the first logical operator is &&
                if pos1 < pos2:
                    left = inputs[:pos1 - 1]
                    right = inputs[pos1 + 3:]
                    expected = True
                # if the first logical operator is ||
                else:
                    left = inputs[:pos2 - 1]
                    right = inputs[pos2 + 3:]
                    expected = False
            # if only && in inputs
            elif '&&' in inputs and '||' not in inputs:
                pos1 = inputs.index('&&', 1)
                left = inputs[:pos1 - 1]
                right = inputs[pos1 + 3:]
                expected = True
            # if only || in inputs
            elif '||' in inputs and '&&' not in inputs:
                pos2 = inputs.index('||', 1)
                left = inputs[:pos2 - 1]
                right = inputs[pos2 + 3:]
                expected = False
            self.user_input = split(left, posix=True)
            command = self.user_input[0]
            if command in self.builtins:
                self.do_builtin(command)
            else:
                self.do_external(command, self.user_input)
            # if exit_code is not what the condition expects then return
            if (not self.exit_code) != expected:
                return self.exit_code
            else:
                self.logical_operator(right)

    # execute the function with the same name as the command
    def do_builtin(self, command):
        return getattr(self, command)()

    # exit feature
    def exit(self):
        print('exit')
        if len(self.user_input) > 1 and not self.user_input[1].isdigit():
            print('intek-sh: exit: ' + self.user_input[1] +
                  ': numeric argument required')
            exit(2)
        elif len(self.user_input) > 2:
            self.exit_code = 1
            print('intek-sh: exit: too many arguments')
        else:
            if len(self.user_input) > 1:
                self.exit_code = int(self.user_input[1])
            exit(self.exit_code)

    # printenv feature
    def printenv(self, flag=False):
        # if no argument is provided
        if len(self.user_input) is 1:
            for key in environ:
                print(key + '=' + environ[key])
        # if arguments are provided
        else:
            for key in self.user_input[1:]:
                try:
                    print(environ[key])
                # catch KeyError when an argument not exists in environ
                except KeyError:
                    flag = True
                    pass
        if not flag:
            self.exit_code = 0
        elif flag:
            self.exit_code = 1

    # export feature
    def export(self, flag=False):
        for item in self.user_input[1:]:
            if '=' in item:
                items = item.split('=', 1)
                if len(items) is 2 and items[0]:
                    for letter in items[0]:
                        if letter not in self.ascii_list:
                            flag = False
                    if flag:
                        environ[items[0]] = items[1]
                    else:
                        print('intek-sh: export:' +
                              ' `%s\': not a valid identifier' % (item))
                else:
                    print('intek-sh: export:' +
                          ' `%s\': not a valid identifier' % (item))
                    flag = True
            else:
                # handle the case ''; '   '; 'b    a'
                item_strip = item.strip().split(' ')
                if len(item_strip) is 1 and item_strip[0]:
                    for letter in item_strip[0]:
                        if letter not in self.ascii_list:
                            flag = False
                    if flag:
                        pass
                    else:
                        print('intek-sh: export:' +
                              ' `%s\': not a valid identifier' % (item))
                else:
                    print('intek-sh: export:' +
                          ' `%s\': not a valid identifier' % (item))
                    flag = True
        if not flag:
            self.exit_code = 0
        elif flag:
            self.exit_code = 1

    # unset feature
    def unset(self, flag=False):
        for key in self.user_input[1:]:
            flag = True
            try:
                # handle the case ''; '   '; 'b    a'
                key_strip = key.strip().split(' ')
                if len(key_strip) is 1 and key_strip[0]:
                    for letter in key_strip[0]:
                        if letter not in self.ascii_list:
                            flag = False
                    if flag:
                        try:
                            del environ[key]
                        # catch if key not an environ variables
                        except KeyError:
                            pass
                    else:
                        print('intek-sh: unset:' +
                              ' `%s\': not a valid identifier' % (key))
                else:
                    print('intek-sh: unset:' +
                          ' `%s\': not a valid identifier' % (key))
                    flag = True
            # catch if no execute permission on key
            except OSError:
                print('intek-sh: unset:' +
                      ' `%s\': not a valid identifier' % (key))
                flag = True
        if not flag:
            self.exit_code = 0
        elif flag:
            self.exit_code = 1

    # cd feature
    def cd(self, flag=False):
        try:
            if len(self.user_input) is 1:
                dir_path = environ['HOME']
            elif self.user_input[1] is '.':
                pass
            elif self.user_input[1] is '..':
                dir_path = dirname(getcwd())
            else:
                dir_path = getcwd() + '/%s' % (self.user_input[1])
            chdir(dir_path)
        # catch when variable HOME doesn't have value
        except KeyError:
            print('intek-sh: cd: HOME not set')
            flag = True
        # catch when destination not exist
        except FileNotFoundError:
            print('intek-sh: cd:' +
                  ' %s: No such file or directory' % (self.user_input[1]))
            flag = True
        # catch when destination is not a directory
        except NotADirectoryError:
            print('intek-sh: cd:' +
                  ' %s: Not a directory' % (self.user_input[1]))
            flag = True
        if not flag:
            self.exit_code = 0
        elif flag:
            self.exit_code = 1

    def history(self):
        # with only 'history' command
        if len(self.user_input) is 1:
            with open('history.txt', 'r') as history_file:
                for line in history_file:
                    print('  ' + line.strip())
        # 'history + options' command
        else:
            # clear option 'history -c'
            if '-c' in self.user_input[1:]:
                open('history.txt', "w").close()
            # display [n] newest history 'history [n]'
            else:
                # number of last lines need to print
                n = self.user_input[1]
                # function to print
                print_newest_history(n)

    # '!' command, ralating to history
    def do_exclamation(self, command):
        try:
            if command == '!!':
                numline = 0
            else:
                numline = int(command[1:])
                
            self.do_past_input(numline)

        except (IndexError, ValueError):
            print('intek-sh: %s: event not found' % (command))

    def do_past_input(self, numline):
        with open('history.txt', 'r') as history_file:
            content = history_file.readlines()
            line_content = content[numline - 1].split('\t')[1].strip()
            line_contents = split(line_content, posix=True)

            print(line_content)
            self.execute_commands(line_contents)

    # execute external command
    def do_external(self, command, commands):
        # if command is an executable file
        if command.startswith('./'):
            self.run_file(command, commands)
        # if command is not an executable file
        else:
            self.run_binary(command, commands)

    # run the executable file
    def run_file(self, command, commands):
        try:
            # catch if only ./ is prompted in
            if command == './':
                print('intek-sh: ./: Is a directory')
                self.exit_code = 126
            else:
                # run the file
                self.exit_code = run(commands).returncode
        # catch if no execute permission on the file
        except PermissionError:
            print('intek-sh: %s: Permission denied' % (command))
            self.exit_code = 126
        # catch if the file doesn't exist
        except FileNotFoundError:
            print('intek-sh: %s: No such file or directory' % (command))
            self.exit_code = 127
        # catch if file is not an executable file
        except OSError:
            self.exit_code = 0
            pass

    # run the external binaries
    def run_binary(self, command, commands):
        try:
            # get paths to external binaries indicated by variable PATH
            paths = environ['PATH'].split(':')
            # check if the command is in paths
            if command and (exists(path + '/' + command) for path in paths):
                self.exit_code = run(commands).returncode
        # catch if the command doesn't exist
        except FileNotFoundError:
            print('intek-sh: %s: command not found' % (command))
            self.exit_code = 127
        # catch if PATH variable doesn't exist
        except KeyError:
            print('intek-sh: %s: No such file or directory' % (command))
            self.exit_code = 127
        # catch if no execute permission on the command
        except PermissionError:
            print('intek-sh: %s: Permission denied' % (command))
            self.exit_code = 126


# Run the Shell
if __name__ == '__main__':
    Shell()
