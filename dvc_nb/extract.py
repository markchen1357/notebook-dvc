import yaml
import sys
import re
import os

def cleanup(str):
    start = str.lstrip(' ')
    space = (len(str)-len(start))*' '
    
    if start.startswith('import IPython') or str.startswith('ipython_shell ='):
        return None
    if start.startswith('ipython_shell.run_line_magic('):
        extract = start[len('ipython_shell.run_line_magic('):]
        command = extract.split(',')[0].strip(' \'')
        param = extract.split(',')[1].strip(' \')\n')
        return '%{}{}{}\n'.format(space, command, param)

    if start.startswith('os.system('):
        extract = start[len('os.system('):]
        command = extract.strip(' )\'\n')
        return '!{}{}\n'.format(space, command)
    return str


def replace_sys_gen(deps):
    def replace_sys(match):
        return '\'{}\''.format(deps[int(match.group(1))-1])
    return replace_sys


def extract_cell(code_file, num, deps):
    replace_sys = replace_sys_gen(deps)
    flag = 0
    space = ''
    code = open(code_file, 'r')
    new_code = []
    for line in code:
      
        if flag == 1:
            if len(line) - len(line.lstrip(' ')) > space:
                continue 
            else:
                flag = 0
    
        if 'len(sys.argv)' in line:
            flag = 1
            space = len(line) - len(line.lstrip(' '))
            continue
        new_code.append(re.sub('sys.argv\[(\d+)\]', replace_sys, line))

    if not os.path.exists('notebook'):
        os.mkdir('notebook')

    with open('notebook/cell{}.py'.format(num), 'w') as f:

        load_code = False
        cell_code = False
        for line in new_code:
            if line.strip(' ') == '\n':
                line = line.strip(' ')
            if load_code:
                if line.startswith('def cell('):
                    load_code = False
                    cell_code = True
                    continue
                else:
                    continue
            if line.startswith('def load('):
                load_code = True
                continue
            if line.startswith('def cell('):
                cell_code = True
                continue
        
            if (line.startswith('    return ') and cell_code) or line.startswith('def store(') or line.startswith('def main('):
                break

            original = len(line)
            line = line.lstrip(' ')
            addback = original - len(line) - 4
            line = cleanup(line)
            if line is None:
                continue
            if addback > 0:
                line = ' '*addback + line
            f.write(line)

def extract_cells():
    dvc_file = yaml.safe_load(open('dvc.yaml'))
    for i,(name,stage) in enumerate(dvc_file['stages'].items()):
        code_file = stage['cmd'].split(' ')[1]
        deps = stage['cmd'].split(' ')[2:]
        extract_cell(code_file, i, deps)
    return len(dvc_file['stages'])









    
        
        



