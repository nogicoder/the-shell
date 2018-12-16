from os.path import expanduser, expandvars
from os import getenv


def expand_pwd(path):
    if getenv('PWD'):
        return path.replace('~+', getenv('PWD'), 1)
    else:
        return path


def expand_oldpwd(path):
    if getenv('OLDPWD'):
        return path.replace('~-', getenv('OLDPWD'), 1)
    else:
        return path


def tilde_expand_one(elem):
    expanded = expanduser(elem)
    if expanded.startswith('~'):
        if expanded.startswith('~+'):
            expanded = expand_pwd(expanded)
        elif expanded.startswith('~-'):
            expanded = expand_oldpwd(expanded)
    return expanded


def tilde_expans_elem(elems):
    expand_elems = []
    for elem in elems:
        expanded = tilde_expand_one(elem)
        expand_elems.append(expanded)
    return expand_elems


def tilde_expans_side(sides):
    expand_sides = []
    for side in sides:
        if ':' in side:
            elems = side.split(':')
            expand_elems = tilde_expans_elem(elems)
            expand_sides.append(':'.join(expand_elems))
        else:
            expand_sides.append(tilde_expand_one(side))
    return expand_sides


def tilde_expans(path):
    if '~' in path:
        if '=' in path:
            sides = path.split('=', 1)
            expand_sides = tilde_expans_side(sides)
            return '='.join(expand_sides)
        else:
            return tilde_expand_one(path)
    else:
        return path


def find_bracket(var):
    try:
        i = var.index('${')
        j = var.index('}')
        while j < i:
            try:
                j = var[j+1:].index('}') + (j + 1)
                if i < j:
                    break
            except ValueError:
                break
        return i, j
    except Exception:
        pass


def find_var(var):
    try:
        i = var.index('$')
        j = i + 1
        while (j < len(var) and (var[j].isalnum() or var[j] is '_')
               and var[j] != ' '):
            j += 1
        return i, j
    except ValueError:
        pass


def has_bad_substitution(var):
    # if bracket has irregular character inside then True
    try:
        i, j = find_bracket(var)
        bracket = var[i:j+1]
        item = ['.', '#', '!', '%', '*', '@', '&', '(', ')']
        if any(x in bracket for x in item):
            return True
        # if bracket is empty then True
        elif j == i + 2:
            return True
        else:
            return False
    except Exception:
        return False


def is_good_pattern_bracket(var):
    i, j = find_bracket(var)
    if i < j:
        if has_bad_substitution(var):
            return False
        else:
            return True
    else:
        return False


def is_good_pattern_var(var):
    i, j = find_var(var)
    # if var[i:j] is $ then no need to strip
    return j > i + 1


def is_good_pattern(var):
    if '$' in var:
        if '${' in var:
            return is_good_pattern_bracket(var)
        else:
            return is_good_pattern_var(var)
    else:
        return False


def update_var(var, old, new):
    if new == old:
        updated = var.replace(old, '', 1)
    else:
        updated = var.replace(old, new, 1)
    return updated


def para_expans_bracket(var):
    i, j = find_bracket(var)
    bracket = var[i:j+1]
    new_var = expandvars(bracket)
    return update_var(var, bracket, new_var)


def para_expans_var(var):
    i, j = find_var(var)
    little_var = var[i:j]
    new_var = expandvars(little_var)
    return update_var(var, little_var, new_var)


def para_expans_one(var):
    i = var.index('$')
    if var[i+1] is '{' and '}' in var:
        return para_expans_bracket(var)
    else:
        return para_expans_var(var)


def para_expans(var):
    if '$' in var:
        if var == '$':
            return var
        else:
            var = para_expans_one(var)
        if is_good_pattern(var):
            var = para_expans(var)
    return var


def path_expans_one(path):
    try:
        if '~' in path or '$' in path:
            return para_expans(tilde_expans(path))
        else:
            return path
    except Exception:
        return path


def path_expans(inp):
    path_expaned = []
    glob_sign = ['\\*', '\\?', '\\[', '\\]']
    try:
        for arg in inp:
            if '\\$' in arg or '$\\' in arg:
                pos = arg.index('\\')
                arg = path_expans_one(arg[:pos]) + arg[pos + 1:]
                path_expaned.append(arg)
            elif '\\' in arg:
                pos = arg.index('\\')
                if all(i not in arg for i in glob_sign):
                    arg = path_expans_one(arg[:pos]) + arg[pos + 1:]
                    path_expaned.append(arg)
                else:
                    arg = path_expans_one(arg[:pos]) + arg[pos:]
                    path_expaned.append(arg)
            elif '$' in arg or '~' in arg:
                if '${' in arg:
                    if has_bad_substitution(arg):
                        print('intek-sh: {}: bad substitution'.format(arg))
                        return []
                    else:
                        path_expaned.append(path_expans_one(arg))
                else:
                    path_expaned.append(path_expans_one(arg))
            else:
                path_expaned.append(arg)
        return path_expaned
    except Exception as error:
        print('Path expansion: case not incuded')
        return []
