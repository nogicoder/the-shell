# convert $? to exit code
def handle_exit_code(raw_input, exit_code):
    user_input = raw_input
    if '$?' in raw_input:
        user_input = raw_input.replace('$?', str(exit_code))
        if '${?}' in user_input:
            user_input = user_input.replace('${?}', str(exit_code))
    return user_input


def error_flag_handle(error_flag):
    if not error_flag:
        return 0
    return 1
