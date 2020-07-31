import json
import os

def generate(cells):
    relative = os.path.dirname(__file__)
    with open(os.path.join(relative,'format.json'), 'r') as f:
        notebook = json.load(f)
    cell_list = []
    cell_dict = {}
    cell_dict['cell_type'] = "code"
    cell_dict['metadata'] = {}
    cell_dict['outputs'] = []
    cell_dict['execution_count'] = 0
    for cell in range(cells):

        with open('notebook/cell{}.py'.format(cell), 'r') as f:
            cell_dict['source'] = f.read().splitlines(keepends=True)     
            cell_list.append(cell_dict.copy())

    notebook['cells'] = cell_list
    with open('notebook.ipynb', 'w') as f:
        json.dump(notebook, f, indent = ' ')



