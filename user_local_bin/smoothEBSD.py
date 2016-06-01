#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
'''
 File Name: smoothEBSD.py
 Author: Haiming Zhang
 Mail: hm.zhang@sjtu.edu.cn
 Created Time: 2016年05月30日 星期一 23时33分03秒
'''

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
                    

                    
