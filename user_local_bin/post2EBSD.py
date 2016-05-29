#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
'''
 Author: Haiming Zhang
 Mail: hm.zhang@sjtu.edu.cn
 Created Time: 2016年05月28日 星期六 15时47分28秒
'''

from optparse import OptionParser
import os,sys,math,string
import numpy as np


def getHeader(xCells,yCells,xStep, yStep):
    # ctf format
    return [ \
    'Channel Text File',
    'Prj\tX:\\xxx\\xxxx.cpr',
    'Author\t[Haiming Zhang at Shanghai Jiao Tong University]',
    'JobMode\tGrid',
    'XCells\t'+ str(xCells),
    'YCells\t'+ str(yCells),
    'XStep\t'+ str(xStep),
    'YStep\t'+ str(yStep),
    'AcqE1\t0',
    'AcqE2\t90',
    'AcqE3\t0',
    'Euler angles refer to Sample Coordinate system (CS0)!\tMag\t300\tCoverage\t100\tDevice\t0\tKV\t20\tTiltAngle\t70\tTiltAxis\t0',
    'Phases\t1',
    '4.05;4.05;4.05\t90;90;90\tAluminium\t11\t225\t3803863129_5.0.6.3\t-2102160418\tCryogenics18,54-55',
    'Phase\tX\tY\tBands\tError\tEuler1\tEuler2\tEuler3\tMAD\tBC\tBS'
           ]


def getElemConnectFFTW(ipcoords, elemList):
    '''
    get the initial connectivity of grids of Fourier points
    Row - x axis; Column - y axis
    '''
    print ipcoords
    minIpCoords = np.min( ipcoords[:,0] ), np.min( ipcoords[:,1] ) # minx, miny
    maxIpCoords = np.max( ipcoords[:,0] ), np.max( ipcoords[:,1] ) # maxx, maxy

    elemSizeX, elemSizeY = 2.0*minIpCoords[0], 2.0*minIpCoords[1]
    maxRow = int( np.round( maxIpCoords[1]/elemSizeY + 0.5 ) )
    maxCol = int( np.round( maxIpCoords[0]/elemSizeX + 0.5 ) )

    print 'total row = %s, total column = %s, nrow*ncol = %s, total element is %s'%(maxRow, maxCol, maxRow*maxCol, len(elemList))
    if maxRow*maxCol != len(elemList):
        print 'total element is not equal to nrow*nrol!'

    elemPosition = np.empty_like(ipcoords, dtype=int)
    mapPosElemNo = np.empty([maxCol, maxRow], dtype=int)
    for elem in elemList:
        # row and colume, start from 0 row and 0 column
        # elemPosition[i] = columnNo., orowNo., the begin No. of the row/column is zero.
        ele = elem - 1
        elemPosition[ele] = int( np.round(ipcoords[ele, 0]/elemSizeX - 0.5) ), int( np.round(ipcoords[ele, 1]/elemSizeY - 0.5) )
        mapPosElemNo[ elemPosition[ele, 0], elemPosition[ele, 1] ] = elem

    return elemPosition, mapPosElemNo, maxRow, maxCol, elemSizeX, elemSizeY


def getIpsEffectDomain(nodeCoords, maxRow, maxCol):
    '''
    xxx
    '''
    eleDomain = np.empty( [ maxCol, maxRow, 4] ) # left, right, lower, upper/ x-, x+, y-, y+
    minNodeCoordsX = np.min( nodeCoords[0, :, 0] ) # xmin, search in first column
    minNodeCoordsY = np.min( nodeCoords[:, 0, 1] ) # ymin, search in first row
    maxNodeCoordsX = np.max( nodeCoords[-1, :, 0] ) - minNodeCoordsX # xmax, search in the last column
    maxNodeCoordsY = np.max( nodeCoords[:, -1, 1] ) - minNodeCoordsY # ymax, search in the last row


    for irow in xrange(maxRow):
        for jcol in xrange(maxCol):
            eleDomain[jcol, irow, 0:2 ] = nodeCoords[jcol, irow, 0]-minNodeCoordsX, nodeCoords[jcol+1, irow, 0]-minNodeCoordsX
            eleDomain[jcol, irow, 2:4 ] = nodeCoords[jcol, irow, 1]-minNodeCoordsY, nodeCoords[jcol, irow+1, 1]-minNodeCoordsX

    return eleDomain, maxNodeCoordsX, maxNodeCoordsY


def getNodeCoordsFromVtk(fileCurrentIpCoordsFile, maxRow, maxCol):
    openVTK = open(fileCurrentIpCoordsFile, 'r')
    line = openVTK.readline()

    maxRow1 = maxRow + 1; maxCol1 = maxCol + 1
    counter = 0; nNodes = maxRow1*maxCol1
    nodeCoords = np.empty( [maxCol1, maxRow1, 2] )
    beginRecord = False
    while line:
        if beginRecord:
            texts = line.split()
            nodeCoords[ np.mod(counter, maxCol1), counter/maxCol1, : ] = texts[0], texts[1]
            counter += 1

        if ('POINTS' in line):
            beginRecord = True

        if counter == nNodes: break
        line = openVTK.readline()

    openVTK.close()
    return nodeCoords


def allIsDigit(line):
    return all(i.isdigit() for i in line.split())


# --------------------------------------------------------------------
#                                MAIN
# --------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """
Transform linear binned data into Euler angles. ***This script does not support the case that one CRYSTALLITE contains
more than one (constituent).***

""")

parser.add_option('-r', '--ratio',      dest='ebsdStepRatio', type='int', metavar = 'int',
                  help='homogenization index for <microstructure> configuration [%default]')

parser.add_option('-p', '--phase',      dest='phase', type='int', metavar = 'int',
                  help='homogenization index for <microstructure> configuration [%default]')

parser.add_option('-a', '--axis',       dest='surface', type='string', metavar = 'string',
                  help='homogenization index for <microstructure> configuration [%default]')

parser.set_defaults( ebsdStepRatio = 2, 
                     phase         = 1,
                     surface       = 'z'
                   )

(options,filenames) = parser.parse_args()

keywords = ['_ipinitialcoord', '_eulerangles']
axisPositionList = {'x': ['2', '3'], 'y': ['1', '3'], 'z': ['1', '2']}
axisPos = axisPositionList [options.surface]


if filenames == []:
    print 'missing the input file, please specify a geom file!'
else:
    getInitialTopology = False    # get the initial coordinates and the connectivity

    for filename in filenames:
        fileCurrentIpCoordsFile = 'mesh_' + os.path.splitext(filename)[0] + '.vtk'
        if os.path.exists(filename) and os.path.exists( fileCurrentIpCoordsFile ):

            elemList = []; phaseList = []; ipcoordsList = []; euleranglesList = []
            if not getInitialTopology: ipcoordsInitList = []

            fopen = open(filename, 'r')
            line = fopen.readline()
            header = int(line.split()[0])
            counter = 0

            print 'get the the coordinates, phase, eulerangles of IPs'
            while line:
                texts = line.split()
                if counter == header:
                    if all(text in line for text in keywords):
                        ipcoordsInitIndex = texts.index( axisPos[0]+keywords[0] ), texts.index( axisPos[1]+keywords[0] )
                        euleranglesIndex  = texts.index('1'+keywords[1])
                        elemIndex         = texts.index('elem')
                        phaseIndex        = texts.index('phase') if 'phase' in line else -1
                    else:
                        print 'euler angles are not found in the input files'
                        exit()

                # get Ip coordinates and eulerangles
                if counter > header:
                    elemList.append( int(texts[elemIndex]) )
                    euleranglesList.append( [float(texts[euleranglesIndex + i]) for i in xrange(3) ] )
                    phaseList.append( int(texts[phaseIndex]) if phaseIndex > -1 else options.phase )
                    if not getInitialTopology:  ipcoordsInitList.append( [float(texts[i]) for i in ipcoordsInitIndex ] )

                line = fopen.readline()
                counter += 1

            nelem = len(elemList)
            eulerangles = np.empty([nelem, 3])
            if not getInitialTopology: ipcoordsInit = np.empty([nelem, 2])

            for i in xrange(nelem):
                eulerangles[ elemList[i] - 1 ] = np.array( euleranglesList[i] )
                if not getInitialTopology:  ipcoordsInit[ elemList[i] - 1 ] = np.array( ipcoordsInitList[i] )

            if not getInitialTopology:
                print 'get the connectivity and ebsdSteps'
                elemPosition, mapPosElemNo, maxRow, maxCol, elemSizeX, elemSizeY = getElemConnectFFTW(ipcoordsInit, elemList)

                ebsdStepX = elemSizeX/float(options.ebsdStepRatio)
                ebsdStepY = elemSizeY/float(options.ebsdStepRatio)
                getInitialTopology = True

            if getInitialTopology:
                print 'get the domains of each current element'

                # eleDomain[ ele, 0:3 ] corresponds to 0:y-, 1:y+, 2:x-, 3:x+
                nodeCoords = getNodeCoordsFromVtk(fileCurrentIpCoordsFile, maxRow, maxCol)
                eleDomain, ebsdSizeX, ebsdSizeY = getIpsEffectDomain(nodeCoords, maxRow, maxCol)

                print eleDomain
                ebsdCellX, ebsdCellY = int(ebsdSizeX/ebsdStepX) + 1, int(ebsdSizeY/ebsdStepY) + 1

                print 'total xCells = %s, total yCells = %s, xStep = %s, yStep = %s'%(ebsdCellX, ebsdCellY, ebsdStepX, ebsdStepY)
                # declare the array
                mapEBSDgrid2Elems = np.zeros( [ebsdCellX, ebsdCellY], dtype=int )

                for elem in xrange(nelem):
                    ele = elemList[elem] - 1
                    jcol, irow = elemPosition[ele]
                    xNeg, xPos, yNeg, yPos = eleDomain[jcol, irow]

                    rowLower, rowUpper = int( (yNeg/ebsdStepY) ), int( (yPos/ebsdStepY) )
                    colLeft,  colRight = int( (xNeg/ebsdStepX) ), int( (xPos/ebsdStepX) )

                    for irow in xrange(rowLower, rowUpper+1):
                        for jcol in xrange(colLeft, colRight+1):
                            mapEBSDgrid2Elems[ jcol, irow ] = elemList[elem]

                # write ctf format ebsd data
                angFile = open(os.path.splitext(filename)[0] + '.ctf','w')
                print angFile
                for line in getHeader(ebsdCellX, ebsdCellY, ebsdStepX, ebsdStepY):
                    angFile.write(line + '\n')

                for irow in xrange(ebsdCellY):
                    coordY = irow * ebsdStepY
                    for jcol in xrange(ebsdCellX):
                        coordX = jcol * ebsdStepX

                        elem = mapEBSDgrid2Elems[ jcol, irow ]
                        eulerAngs = eulerangles[elem - 1] if elem > 0 else np.zeros(3)
                        phaseNo   = phaseList[elem - 1] if elem > 0 else 0
                        angFile.write(str(phaseNo)+'\t'+
                                                   '\t'.join([str(coord) for coord in [ coordX, coordY ]])+
                                                   '\t5\t0\t'+
                                                   '\t'.join([str(angle) for angle in eulerAngs])+
                                                   '\t0.5000\t100\t0\n')
                angFile.close()
        else:
            print 'the input file %s is not found'
