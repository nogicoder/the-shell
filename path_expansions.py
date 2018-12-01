from os.path import expanduser, expandvars
from os import getenv


# def get_dirs_stack(expanded):
#     if expanded[1:].isdigit():
#         pass
#     elif expanded.startswith('~+') or expanded.startswith('~-'):
#         if expanded[2:].isdigit():
#             pass
#     return expanded


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
    return expandvars(path)


def path_expans(path):
    if path.startswith('~'):
        return tilde_expans(path)
    elif path.startswith('$'):
        return para_expans(path)



if __name__ == '__main__':
    print(path_expans('~-/'))
