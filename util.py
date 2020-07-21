import re

def empty_cell(cell):
    for line in cell['source']:
        if line != '\n':
            return False
    
    return True

def single_quotes(str):
    return str[:len(str)-1].count('\'') % 2 == 1

def double_quotes(str):
    return str[:len(str)-1].count('\"') % 2 == 1

def in_quotes(str):
    if len(str) < 1:
        return False
    return single_quotes(str) or double_quotes(str)

def is_import(str):
    if str.find('import ') == 0:
        return True

    ind = str.find(' import ')
    cutoff = ind + len(' import ')
    if str.find('from ') == 0 and ind != -1 and not in_quotes(str[:cutoff]):
        return True
    return False

def is_magic(str):
    ind = str.find('%')
    cutoff = ind + len('%')
    if ind != -1 and not in_quotes(str[:cutoff]):
        return True
    return False

def replace_magic(str):
    str = str.strip('%\n')
    command = str.split(' ')[0]
    if len(str.split(' ')) > 1:
        param = ' '.join(str.split(' ')[1:])
    return 'ipython_shell.run_line_magic(\'{}\', \'{}\')\n'.format(command, param)
        