def quote(s):

    if '"' in s:
        return '"'
    elif "'" in s:
        return "'"
    elif '`' in s:
        return '`'
    return None
