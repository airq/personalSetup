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


def readMTEXfile(fopen):
    position = {'phi1':0, 'phase':3, 'x':9, 'y':10}
    content = fopen.readlines()
    line = content[0].split()
    for key in position.keys():
        position[key] = line.index(key)

    eulerAngles0 = []; coordsX = []; coordsY=[]; phase0 = []

    for line in content[1:]:
        if line.strip() != '':
            words = line.split()
            eulerAngles0.append( map(float, words[position['phi1']:position['phi1']+3]))
            coordsX.append( float(words[position['x']] ))
            coordsY.append( float(words[position['y']] ))
            phase0.append( int(words[position['phase']]))

    xcells = len(set(coordsX)); ycells = len(set(coordsY))
    xstep  = ( np.max(coordsX) - np.min(coordsX) )/(xcells-1)
    ystep  = ( np.max(coordsY) - np.min(coordsY) )/(ycells-1)

    eulerangles = np.empty([xcells, ycells, 3])
    coords = np.empty([xcells, ycells, 2])
    phases = -np.ones([xcells, ycells ])

    for i in xrange(len(phase0)):
        jrow = int( np.round( coordsY[i]/ystep ))
        icol = int( np.round( coordsX[i]/xstep ))
        eulerangles[icol, jrow, :] = np.array( eulerAngles0[i] )
        coords[icol, jrow, :] = np.array( [ coordsX[i], coordsY[i] ] )
        phases[icol, jrow] = phase0[i]

    # data check
    for jrow in xrange(ycells):
        for icol in xrange(xcells):
            if phases[icol, jrow] < 0:
                print 'data is incorrect at y=%s, x=%s'%(jrow*ystep, icol*xstep)
                exit()

    return coords, eulerangles, phases, xcells, ycells, xstep, ystep


# --------------------------------------------------------------------
#                                MAIN
# --------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """
Transform linear binned data into Euler angles. ***This script does not support the case that one CRYSTALLITE contains
more than one (constituent).***

""")


parser.add_option("-f", "--format", type="string", metavar = 'string', dest="format",
                  help="the format of the output file [%default]")
parser.add_option("--mat", metavar = '<string LIST>', dest="materials",
                  help="list of materials for phase 1, phase2, ... [%default] ['Al','Mg']")


parser.set_defaults(
                    format         = 'ctf',
                    materials      = ['Al']
                 )

(options,filenames) = parser.parse_args()

if filenames == []:
    print 'missing the .mtx file, please specify a mtex file!'
else:
    for filename in filenames:
        print 'process file %s by %s'%(filename, scriptName)
        if os.path.exists(filename):

            fopen = open(filename, 'r')
            coords, eulerangles, phases, xCells, yCells, xStep, yStep = readMTEXfile(fopen)
            fopen.close()

            # write header
            if options.format == 'ang': # 'ang' file, radian
                angFile = open(os.path.splitext(filename)[0] + '.ang','w')
            else:                       # 'ctf' file, degree
                angFile = open(os.path.splitext(filename)[0] + '.ctf','w')

            print 'xStep is %s, yStep is %s'%(xStep, yStep)
            print 'xCells is %s, yCells is %s'%(xCells, yCells)


            for line in  getEBSDHeader(xCells,yCells,xStep, yStep, options.format, options.materials):
                angFile.write(line + '\n')

            # write data
            for jrow in xrange(yCells):
                for icol in xrange(xCells):

                    eulerAngs = eulerangles[icol, jrow, :]
                    coords0   = coords[icol, jrow, :]
                    phaseNo   = phases[icol, jrow]

                    if options.format == 'ang': 
                        angFile.write(''.join(['%12.5f'%(angle*np.pi/180.) for angle in eulerAngs])+''.join(['%12.5f'%coord for coord in coords0 ])+
                            ' 100.0 1.0 0 1 1.0\n')
                        counter += 1
                    else:
                        angFile.write(str(phaseNo)+'\t'+
                                           '\t'.join([str(coord) for coord in coords0])+
                                           '\t5\t0\t'+
                                           '\t'.join([str(angle) for angle in eulerAngs])+
                                           '\t0.5000\t100\t0\n')
            angFile.close()

        else:
            print 'the geom file %s is not found'%options.geomfile
