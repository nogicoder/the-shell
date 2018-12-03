#!/usr/bin/env python3

from os import chdir, environ, getcwd
from os.path import dirname, exists
from shlex import split
from subprocess import run

'''----------------------Create a Shell Object-----------------------------'''


class Shell:
    # Initialize Shell
    def __init__(self):
        # list of built-in features
        self.builtins = ['exit', 'printenv', 'export', 'unset', 'cd', 'history']
        # run the REPL
        loop = True
        while loop:
            # get inputs from user as a list
            self.inp = input('intek-sh$ ')
            self.user_input = split(self.inp, posix=True)

            if self.inp is not '' and not self.inp.startswith('!'):
                # write history file
                self.write_history(self.inp)
            try:                
                command = self.user_input[0]
                # check if command is a built-in
                if command in self.builtins:
                    self.do_builtin(command)
                # check if command is '!*'
                elif command.startswith('!'):
                    self.do_exclamation(command)
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
            if '=' in item:
                items = item.split('=', 1)
                if len(items) is 2 and items[0]:
                    environ[items[0]] = items[1]
                else:
                    print('intek-sh: export:' +
                          ' `%s\': not a valid identifier' % (item))
            else:
                # handle the case ''; '   '; 'b    a'
                item_strip = item.strip().split(' ')
                if len(item_strip) is 1 and item_strip[0]:
                    pass
                else:
                    print('intek-sh: export:' +
                          ' `%s\': not a valid identifier' % (item))

    # unset feature
    def unset(self):
        for key in self.user_input[1:]:
            try:
                # handle the case ''; '   '; 'b    a'
                key_strip = key.strip().split(' ')
                if len(key_strip) is 1 and key_strip[0]:
                    try:
                        del environ[key]
                    # catch if key not an environ variables
                    except KeyError:
                        pass
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
            if (exists(path + '/' + command) for path in paths):
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
            # delete option 'history -d offset'
            elif '-d' in self.user_input[1]:
                self.delete_history()
            # display [n] newest history 'history [n]'
            else:
                # number of last lines need to print
                n = self.user_input[1]
                # function to print
                self.print_newest_history(n)
    
    def write_history(self, inp):
        with open("history.txt", 'a+') as history_file:
            # when open in 'a+', offset at end of file, move to begining
            history_file.seek(0)
            # get the next line number
            num_line = sum(1 for line in history_file) + 1
            history_file.seek(0)
            # get content of history file
            content = history_file.readlines()
            # check if history file is not empty
            if num_line > 1:
                should_write = True
                last_line = content[-1].split('\t')
                last_inp = last_line[1].strip()
                # check if current input == last input, should not write
                if inp == last_inp:
                    should_write = False
            # if history file is empty
            else:
                should_write = True
            # write to history file
            if should_write:
                history_file.write(str(num_line) + '\t' + inp + '\n')
    
    def delete_history(self):       # not finish, buggy
        # get the 'offset'
        offset_index = self.user_input.index('-d') + 1
        offset = self.user_input[offset_index]
        with open('history.txt', 'r+') as history_file:
            num_line = 1
            content = history_file.readlines()
            history_file.seek(0)
            for line in content:
                line = line.strip().split('\t')
                if not offset is line[0]:
                    history_file.write(str(num_line) + '\t' + line[1] + '\n')
                    num_line += 1
    
    def print_newest_history(self, n):
        try:
            with open('history.txt', 'r') as history_file:
                # get content of history file
                content = history_file.readlines()
                # print n newest lines 
                for line in content[-int(n):]:
                    print('  ' + line.strip())
        except ValueError:
            print('intek-sh: history: %s: numeric argument required' % (n))
    
    def do_exclamation(self, command):
        # print(self.user_input)
        # print(command)
        numline = int(command[1:])
        with open('history.txt','r') as history_file:
            content = history_file.readlines()
            line_content = content[numline - 1].split('\t')[1].strip()
            print(line_content)

            line_contents = split(line_content, posix=True)
            if line_content is not '':
                # write history file
                self.write_history(line_content)
            try:                
                command = line_contents[0]
                # check if command is a built-in
                if command in self.builtins:
                    self.do_builtin(command)
                # check if command is '!*'
                elif command.startswith('!'):
                    self.do_exclamation(command)
                # if command is not a built-in
                else:
                    self.do_external(command)
            # catch EOFError when no input is prompted in
            # catch IndexError when nothing is input in (empty input list)
            except IndexError:
                pass


# Run the Shell
if __name__ == '__main__':
    Shell()
