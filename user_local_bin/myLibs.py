#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
'''
 File Name: myLibs.py
 Author: Haiming Zhang
 Mail: hm.zhang@sjtu.edu.cn
 Created Time: 2016年06月01日 星期三 17时04分00秒
'''

import os,sys,math
import numpy as np

ebsdInfo = {
            'xstep' : 0,
            'ystep' : 0,
            'xcells': 0,
            'ycells': 0,
            'ncols_odd':  0,  # xcells for ang
            'ncols_even': 0,
            'nrows':      0
           }


'''
Comments on readCtfFile, readAngFile.
arrayStoreNo. phase   x   y   euler1  euler2  euler3
   0          n       0   0     e1      e2      e3
   1          n       1   0     e1      e2      e3
   2          n       2   0     e1      e2      e3
   ...        n     ...   0     e1      e2      e3
   N          n       N   0     e1      e2      e3
   N+1        n       0   1     e1      e2      e3
   N+2        n       1   1     e1      e2      e3
   N+3        n       2   1     e1      e2      e3
   ...
fix y first, and loop x
'''
def readCtfFile(fopen):
    fileHeader = []; coords0 = []; eulerangles0 = []; phase0 = []
    beginRecord = False
    line = fopen.readline()
    while line:
        if line.strip() != '':                        # non-empty line
            words = line.split()
            if beginRecord:                                                                               # process initial comments/header block
                coords0.append(map(float, words[1:3]))                       # coordinates
                eulerangles0.append(map(float,words[5:8])) # radius to degree
                if map(int, words[0]) <= 0:
                    print 'negative phase No. detected, I will see it as 0, please check the input data'
                    phase0.append(0)
                else:
                    phase0.append(map(int, words[0])) #phase
            else:
                fileHeader.append(line)
                for key in ebsdInfo.keys():
                    if key in line.lower(): ebsdInfo[key] = float(words[-1])
        if 'phase' in line.lower() and 'euler1' in line.lower():
            beginRecord = True
        line = fopen.readline()

    if any( [ebsdInfo[key] for key in ['xstep', 'ystep', 'xcells', 'ycells']] ) == 0:
        coordsArray = np.array(coords0)
        ebsdInfo['xstep']  = coordsArray[1,0] - coordsArray[0,0]
        ebsdInfo['xcells'] = int( np.round( (np.max(coordsArray[:,0]) - coordsArray[0,0] )/ebsdInfo['xstep'] )) + 1
        ebsdInfo['ystep']  = coordsArray[ebsdInfo['xcells'], 1] - coordsArray[0,1]
        ebsdInfo['ycells']  = int( np.round( (np.max(coordsArray[:,1]) - coordsArray[0,0] )/ebsdInfo['ystep'] )) + 1

    return np.array(eulerangles0,dtype='f').reshape(ebsdInfo['xcells']*ebsdInfo['ycells'],3), \
           np.array(coords0,dtype='f').reshape(ebsdInfo['xcells']*ebsdInfo['ycells'],2), \
           np.array(phase0,dtype='i').reshape(ebsdInfo['xcells']*ebsdInfo['ycells']), \
           fileHeader

def readAngFile(fopen, phaseList, phaseColumn, phaseThreshold):
    fileHeader = []; coords0 = []; eulerangles0 = []; phase0 = []
    line = fopen.readline()
    while line:
        if line.strip() != '':                        # non-empty line
            words = line.split()
            if words[0] == '#':                                                                               # process initial comments/header block
                fileHeader.append(line)
                for key in ebsdInfo.keys():
                    if key in line.lower(): ebsdInfo[key] = float(words[-1])
            else:
                coords0.append(map(float, words[3:5]))                       # coordinates
                eulerangles0.append(map(math.degrees, map(float,words[:3]))) # radius to degree
                phase0.append(phaseList[int(float(words[phaseColumn-1]) > phaseThreshold)]) # phase
        line = fopen.readline()

    if any( [ebsdInfo[key] for key in ['xstep', 'ystep', 'nrows']] ) == 0:
        coordsArray = np.array(coords0)
        ebsdInfo['xstep'] = coordsArray[1,0] - coordsArray[0,0]
        ebsdInfo['ncols_odd'] = ebsdInfo['ncols_even'] = int( np.round( (np.max(coordsArray[:,0]) - coordsArray[0,0] )/ebsdInfo['xstep'] )) + 1
        ebsdInfo['ystep'] = coordsArray[ebsdInfo['ncols_odd'], 1] - coordsArray[0,1]
        ebsdInfo['nrows'] = int( np.round( (np.max(coordsArray[:,1]) - coordsArray[0,0] )/ebsdInfo['ystep'] )) + 1


    # processs the hexgrid data, i.e., ncols_odd != ncols_even
    ncols_odd = ebsdInfo['ncols_odd'];  ncols_even = ebsdInfo['ncols_even']; xstep = ebsdInfo['xstep']
    if ncols_odd == ncols_even:
        coords = coords0; eulerangles = eulerangles0; phase = phase0
    else:
        coords = []; phase = []; eulerangles = []
        ncols = ncols_odd+ncols_even
        for i in xrange(len(coords0)):
            if np.mod(i, ncols) < ncols_odd:
                coords.append(coords0[i])
                phase.append(phase0[i])
                eulerangles.append(eulerangles0[i])
            elif np.mod(i, ncols) == ncols_odd:
                coords.append([coords0[i][0]-0.5*xstep, coords0[i][1]])
                phase.append(phase0[i])
                eulerangles.append(eulerangles0[i])
            else:
                coords.append([(coords0[i][0] + coords0[i-1][0])*0.5, coords0[i][1]])
                phase.append((phase0[i] +phase0[i-1])*0.5)
                eulerangles.append([(eulerangles0[i][0] +eulerangles0[i-1][0])*0.5, (eulerangles0[i][1] +eulerangles0[i-1][1])*0.5, (eulerangles0[i][2]
                    +eulerangles0[i-1][2])*0.5] )
                if np.mod(i, ncols) == ncols-1:
                    coords.append([coords0[i][0]+0.5*xstep, coords0[i][1]])
                    phase.append(phase0[i])
                    eulerangles.append(eulerangles0[i])

    return np.array(eulerangles,dtype='f').reshape(ebsdInfo['ncols_odd']*ebsdInfo['nrows'],3), \
           np.array(coords,dtype='f').reshape(ebsdInfo['ncols_odd']*ebsdInfo['nrows'],2), \
           np.array(phase,dtype='i').reshape(ebsdInfo['ncols_odd']*ebsdInfo['nrows']), \
           fileHeader
