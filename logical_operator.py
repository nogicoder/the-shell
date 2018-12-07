from shlex import split


def check_operator(inputs):
    flag = False
    for char in split(inputs, posix=True):
        if char in ['&&', '||']:
            flag = True
    if flag:
        if '&&' in inputs and '||' in inputs:
            pos1 = inputs.index('&&', 1)
            pos2 = inputs.index('||', 1)
            # if the first logical operator is &&
            if pos1 < pos2:
                operator = '&&'
                inputs = inputs.split('&&', 1)
            # if the first logical operator is ||
            else:
                operator = '||'
                inputs = inputs.split('||', 1)
        # if only && in inputs
        elif '&&' in inputs and '||' not in inputs:
            operator = '&&'
            inputs = inputs.split('&&', 1)
        # if only || in inputs
        elif '||' in inputs and '&&' not in inputs:
            operator = '||'
            inputs = inputs.split('||', 1)
        return operator + inputs[1]
    return flag
