#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
'''
 Author: Haiming Zhang
 Mail: hm.zhang@sjtu.edu.cn
 Created Time: 2016年05月28日 星期六 15时47分28秒
'''

from optparse import OptionParser
import os,sys,math,re,random,string
import numpy as np


def getHeader(xCells,yCells,xStep, yStep, format):
  if format == 'ang':
    return [ 
    '# TEM_PIXperUM          1.000000', 
    '# x-star                0.509548', 
    '# y-star                0.795272', 
    '# z-star                0.611799', 
    '# WorkingDistance       18.000000', 
    '#', 
    '# Phase                 1', 
    '# MaterialName          Al', 
    '# Formula               Fe', 
    '# Info', 
    '# Symmetry              43', 
    '# LatticeConstants      2.870 2.870 2.870  90.000  90.000  90.000', 
    '# NumberFamilies        4', 
    '# hklFamilies           1  1  0 1 0.000000 1', 
    '# hklFamilies           2  0  0 1 0.000000 1', 
    '# hklFamilies           2  1  1 1 0.000000 1', 
    '# hklFamilies           3  1  0 1 0.000000 1', 
    '# Categories            0 0 0 0 0 ', 
    '#', 
    '# GRID: SquareGrid', 
    '# XSTEP: ' + str(xStep), 
    '# YSTEP: ' + str(yStep), 
    '# NCOLS_ODD: ' + str(xCells), 
    '# NCOLS_EVEN: ' + str(xCells), 
    '# NROWS: ' + str(yCells), 
    '#', 
    '# OPERATOR: ODFsammpling', 
    '#', 
    '# SAMPLEID: ', 
    '#', 
    '# SCANID: ', 
    '#'
    ]
  else:  # ctf format
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

def allIsDigit(line):
    return all(i.isdigit() for i in line.split())

def getMicroInfo(fopen):
    ''' this subroutine deals with the .geom file or material.config file '''
    line = fopen.readline()
    mapMicro = []; mapEulerAngle = []
    while line:
        if not line.strip() == '':        # non empty line
            texts = line.split()
            # get the index of phase and texture
            if texts[0] == '(constituent)': mapMicro.append( [ int(texts[2]), int(texts[4]) ] )

            # get the index of phase and texture
            if texts[0] == '(gauss)': mapEulerAngle.append( [ float(texts[2]), float(texts[4]), float(texts[6]) ] )

        line = fopen.readline()
    return np.array(mapMicro), np.array(mapEulerAngle)

def mapCoordCrystalNo(fopen, surface='z', sliceNo = 1):
    '''
    this subroutine deals with the .geom file, get the grain No of each grid.
    fopen is the read object of the .geom file, 
    surfPlot is the surface in which the orientation, x, y, or z
    sliceNo is the No. of slice will be along the normal of surfPlot
    will be plot.
    '''
    position = { 'x': [4, 6],                 # y,z
                 'y': [6, 2],                 # z,x
                 'z': [2, 4]                  # x,y
               }

    line = fopen.readline()
    geomInfo = {}
    mapCrystalNo = []
    while line:
        if not line.strip() == '':        # non empty line
            texts = line.split()

            if texts[0] in ['grid', 'size', 'origin']: 
                geomInfo[texts[0]] = [ texts[ position[surface][0] ], texts[ position[surface][0] ] ]
            elif texts[0] in [ 'homogenization', 'microstructures']: 
                geomInfo[texts[0]] = texts[1]
            elif all(i.isdigit() for i in texts):
                mapCrystalNo.append( [ int(i) for i in texts ] )

        line = fopen.readline()
    return geomInfo, np.array(mapCrystalNo)


# --------------------------------------------------------------------
#                                MAIN
# --------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """
Transform linear binned data into Euler angles. ***This script does not support the case that one CRYSTALLITE contains
more than one (constituent).***

""")


parser.add_option('--slice', dest='slice', type='int', metavar = 'int',
                  help='number of orientations to be generated [%default]')
parser.add_option('-s', '--surface', dest='surface', type='string', metavar = 'string',
                  help='number of orientations to be generated [%default]')
parser.add_option("-m", "--microfile", type="string", metavar = 'string', \
                  dest="microfile", help='''specify the microstructure file, if no file is specified, then
 it is assume the .geom contains the microstructure information.''')
parser.add_option("-f", "--format", type="string", metavar = 'string', dest="format",
                  help="the format of the output file [%default]")


parser.set_defaults(slice          = 1,
                    surface        = 'z',
                    microfile      = 'None',
                    format         = 'ctf'
                 )

(options,filenames) = parser.parse_args()

if filenames == []:
    print 'missing the .geom file, please specify a geom file!'
else:
    for filename in filenames:
        if os.path.exists(filename):
            if options.microfile == 'None':
                fopen = open(filename, 'r')
            else:
                if os.path.exists(options.microfile):
                    fopen = open(options.microfile)
                else:
                    print 'the microstructure file %s is not found'%options.microfile
                    exit()

            mapMicro, mapEulerAngle = getMicroInfo(fopen)
            fopen.close()

            fopen = open(filename, 'r')
            geomInfo, mapCrystalNo  = mapCoordCrystalNo(fopen, options.surface.lower(), options.slice)
            fopen.close()

            nOrientations = int(geomInfo['microstructures'])
            if nOrientations != len(mapMicro): 
                print 'The No. of <microstructure> is not equal to microstructure'
                print 'The number of orientation is %s'%nOrientations
                print 'The number of <microstructure> is %s'%len(mapMicro)
                exit()

            if nOrientations != len(mapEulerAngle): 
                print 'The No. of <texture> is not equal to microstructure, exit'
                print 'The number of orientation is %s'%nOrientations
                print 'The number of <texture> is %s'%len(mapEulerAngle)
                exit()

            # write header
            if options.format == 'ang': # 'ang' file, radian
                angFile = open(os.path.splitext(filename)[0] + '.ang','w')
            else:                       # 'ctf' file, degree
                angFile = open(os.path.splitext(filename)[0] + '.ctf','w')

            xCells,  yCells  = int(geomInfo['grid'][0]), int(geomInfo['grid'][1])
            xSize,   ySize   = float(geomInfo['size'][0]) - float(geomInfo['origin'][0]), float(geomInfo['size'][1]) - float(geomInfo['origin'][1])
            xstep, ystep = xSize/xCells, ySize/yCells
            xStep, yStep = xstep/min(xstep, ystep), ystep/min(xstep, ystep)
            xCells, yCells = xCells+1, yCells+1

            for line in getHeader(xCells,yCells,xStep, yStep, options.format):
                angFile.write(line + '\n')

            # write data
            for iy in xrange(xCells):
                coordY = iy*yStep
                grainPosY = iy-1 if iy>0 else 0
                for ix in xrange(yCells):
                    coordX = ix*xStep
                    grainPosX = ix-1 if ix>0 else 0

                    grainNo = mapCrystalNo[grainPosY][grainPosX] - 1
                    eulerAngs = mapEulerAngle[ mapMicro[grainNo][1] - 1 ]
                    phaseNo   = mapMicro[grainNo][0]

                    if options.format == 'ang': 
                        angFile.write(''.join(['%12.5f'%(angle*np.pi/180.) for angle in point])+''.join(['%12.5f'%coord for coord in [counter%xCells,counter//sizeX]])+
                            ' 100.0 1.0 0 1 1.0\n')
                        counter += 1
                    else:
                        angFile.write(str(phaseNo)+'\t'+
                                           '\t'.join([str(coord) for coord in [ coordX, coordY ]])+
                                           '\t5\t0\t'+
                                           '\t'.join([str(angle) for angle in eulerAngs])+
                                           '\t0.5000\t100\t0\n')
            angFile.close()

        else:
            print 'the geom file %s is not found'%options.geomfile
