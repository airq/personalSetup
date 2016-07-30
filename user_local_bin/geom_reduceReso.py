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

scriptName = os.path.splitext(os.path.basename(__file__))[0]


#-------------------------------------re-------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """

""")

parser.add_option('-r','--reduce',      dest='reduce', type='int', metavar = 'int',
                  help='times of reducing the resolution [%default]')
parser.set_defaults(
                    reduce = 1,
                 )
(options,filenames) = parser.parse_args()

reduce = float(options.reduce)
# --- loop over input files -------------------------------------------------------------------------
if filenames == []: 
    print 'missing input files'
    exit()

for filename in filenames:

    fopen = open(filename, 'r')
    fout  = open(os.path.splitext(filename)[0] +'_reduce' + '.geom','w')

    content = fopen.readlines()
    nheader = int(content[0].split()[0])

#-- report ---------------------------------------------------------------------------------------
    print 'write geom file'
    fout.write('%i   header\n'%(nheader+1))
    fout.write('This model is modified by geom_reduceReso.py\n')

    for line in content[1:nheader+1]:
        words = line.split()
        if words[0] == 'grid':
            grid0 = int(words[2]), int(words[4]), int(words[6])
        elif words[0] == 'size':
            size0 = float(words[2]), float(words[4]), float(words[6])
        elif words[0] == 'origin':
            origin = float(words[2]), float(words[4]), float(words[6])
        elif words[0] == 'homogenization':
            homogenization = int(words[1])
        elif words[0] == 'microstructures':
            microstructures = int(words[1])
        else:
            fout.write(line)

    newgrid = [1,1,1]; newsize = [1.0, 1.0, 1.0]
    for i in xrange(3):
        newgrid[i] = 1 if grid0[i]/reduce < 1 else int(grid0[i]/reduce)
        newsize[i] = newgrid[i]/float(grid0[i]) * size0[i]

    fout.write('grid     a %s  b %s  c %s\n'%(str(newgrid[0]), str(newgrid[1]), str(newgrid[2]) ))
    fout.write('size     x %s  y %s  z %s\n'%(str(newsize[0]), str(newsize[1]), str(newsize[2]) ))
    fout.write('origin   x %s  y %s  z %s\n'%(str(origin[0]), str(origin[1]), str(origin[2])))
    fout.write('homogenization  %i\n'%homogenization)
    fout.write('microstructures %i\n'%microstructures)

    for iz in xrange(newgrid[2]):
        for iy in xrange(newgrid[1]):
            line = content[nheader + 1 + iz*grid0[1]*options.reduce + iy*options.reduce ].split()
            fout.write(' '.join( [ line[i*options.reduce] for i in xrange(newgrid[0]) ] ) +'\n')
