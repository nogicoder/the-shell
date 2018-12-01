def globbing(inp):
    '''
    input: path patern
    output: list of posible path'''
    from glob import glob
    return glob(inp)


if __name__ == '__main__':
    print(globbing('*.??'))
