from os.path import expanduser, expandvars
from os import getenv


def tilde_expans(path):
    expanded = expanduser(path)
    if expanded.startswith('~'):
        if expanded.startswith('~+'):
            expanded = expanded.replace('~+', getenv('PWD'), 1)
        elif expanded.startswith('~-'):
            expanded = expanded.replace('~-', getenv('OLDPWD'), 1)
        else:
            pass
    return expanded


def para_expans(path):
    var = expandvars(path)
    if '$' in var:
        i = var.index('$') + 1
        j = i
        while j < len(var) and var[j].isalnum() and var[j] != ' ':
            j+=1
        return var[:i-1] + var[j:]
    else:
        return var


def path_expans_one(path):
    if path.startswith('~'):
        return tilde_expans(path)
    elif '$' in path:
        return para_expans(path)


def path_expans(inp):
    path_expaned = []
    for arg in inp:
        if '$' in arg or '~' in arg:
            path_expaned.append(path_expans_one(arg))
        else:
            path_expaned.append(arg)
    return path_expaned


if __name__ == '__main__':
    print(path_expans('~/*'))
