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

# the last one must be the name of the tuple.
cr_stress = ('p', 's', 'work', 'cr_stress')
cr_deform = ('f', 'fe', 'fp', 'e', 'ee', 'lp', 'cr_deform')
cr_orient = ( 'eulerangles', 'grainrotation', 'cr_orient')
co_stress = ( 'resistance_slip', 'resolvedstress_slip',
              'resistance_twin', 'resolvedstress_twin',
              'thresholdstress_twin',
              'flowstress',
              'co_stress',
            )
co_shear  = ( 'shearrate_slip', 'accumulatedshear_slip', 'totalshear',
              'shearrate_twin', 'accumulatedshear_twin',
              'strainrate',
              'co_shear'
            )
co_dislo =  ( 'edge_density', 'dipole_density',
              'co_dislo'
            )

allVariables = [cr_stress, cr_deform, cr_orient, co_stress, co_shear, co_dislo]
outputPrecision = {
                   'cr_stress': [6, 1.0e-6, '.%se'],     # MPa
                   'cr_deform': [6, 6,      '.%se'],
                   'cr_orient': [3, 3,      '6.%sf'],
                   'co_stress': [5, 1.0e-6, '.%se'],     # MPa
                   'co_shear' : [5, 5,      '.%se'],
                   'co_dislo' : [5, 1.0e-6, '.%se'],     # mm^-2
                   'others'   : [5, 5,      '.%se']
                 }


def delPlusZero(string):
    '''
    for a number like 1.2e+01, it is changed like 1.2e1; for a number like 1.2e-01, it is changed like 1.2e-1, can not be used in xxxxe0yy
    '''
    if not string[-3:].isdigit():
        if 'e+' in string:
            return string.replace('e+0','e').replace('e+', 'e') if string[-1] != '0' else string.replace('e+00','').replace('e+0','')
        elif 'e-0' in string:
            return string.replace('e-0', 'e-') if string[-1] != '0' else string.replace('e-00','').replace('e-0', '')
        elif 'e0' in string:
            return string.replace('e0', 'e') if string[-1] != '0' else string.replace('e00','').replace('e0', '')
        else:
            return string
    else:
        print 'I can not change the data like xxxe0yy!'
        return string

def allIsDigit(line):
    return all(i.isdigit() for i in line.split())

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
    '''
    # remenber, euler = eulerangles.reshape(ycells, xcells, 3); euler(jrow, icol, :)
    '''
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
                    if key in line.lower(): 
                        ebsdInfo[key] = float(words[-1]) if key in ['xstep', 'ystep'] else int(words[-1])

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
    # remenber, euler = eulerangles.reshape(ycells, xcells, 3); euler(jrow, icol, :)


def getEBSDHeader(xCells,yCells,xStep, yStep, format, materials=['Al']):
    '''
    materials is a list, for example. ['Al', 'Mg'], then the phase No. is Al-1, Mg-2 
    '''
    materialLatticeParas = \
      {
        'ang': 
          { 'Al': [ '# MaterialName          Al',  '# Formula               Fe',  '# Info',  '# Symmetry              43', 
                    '# LatticeConstants      2.870 2.870 2.870  90.000  90.000  90.000',  '# NumberFamilies        4', 
                    '# hklFamilies           1  1  0 1 0.000000 1',  '# hklFamilies           2  0  0 1 0.000000 1', 
                    '# hklFamilies           2  1  1 1 0.000000 1',  '# hklFamilies           3  1  0 1 0.000000 1', 
                    '# Categories            0 0 0 0 0 ', ]
          },
        'ctf':
          { 'Al': [ '4.05;4.05;4.05\t90;90;90\tAluminium\t11\t225\t3803863129_5.0.6.3\t-2102160418\tCryogenics18,54-55',
                    'Phase\tX\tY\tBands\tError\tEuler1\tEuler2\tEuler3\tMAD\tBC\tBS'],
            'Mg': [ '3.209;3.209;3.209\t90;90;120\tMagnesium\t9\t194',
                    'Phase\tX\tY\tBands\tError\tEuler1\tEuler2\tEuler3\tMAD\tBC\tBS'],
            'Cu': ['3.6144;3.6144;3.6144\t90;90;90\tCopper\t11\t225\t3803863129\t5.0.6.3\t-906185425'],
          }
      }
#
    header0 = \
      {
        'ang': [ '# TEM_PIXperUM          1.000000',  '# x-star                0.509548',  '# y-star                0.795272', 
                 '# z-star                0.611799',  '# WorkingDistance       18.000000',  '#', ],
        'ctf': [ 'Channel Text File',    'Prj\tX:\\xxx\\xxxx.cpr',
                 'Author\t[Haiming Zhang at Shanghai Jiao Tong University]',  'JobMode\tGrid', ]
      }

    tail = \
      {
        'ang': [ '#',  '# OPERATOR: ODFsammpling',  '#',  '# SAMPLEID: ',  '#',  '# SCANID: ', '#'],
        'ctf': [ 'AcqE1\t0',  'AcqE2\t0', 'AcqE3\t0', 
                 'Euler angles refer to Sample Coordinate system (CS0)!\tMag\t300\tCoverage\t100\tDevice\t0\tKV\t20\tTiltAngle\t70\tTiltAxis\t0'],
      }

    phasePrefix = \
      {
        'ang': '# Phase                 ',
        'ctf': 'Phases\t'
      }

    sizeInfo = \
      {
        'ang': [ '#', '# GRID: SquareGrid', '# XSTEP: ' + str(xStep), '# YSTEP: ' + str(yStep), '# NCOLS_ODD: ' + str(xCells), 
                 '# NCOLS_EVEN: ' + str(xCells), '# NROWS: ' + str(yCells), ],
        'ctf': [ 'XCells\t'+ str(xCells), 'YCells\t'+ str(yCells), 'XStep\t'+ str(xStep), 'YStep\t'+ str(yStep), ]
      }

    phaseText = []
    for phasei, m in enumerate(materials):
        phaseText = phaseText + [phasePrefix[format] + str(phasei+1)] + materialLatticeParas[format][m]
    if format == 'ang':
        return header0[format] + phaseText + sizeInfo[format] + tail[format]
    else:
        return header0[format] + sizeInfo[format] + tail[format] + phaseText 

# operate .geom or material.config file

def mapCoordCrystalNo(fopen, xyzposition):
    '''
    this subroutine deals with the .geom file, get the grain No of each grid.
    fopen is the read object of the .geom file, 
    surfPlot is the surface in which the orientation, x, y, or z
    sliceNo is the No. of slice will be along the normal of surfPlot
    will be plot.
    '''

    line = fopen.readline()
    geomInfo = {}
    mapCrystalNo = []
    while line:
        if not line.strip() == '':        # non empty line
            texts = line.split()

            if texts[0] in ['grid', 'size', 'origin']: 
                geomInfo[texts[0]] = [ texts[i] for i in xyzposition ]
            elif texts[0] in [ 'homogenization', 'microstructures']: 
                geomInfo[texts[0]] = texts[1]
            elif all(i.isdigit() for i in texts):
                mapCrystalNo.append( [ int(i) for i in texts ] )
            elif '1 to ' in line:
                for irow in xrange(int(geomInfo['grid'][1])):
                    mapCrystalNo.append( [int(irow*int(geomInfo['grid'][0]) + jcol + 1) for jcol in xrange(int(geomInfo['grid'][0])) ] )

        line = fopen.readline()
    return geomInfo, mapCrystalNo

