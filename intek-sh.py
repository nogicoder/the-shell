#!/usr/bin/env python3

import os
from shlex import split
from subprocess import run


'''----------------------Create a Shell Object-----------------------------'''


class Shell:
    # Initialize Shell
    def __init__(self):
        # list of built-in features
        self.builtins = ['exit', 'printenv', 'export', 'unset', 'cd']
        # run the REPL
        loop = True
        while loop:
            # get inputs from user as a list
            self.user_input = split(input('intek-sh$ '), posix=True)
            try:
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
            for key in os.environ:
                print(key + '=' + os.environ[key])
        # if arguments are provided
        else:
            for key in self.user_input[1:]:
                try:
                    print(os.environ[key])
                # catch KeyError when an argument not exists in os.environ
                except KeyError:
                    pass

    # export feature
    def export(self):
        for item in self.user_input[1:]:
            if '=' in item:
                items = item.split('=', 1)
                if len(items) is 2 and items[0]:
                    os.environ[items[0]] = items[1]
                else:
                    print('intek-sh: export:' +
                          ' `{}\': not a valid identifier'.format(item))
            else:
                if item:
                    pass
                else:
                    print('intek-sh: export:' +
                          ' `{}\': not a valid identifier'.format(item))

    # unset feature
    def unset(self):
        try:
            for key in self.user_input[1:]:
                del os.environ[key]
        # catch if key not exist in os.environ
        except KeyError:
            pass
        # catch if no execute permission on key
        except Exception:
            print('intek-sh: unset:' +
                  ' {}: cannot unset: readonly variable'.format(key))

    # cd feature
    def cd(self):
        try:
            if len(self.user_input) is 1:
                dir_path = os.environ['HOME']
            elif self.user_input[1] is '.':
                pass
            elif self.user_input[1] is '..':
                dir_path = os.path.dirname(os.getcwd())
            else:
                dir_path = os.getcwd() + '/{}'.format(self.user_input[1])
            os.chdir(dir_path)
        # catch when variable HOME doesn't have value
        except KeyError:
            print('intek-sh: cd: HOME not set')
        # catch when destination not exist
        except FileNotFoundError:
            print('intek-sh: cd:' +
                  ' {}: No such file or directory'.format(self.user_input[1]))
        # catch when destination is not a directory
        except NotADirectoryError:
            print('intek-sh: cd:' +
                  ' {}: Not a directory'.format(self.user_input[1]))

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
            # open and run the content of the file
            file_name = command[2:]
            with open(file_name, 'r') as file:
                content = file.read()
                exec(content)
        # catch if doesn't have execute permission on the file
        except PermissionError:
            print('intek-sh: {input[0][2:]}: Permission ' +
                  'denied'.format(command[2:]))
        # catch if the file doesn't exist
        except FileNotFoundError:
            print('intek-sh:' +
                  ' {}: No such file or directory'.format(command[2:]))

    # check if the file is an executable external binaries
    def run_binary(self, command):
        exist = False
        try:
            # check if the command is in the paths indicated by variable PATH
            for path in os.environ['PATH'].split(':'):
                if os.path.exists(path + '/' + command):
                    run(self.user_input)
                    exist = True
                    break
            # catch if the command doesn't exist at all
            if not exist:
                print('intek-sh: {}: command not found'.format(command))
        # catch if PATH variable doesn't exist
        except KeyError:
            print('intek-sh:' +
                  ' {}: No such file or directory'.format(command))
        # catch if doesn't have execute permission on the command
        except PermissionError:
            print('intek-sh: {}: Permission denied'.format(command))


# Run the Shell
if __name__ == '__main__':
    Shell()
