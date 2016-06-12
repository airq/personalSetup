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
from myLibs import allIsDigit, getEBSDHeader, mapCoordCrystalNo


scriptName = os.path.splitext(os.path.basename(__file__))[0]

def getMicroInfo(fopen):
    ''' this subroutine deals with the .geom file or material.config file '''
    line = fopen.readline()
    mapMicro = []; mapEulerAngle = []
    while line:
        if not line.strip() == '':        # non empty line
            texts = line.split()
            # get the index of phase and texture
            if texts[0] == '(constituent)': mapMicro.append( [ int(texts[2]), int(texts[4]) ] )

            # get Euler angles 
            if texts[0] == '(gauss)': mapEulerAngle.append( [ float(texts[2]), float(texts[4]), float(texts[6]) ] )

        line = fopen.readline()
    return np.array(mapMicro), np.array(mapEulerAngle)


position = { 'x': [4, 6],                 # y,z
             'y': [6, 2],                 # z,x
             'z': [2, 4]                  # x,y
           }
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
parser.add_option("--mat", metavar = '<string LIST>', dest="materials",
                  help="list of materials for phase 1, phase2, ... [%default] ['Al','Mg']")


parser.set_defaults(slice          = 1,
                    surface        = 'z',
                    microfile      = 'None',
                    format         = 'ctf',
                    materials      = ['Al']
                 )

(options,filenames) = parser.parse_args()

if filenames == []:
    print 'missing the .geom file, please specify a geom file!'
else:
    for filename in filenames:
        print 'process file %s by %s'%(filename, scriptName)
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
            geomInfo, mapCrystalNo  = mapCoordCrystalNo(fopen, position[options.surface])
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
            #xCells, yCells = xCells+1, yCells+1
            print 'xStep is %s, yStep is %s'%(xStep, yStep)
            print 'xCells is %s, yCells is %s'%(xCells, yCells)


            for line in  getEBSDHeader(xCells,yCells,xStep, yStep, options.format, options.materials):
                angFile.write(line + '\n')

            # write data, mapCrystalNo[yCells][xCells]
            for iy in xrange(yCells):
                coordY = iy*yStep
                #grainPosY = iy-1 if iy>0 else 0
                grainPosY = iy
                for ix in xrange(xCells):
                    coordX = ix*xStep
                    #grainPosX = ix-1 if ix>0 else 0
                    grainPosX = ix

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
