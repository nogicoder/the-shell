#!/usr/bin/env python3

from os import chdir, environ, getcwd, kill
from os.path import dirname, exists, isdir
from shlex import split
from signal import SIG_DFL, SIG_IGN, SIGINT, SIGQUIT, SIGTERM, SIGTSTP, signal
from string import ascii_letters
from subprocess import Popen

from exit_code import error_flag_handle
from globbing import globbing
from auto_completion import Initialize_completion
from history import write_history, print_newest_history
from logical_operator import check_operator, check_valid_operator
from path_expansions import path_expans
from quoting import adding_backslash, handle_quotes


'''----------------------Create a Shell Object-----------------------------'''


class Shell:
    # Initialize Shell
    def __init__(self):
        self.ascii_list = ascii_letters
        # list of built-in features
        self.builtins = ('exit', 'printenv', 'export',
                         'unset', 'cd', 'history')
        # set initial exit_code value
        self.exit_code = 0
        # run the REPL -- MAIN LOOP
        loop = True
        while loop:
            self.pid_list = []
            try:
                self.handle_signal()
                self.raw_input = self.handle_input()
                if self.raw_input:
                    self.user_input = self.handle_expansion(self.raw_input)
                    self.execute_commands(self.user_input, self.raw_input)
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
            # try not to crashed
            except Exception:
                pass

    # handle the signal
    def do_signal(self, signal, frame):
        try:
            self.exit_code = 128 + signal
            for item in self.pid_list:
                kill(item, signal)
                # return to prompt
                item.kill()
            self.pid_list = []
        except ProcessLookupError:
            pass

    # ignore the signal with intek-sh and apply to child process after
    def handle_signal(self, signal_flag=False):
        signal(SIGQUIT, SIG_IGN)  # -3
        signal(SIGTSTP, SIG_IGN)  # -20
        signal(SIGTERM, SIG_IGN)
        if signal_flag:
            signal(SIGQUIT, self.do_signal)
            signal(SIGTSTP, self.do_signal)
            signal(SIGTERM, self.do_signal)

    # Handling input to match each feature's requirement
    def handle_input(self):
        Initialize_completion()
        raw_input = input('\x1b[1m\033[92mintek-sh$\033[0m\x1b[1m\x1b[0m ')
        if not raw_input:
            self.exit_code = 0
        return raw_input

    # handle expansion of inputs (quotes, path expans, glob)
    def handle_expansion(self, raw_input):
        # handle the quotes
        user_input = adding_backslash(raw_input)

        if user_input == raw_input:
            if "\\" in user_input:
                user_input = user_input.replace("\\", r"\\")

        user_input = split(user_input, posix=True)
        user_input = handle_quotes(user_input, self.exit_code)

        return user_input

    # execute commands with builtin, external and logical operators
    def execute_commands(self, user_input, raw_input):
        if not user_input:
            self.exit_code = 1
            return

        command = user_input[0]
        write_history(command, raw_input)

        if ("\\&&" not in raw_input and "\\||" not in raw_input and
           ('&&' in raw_input or '||' in raw_input)):
                if check_valid_operator(raw_input):
                    return self.logical_operator(raw_input)
                else:
                    self.exit_code = 2
                    return

        # check if command is a built-in
        if command in self.builtins:
            self.do_builtin(user_input)
        # check if command is '!*'
        elif command.startswith('!') and len(command) > 1:
            self.do_exclamation(user_input)
            self.should_write_history = False
        # if command is not a built-in
        else:
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
    def printenv(self, user_input, error_flag=False):
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
                    error_flag = True
                    pass
        self.exit_code = error_flag_handle(error_flag)

    # export feature
    def export(self, user_input, error_flag=False):
        for item in user_input[1:]:
            if '=' in item:
                items = item.split('=', 1)
                if len(items) is 2 and items[0]:
                    ascii_flag = True
                    for letter in items[0]:
                        if letter not in self.ascii_list:
                            ascii_flag = False
                    if ascii_flag:
                        environ[items[0]] = items[1]
                    else:
                        print('intek-sh: export:' +
                              ' `{}\': not a valid identifier'.format(item))
                        error_flag = True
                else:
                    print('intek-sh: export:' +
                          ' `{}\': not a valid identifier'.format(item))
                    error_flag = True
            else:
                # handle the case ''; '   '; 'b    a'
                item_strip = item.strip().split(' ')
                if len(item_strip) is 1 and item_strip[0]:
                    ascii_flag = True
                    for letter in item_strip[0]:
                        if letter not in self.ascii_list:
                            ascii_flag = False
                    if ascii_flag:
                        environ[item_strip[0]] = ' '
                    else:
                        print('intek-sh: export:' +
                              ' `{}\': not a valid identifier'.format(item))
                        error_flag = True
                else:
                    print('intek-sh: export:' +
                          ' `{}\': not a valid identifier'.format(item))
                    error_flag = True
        self.exit_code = error_flag_handle(error_flag)

    # unset feature
    def unset(self, user_input, error_flag=False):
        for key in user_input[1:]:
            try:
                # handle the case ''; '   '; 'b    a'
                key_strip = key.strip().split(' ')
                if len(key_strip) is 1 and key_strip[0]:
                    ascii_flag = True
                    for letter in key_strip[0]:
                        if letter not in self.ascii_list:
                            ascii_flag = False
                    if ascii_flag:
                        try:
                            del environ[key]
                        # catch if key not an environ variables
                        except KeyError:
                            pass
                    else:
                        print('intek-sh: unset:' +
                              ' `{}\': not a valid identifier'.format(key))
                        error_flag = True
                else:
                    print('intek-sh: unset:' +
                          ' `{}\': not a valid identifier'.format(key))
                    error_flag = True
            # catch if no execute permission on key
            except OSError:
                print('intek-sh: unset:' +
                      ' `{}\': not a valid identifier'.format(key))
                error_flag = True
        self.exit_code = error_flag_handle(error_flag)

    # cd feature
    def cd(self, user_input, error_flag=False):
        try:
            if len(user_input) is 1:
                dir_path = environ['HOME']
            elif user_input[1] is '.':
                pass
            elif user_input[1] is '..':
                dir_path = dirname(getcwd())
            else:
                dir_path = getcwd() + '/{}'.format(user_input[1])
            chdir(dir_path)
            error_flag = False
        # catch when variable HOME doesn't have value
        except KeyError:
            print('intek-sh: cd: HOME not set')
            error_flag = True
        # catch when destination not exist
        except FileNotFoundError:
            print('intek-sh: cd:' +
                  ' {}: No such file or directory'.format(user_input[1]))
            error_flag = True
        # catch when destination is not a directory
        except NotADirectoryError:
            print('intek-sh: cd:' +
                  ' {}: Not a directory'.format(user_input[1]))
            error_flag = True
        self.exit_code = error_flag_handle(error_flag)

    # history feature
    def history(self, user_input):
        self.exit_code = 0
        # with only 'history' command
        if len(user_input) is 1:
            with open('.history.txt', 'r') as history_file:
                for line in history_file:
                    print('  ' + line.strip())
        else:
            if '-c' in user_input[1:]:
                open('.history.txt', "w").close()
            else:
                n = user_input[1]
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
                        numline = -1
                        self.do_past_input(numline)
                    else:
                        print('intek-sh: {}: event not found'.format(command))
            else:
                numline = int(command[1:])
                self.do_past_input(numline)

        except (IndexError, ValueError):
            print('intek-sh: {}: event not found'.format(command))
        except RecursionError:
            pass

    # do command from history
    def do_past_input(self, numline):
        with open('.history.txt', 'r') as history_file:
            content = history_file.readlines()
            if numline > 0:
                line_content = content[numline - 1].split('\t')[1].strip()
            elif numline == 0:
                print('intek-sh: !0: event not found')
                return
            else:
                line_content = content[numline].split('\t')[1].strip()
            line_contents = split(line_content, posix=True)

            print(line_content)
            self.execute_commands(line_contents, line_content)

    # execute external command
    def do_external(self, user_input):
        command = user_input[0]
        # if command is an executable file
        if command.startswith('./') or command.startswith('../'):
            self.run_file(user_input)
        elif command is 'false':
            self.exit_code = 1
        elif command is 'true':
            self.exit_code = 0
        # if command is not an executable file
        else:
            self.run_binary(user_input)

    # run the executable file
    def run_file(self, user_input):
        self.handle_signal(True)
        command = user_input[0]
        try:
            # catch if only ./ is prompted in
            if command == './' or command == '../':
                print('intek-sh: {}: Is a directory'.format(command))
                self.exit_code = 126
            else:
                # run the file
                child = Popen(user_input)
                self.pid_list.append(child.pid)
                child.wait()
                self.exit_code = child.returncode
        # catch if no execute permission on the file
        except PermissionError:
            print('intek-sh: {}: Permission denied'.format(command))
            self.exit_code = 126
        # catch if the file doesn't exist
        except FileNotFoundError:
            print('intek-sh: {}: No such file or directory'.format(command))
            self.exit_code = 127
        # catch if file is not an executable file
        except OSError:
            self.exit_code = 0
            pass

    # run the external binaries
    def run_binary(self, user_input):
        self.handle_signal(True)
        command = user_input[0]
        try:
            if isdir(command):
                print('intek-sh: {}: Is a directory'.format(command))
                self.exit_code = 126
            else:
                # get paths to external binaries indicated by variable PATH
                paths = environ['PATH'].split(':')
                # check if the command is in paths
                if command and (exists(path + '/' + command)
                                for path in paths):
                    child = Popen(user_input)
                    self.pid_list.append(child.pid)
                    child.wait()
                    if child.returncode < 0:
                        self.exit_code = 128 - child.returncode
                    else:
                        self.exit_code = child.returncode
        # catch if the command doesn't exist
        except FileNotFoundError:
            print('intek-sh: {}: command not found'.format(command))
            self.exit_code = 127
        # catch if PATH variable doesn't exist
        except KeyError:
            print('intek-sh: {}: No such file or directory'.format(command))
            self.exit_code = 127
        # catch if no execute permission on the command
        except PermissionError:
            print('intek-sh: {}: Permission denied'.format(command))
            self.exit_code = 126


# Run the Shell
if __name__ == '__main__':
    Shell()
