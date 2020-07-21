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
    cell_outputs = defaultdict(lambda: [])
    with open(dep_file, 'r') as f:
        for line in f:
            d, u, v = ast.literal_eval(line)
            cell_outputs[d].append(v)
    return cell_outputs


def command_line(program, inputs):
    input_string = ''
    for i in inputs:
        input_string += ' data/{}.pkl'.format(i)

    return " python {}{}".format(program, input_string)


def get_dep_string(stage, inputs):
    dep_string = ' -d ./code/{}.py'.format(stage)
    for i in inputs:
        dep_string += ' -d data/{}.pkl'.format(i)
    return dep_string

def get_output_string(outputs):
    output_string = ''
    for o in outputs:
        output_string += ' -o data/{}.pkl'.format(o)
    return output_string

def run_stage(stage, inputs, outputs):
    dep_string = get_dep_string(stage, inputs)
    output_string = get_output_string(outputs)
    command_string = command_line('./code/{}.py'.format(stage), inputs)

    os.system('dvc run -n {}{}{}{}'.format(stage, dep_string, output_string, command_string))


def make_stage(stage, inputs, outputs):
    dep_string = get_dep_string(stage, inputs)
    output_string = get_output_string(outputs)
    command_string = command_line('./code/{}.py'.format(stage), inputs)

    return 'dvc run -n {}{}{}{}\n'.format(stage, dep_string, output_string, command_string)

def make_script(dep_file, stages):
    cell_inputs = get_inputs(dep_file)
    cell_outputs = get_outputs(dep_file)
    f = open('script.sh', 'w')

    for i in range(1,len(stages)+1):
        f.write(make_stage(stages[i], cell_inputs[i], cell_outputs[i]))

def run_stages(dep_file, stages):
    cell_inputs = get_inputs(dep_file)
    cell_outputs = get_outputs(dep_file)
    if not os.path.exists('./.git'):
        os.system('git init')
    if not os.path.exists('./.dvc'):
        os.system('dvc init')

    for i in range(1,len(stages)+1):
        run_stage(stages[i], cell_inputs[i], cell_outputs[i])

#run_stages('./dep.txt', './stages.txt')

