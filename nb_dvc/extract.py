import json
import os
import util
from collections import defaultdict

class stage_error(Exception):
    pass

class import_error(Exception):
    pass

class format_error(Exception):
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

def get_options(source, stage_count, metadata):
    newline = 0
    for i,s in enumerate(source[1:]):
        if s == '\n':
            newline = 1
        else:
            if newline ==  0:
                raise format_error
            newline = 0

            if s.startswith('*inputs* '):
                s = s[len('*inputs* '):].strip('\n')
                metadata[stage_count]['inputs'] = s.split(', ') 
            elif s.startswith('*outputs* '):
                s = s[len('*outputs* '):].strip('\n')
                metadata[stage_count]['outputs'] = s.split(', ') 
            elif s.startswith('*params* '):
                s = s[len('*params* '):].strip('\n')
                metadata[stage_count]['params'] = s.split(', ')
                metadata[stage_count]['yaml'] = True
                metadata['params'] = True
            elif s.startswith('*metrics* '):
                s = s[len('*metrics* '):].strip('\n')
                metadata[stage_count]['metrics'] = s.split(', ')
                metadata[stage_count]['json'] = True
            else:
                raise format_error
      
    

def write_cell_file(stage_count, cell, script, imports):
    magic = False
    #system = False
    lines = 0
    cell_file = open('./cells/cell{}.py'.format(stage_count),'w')
    for line in cell['source']:
        if line[-1] != '\n':
            line += '\n'

        if util.is_magic(line):
            line = util.replace_magic(line)
            magic = True
    
        if util.is_shell(line):
            line = util.replace_shell(line)
            #system = True
          
        if util.is_import(line):
            imports.append(line)
            continue
        #if util.is_print(line.strip('\n')):
            #continue
        cell_file.write(line)
        script.write(line)
        lines += 1
    cell_file.close()
    return lines, imports, magic #system


def extract_cells(file):

    with open(file, 'r') as f:
        data = json.load(f)

    script = open('./script.py', 'w')
    stages = {}
    imports = []
    metadata = defaultdict(lambda : defaultdict(lambda : []))
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
                            raise import_error 
                    continue
    
            else:
                stage = get_stage(cell_list, i)
                
            stage_count += 1
            stages[stage_count] = stage
            get_options(cell_list[i-1]['source'], stage_count, metadata)

            lines, imports, magic = write_cell_file(stage_count, cell, script, imports)
            metadata[stage_count]['magic'] = magic
            # metadata[stage_count]['system'] = system
            cell_lines['cell{}'.format(stage_count)] = (counter+1, counter+lines)
            counter += lines

    with open('./cell_lines.json','w') as f:
        json.dump(cell_lines, f)
    with open('./cells/cell0.py', 'w') as f:
        f.write(''.join(imports))
 

    return stage_count, stages, imports, metadata
    
 
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






