import sys
from pathlib import Path
import os
import ast
import util
from collections import defaultdict
import re

indent = '    '


def ind_str(str):
    return '{}{}'.format(indent, str)


def make_code():
    if not os.path.exists('./code'):
        os.mkdir('./code')


def delete_file(file):
    return "if os.path.exists(\'{}\'):\n{}{}os.remove('{}')\n".format(file, indent, indent, file)


def load_dep(dep_file):
    if not os.path.exists(dep_file):
        sys.exit("no dependency file")
    return open(dep_file)

def get_outputs(dep_file):
    cell_outputs = defaultdict(lambda: [])
    with open(dep_file, 'r') as f:
        for line in f:
            d, u, v = ast.literal_eval(line)
            cell_outputs[d].append(v)
    return cell_outputs

def get_inputs(dep_file):
    cell_inputs = defaultdict(lambda: [])
    with open(dep_file,'r') as f:
        for line in f:
            d,u,v = ast.literal_eval(line)
            cell_inputs[u].append(v)
    return cell_inputs

def reduce_imports(imports, cell):
    reduced = []
    for i in imports:
        i = i.strip('\n')
        if i.startswith('import '):
            if ' as ' in i:
                target = [i.split(' as ')[1]]
            else:
                target = [i.split('import ')[1]]

        if i.startswith('from '):
            if ' *' in i:
                reduced.append(i+'\n')
                continue
            else:
                target = i.split('import ')[1].split(', ')
        used = False
        cell.seek(0)
        for line in cell:
            for t in target:
                if t in line:
                    used = True
        if used:
            reduced.append(i+'\n')
    return reduced


def write_imports(file, imports, cell, magic):
    # need to not repeat imports
    
    write_ipython = magic
    write_sys = True
    write_joblib = True
    write_dill = True

    for i in imports:
        if 'import sys as' in i or i == 'import sys':
            write_sys = False
        if 'import joblib' in i:
            write_joblib = False
        if 'import Ipython' in i:
            write_ipython = False
        if 'import dill' in i:
            write_dill = False

    if (write_ipython):
        file.write('import IPython\n')

    if (write_sys):
        file.write('import sys\n')

    if (write_joblib):
        file.write('import joblib\n')
    
    if (write_dill):
        file.write('import dill\n')

    reduced = reduce_imports(imports, cell)
    for line in reduced:
        file.write(line)
    file.write('\n')


def write_load(inputs, file):

    load = ['def load():\n']

    dill = ''

    for i in range(len(inputs)):
        if i > 0:
            dill += ', '
        dill += 'dill.load(open(sys.argv[{}], \'rb\'))'.format(str(i+1))

    load.append(indent+'return ' + dill+'\n')

    if inputs:
        for line in load:
            file.write(line)
        file.write('\n')

def write_cell(inputs, outputs, file, cell_file, magic):

    cell = []
    seperator = ', '

    cell.append('def cell(' + seperator.join(inputs) + '):\n')

    if magic:
        cell.append(indent + 'ipython_shell = IPython.core.interactiveshell.InteractiveShell()\n')

    cell_file.seek(0)
    for line in cell_file:
        if line[-1] != '\n':
            line += '\n'
        cell.append(indent+line)

    if outputs:
        cell.append(indent+'return '+seperator.join(outputs)+'\n')

    for line in cell:
        file.write(line)

    file.write('\n')

def write_store(outputs, file):

    seperator = ', '
    store = []
    store.append('def store(' + seperator.join(outputs) + '):\n')

    for o in outputs:
     
        store.append('{}dill.dump({}, open(\'./data/{}.pkl\', \'wb\'))\n'.format(indent, o, o))


    if outputs:
        for line in store:
            file.write(line)
        file.write('\n')


def write_main(input_len, output_len, file):  

    file.write('def main():\n')

    if input_len == 0:

        if output_len == 0:
            file.write(indent + 'cell()')

        elif output_len == 1:
            file.write(indent + 'store(cell())')

        else:
            file.write(indent + 'store(*cell())')

    elif input_len == 1:

        if output_len == 0:
            file.write(indent + 'cell(load())')

        elif output_len == 1:
            file.write(indent + 'store(cell(load()))')

        else:
            file.write(indent + 'store(*cell(load()))')

    else:

        if output_len == 0:
            file.write(indent + 'cell(*load())')

        elif output_len == 1:
            file.write(indent + 'store(cell(*load()))')
        else:
            file.write(indent + 'store(*cell(*load()))')

    file.write('\n\n')
    file.write('if __name__ == \'__main__\':\n{}main()'.format(indent))


def write_file(stage, cell_file, inputs, outputs, imports, magic):

    f = open('./code/{}.py'.format(stage),'w')
    cell = open(cell_file, 'r')
    write_imports(f, imports, cell, magic)
    write_load(inputs, f)
    write_cell(inputs, outputs, f, cell, magic)
    write_store(outputs, f)
    write_main(len(inputs), len(outputs), f)


def write_files(cell_count, stages, imports, magics):
    make_code()

    if not os.path.exists('./dep.txt'):
        sys.exit("no dependency file")

    cell_inputs = get_inputs('./dep.txt')
    cell_outputs = get_outputs('./dep.txt')
    
    if len(stages) != cell_count:
        sys.exit('stages and cell count does not match')
    for i in range(1, cell_count+1):
        if not os.path.exists('./cells/cell{}.py'.format(i)):
            sys.exit('./cells/cell{}.py does not exist'.format(i))
        write_file(stages[i], './cells/cell{}.py'.format(i), cell_inputs[i], cell_outputs[i], imports, magics[i-1])
        

#write_files(5, './stages.txt')
            

