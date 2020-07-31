import ast
import os
from collections import defaultdict



def get_inputs(dep_file):
    cell_inputs = defaultdict(lambda: [])
    with open(dep_file,'r') as f:
        for line in f:
            d,u,v = ast.literal_eval(line)
            cell_inputs[u].append(v)
    return cell_inputs

def get_outputs(dep_file):
    cell_outputs = defaultdict(lambda: set())
    with open(dep_file, 'r') as f:
        for line in f:
            d, u, v = ast.literal_eval(line)
            cell_outputs[d].add(v)
    return cell_outputs


def command_line(program, inputs):
    input_string = ''
    for i in inputs:
        input_string += ' data/{}.pkl'.format(i)

    return " python {}{}".format(program, input_string)


def get_dep_string(stage, inputs, meta):
    dep_string = ' -d ./code/{}.py'.format(stage)
    for i in inputs:
        dep_string += ' -d data/{}.pkl'.format(i)
    for i in meta['inputs']:
        dep_string += ' -d {}'.format(i)
    return dep_string

def get_output_string(outputs, meta):
    output_string = ''
    for o in outputs:
        output_string += ' -o data/{}.pkl'.format(o)
    for o in meta['outputs']:
        output_string += ' -o outputs/{}.pkl'.format(o)
    return output_string

def get_metric_string(meta):
    metric_string = ''
    for m in meta['metrics']:
        metric_string += ' -M metrics/{}.json'.format(m)
    return metric_string

def get_param_string(stage, meta):
    param_string = ''
    for p in meta['params']:
        param_string += ' -p {}.{}'.format(stage,p)
    return param_string

def make_stage(stage, inputs, outputs, meta):
    param_string = get_param_string(stage, meta)
    metric_string = get_metric_string(meta)
    dep_string = get_dep_string(stage, inputs, meta)
    output_string = get_output_string(outputs, meta)
    command_string = command_line('./code/{}.py'.format(stage), inputs)
    

    return 'dvc run -n {}{}{}{}{}{}\n'.format(stage, dep_string, output_string, param_string, metric_string, command_string)

def make_script(dep_file, stages, metadata):
    cell_inputs = get_inputs(dep_file)
    cell_outputs = get_outputs(dep_file)
    f = open('script.sh', 'w')
    for i in range(1,len(stages)+1):
        f.write(make_stage(stages[i], cell_inputs[i], cell_outputs[i], metadata[i]))

#deprecated

def run_stage(stage, inputs, outputs):
    dep_string = get_dep_string(stage, inputs)
    output_string = get_output_string(outputs)
    command_string = command_line('./code/{}.py'.format(stage), inputs)

    os.system('dvc run -n {}{}{}{}'.format(stage, dep_string, output_string, command_string))
def run_stages(dep_file, stages):
    cell_inputs = get_inputs(dep_file)
    cell_outputs = list(set(get_outputs(dep_file)))
 
    if not os.path.exists('./.git'):
        os.system('git init')
    if not os.path.exists('./.dvc'):
        os.system('dvc init')

    for i in range(1,len(stages)+1):
        run_stage(stages[i], cell_inputs[i], cell_outputs[i])


