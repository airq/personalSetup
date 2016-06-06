#!/usr/bin/python
# -*- coding: utf-8 no BOM -*-
"""
@version:      ??
@author:       Haiming Zhang
@address:      Shanghai Jiao Tong University, Shanghai, China
@email:        hm.zhang@sjtu.edu.cn
@file:         xx
@created with: PyCharm
@time:         2016/5/18 16:58
"""
"""
This script aims to xxx
"""
import numpy as np
import matplotlib.pyplot as plt


def getSegmentsVertices(fopen):
    dataRecord = 0
    line = fopen.readline()

    segments = []
    vertices = []
    while line:
        if '#' not in line:
            if dataRecord == 1:      # record the info of segments, #0 is segmentID, #1 is segment size #3#4 is both vertices
                segments.append( [int(i) for i in line.split() ])
            elif dataRecord == 2:    # record the coordinates of vertices
                vertices.append( [float(i) for i in line.split() ])

        if 'segmentID' in line:
            dataRecord = 1
        elif 'vertices' in line:
            dataRecord = 2

        line = fopen.readline()
    return np.array(segments, dtype=int), np.array(vertices, dtype=float)

# --------------------------------------------------------------------
#                                MAIN
# --------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """
Transform linear binned data into Euler angles. ***This script does not support the case that one CRYSTALLITE contains
more than one (constituent).***

""")


parser.add_option('-t', dest='threshold', type='int', metavar = 'int',
                  help='only the GBs with segment size larger than threshold will be considered [%default]')
parser.add_option('--tiny', dest='tinyGB', action='store_false',
                  help = 'plot tiny grain boundary [%default]' )
parser.add_option('-p', dest='phase', type='int', metavar = 'int',
                  help='phase of grain boundary')
parser.add_option('-c', '--clear', dest='clearEulerAngs', action='store_false',
                  help = 'the Euler angles of GB phase will be cleared to be zero, if True [%default]' )


parser.set_defaults(
                    threshold      = 10.0,
                    format         = 'ctf',
                    materials      = ['Al'],
                    smooth         = True,
                    maxround       = 5,
                    fill           = True
                    phase          = 0
                 )


(options,filenames) = parser.parse_args()

halfGBwidth = options.width/2
if filenames == []:
    print 'missing the .geom filgroue, please specify a geom file!'
else:
    for filename in filenames:
        print 'process file %s by %s'%(filename, scriptName)
        if os.path.exists(filename):
            #
            gbFile = os.path.splitext(filename)[0]+'.mgb'
            if not os.path.exist(gbFile):
                print 'I cannot find the grain boundary file: %s'%gbFile
                continue

            fopen = open(filename, 'r')
            eulerangles, coords, phases, fileHeader = readCtfFile(fopen)  
            fopen.close()
            xcells = ebsdInfo['xcells']; ycells = ebsdInfo['ycells']
            xstep  = ebsdInfo['xstep'];  ystep  = ebsdInfo['ystep']
            if options.phase == 0:
                options.phase = np.max(phases) + 1

            xstep, ystep = ebsdInfo['xstep'], ebsdInfo['ystep']
            xcells, ycells = ebsdInfo['xcells'], ebsdInfo['ycells']

            fopen = open(gbFile, 'r')
            segments, vertices = getSegmentsVertices(fopen)
            fopen.close()

            vertexInBox = np.ones(len(vertices), dtype=bool)

            maxSegment = np.max(segments[:,0])
            segmentInfoDict = {}
            for seg in segments:
                segIDkey = str(seg[0])
                if segIDkey in segmentInfoDict.keys():
                    segmentInfoDict[segIDkey]['vertices'].append( [seg[2], seg[3]] )
                else:
                    segmentInfoDict[segIDkey] = {'size': seg[1], 'tinyGB': False, 'vertices': [ [seg[2], seg[3]] ] }

            if not options.tinyGB:
                for segIDkey in segmentInfoDict.keys():
                    if segmentInfoDict[segIDkey]['size'] <= thresholdSegSize:
                        verticeSet = []
                        if segmentInfoDict[segIDkey]['size'] > len(set( verticeSet.extend(vlist) \
                           for vlist in segmentInfoDict[segIDkey]['vertices'] )) + duplicateVertices:
                            segmentInfoDict[segIDkey]['tinyGB'] = True

            for i, v in enumerate(vertices):
                if not 0.0 < v[0] < (xcells-1.0)*xstep or not 0.0 < v[1] < (ycells-1.0)*ystep: vertexInBox[i] = False


            for segIDkey in segmentInfoDict.keys():
                vertexList = segmentInfoDict[segIDkey]['vertices']

                if not segmentInfoDict[segIDkey]['tinyGB']:
                    for p1, p2 in vertexList:
                        for p in [p1,p2]:
                            if vertexInBox[p-1]:
                                x, y = vertices[p-1, 0], vertices[p-1, 1]
                                icols, jrows = x/xstep, y/ystep
                                minCol = max(icols-halfGBwidth-1, 0); maxCol = min(xcells, icols+halfGBwidth)
                                minRow = max(irows-halfGBwidth-1, 0); maxRow = min(ycells, irows+halfGBwidth)
                                for icol in icols
            plt.show()
