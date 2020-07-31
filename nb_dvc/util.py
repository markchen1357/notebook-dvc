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
    param = ''
    if len(str.split(' ')) > 1:
        param = ' '.join(str.split(' ')[1:])
    return 'ipython_shell.run_line_magic(\'{}\', \'{}\')\n'.format(command, param)

def is_print(str):
    match = re.fullmatch('print(.*)', str)
    if match:
        return True
    else:
        return False

def is_shell(str):
    return str[0] == '!'

def replace_shell(str):
    str = str.strip('\n')
    return 'os.system(\'{}\')\n'.format(str.split('!', 1)[1])

def mult_assign(str):
    match = re.fullmatch("([^']+,)+[^']+=.*", str)

def extract_mult_assign(str):
    str = str.strip('\n ').split('=')[0]
    return [var.strip(' ') for var in str.split(',')]

def is_param_line(line, params):
    for p in params:
        regex = ' *{} *=(.+)'.format(p)
        match = re.fullmatch(regex,line, re.DOTALL)
        if match:
            value = match.group(1).strip(' \n')
            return True, p, value 
    return False, None, None

def modify_param_line(param,stage):
    return '{} = yaml.safe_load(open(\'params.yaml\'))[\'{}\'][\'{}\']\n'.format(param, stage, param)




        