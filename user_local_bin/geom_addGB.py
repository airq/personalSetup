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


def getNeighborList(gridsEachSide, gird, ix,iy,iz):
    '''find the nearest N(gridEachSide) neighbor grid around the grid ix,iy,iz
    gridsEachSide > 0
    '''

    ixStart = 0 if ix - gridsEachSide < 0 else ix - gridsEachSide
    iyStart = 0 if iy - gridsEachSide < 0 else iy - gridsEachSide
    izStart = 0 if iz - gridsEachSide < 0 else iz - gridsEachSide

    ixEnd   = grid[0]-1 if ix + gridsEachSide > grid[0]-1 else ix + gridsEachSide
    iyEnd   = grid[1]-1 if iy + gridsEachSide > grid[1]-1 else iy + gridsEachSide
    izEnd   = grid[2]-1 if iz + gridsEachSide > grid[2]-1 else iz + gridsEachSide

    return [
            [ x for x in xrange(ixStart, ixEnd + 1) ],
            [ y for y in xrange(iyStart, iyEnd + 1) ],
            [ z for z in xrange(izStart, izEnd + 1) ],
            ]

#-------------------------------------re-------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
before using this script, one is suggested to use geom_smoothOddGrid.py to smooth the odd grids.
when the thickness of GB (-t) is greater than 1, the option (-d) should be used.
""", version = scriptID)

parser.add_option('-p','--phase',              dest='phase', type='int', metavar = 'int',
                  help='The phase in which the GBs will be generated [%default]')
parser.add_option('-t','--thick',              dest='thick', type='int', metavar = 'int',
                  help='The half thickness of the GBs [%default]')
parser.add_option('-m','--matconfig',              dest='matconfig', type='string', metavar = 'string',
                  help='The name of the microstructures file [%default]')
parser.add_option('-d', '--diagonal', dest='diagonal', action='store_false',
                  help = "write 'ebsd_ngrains' into to homogenization [%default]")   

parser.set_defaults( phase = 1,
                     thick = 2,
                     matconfig = 'None',
                     diagonal = True,
        )

(options,filenames) = parser.parse_args()

thick = options.thick
numGridOneSide = thick - 1
# --- loop over input files -------------------------------------------------------------------------
if filenames == []:
    print 'missing input files'
    exit()


for filename in filenames:

#   open file and read data
    print 'process file %s by %s'%(filename, scriptName)

    if options.matconfig:
        matInputFile = options.matconfig
    else:
        print 'you did not provide the matconfig file, i will search a matconfig with the same name as the iunput geom file'
        if os.path.exists(os.path.splitext(filename)[0] + '.matconfig'):
            matInputFile =  os.paht.splitext(filename)[0] + '.matconfig'
        else:
            print 'I can not find such matconfig file, so I will generate a new matconfig file, and the initial phase is one.'
            matInputFile = 'None'

    fopen = open(filename, 'r')
    fout  = open(os.path.splitext(filename)[0]+'_addGB_T%s.geom'%(str(thick)), 'w')
    content = fopen.readlines()

    nheader = int( content[0].split()[0] )
    for i in xrange(nheader+1):
        line = content[i].split()
        if line[0] == 'grid': grid = int(line[2]), int(line[4]), int(line[6])
        if line[0] == 'microstructures':
            microstructures = int(line[1])
            content[i] = line[0]+'\t'+str(microstructures+1)+'\n'

    # get the phase of grains, if no matconfig is provides, then the initial phase of all grains is one
    if matInputFile == 'None':
        mapGrain2Phase = np.ones(microstructures, dtype=int)
    #else:

    mapGrid2Grain = np.zeros([grid[0],grid[1],grid[2]], dtype=int)

    for ii in xrange(nheader+1, len(content)):
        i = ii - nheader-1
        iz = i/grid[1]
        iy = i - iz*grid[1]

        mapGrid2Grain[:, iy, iz] = map(int, content[ii].split())

    mapGrid2GrainOut = mapGrid2Grain.copy()
    GBlable = microstructures + 1
    #current, only consider 2D
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
                                mapGrid2GrainOut[gx,gy,gz] = GBlable

  # --- output finalization --------------------------------------------------------------------------
    # write header
    for i in xrange(nheader+1):
        fout.write(content[i])

    for iz in xrange(grid[2]):
        for iy in xrange(grid[1]):
            fout.write( ' '.join( [str(mapGrid2GrainOut[ix, iy,iz]) for ix in xrange(grid[0])] ) + '\n' )
