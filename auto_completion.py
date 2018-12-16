#!/usr/bin/env python3

import readline
from os import listdir, getcwd, environ
from os.path import exists, isdir


# create a manual Completer object
class Completer:

    def __init__(self):
        # create list of options: key is command, value is files
        self.options = self.get_namespace()
        # create list of files
        self.files = []

    def get_namespace(self):
            names = []
            namespace = {}
            file_names = listdir(getcwd())
            try:
                paths = environ['PATH'].split(':')
                for item in paths:
                    if exists(item) and isdir(item):
                        names += listdir(item)
                        names += ['exit', 'printenv', 'export',
                                  'unset', 'cd', 'history']
                for name in names:
                    if name:
                        name += ' '
                        namespace[name] = file_names
                return namespace
            except KeyError:
                return {}

    # create the method for completion
    def complete(self, text, state):
        # set the condition to evoke the files list for users
        response = None

        # if the command is being typed in but not yet the arguments
        if state == 0:

            # return current contents of the line
            origline = readline.get_line_buffer()
            # get the beginning index of the unfinished command
            begin = readline.get_begidx()
            # get the ending index of the unfinished command
            end = readline.get_endidx()
            # get the unfinished element
            being_completed = origline[begin:end]
            # split the whole input into list (if space between)
            words = origline.split()

            # if the list is empty -> nothing is typed in
            if not words:
                # choices list will be the commands
                self.choices = sorted(self.options.keys())
            else:
                try:
                    # if the uncompleted element is the first element
                    if begin is 0:
                        choices = self.options.keys()
                    # if the uncompleted element is the second element
                    else:
                        command = words[0] + ' '
                        choices = self.options[command]
                    # choices for the uncompleted element
                    if being_completed:
                        self.choices = [
                            w for w in choices
                            if w.startswith(being_completed)
                        ]
                    # choices for the empty string
                    else:
                        self.choices = choices
                    # catching error returning empty list
                    # (when no matching found)
                except (KeyError, IndexError) as err:
                    self.choices = []

        try:
            # display all candidates
            choice = self.choices[state]
            # no matching found
        except IndexError:
            choice = None
        # return the choice to choose from
        return choice


def input_loop():
    line = ''
    while line != 'stop':
        line = input('intek-sh$: ')


def Initialize_completion():
    # Register our completer function
    completer = Completer()
    # if only 1 candidates. the readline completer will complete immediately
    readline.set_completer(completer.complete)
    # Use the tab key for completion
    readline.parse_and_bind('tab: complete')


if __name__ == '__main__':
    Initialize_completion()
    # Prompt the user for text
    input_loop()
