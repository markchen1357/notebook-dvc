import os
import re


def organize_dep(names):
    dep = open('./dep.txt', 'r')
    with open('./dep_save.txt', 'w') as f:
        f.write(dep.read())

    dep.seek(0)
    lines = dep.read().splitlines()
    
    new_dep = set()
    
    for line in lines:
        temp = line.split(',')
        if not temp[2] in names and not temp[2] == 'ipython_shell' and not temp[0] >= temp[1]:
            #new_dep.add('({},{},\'{}\')'.format(temp[0][len('cell'):],temp[1][len('cell'):],temp[2]))
            new_dep.add((int(temp[0][len('cell'):]), int(temp[1][len('cell'):]), temp[2]))

    dep.close()
    new_dep = list(new_dep)
    new_dep.sort()

    keep_list = [True] * len(new_dep)
  
    for i,dep in enumerate(new_dep):
        for j,prev in enumerate(new_dep[:i]):
            if prev[1:] == dep[1:]:
                keep_list[j] = False
 
    new_dep = [dep for i,dep in enumerate(new_dep) if keep_list[i]]

    for i,dep in enumerate(new_dep):
        underscore = ''
        repeat = False
        for prev in new_dep[:i]:
            match = re.fullmatch('{}(_*)'.format(dep[2]), prev[2])
            if match and dep[0] != prev[0]:
                repeat = True
                if len(match.group(1)) > len(underscore):
                    underscore = match.group(1)
                    
        if repeat:
            new_dep[i] = (new_dep[i][0], new_dep[i][1], dep[2]+underscore+'_')
 
    for i,dep in enumerate(new_dep):
        #if dep == (3, 4, 'X_train'):
            #dep = (3, 4, 'X_train_')
        new_dep[i] = str(dep)
        

    #new_dep.append('(2, 3, \'X_train\')')
    
    #new_dep.sort()
    dep = open('./dep.txt', 'w')
    dep.write('\n'.join(new_dep))




