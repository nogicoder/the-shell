from subprocess import run


# logical operator handling feature
def logical_operator(self, inputs):
    # base case for recursion - if no logical operator in inputs
    if '&&' not in inputs and '||' not in inputs:
        self.user_input = split(inputs, posix=True)
        command = self.user_input[0]
        if command in self.builtins:
            self.do_builtin(command)
        else:
            self.do_external(command)
        return self.exit_code
    # if logical operator in inputs
    else:
        # if both in inputs
        if '&&' in inputs and '||' in inputs:
            pos1 = inputs.index('&&', 1)
            pos2 = inputs.index('||', 1)
            # if the first logical operator is &&
            if pos1 < pos2:
                left = inputs[:pos1 - 1]
                right = inputs[pos1 + 3:]
                expected = True
            # if the first logical operator is ||
            else:
                left = inputs[:pos2 - 1]
                right = inputs[pos2 + 3:]
                expected = False
        # if only && in inputs
        elif '&&' in inputs and '||' not in inputs:
            pos1 = inputs.index('&&', 1)
            left = inputs[:pos1 - 1]
            right = inputs[pos1 + 3:]
            expected = True
        # if only || in inputs
        elif '||' in inputs and '&&' not in inputs:
            pos2 = inputs.index('||', 1)
            left = inputs[:pos2 - 1]
            right = inputs[pos2 + 3:]
            expected = False
        self.user_input = split(left, posix=True)
        command = self.user_input[0]
        if command in self.builtins:
            self.do_builtin(command)
        else:
            self.do_external(command)
        # if exit_code is not what the condition expects then return
        if not self.exit_code != expected:
            return self.exit_code
        else:
            self.logical_operator(right)
