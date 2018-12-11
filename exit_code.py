# convert $? to exit code
def handle_exit_code(user_input, exit_code):
    if '$?' in user_input:
        pos = user_input.index('$?')
        user_input[pos] = str(exit_code)
    if '${?}' in user_input:
        pos = user_input.index('${?}')
        user_input[pos] = str(exit_code)
    return user_input


def error_flag_handle(error_flag):
    if not error_flag:
        return 0
    return 1
