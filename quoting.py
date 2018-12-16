from shlex import split
from path_expansions import path_expans
from globbing import globbing
from exit_code import handle_exit_code


def process_new_line(new_line, user_input, quote):
    j = 0
    glob_sign = ['*', '?', '[', ']']
    try:
        while new_line[j] != quote:
            if new_line[j] in glob_sign:
                user_input += '\\' + new_line[j]
            else:
                user_input += new_line[j]
            j += 1
        if quote in ['`', '\\']:
            user_input += quote + '"'
        else:
            user_input += quote + '\\' + quote
    except IndexError:
        one_new_line = '\n' + input('>')
        user_input = process_new_line(one_new_line, user_input, quote)
    return user_input


def adding_backslash(raw_input, user_input=''):
    quotes = ['"', "'", '`']
    glob_sign = ['*', '?', '[', ']']
    if not any(quote in raw_input for quote in quotes):
        user_input = raw_input
    else:
        i = 0
        while i < len(raw_input):
            if raw_input[i] not in quotes or raw_input[i - 1] == '\\':
                user_input += raw_input[i]
            else:
                quote = raw_input[i]
                if quote in ['`', '\\']:
                    user_input += '"' + quote
                else:
                    user_input += '\\' + quote + quote
                try:
                    i += 1
                    while raw_input[i] != quote:
                        if raw_input[i] in glob_sign:
                            user_input += '\\' + raw_input[i]
                        else:
                            user_input += raw_input[i]
                        i += 1
                    if quote in ['`', '\\']:
                        user_input += quote + '"'
                    else:
                        user_input += quote + '\\' + quote
                except IndexError:
                    new_line = '\n' + input('>')
                    user_input = process_new_line(new_line, user_input, quote)
            i += 1
    return user_input


def handle_single_quote(item, pos1, pos2, exit_code):
    if pos1 < pos2:
        temp_left = handle_exit_code(item[:pos1], exit_code)
        left = " ".join(path_expans(split('"' + temp_left + '"', posix=True)))
        mid = item[pos1 + 1:pos2]
        temp_right = handle_exit_code(item[pos2 + 1:], exit_code)
        right = " ".join(path_expans(split('"' + temp_right + '"', posix=True)))
    elif pos1 > pos2:
        left = item[:pos2]
        temp_mid = handle_exit_code(item[pos2 + 1:pos1], exit_code)
        mid = " ".join(path_expans(split('"' + temp_mid + '"', posix=True)))
        right = item[pos1 + 1:]

    if "'" in mid:
        pos1 = mid.index("'", 0)
        pos2 = len(mid) - mid[::-1].index("'") - 1
        mid = handle_single_quote(mid, pos2, pos1, exit_code)
    if left and right:
        item = left + mid + right
    elif left and not right:
        item = left + mid
    elif right and not left:
        item = mid + right
    else:
        item = mid
    return item


def split_output(result):
    res = []
    for elem in result:
        res.extend(elem.split(" "))
    return res


def handle_quotes(user_input, exit_code):
    result = []
    for item in user_input:
        if '"' in item and "'" in item:
            pos1 = item.index("'", 0)
            pos2 = item.index('"', 0)
            pos3 = len(item) - item[::-1].index("'") - 1
            pos4 = len(item) - item[::-1].index('"') - 1
            # if single quote open (and close)
            if pos1 < pos2:
                item = handle_single_quote(item, pos1, pos3, exit_code)
            # if double quote open (and close)
            else:
                item = handle_exit_code(item, exit_code)
                item = " ".join(path_expans(split("'" + item + "'", posix=True)))
        elif '"' in item and "'" not in item:
            item = handle_exit_code(item, exit_code)
            item = " ".join(path_expans(split("'" + item + "'", posix=True)))
        elif "'" in item and '"' not in item:
            pos1 = item.index("'", 0)
            pos2 = len(item) - item[::-1].index("'") - 1
            item = handle_single_quote(item, pos1, pos2, exit_code)
        else:
            item = handle_exit_code(item, exit_code)
            if "'" in item:
                item_list = split('"' + item + '"', posix=True)
            else:
                item_list = split("'" + item + "'", posix=True)
            item = " ".join(path_expans(item_list))
        item_list = split("'" + item + "'", posix=True)
        item = " ".join(globbing(item_list))
        result.append(item)
    splited = split_output(result)
    return splited
