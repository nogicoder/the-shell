from shlex import split


def process_new_line(new_line, user_input, quote):
    j = 0
    try:
        while new_line[j] != quote:
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
        

def adding_backslash(raw_input):
    quotes = ['"', "'", '`', '\\']
    if not any(quote in raw_input for quote in quotes):
        user_input = raw_input
    else:
        user_input = ''
        i = 0
        while i < len(raw_input):
            if raw_input[i] not in quotes:
                user_input += raw_input[i]
            else:
                quote = raw_input[i]
                if quote in ['`', '\\'] :
                    user_input += '"' + quote
                else:
                    user_input += '\\' + quote + quote
                i += 1
                try:
                    while raw_input[i] != quote:
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
