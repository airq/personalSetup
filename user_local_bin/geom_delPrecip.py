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

(options,filenames) = parser.parse_args()


# --- loop over input files -------------------------------------------------------------------------
if filenames == []:
    print 'missing input files'
    exit()

for filename in filenames:

#   open file and read data
    print 'process file %s by %s'%(filename, scriptName)
    fopen = open(filename, 'r')
    fout  = open(os.path.splitext(filename)[0]+'_noPrecip.geom', 'w')
    content = fopen.readlines()

    nheader = int( content[0].split()[0] )
    for i in xrange(nheader+1):
        line = content[i].split()
        if line[0] == 'grid': grid = int(line[2]), int(line[4]), int(line[6])
        if line[0] == 'microstructures':
            microstructures = int(line[1])
            content[i] = line[0]+'\t'+str(microstructures-1)+'\n'

    mapGrid2Grain = np.zeros([grid[0],grid[1],grid[2]], dtype=int)

    for ii in xrange(nheader+1, len(content)):
        i = ii - nheader-1
        iz = i/grid[1]
        iy = i - iz*grid[1]

        mapGrid2Grain[:, iy, iz] = map(int, content[ii].split())

    # current, only consider 2D
    iz = 0
    precipExist = True
    while precipExist:
        NoPrecip = 0
        gz = iz
        for iy in xrange(grid[1]):
            if iy == 0:
                NeighborY = [0,1]
            elif iy == grid[1]-1:
                NeighborY = [iy - 1, iy]
            else:
                NeighborY = [iy-1,iy, iy+1]

            for ix in xrange(grid[0]):
                if mapGrid2Grain[ix,iy,iz] == microstructures:
                    NoPrecip += 1
                    if ix == 0:
                        NeighborX = [0,1]
                    elif ix == grid[0]-1:
                        NeighborX = [ix - 1, ix]
                    else:
                        NeighborX = [ix-1,ix, ix+1]

                    NeighGrainList = []

                    for gx in NeighborX:
                        for gy in NeighborY:
                            if gx!=ix or gy!=iy: NeighGrainList.append(mapGrid2Grain[gx,gy,gz])

                    repli = collections.Counter(NeighGrainList)
                    NeighGrainList.sort(key = lambda x:-repli[x])

                    if NeighGrainList[0] != microstructures and repli[NeighGrainList[0]]>=len(NeighGrainList)/2:
                        mapGrid2Grain[ix,iy,iz] = NeighGrainList[0]
                    else:
                        if len(NeighGrainList) > repli[NeighGrainList[0]]:
                            if repli[ NeighGrainList[ repli[NeighGrainList[0]] ] ] > (len(NeighGrainList) - repli[NeighGrainList[0]])/2:
                                mapGrid2Grain[ix,iy,iz] = NeighGrainList[ repli[NeighGrainList[0]] ]

        if NoPrecip == 0: precipExist = False
        print 'number of precipations is %i'%NoPrecip

  # --- output finalization --------------------------------------------------------------------------
    # write header
    for i in xrange(nheader+1):
        fout.write(content[i])

    for iz in xrange(grid[2]):
        for iy in xrange(grid[1]):
            fout.write( ' '.join( [str(mapGrid2Grain[ix, iy,iz]) for ix in xrange(grid[0])] ) + '\n' )
