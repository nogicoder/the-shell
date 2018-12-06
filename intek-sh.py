#!/usr/bin/env python3

from os import chdir
from os import getcwd
from os import environ
from os.path import exists
from os.path import dirname
from shlex import split
from subprocess import run
from string import ascii_lowercase
from string import ascii_uppercase
from globbing import *
from path_expansions import *


'''----------------------Create a Shell Object-----------------------------'''


class Shell:
    # Initialize Shell
    def __init__(self):
        self.ascii_list = ascii_lowercase + ascii_uppercase
        # list of built-in features
        self.builtins = ['exit', 'printenv', 'export', 'unset', 'cd']
        self.exit_code = 0
        # run the REPL
        loop = True
        while loop:
            try:
                # get inputs from user as a list
                inp = input('\x1b[1m\033[92mintek-sh$\033[0m\x1b[1m\x1b[0m ')
                inputs = split(inp, posix=True)
                self.user_input = self.handle_input(inputs)
                # handle && and || separately
                if '&&' in self.user_input or '||' in self.user_input:
                    self.raw_input = ' '.join(self.user_input)
                    self.logical_operator(self.raw_input)
                else:
                    command = self.user_input[0]
                    # check if command is a built-in
                    if command in self.builtins:
                        self.do_builtin(command)
                    # if command is not a built-in
                    else:
                        self.do_external(command)
            # catch EOFError when no input is prompted in
            except EOFError:
                break
            # catch IndexError when nothing is input in (empty input list)
            except IndexError:
                pass
            except ValueError:
                pass

    # convert $? to exit code
    def handle_exit_code(self, inputs):
        if '$?' in inputs:
            pos = inputs.index('$?')
            inputs[pos] = str(self.exit_code)
        if '${?}' in inputs:
            pos = inputs.index('${?}')
            inputs[pos] = str(self.exit_code)

    # Handling input to match each feature's requirement
    def handle_input(self, inputs):
        self.handle_exit_code(inputs)
        user_input = globbing(path_expans(inputs))
        return user_input

    # logical operator handling feature
    def logical_operator(self, inputs):
        # base case for recursion - if no logical operator in inputs
        if '&&' not in inputs and '||' not in inputs:
            self.user_input = split(inputs, posix=True)
            command = self.user_input[0]
            if command in self.builtins:
                self.do_builtin(command)
            else:
                self.do_external(command)
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
                self.do_external(command)
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
            flag = True
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

    # execute external command
    def do_external(self, command):
        # if command is an executable file
        if command.startswith('./'):
            self.run_file(command)
        # if command is not an executable file
        else:
            self.run_binary(command)

    # run the executable file
    def run_file(self, command):
        try:
            # catch if only ./ is prompted in
            if command == './':
                print('intek-sh: ./: Is a directory')
                self.exit_code = 126
            else:
                # run the file
                self.exit_code = run(self.user_input).returncode
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
    def run_binary(self, command):
        try:
            # get paths to external binaries indicated by variable PATH
            paths = environ['PATH'].split(':')
            # check if the command is in paths
            if command and (exists(path + '/' + command) for path in paths):
                self.exit_code = run(self.user_input).returncode
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
