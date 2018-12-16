from shlex import split


def write_history(command, raw_input):
    if raw_input:
        with open(".history.txt", 'a+') as history_file:
            should_write = True
            # get line number
            history_file.seek(0)
            num_line = sum(1 for line in history_file) + 1
            # get content of history file
            history_file.seek(0)
            content = history_file.readlines()

            # check if history file is not empty
            if num_line > 1:

                last_line = content[-1].split('\t')
                last_input = last_line[1].strip()

                # input duplicate, should not write
                if raw_input == last_input or raw_input.startswith('!'):
                    should_write = False

            elif command == '!!' and not content:
                should_write = False

            if should_write:
                history_file.write(str(num_line) + '\t' + raw_input + '\n')


def print_newest_history(n):
    try:
        exit_code = 0
        with open('.history.txt', 'r') as history_file:
            # get content of history file
            content = history_file.readlines()
            # print n newest lines
            for line in content[-int(n):]:
                print('  ' + line.strip())
        return exit_code
    except ValueError:
        exit_code = 1
        print('intek-sh: history: {}: numeric argument required'.format(n))
        return exit_code
