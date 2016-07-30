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

Generate geometry description and material configuration from EBSD data in given square-gridded 'ang' file.
Two phases can be discriminated based on threshold value in a given data column.

""")

parser.add_option('-z','--zenlarge',      dest='zEnlarge', type='int', metavar = 'int',
                  help='thickness [%default]')
parser.add_option('-a','--addair',      dest='addAir', type='string', metavar = 'string',
                  help='x or y + ratio, for example x1.0 [%default]')
parser.set_defaults(
                    zEnlarge = 1,
                    addAir = 'None',
                 )
(options,filenames) = parser.parse_args()


# --- loop over input files -------------------------------------------------------------------------
if filenames == []: 
    print 'missing input files'
    exit()

for filename in filenames:

    fopen = open(filename, 'r')
    fout  = open(os.path.splitext(filename)[0] +'_addAir' + '.geom','w')

    content = fopen.readlines()
    nheader = int(content[0].split()[0])


#-- report ---------------------------------------------------------------------------------------
    print 'write geom file'
    fout.write('%i   header\n'%(nheader+1))
    fout.write('This model is modified by geom_addAir_zRepeat.py\n')

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

    if options.addAir[0] == 'x':
        newgrid = [ int (grid0[0]*(1 + float(options.addAir[1:]))), grid0[1], grid0[2] ]
        newsize = [ newgrid[0] * size0[0]/grid0[0], size0[1], size0[2] ]
        ngrains = microstructures + 1
    elif options.addAir[0] == 'y':
        newgrid = [ grid0[0], int (grid0[1]*(1 + float(options.addAir[1:]))), grid0[2] ]
        newsize = [ size0[0], newgrid[1] * size0[1]/grid0[1], size0[2] ]
        ngrains = microstructures + 1
    elif options.addAir == 'None':
        newgrid = [ grid0[0], grid0[1], grid0[2] ]
        newsize = [ size0[0], size0[1], size0[2] ]
        ngrains = microstructures
    else:
        print 'the format of addAir is wrong'
        exit

    if options.zEnlarge > 1:
        newgrid[2] = newgrid[2]*options.zEnlarge
        newsize[2] = newsize[2]*options.zEnlarge

    fout.write('grid     a %s  b %s  c %s\n'%(str(newgrid[0]), str(newgrid[1]), str(newgrid[2]) ))
    fout.write('size     x %s  y %s  z %s\n'%(str(newsize[0]), str(newsize[1]), str(newsize[2]) ))
    fout.write('origin   x %s  y %s  z %s\n'%(str(origin[0]), str(origin[1]), str(origin[2])))
    fout.write('homogenization  %i\n'%homogenization)
    fout.write('microstructures %i\n'%ngrains)

    newcontent = []
    for line in content[nheader+1:]:
        if options.addAir[0] == 'x':
            newcontent.append( ' '.join( [i for i in line.split()]) +( ' '+str(ngrains) )*(newgrid[0]-grid0[0]) + '\n' )
        else:
            newcontent.append( line )

    if options.addAir[0] == 'y':
        for i in xrange( newgrid[1]-grid0[1] ):
            newcontent.append( str(ngrains) + (' ' + str(ngrains))*(newgrid[0]-1) + '\n' )

    for iz in xrange(options.zEnlarge):
        for line in newcontent:
            fout.write(line)
