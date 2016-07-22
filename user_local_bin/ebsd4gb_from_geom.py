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
import collections

scriptName = os.path.splitext(os.path.basename(__file__))[0]
scriptID   = ' '.join([scriptName,damask.version])


#-------------------------------------re-------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
before using this script, one is suggested to use geom_smoothOddGrid.py to smooth the odd grids.
when the thickness of GB (-t) is smaller than 2, the option (-d) should be used.
""", version = scriptID)

parser.add_option('-p','--phase',              dest='phase', type='int', metavar = 'int',
                  help='The phase in which the GBs will be generated [%default]')
parser.add_option('-t','--thick',              dest='thick', type='int', metavar = 'int',
                  help='The half thickness of the GBs [%default]')
parser.add_option('-m','--matconfig',              dest='matconfig', type='string', metavar = 'string',
                  help='The name of the microstructures file [%default]')
parser.add_option('-d', '--diagonal', dest='diagonal', action='store_true',
                  help = "if false, then the grids at the diagonal of the considered grid will not used to identify gbs [%default]")   
parser.add_option('-n', '--number', dest='number', action='store_true',
                  help = "number the generated grain boundary, if ture, then the number of gbs is different, i.e., microstructure+i, \
                  else all grains have the same microstructure No., i.e., microstructures+1 [%default]")   

parser.set_defaults( phase = 1,
                     thick = 2,
                     matconfig = 'None',
                     diagonal = False,
                     number   = False,
        )

(options,filenames) = parser.parse_args()

# --- loop over input files -------------------------------------------------------------------------
if filenames == []:
    print 'missing input files'
    exit()


for filename in filenames:

#   open file and read data
    print 'process file %s by %s'%(filename, scriptName)

    fopen = open(filename, 'r')
    fout  = open(os.path.splitext(filename)[0]+'_4GettingGB.geom'%(str(thick)), 'w')
    content = fopen.readlines()

    nheader = int( content[0].split()[0] )
    for i in xrange(nheader+1):
        line = content[i].split()
        if line[0] == 'grid': grid = int(line[2]), int(line[4]), int(line[6])
        if line[0] == 'microstructures':
            microstructures = int(line[1])
            Ngb = microstructures if options.number else 1
            content[i] = line[0]+'\t'+str(microstructures+Ngb)+'\n'

    mapGrid2Grain = np.zeros([grid[0],grid[1],grid[2]], dtype=int)

    # get the grain number of each grid
    for ii in xrange(nheader+1, len(content)):
        i = ii - nheader-1
        iz = i/grid[1]
        iy = i - iz*grid[1]

        mapGrid2Grain[:, iy, iz] = map(int, content[ii].split())

    for iz in xrange(grid[2]):
        for iy in xrange(grid[1]):
            for ix in xrange(grid[0]):
                # first, get its neighbor girds(8 for 2d, 27 for 3d)
                # to do

                #if phases[mapGrid2Grain[ix,iy,iz]] == options.phase
                neighborList1 = getNeighborList(1, grid, ix, iy, iz)
                neighborGrainNoList = []
                for gz in neighborList1[2]:
                    for gy in neighborList1[1]:
                        for gx in neighborList1[0]:
                            if not options.diagonal:
                                if abs(gx-ix)+abs(gy-iy)+abs(gz-iz) < 2:
                                    neighborGrainNoList.append(mapGrid2Grain[gx,gy,gz])
                            else:
                                neighborGrainNoList.append(mapGrid2Grain[gx,gy,gz])

                if len(set(neighborGrainNoList)) > 1:
                    # it is a triple point, 
                    locateInGB = True
                elif len(set(neighborGrainNoList)) == 2:
                    # the considered grid may locate in GBs
                    # i think the grid locates in GBs, now the considered grid and its neighbors are see as GBs
                    locateInGB = True if min(set(neighborGrainNoList)) > len( neighborGrainNoList )/3 else False

                else:
                    locateInGB = False

                # get the neighbor list of the consider grid
                if locateInGB:
                    neighborList = getNeighborList(numGridOneSide, grid, ix, iy, iz)
                    for gz in neighborList[2]:
                        for gy in neighborList[1]:
                            for gx in neighborList[0]:
                                mapGrid2GrainOut[gx,gy,gz] = mapGrid2Grain[ix,iy,iz] + Ngb

  # --- output finalization --------------------------------------------------------------------------
    # write header
    for i in xrange(nheader+1):
        fout.write(content[i])

    for iz in xrange(grid[2]):
        for iy in xrange(grid[1]):
            fout.write( ' '.join( [str(mapGrid2GrainOut[ix, iy,iz]) for ix in xrange(grid[0])] ) + '\n' )
