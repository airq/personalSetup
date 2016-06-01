#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
'''
 File Name: smoothEBSD.py
 Author: Haiming Zhang
 Mail: hm.zhang@sjtu.edu.cn
 Created Time: 2016年05月30日 星期一 23时33分03秒
'''

from myLibs import readCtfFile, ebsdInfo

def getNeighbor(nCol, nRow):
    mapPosition2Grids = np.empty( [nRow, nCol])
    for jrow in xrange(nRow):
        mapPosition2Grids[jrow, :] = [icol + jrow*nCol for icol in nCol]


    for jrow in xrange(nRow):
        for icol in xrange(nCol):
            if jrow == 0:
                if icol == 0:
                    neibour.append[ mapPos2Grid[jrow+1, icol],  mapPos2Grid[jrow+1, icol+1], mapPos2Grid[jrow, icol+1] ]
                elif icol = nCol - 1
                    neibour.append[ mapPos2Grid[jrow, icol-1],  mapPos2Grid[jrow+1, icol-1], mapPos2Grid[jrow+1,icol] ]
                else:
                    neibour.append[ mapPos2Grid[jrow, icol-1], mapPos2Grid[jrow+1, icol-1], mapPos2Grid[jrow+1, icol],  mapPos2Grid[jrow+1, icol+1],
                            mapPos2Grid[jrow, icol+1]  ]
            elif jrow == nRow-1:
                if icol == 0:
                    neibour.append[ mapPos2Grid[jrow, icol+1],  mapPos2Grid[jrow-1, icol+1], mapPos2Grid[jrow-1, icol] ]
                elif icol = nCol - 1
                    neibour.append[ mapPos2Grid[jrow-1, icol],  mapPos2Grid[jrow-1, icol-1], mapPos2Grid[jrow,icol-1] ]
                else:
                    neibour.append[ mapPos2Grid[jrow, icol+1], mapPos2Grid[jrow-1, icol+1], mapPos2Grid[jrow-1, icol],  mapPos2Grid[jrow-1, icols-1],
                            mapPos2Grid[jrow, icol-1]  ]
            else:
                if icol = 0:
                    neibour.append[ mapPos2Grid[jrow+1, icol], mapPos2Grid[jrow+1, icol+1], mapPos2Grid[jrow, icol+1],  mapPos2Grid[jrow-1, icols+1],
                            mapPos2Grid[jrow-1, icol]  ]
                elif icol = nCol:
                    neibour.append[ mapPos2Grid[jrow-1, icol], mapPos2Grid[jrow-1, icol-1], mapPos2Grid[jrow, icol-1],  mapPos2Grid[jrow+1, icols-1],
                            mapPos2Grid[jrow+1, icol]  ]
                else:
                    neibour.append[ mapPos2Grid[jrow+1, icol], mapPos2Grid[jrow+1, icol+1], mapPos2Grid[jrow, icol+1],  mapPos2Grid[jrow-1, icol+1],
                                    mapPos2Grid[jrow-1, icol], mapPos2Grid[jrow-1, icol-1], mapPos2Grid[jrow, icol-1],  mapPos2Grid[jrow+1, icol-1]  ]
                    

                    
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
            #
            eulerangles0, coords0, phase0, fileHeader = readCtf(fopen)  
            xcells, ycells = ebsdInfo['xcells'], ebsdInfo['ycells']
            eulerangles = eulerangles0.reshape(ycells, xcells, 3)
            phases      = phase0.reshape(ycells, xcells)


            neighbors = getNeighbor(xcells, ycells)

            for jrow in xrange(ycells):
                for icol in xrange(xcells):
                   
                    pos = jrow*xcells + icol
                    neighborGrids = neighbors[pos]

