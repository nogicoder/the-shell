#!/usr/bin/env python3

from subprocess import run
from globbing import globbing
from shlex import split, quote
from os.path import dirname, exists
from os import chdir, environ, getcwd
from exit_code import handle_exit_code
from path_expansions import path_expans
from signal_handling import handle_signal
from logical_operator import check_operator
from string import ascii_lowercase, ascii_uppercase
from history import write_history, print_newest_history


'''----------------------Create a Shell Object-----------------------------'''


class Shell:
    # Initialize Shell
    def __init__(self):
        self.ascii_list = ascii_lowercase + ascii_uppercase
        # list of built-in features
        self.builtins = ('exit', 'printenv', 'export',
                         'unset', 'cd', 'history')
        # set initial exit_code value
        self.exit_code = 0
        # run the REPL -- MAIN LOOP
        loop = True
        while loop:
            try:
                handle_signal()
                self.user_input = self.handle_input()
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
        raw_input = input('\x1b[1m\033[92mintek-sh$\033[0m\x1b[1m\x1b[0m ')
        user_input = split(raw_input, posix=True)
        user_input = handle_exit_code(user_input, self.exit_code)
        return globbing(path_expans(user_input))

    def execute_commands(self, user_input):
        command = user_input[0]
        raw_input = ' '.join(user_input)
        write_history(command, raw_input)
        if user_input:
            # handle && and || separately
            if '&&' in user_input or '||' in user_input:
                self.logical_operator(raw_input)
            else:
                command = user_input[0]
                # check if command is a built-in
                if command in self.builtins:
                    self.do_builtin(user_input)
                # check if command is '!*'
                elif command.startswith('!') and len(command) > 1:
                    self.do_exclamation(user_input)
                    self.should_write_history = False
                # if command is not a built-in
                else:
                    # Only this function use 'commands'
                    self.do_external(user_input)

    # logical operator handling feature
    def logical_operator(self, raw_input):
        # base case for recursion - if no logical operator in inputs
        if '&&' not in raw_input and '||' not in raw_input:
            user_input = split(raw_input, posix=True)
            command = user_input[0]
            # check if command is a built-in
            if command in self.builtins:
                self.do_builtin(user_input)
            # check if command is '!*'
            elif command.startswith('!') and len(command) > 1:
                self.do_exclamation(user_input)
                self.should_write_history = False
            # if command is not a built-in
            else:
                # Only this function use 'commands'
                self.do_external(user_input)
            return self.exit_code
        # if logical operator in inputs
        else:
            # if both in inputs
            if '&&' in raw_input and '||' in raw_input:
                pos1 = raw_input.index('&&', 1)
                pos2 = raw_input.index('||', 1)
                # if the first logical operator is &&
                if pos1 < pos2:
                    inputs = raw_input.split('&&', 1)
                    expected = True
                # if the first logical operator is ||
                else:
                    inputs = raw_input.split('||', 1)
                    expected = False
            # if only && in inputs
            elif '&&' in raw_input and '||' not in raw_input:
                inputs = raw_input.split('&&', 1)
                expected = True
            # if only || in inputs
            elif '||' in raw_input and '&&' not in raw_input:
                inputs = raw_input.split('||', 1)
                expected = False
            left = inputs[0]
            right = inputs[1]
            user_input = split(left, posix=True)
            command = user_input[0]
            # check if command is a built-in
            if command in self.builtins:
                self.do_builtin(user_input)
            # check if command is '!*'
            elif command.startswith('!') and len(command) > 1:
                self.do_exclamation(user_input)
                self.should_write_history = False
            # if command is not a built-in
            else:
                # Only this function use 'commands'
                self.do_external(user_input)
            # if exit_code is not what the condition expects then return
            if (not self.exit_code) != expected:
                right = check_operator(right)
                if right:
                    new_input = str(not self.exit_code) + right
                    self.logical_operator(new_input)
                else:
                    return self.exit_code
            else:
                self.logical_operator(right)

    # execute the function with the same name as the command
    def do_builtin(self, user_input):
        command = user_input[0]
        return getattr(self, command)(user_input)

    # exit feature
    def exit(self, user_input):
        print('exit')
        if len(user_input) > 1 and not user_input[1].isdigit():
            print('intek-sh: exit: ' + user_input[1] +
                  ': numeric argument required')
            exit(2)
        elif len(user_input) > 2:
            self.exit_code = 1
            print('intek-sh: exit: too many arguments')
        else:
            if len(user_input) > 1:
                self.exit_code = int(user_input[1])
            exit(self.exit_code)

    # printenv feature
    def printenv(self, user_input, flag=False):
        # if no argument is provided
        if len(user_input) is 1:
            for key in environ:
                print(key + '=' + environ[key])
        # if arguments are provided
        else:
            for key in user_input[1:]:
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
    def export(self, user_input, flag=False):
        for item in user_input[1:]:
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
    def unset(self, user_input, flag=False):
        for key in user_input[1:]:
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
    def cd(self, user_input, flag=False):
        try:
            if len(user_input) is 1:
                dir_path = environ['HOME']
            elif user_input[1] is '.':
                pass
            elif user_input[1] is '..':
                dir_path = dirname(getcwd())
            else:
                dir_path = getcwd() + '/%s' % (user_input[1])
            chdir(dir_path)
        # catch when variable HOME doesn't have value
        except KeyError:
            print('intek-sh: cd: HOME not set')
            flag = True
        # catch when destination not exist
        except FileNotFoundError:
            print('intek-sh: cd:' +
                  ' %s: No such file or directory' % (user_input[1]))
            flag = True
        # catch when destination is not a directory
        except NotADirectoryError:
            print('intek-sh: cd:' +
                  ' %s: Not a directory' % (user_input[1]))
            flag = True
        if not flag:
            self.exit_code = 0
        elif flag:
            self.exit_code = 1

    def history(self, user_input):
        self.exit_code = 0
        # with only 'history' command
        if len(user_input) is 1:
            with open('.history.txt', 'r') as history_file:
                for line in history_file:
                    print('  ' + line.strip())
        # 'history + options' command
        else:
            # clear option 'history -c'
            if '-c' in user_input[1:]:
                open('.history.txt', "w").close()
            # display [n] newest history 'history [n]'
            else:
                # number of last lines need to print
                n = user_input[1]
                # function to print
                self.exit_code = print_newest_history(n)

    # '!' command, ralating to history
    def do_exclamation(self, user_input):
        command = user_input[0]
        self.exit_code = 0
        try:
            if command == '!!':
                with open('.history.txt') as history_file:
                    content = history_file.read()
                    if content:
                        numline = 0
                        self.do_past_input(numline)
                    else:
                        print('intek-sh: %s: event not found' % (command))
            else:
                numline = int(command[1:])
                self.do_past_input(numline)

        except (IndexError, ValueError):
            print('intek-sh: %s: event not found' % (command))
        except RecursionError:
            pass

    def do_past_input(self, numline):
        with open('.history.txt', 'r') as history_file:
            content = history_file.readlines()
            line_content = content[numline - 1].split('\t')[1].strip()
            line_contents = split(line_content, posix=True)

            print(line_content)
            self.execute_commands(line_contents)

    # execute external command
    def do_external(self, user_input):
        command = user_input[0]
        # if command is an executable file
        if command.startswith('./'):
            self.run_file(user_input)
        elif command is False or command in ['false', 'False']:
            self.exit_code = 1
        elif command is True or command == ['true', 'True']:
            self.exit_code = 0
        # if command is not an executable file
        else:
            self.run_binary(user_input)

    # run the executable file
    def run_file(self, user_input):
        command = user_input[0]
        try:
            # catch if only ./ is prompted in
            if command == './':
                print('intek-sh: ./: Is a directory')
                self.exit_code = 126
            else:
                # run the file
                self.exit_code = run(user_input).returncode
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
    def run_binary(self, user_input):
        command = user_input[0]
        try:
            # get paths to external binaries indicated by variable PATH
            paths = environ['PATH'].split(':')
            # check if the command is in paths
            if command and (exists(path + '/' + command) for path in paths):
                self.exit_code = run(user_input).returncode
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
