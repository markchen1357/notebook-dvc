import dvc
import refactor
import extract
import dep
import sys
import os
import clean
import subprocess


def main():
    dir = os.path.dirname(__file__)
    file = sys.argv[1]

    print('Extracting cells...')
    stage_count, stages, imports, metadata = extract.extract_cells(file)
    names = extract.extract_requirements(imports)
    if os.path.exists('./dep.txt'):
        os.remove('./dep.txt')
    if not os.path.exists('data'):
        os.makedirs('data')

    subprocess.run(['node', os.path.join(dir,'cell_dep.js')])
    dep.organize_dep(names)
    print('Detected {} stages'.format(stage_count))
    print('Making python files...')
    refactor.write_files(stage_count, stages, imports, metadata)
    print('Integrating with DVC...')
    dvc.make_script('./dep.txt', stages, metadata)



if __name__ == "__main__":
    main()
