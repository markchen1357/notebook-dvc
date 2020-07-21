class undefined_magic(Exception):
    pass

def get_magic(str):
    magic_funcs = {}
    if str.strip('\n') in magic_funcs:
        return magic_funcs[str.strip('\n')]
    else:
        raise undefined_magic