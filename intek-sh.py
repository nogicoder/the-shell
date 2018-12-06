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
        # run the REPL
        loop = True
        while loop:
            try:
                # get inputs from user as a list
                inp = input('\x1b[1m\033[92mintek-sh$\033[0m\x1b[1m\x1b[0m ')
                inputs = split(inp, posix=True)
                self.user_input = self.handle_input(inputs)
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

    # Handling input to match each feature's requirement
    def handle_input(self, inputs):
        user_input = globbing(path_expans(inputs))
        return user_input

    # execute the function with the same name as the command
    def do_builtin(self, command):
        return getattr(self, command)()

    # exit feature
    def exit(self):
        print('exit')
        if len(self.user_input) is 2 and not self.user_input[1].isdigit():
            print('intek-sh: exit:')
        exit()

    # printenv feature
    def printenv(self):
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
                    pass

    # export feature
    def export(self):
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

    # unset feature
    def unset(self):
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
            except OSError:
                print('intek-sh: unset:' +
                      ' `%s\': not a valid identifier' % (key))

    # cd feature
    def cd(self):
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
        # catch when destination not exist
        except FileNotFoundError:
            print('intek-sh: cd:' +
                  ' %s: No such file or directory' % (self.user_input[1]))
        # catch when destination is not a directory
        except NotADirectoryError:
            print('intek-sh: cd:' +
                  ' %s: Not a directory' % (self.user_input[1]))

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
            else:
                # run the file
                run(self.user_input)
        # catch if no execute permission on the file
        except PermissionError:
            print('intek-sh: %s: Permission denied' % (command))
        # catch if the file doesn't exist
        except FileNotFoundError:
            print('intek-sh: %s: No such file or directory' % (command))
        # catch if file is not an executable file
        except OSError:
            pass

    # run the external binaries
    def run_binary(self, command):
        try:
            # get paths to external binaries indicated by variable PATH
            paths = environ['PATH'].split(':')
            # check if the command is in paths
            if command and (exists(path + '/' + command) for path in paths):
                run(self.user_input)
        # catch if the command doesn't exist
        except FileNotFoundError:
            print('intek-sh: %s: command not found' % (command))
        # catch if PATH variable doesn't exist
        except KeyError:
            print('intek-sh: %s: No such file or directory' % (command))
        # catch if no execute permission on the command
        except PermissionError:
            print('intek-sh: %s: Permission denied' % (command))


# Run the Shell
if __name__ == '__main__':
    Shell()
