#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
'''
 File Name: smoothEBSD.py
 Author: Haiming Zhang
 Mail: hm.zhang@sjtu.edu.cn
 Created Time: 2016年05月30日 星期一 23时33分03秒
'''

from optparse import OptionParser
import os,sys,math,re,random,string
import numpy as np
from myLibs import readCtfFile, ebsdInfo, getEBSDHeader


scriptName = os.path.splitext(os.path.basename(__file__))[0]

def getNeighbor(nRow, nCol):
    mapPos2Grid = np.empty( [nRow, nCol], dtype=int)
    neighbor = []
    for jrow in xrange(nRow):
        mapPos2Grid[jrow, :] = [icol + jrow*nCol for icol in xrange(nCol)]

    for jrow in xrange(nRow):
        for icol in xrange(nCol):
            if jrow == 0:
                if icol == 0:   # left down corner
                    neighbor.append([ mapPos2Grid[jrow+1, icol],  mapPos2Grid[jrow+1, icol+1], mapPos2Grid[jrow, icol+1] ])
                elif icol == nCol - 1: # right down corner
                    neighbor.append([ mapPos2Grid[jrow, icol-1],  mapPos2Grid[jrow+1, icol-1], mapPos2Grid[jrow+1,icol] ])
                else:  # lower line
                    neighbor.append([ mapPos2Grid[jrow, icol-1], mapPos2Grid[jrow+1, icol-1], mapPos2Grid[jrow+1, icol],  mapPos2Grid[jrow+1, icol+1],
                            mapPos2Grid[jrow, icol+1]  ])
            elif jrow == nRow-1:
                if icol == 0:   # left upper corner
                    neighbor.append([ mapPos2Grid[jrow, icol+1],  mapPos2Grid[jrow-1, icol+1], mapPos2Grid[jrow-1, icol] ])
                elif icol == nCol - 1:  # right upper corner
                    neighbor.append([ mapPos2Grid[jrow-1, icol],  mapPos2Grid[jrow-1, icol-1], mapPos2Grid[jrow,icol-1] ])
                else:  # upper line
                    neighbor.append([ mapPos2Grid[jrow, icol+1], mapPos2Grid[jrow-1, icol+1], mapPos2Grid[jrow-1, icol],  mapPos2Grid[jrow-1, icol-1],
                            mapPos2Grid[jrow, icol-1]  ])
            else:
                if icol == 0: #left line
                    neighbor.append([ mapPos2Grid[jrow+1, icol], mapPos2Grid[jrow+1, icol+1], mapPos2Grid[jrow, icol+1],  mapPos2Grid[jrow-1, icol+1],
                            mapPos2Grid[jrow-1, icol]  ])
                elif icol == nCol - 1: # right line
                    neighbor.append([ mapPos2Grid[jrow-1, icol], mapPos2Grid[jrow-1, icol-1], mapPos2Grid[jrow, icol-1],  mapPos2Grid[jrow+1, icol-1],
                            mapPos2Grid[jrow+1, icol]  ])
                else: # others
                    neighbor.append([ mapPos2Grid[jrow+1, icol], mapPos2Grid[jrow+1, icol+1], mapPos2Grid[jrow, icol+1],  mapPos2Grid[jrow-1, icol+1],
                                    mapPos2Grid[jrow-1, icol], mapPos2Grid[jrow-1, icol-1], mapPos2Grid[jrow, icol-1],  mapPos2Grid[jrow+1, icol-1]
                                    ])
    return neighbor


def groupEulerAngles(eulerList, threshold):
    '''
    eulerList is a list of euler angles arrays, [ np.array([phi1, phi, phi2]), np.array( [phi1, phi, phi2] ) ]
    '''
    npt = len(eulerList)
    if npt == 0:
        return []
    else:
        groupList = [ [] for i in xrange(npt) ]
        groupList[0].append( eulerList[0] )
        for p in xrange(1, npt):
            for i, groupi in enumerate(groupList):
                if groupi != []:
                    if np.linalg.norm( np.average(groupi, 0) - eulerList[p] ) < threshold:
                        groupi.append(eulerList[p])
                        break
                else:
                    groupi.append(eulerList[p])
                    break

        for i in groupList:
            if i == []: groupList.remove(i)
        groupList.sort(key=lambda x: -len(x))

        return groupList


def gridNeedSmooth(eulerList, eulerCurrent, threshold):
    '''
    if the mis-orientation between the current grid with its neighboring grids is larger than the threshold, then 
    return False, else return True (means the current grid does not need to be smoothed'')
    '''
    counter = 0
    if len(eulerList) > 1:
        for angle in eulerList:
            if np.linalg.norm( angle-eulerCurrent ) > threshold: 
                counter = counter + 1
        #print counter
        return True if counter > len(eulerList)/2.0 else False
    else:
        return False


# --------------------------------------------------------------------
#                                MAIN
# --------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """
Transform linear binned data into Euler angles. ***This script does not support the case that one CRYSTALLITE contains
more than one (constituent).***

""")


parser.add_option('-t', dest='threshold', type='float', metavar = 'float',
                  help='number of  [%default]')
parser.add_option("-f", "--format", type="string", metavar = 'string', dest="format",
                  help="the format of the output file [%default]")
parser.add_option("--mat", metavar = '<string LIST>', dest="materials",
                  help="list of materials for phase 1, phase2, ... [%default] ['Al','Mg']")
parser.add_option('-s', '--smooth', dest='smooth', action='store_false',
                  help = '[%default]' )
parser.add_option('--fill', dest='fill', action='store_false',
                  help = '[%default]' )
parser.add_option('-m', dest='maxround', type='int', metavar = 'int',
                  help='number of  [%default]')


parser.set_defaults(
                    threshold      = 10.0,
                    format         = 'ctf',
                    materials      = ['Al'],
                    smooth         = True,
                    maxround       = 5,
                    fill           = True
                 )


(options,filenames) = parser.parse_args()

if filenames == []:
    print 'missing the .geom filgroue, please specify a geom file!'
else:
    for filename in filenames:
        print 'process file %s by %s'%(filename, scriptName)
        if os.path.exists(filename):
            #
            fopen = open(filename, 'r')
            eulerangles, coords, phases, fileHeader = readCtfFile(fopen)  
            fopen.close()

            xstep, ystep = ebsdInfo['xstep'], ebsdInfo['ystep']
            xcells, ycells = ebsdInfo['xcells'], ebsdInfo['ycells']

            #print ycells, xcells
            neighbor = getNeighbor(ycells, xcells)

            round = 0
            while True:
                round += 1
                if round > options.maxround:
                    break
                print '%s round ================'%(round)
                allAreSmoothed = True
                allAreFilled   = True
                isFinished     = True
                smoothPrint = False; fillPrint = False
                counter = 0
                for jrow in xrange(ycells):
                    for icol in xrange(xcells):
                        neighPts = neighbor[counter]
                        eulerList = [eulerangles[i] for i in neighPts if phases[i] > 0]
                        #print jrow, icol
                        groupList = groupEulerAngles(eulerList, options.threshold)  # group the euler angles of its neighbors
                        #print groupList, len(groupList)
                        if options.smooth:
                            if not smoothPrint:
                                print 'smoothing ...'
                                smoothPrint = True
                            if phases[counter] > 0:  # non-empty grid
                                if gridNeedSmooth(eulerList, eulerangles[counter], options.threshold):  #need smooth
                                    #print 'yes', jrow, icol
                                    #if len(groupList[0]) > len(eulerList)/2:
                                    eulerangles[counter] = np.average(groupList[0], 0)
                                    allAreSmoothed = False

                        if options.fill:
                            if not fillPrint:
                                print 'interpolating ...'
                                fillPrint = True
                            if phases[counter] < 1: # empty grid
                                phasesList = [phases[i] for i in neighPts if phases[i] > 0]
                                #print phasesList
                                if phasesList != []:
                                    phases[counter] = max( phasesList, key=phasesList.count )

                                    #if len(groupList[0]) > len(eulerList)/2:
                                    eulerangles[counter] = np.average(groupList[0], 0)

                                allAreFilled = False
                        counter += 1

                if options.smooth and not allAreSmoothed:
                    isFinished = False
                if options.fill   and not allAreFilled:
                    isFinished = False
                if isFinished:
                    break

            # write header
            if options.format == 'ang': # 'ang' file, radian
                angFile = open(os.path.splitext(filename)[0] + '_smooth.ang','w')
            else:                       # 'ctf' file, degree
                angFile = open(os.path.splitext(filename)[0] + '_smooth.ctf','w')


            for line in  fileHeader:
                angFile.write(line)

            # write data
            counter = 0
            for iy in xrange(xcells):
                for ix in xrange(ycells):
                    coordX, coordY = coords[counter]
                    eulerAngs = eulerangles[counter]
                    phaseNo   = phases[counter]

                    if options.format == 'ang':
                        angFile.write(''.join(['%12.5f'%(angle*np.pi/180.) for angle in eulerAngs])+''.join(['%12.5f'%coord for coord in [coordX, coordY]])+
                            ' 100.0 1.0 0 1 1.0\n')
                    else:
                        angFile.write(str(phaseNo)+'\t'+
                                           '\t'.join([str(coord) for coord in [ coordX, coordY ]])+
                                           '\t5\t0\t'+
                                           '\t'.join([str(angle) for angle in eulerAngs])+
                                           '\t0.5000\t100\t0\n')
                    counter += 1
            angFile.close()

        else:
            print 'the geom file %s is not found'%options.geomfile
