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

Generate geometry description and material configuration from EBSD data in given square-gridded 'ang' file.
Two phases can be discriminated based on threshold value in a given data column.

""", version = scriptID)
parser.add_option('-l','--loops',              dest='loops', type='int', metavar = 'int',
                  help='The number of loops used to smooth the odd grids [%default]')
parser.add_option('-t','--threshold',              dest='threshold', type='int', metavar = 'int',
                  help='The number of loops used to smooth the odd grids [%default]')

parser.set_defaults( loops = 1, 
                     threshold = 1,
        )

(options,filenames) = parser.parse_args()


# --- loop over input files -------------------------------------------------------------------------
if filenames == []:
    print 'missing input files'
    exit()


# --- loop over input files -------------------------------------------------------------------------
if filenames == []:
    print 'missing input files'
    exit()

for filename in filenames:

#   open file and read data
    print 'process file %s by %s'%(filename, scriptName)
    fopen = open(filename, 'r')
    fout  = open(os.path.splitext(filename)[0]+'_smoothOddGrids.geom', 'w')
    content = fopen.readlines()

    nheader = int( content[0].split()[0] )
    for i in xrange(nheader+1):
        line = content[i].split()
        if line[0] == 'grid': grid = int(line[2]), int(line[4]), int(line[6])

    mapGrid2Grain = np.zeros([grid[0],grid[1],grid[2]], dtype=int)

    for ii in xrange(nheader+1, len(content)):
        i = ii - nheader-1
        iz = i/grid[1]
        iy = i - iz*grid[1]

        mapGrid2Grain[:, iy, iz] = map(int, content[ii].split())

    # current, only consider 2D
    iz = 0
    smoothedGrids = 0
    for iloop in  xrange(options.loops):
        gz = iz
        for iy in xrange(grid[1]):
            if iy == 0:
                NeighborY = [0,1]
            elif iy == grid[1]-1:
                NeighborY = [iy - 1, iy]
            else:
                NeighborY = [iy-1,iy, iy+1]
            for ix in xrange(grid[0]):
                if ix == 0:
                    NeighborX = [0,1]
                elif ix == grid[0]-1:
                    NeighborX = [ix - 1, ix]
                else:
                    NeighborX = [ix-1,ix, ix+1]

                NeighGrainList = []

                for gx in NeighborX:
                    for gy in NeighborY:
                        if gx !=ix or gy !=iy: NeighGrainList.append(mapGrid2Grain[gx,gy,gz])

                repli = collections.Counter(NeighGrainList)
                NeighGrainList.sort(key = lambda x:-repli[x])

                if repli[NeighGrainList[0]]>len(NeighGrainList)/2 + 1 - options.threshold:
                    #print NeighGrainList
                    if mapGrid2Grain[ix,iy,iz] != NeighGrainList[0]:
                        smoothedGrids += 1
                        mapGrid2Grain[ix,iy,iz] = NeighGrainList[0]

    print 'number of smoothed grids %i'%smoothedGrids

  # --- output finalization --------------------------------------------------------------------------
    # write header
    for i in xrange(nheader+1):
        fout.write(content[i])

    for iz in xrange(grid[2]):
        for iy in xrange(grid[1]):
            fout.write( ' '.join( [str(mapGrid2Grain[ix, iy,iz]) for ix in xrange(grid[0])] ) + '\n' )
