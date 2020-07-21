import os


def organize_dep(names):
    dep = open('./dep.txt', 'r')

    lines = dep.read().splitlines()

    new_dep = set()
    for line in lines:
        temp = line.split(',')
        if not temp[2] in names:
            new_dep.add('({},{},\'{}\')'.format(temp[0][len('cell'):],temp[1][len('cell'):],temp[2]))

    dep.close()

    dep = open('./dep.txt', 'w')
    dep.write('\n'.join(new_dep))




