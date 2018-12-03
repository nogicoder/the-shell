def globbing_one(arg):
    '''
    input: path patern
    output: list of posible path'''
    from glob import glob
    value = glob(arg)
    if arg == '.*':
        value.extend(['.', '..'])
    return sorted(value) if value else [arg]


def globbing(inp):
    glob_op = []
    for arg in inp:
        if '*' in arg or '?' in arg or ('[' in arg and ']' in arg):
            glob_op.extend(globbing_one(arg))
        else:
            glob_op.append(arg)
    return glob_op


if __name__ == '__main__':
    print(globbing('ashgajd'))
