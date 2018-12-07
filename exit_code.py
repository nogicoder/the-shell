# convert $? to exit code
def handle_exit_code(user_input, exit_code):
    if '$?' in user_input:
        pos = user_input.index('$?')
        user_input[pos] = str(exit_code)
    if '${?}' in user_input:
        pos = user_input.index('${?}')
        user_input[pos] = str(exit_code)
    return user_input
