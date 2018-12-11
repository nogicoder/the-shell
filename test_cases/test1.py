def test(flag=True):
    if flag:
        return 'aa'
    else:
        pass

print(test())
print(test(False))