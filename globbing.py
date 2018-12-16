from glob import glob
from os import listdir, getcwd
from fnmatch import fnmatch
from os import path


def glob_basic(arg):
        value = glob(arg)
        return sorted(value) if value else [arg]


def get_match_dir(dirs, pat):
    match_dirs = []
    for dir in dirs:
        if fnmatch(dir, pat):
            match_dirs.append(dir)
    return match_dirs


def find_in_root(root, base, arg):
    roots = glob(arg)
    if roots:
        child_dirs = []
        for dir in roots:
            child_dirs.extend(listdir(dir))
        return get_match_dir(child_dirs, base)
    else:
        return [arg]


def find_in_curdir(arg):
    dirs = listdir(getcwd())
    dirs.extend(['.', '..'])
    match_dirs = get_match_dir(dirs, arg)
    return match_dirs if match_dirs else [arg]


def get_hidden_dir(arg):
    return find_in_curdir(arg)


def globbing_one(arg):
    try:
        if arg.startswith('.*') or arg.startswith('..*'):
            return get_hidden_dir(arg)
        else:
            if arg is glob_basic(arg)[0] and '\\' in arg:
                temp = []
                pos = arg.index('\\')
                arg = arg[:pos] + arg[pos + 1:]
                temp.append(arg)
                return temp
            return glob_basic(arg)

    except Exception:
        return [arg]


def globbing(inp):
    globbed = []
    try:
        for arg in inp:
            if any(x in arg for x in ['*', '?', '[', ']']):
                globbed.extend(globbing_one(arg))
            else:
                globbed.append(arg)
        return globbed
    except Exception:
        print('Globbing: Case not included')
