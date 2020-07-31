import os
import shutil



if os.path.exists('./.dvc'):
    shutil.rmtree('./.dvc')

if os.path.exists('./dvc.yaml'):
    os.remove('./dvc.yaml')

if os.path.exists('./dvc.lock'):
    os.remove('./dvc.lock')


if os.path.exists('./data/.gitignore'):
    os.remove('./data/.gitignore')

if os.path.exists('./models'):
    shutil.rmtree('./models')


if os.path.exists('./script.py'):
    os.remove('./script.py')

if os.path.exists('./cell_lines.json'):
    os.remove('./cell_lines.json')

if os.path.exists('./dep.txt'):
    os.remove('./dep.txt')

if os.path.exists('./code'):
    shutil.rmtree('./code')


if os.path.exists('./data'):
    shutil.rmtree('./data')

if os.path.exists('./cells'):
    shutil.rmtree('./cells')

if os.path.exists('./stages.txt'):
    os.remove('./stages.txt')

if os.path.exists('./requirements.txt'):
    os.remove('./requirements.txt')