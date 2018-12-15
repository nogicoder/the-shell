from subprocess import Popen
from subprocess import PIPE

def pipe(inp):
    inputs = inp.split('|')
    for i, command in enumerate(inputs):
        cmd = command.strip().split()
        p = Popen(cmd, stdout=PIPE, stdin=PIPE if i != 0 else None)
        print('Stdin: %s' % (p.stdin))
        print('Stdout: %s' % (p.stdout))
    return p.communicate()[0].decode()


if __name__ == '__main__':
    print(pipe('ls -l| grep a| echo 3333333'))
    # print(pipe('ls| grep --color=auto a'))