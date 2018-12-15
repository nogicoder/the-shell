from subprocess import Popen, PIPE
from intekshell import Shell
import shlex

def pipe(inp):
    inputs = inp.split('|')
    print(inputs)
    processes = {}
    i = 0
    for command in inputs:
        command = shlex.split(command.strip())
        print(command)
        if i == 0:
            print(i)
            processes[i] = Popen(command, stdout=PIPE, stdin=None, stderr=PIPE)
        else:
            print(i)
            processes[i] = Popen(command, stdout=PIPE, stdin=processes[i-1].stdout, stderr=PIPE)
            processes[i-1].stdout.close()
            print(i)

        i = i + 1
        (output, err) = processes[i - 1].communicate()
        exit_code = processes[0].wait()
        print(processes)

    return output.decode(), err.decode(), exit_code


if __name__ == '__main__':
    print(pipe('ls | grep a')[0])
    # print(pipe('ls| grep --color=auto a'))


