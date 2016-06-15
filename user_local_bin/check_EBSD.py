#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
'''
 Author: Haiming Zhang
 Mail: hm.zhang@sjtu.edu.cn
 Created Time: 2016年05月28日 星期六 15时47分28秒
'''

import os,sys
from optparse import OptionParser
from myLibs import  readAngFile, readCtfFile

scriptName = os.path.splitext(os.path.basename(__file__))[0]

  
#-------------------------------------re-------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """

check is there any zero phase in the ebsd file
""")

parser.add_option('--column',              dest='column', type='int', metavar = 'int',
                  help='data column to discriminate between both phases [%default]')
parser.add_option('-t','--threshold',      dest='threshold', type='float', metavar = 'float',
                  help='threshold value for phase discrimination [%default]')
 
parser.set_defaults(column         = 8,
                    threshold      = 0.5,
                 )
(options,filenames) = parser.parse_args()



# --- loop over input files -------------------------------------------------------------------------
if filenames == []: 
    print 'missing input files'
    exit()

for filename in filenames:
#   open file and read data
    fopen = open(filename, 'r')
    if os.path.splitext(filename)[-1] == '.ang':
        eulerangles, coords, phase, geomHeader = readAngFile(fopen, [0,1], options.column, options.threshold)

    elif os.path.splitext(filename)[-1] == '.ctf':
        eulerangles, coords, phase, geomHeader = readCtfFile(fopen)

    else:
        print 'unknown input file type!!'
        continue
    
    noZeroPhase = True
    for i in phase:
        if i == 0:
            print '***** zero phase exists *****'
            noZeroPhase = False
    if noZeroPhase:
        print 'non zero phase found! It is okay'
