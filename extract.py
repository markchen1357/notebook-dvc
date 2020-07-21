import json
import os
import util

class stage_error(Exception):
    pass

class import_error(Exception):
    pass

marker = '*stage*'

def extract_stage_name(str):
    if marker in str:
        return str.split(marker,1)[1].strip()
    else:
        return ''

def process_markdown(source):
    if source:
        extract = extract_stage_name(source[0])
        if not extract:
            raise stage_error
        else:
            return extract
    else:
        raise stage_error

def get_stage(cell_list, index):
    if index != 0 and cell_list[index-1]['cell_type'] == 'markdown':
        return process_markdown(cell_list[index-1]['source'])

    else:
        raise stage_error

def write_cell_file(stage_count, cell, script, imports):
    magic = False
    lines = 0
    cell_file = open('./cells/cell{}.py'.format(stage_count),'w')
    for line in cell['source']:
        if line[-1] != '\n':
            line += '\n'
        if util.is_magic(line):
            line = util.replace_magic(line)
            magic = True
        if util.is_import(line):
            imports.append(line)
        else:
            script.write(line)
            cell_file.write(line)
            lines += 1
    cell_file.close()
    return lines, imports, magic


def extract_cells(file):

    with open(file, 'r') as f:
        data = json.load(f)

    script = open('./script.py', 'w')
    stages = {}
    imports = []
    magics = []
    cell_lines = {}
    counter = 0
    stage_count = 0

    if not os.path.exists('./cells'):
        os.mkdir('./cells')

    first_code = 1
    cell_list = data['cells']

    for i, cell in enumerate(cell_list):
        if not cell['source']:
            continue

        if cell['cell_type'] == 'code':
            # checks if the first code cell is an optional import cell         
            if first_code:
                first_code = 0
                try:
                    stage = get_stage(cell_list, i)
                except:
                    # case where there is an import cell
                    for line in cell['source']:
                        if line == '\n':
                            continue
                        if util.is_import(line):
                            if line[-1] != '\n':
                                line += '\n'
                            imports.append(line)
                        else:
                            print(line)
                            raise import_error 
                    continue
    
            else:
                stage = get_stage(cell_list, i)
                
            stage_count += 1
            stages[stage_count] = stage

            lines, imports, magic = write_cell_file(stage_count, cell, script, imports)
            magics.append(magic)
            cell_lines['cell{}'.format(stage_count)] = (counter+1, counter+lines)
            counter += lines

    with open('./cell_lines.json','w') as f:
        json.dump(cell_lines, f)

    return stage_count, stages, imports, magics
    
 
def extract_requirements(imports):
    
    if os.path.exists('./requirements.txt'):
        os.remove('./requirements.txt')
    f = open('./requirements.txt', 'w')
    req = set()
    names = set()
    for i in imports:
        i = i.strip('\n')
        if i.startswith('import '):
            temp = i[len('import '):].split(' ')[0]
            req.add(temp.split('.')[0])
        elif i.startswith('from '):
            temp = i[len('from '):].split(' ')[0]
            req.add(temp.split('.')[0])

    for i in imports:
        i = i.strip('\n')
        if i.startswith('import '):
            if " as " in i:
                names.add(i.split(' as ')[1])
            else:
                temp = i[len('import '):].split(' ')[0]
                names.add(temp.split('.')[0])
        elif i.startswith('from '):
            names.add(i.split('import ')[1])

    for r in req:
        f.write('{}\n'.format(r))
    return names

#extract_cells(file)






