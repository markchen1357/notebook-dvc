import dvc
import refactor
import extract
import dep
import sys
import os
import clean


def main():
    file = sys.argv[1]

    print('Extracting cells...')
    stage_count, stages, imports, magics = extract.extract_cells(file)
    print(imports)
    names = extract.extract_requirements(imports)
    if os.path.exists('./dep.txt'):
        os.remove('./dep.txt')
    if os.path.exists('./dep.txt'):
        os.remove('./dep.txt')
    if not os.path.exists('data'):
        os.makedirs('data')
    os.system('node cell_dep.js')
    dep.organize_dep(names)
    print('Detected {} stages'.format(stage_count))
    print('Making python files...')
    refactor.write_files(stage_count, stages, imports, magics)
    print('Integrating with DVC...')
    dvc.make_script('./dep.txt', stages)



if __name__ == "__main__":
    main()
