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
from myLibs import mapCoordCrystalNo, allIsDigit


scriptName = os.path.splitext(os.path.basename(__file__))[0]

def getMicroInfo(fopen):
    ''' this subroutine deals with the .geom file or material.config file '''
    line = fopen.readline()
    mapGrain2Phase = []
    while line:
        if not line.strip() == '':        # non empty line
            texts = line.split()
            # get the index of phase and texture
            if texts[0] == '(constituent)' and texts[3] == 'texture': mapGrain2Phase.append(texts[2])

        line = fopen.readline()
    return mapGrain2Phase 




# --------------------------------------------------------------------
#                                MAIN
# --------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """
Transform linear binned data into Euler angles. ***This script does not support the case that one CRYSTALLITE contains
more than one (constituent).***

""")


parser.add_option("-m", "--microfile", type="string", metavar = 'string', \
                  dest="microfile", help='''specify the microstructure file, if no file is specified, then
 it is assume the .geom contains the microstructure information.''')

parser.set_defaults( microfile      = 'None', )

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

            mapGrain2Phase = getMicroInfo(fopen)
            fopen.close()

            fopen = open(filename, 'r')
            geomInfo, mapCrystalNo  = mapCoordCrystalNo(fopen, [2,4,6])
            fopen.close()

            nOrientations = int(geomInfo['microstructures'])
            if nOrientations != len(mapGrain2Phase): 
                print 'The No. of <microstructure> is not equal to microstructure'
                print 'The number of orientation is %s'%nOrientations
                print 'The number of <microstructure> is %s'%len(mapGrain2Phase)
                exit()


            for irow in xrange(len(mapCrystalNo)):
                for jcol in xrange(len(mapCrystalNo[irow])):
                    mapCrystalNo[irow][jcol] = mapGrain2Phase[ mapCrystalNo[irow][jcol] - 1 ]

            maxPhase = int( max(max(mapCrystalNo)) )

            fopen = open(os.path.splitext(filename)[0]+'_phase.geom', 'w')
            fopen.write('5  header\n')
            fopen.write('this file is not the geometrically file of DAMASK/Spectral !!\n')
            fopen.write('grid    a '+geomInfo['grid'][0]+'  b '+geomInfo['grid'][1]+'  c '+geomInfo['grid'][2]+'\n')
            fopen.write('size    x '+geomInfo['size'][0]+'  y '+geomInfo['size'][1]+'  z '+geomInfo['size'][2]+'\n')
            fopen.write('origin    x '+geomInfo['origin'][0]+'  y '+geomInfo['origin'][1]+'  z '+geomInfo['origin'][2]+'\n')
            fopen.write('microstructures  '+str(maxPhase)+'\n')
            for line in mapCrystalNo:
                fopen.write(' '.join(i for i in line)+'\n')
        else:
            print 'the geom file %s is not found'%options.geomfile
