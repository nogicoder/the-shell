from subprocess import run


def logical_operator(inputs):

    if '&&' not in inputs and '||' not in inputs:
        exit_code = run(inputs.split()).returncode
        print(exit_code)
        return exit_code
    else:
        if '&&' in inputs and '||' in inputs:
            pos1 = inputs.index('&&', 1)
            pos2 = inputs.index('||', 1)
            if pos1 < pos2:
                left = inputs[:pos1 - 1]
                right = inputs[pos1 + 3:]
                expected = True
            else:
                left = inputs[:pos2 - 1]
                right = inputs[pos2 + 3:]
                expected = False
        elif '&&' in inputs and '||' not in inputs:
            pos1 = inputs.index('&&', 1)
            left = inputs[:pos1 - 1]
            right = inputs[pos1 + 3:]
            expected = True
        elif '||' in inputs and '&&' not in inputs:
            pos2 = inputs.index('||', 1)
            left = inputs[:pos2 - 1]
            right = inputs[pos2 + 3:]
            expected = False
        exit_code = run(left.split()).returncode
        if not exit_code != expected:
            return exit_code
        else:
            logical_operator(right)
