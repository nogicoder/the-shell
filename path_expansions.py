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


def strip_bracket(var):
    i = var.index('${')
    j = var.index('}')
    while j < i:
        try:
            j = var[j+1:].index('}') + (j + 1)
        except ValueError:
            break
    return var[:i] + var[j+1:] if i < j else var


def strip_var(var):
    i = var.index('$')
    j = i + 1
    while j < len(var) and var[j].isalnum() and var[j] != ' ':
        j += 1
    return var[:i] + var[j:]


def para_expans(path):
    var = expandvars(path)
    if '$' in var:
        if var == '$':
            return var
        elif '${' in var and '}' in var:
            return strip_bracket(var)
        else:
            return strip_var(var)
    else:
        return var


def path_expans_one(path):
    try:
        if path.startswith('~'):
            return tilde_expans(path)
        elif '$' in path:
            return para_expans(path)
    except Exception:
        return path


def path_expans(inp):
    path_expaned = []
    try:
        for arg in inp:
            if '$' in arg or '~' in arg:
                path_expaned.append(path_expans_one(arg))
            else:
                path_expaned.append(arg)
        return path_expaned
    except Exception:
        print('Path expandsion: case not included')


if __name__ == '__main__':
    print(path_expans('~/*'))
