# from os import fork, waitpid
#
#
# def handle_backquotes(user_input, ):
#     arg_lst = []
#     for item in user_input:
#         if "`" in item:
#             result=''
#             i = 0
#             while i < len(item):
#                 if item[i] != '`':
#                     result += item[i]
#                     i += 1
#                 elif item[i] == '`':
#                     temp = ''
#                     i += 1
#                     while item[i] != '`':
#                         temp += item[i]
#                         i += 1
#                     result += execute_cmd(temp)
#                     i += 1
#         else:
#             result = item
#         arg_lst.append(result)
#     return arg_lst
#
#
# def execute_cmd(item):
#     user_item = split(item, posix=True)
#     child = os.fork()
#     if not child:
#         execute_cmd(user_item, item)
