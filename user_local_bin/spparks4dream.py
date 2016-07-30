#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
'''
 Author: Haiming Zhang
 Mail: hm.zhang@sjtu.edu.cn
 Created Time: 2016年05月28日 星期六 15时47分28秒
'''

import os,sys,math
import numpy as np
from optparse import OptionParser
from myLibs import ebsdInfo, readAngFile, readCtfFile
import damask
from subprocess import call

scriptName = os.path.splitext(os.path.basename(__file__))[0]
scriptID   = ' '.join([scriptName,damask.version])


#-------------------------------------re-------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """

generate geom and vtr file based on the results of spparks
""", version = scriptID)

parser.add_option('-n', '--nheader',      dest='nheader', type='int', metavar = 'int',
                  help='the number of header in the input spparks files [%default]')
parser.add_option('-i', '--item', dest='item', type='int',metavar = 'int',
                  help = "the item will be extracted [%default]")   
parser.set_defaults(
                    nheader = 9,
                 )
(options,filenames) = parser.parse_args()


# --- loop over input files -------------------------------------------------------------------------
if filenames == []: 
    print 'missing input files'
    exit()

for filename in filenames:

    fileNamePrefix = os.path.splitext(filename)[0]
    fopen = open(filename, 'r')

    content = []
    for i in xrange(options.nheader):
        content.append(fopen.readline())

    # Get the global info about the geom file.
    grid = [int(content[i].split()[1]) for i in range(5,8)]
    ndim = 2 if grid[2] == 1 else 3
    maxGrid = int(content[3].split()[0])

    lengthOfEachFile = maxGrid + options.nheader

    counter = options.nheader
    line = fopen.readline()
    grainList = []

    # read the input spparks file
    while line:
        if counter - lengthOfEachFile*options.item > options.nheader-1:
            grainList.append(int(line.split()[1]))

        if len(grainList) == maxGrid: break
        line = fopen.readline()
        counter += 1

    fout  = open(fileNamePrefix +'_item'+str(options.item)+'.dump','w')

    #-- report ---------------------------------------------------------------------------------------
    fout.write('-\n')
    fout.write('%i dimension\n'%ndim)
    fout.write('%i sites\n'%maxGrid)
    fout.write('%i max neighbors\n'%({2:8, 3:26}[ndim]))
    fout.write('0 %i xlo xhi\n'%grid[0])
    fout.write('0 %i ylo yhi\n'%grid[1])
    fout.write('0 %i zlo zhi\n'%grid[2])
    fout.write('\n')
    fout.write('Values\n')
    fout.write('\n')

    reNumGrain = {}
    for i,ig in enumerate(set(grainList)):
        reNumGrain[ig] = i+1
    for i,grain in enumerate(grainList):
        fout.write('%i %i\n'%(i+1, reNumGrain[grain]))

    fout.close()

