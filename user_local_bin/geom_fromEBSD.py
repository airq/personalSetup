#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
'''
 Author: Haiming Zhang
 Mail: hm.zhang@sjtu.edu.cn
 Created Time: 2016年05月28日 星期六 15时47分28秒
'''

import os,sys,math
import numpy as np
from optparse import OptionParser
from myLibs import ebsdInfo, readAngFile, readCtfFile
import damask

scriptName = os.path.splitext(os.path.basename(__file__))[0]
scriptID   = ' '.join([scriptName,damask.version])


info = {
          'grid':   np.ones(3,'i'),
          'size':   np.zeros(3,'d'),
          'origin': np.zeros(3,'d'),
          'microstructures': 0,
          'homogenization': 0
         }

  
#-------------------------------------re-------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """

Generate geometry description and material configuration from EBSD data in given square-gridded 'ang' file.
Two phases can be discriminated based on threshold value in a given data column.

""", version = scriptID)

parser.add_option('--column',              dest='column', type='int', metavar = 'int',
                  help='data column to discriminate between both phases [%default]')
parser.add_option('-t','--threshold',      dest='threshold', type='float', metavar = 'float',
                  help='threshold value for phase discrimination [%default]')
parser.add_option('--homogenization',      dest='homogenization', type='int', metavar = 'int',
                  help='homogenization index for <microstructure> configuration [%default]')
parser.add_option('--phase',               dest='phase', type='int', nargs = 2, metavar = 'int int',
                  help='phase indices for <microstructure> configuration %default')
parser.add_option('--crystallite',         dest='crystallite', type='int', metavar = 'int',
                  help='crystallite index for <microstructure> configuration [%default]')
parser.add_option('-a', '--axes',         dest='axes', nargs = 3, metavar = 'string string string',
                  help='Euler angle coordinate system for <texture> configuration x,y,z = %default')
parser.add_option('-p', '--precision',    dest='precision', choices=['0','1','2','3'], metavar = 'int',
                  help = 'euler angles decimal places for output format and compressing (0,1,2,3,4) [3]')
parser.add_option('-e','--enlarge',         dest='enlarge', type='int', metavar = 'int',
                  help='enlarge the resolution [%default]')
 
parser.set_defaults(column         = 11,
                    threshold      = 0.5,
                    homogenization = 1,
                    phase          = [1,2],
                    crystallite    = 1,
                    compress       = False,
                    axes           = [], #['y','x','-z'],
                    precision      = '3',
                    enlarge        = 1,
                 )
(options,filenames) = parser.parse_args()


for i in options.axes:
    if i.lower() not in ['x','+x','-x','y','+y','-y','z','+z','-z']:
        parser.error('invalid axes %s %s %s' %(options.axes[0],options.axes[1],options.axes[2]))

# --- loop over input files -------------------------------------------------------------------------
if filenames == []: 
    print 'missing input files'
    exit()

for filename in filenames:
    try:
        table = damask.ASCIItable(name = filename,
                                  outname = os.path.splitext(filename)[-2]+'.geom',
                                  buffered = False, labeled = False)
    except: continue
    damask.util.report(scriptName,filename)

#   open file and read data
    fopen = open(filename, 'r')
    if os.path.splitext(filename)[-1] == '.ang':
        eulerangles, coords, phase, geomHeader = readAngFile(fopen, options.phase, options.column, options.threshold)

        info['grid'][:] = ebsdInfo['ncols_odd'], ebsdInfo['nrows'], 1
        info['size'][:] = ebsdInfo['ncols_odd']*ebsdInfo['xstep'], ebsdInfo['nrows']*ebsdInfo['ystep'], min(ebsdInfo['xstep'], ebsdInfo['ystep'])
    elif os.path.splitext(filename)[-1] == '.ctf':
        eulerangles, coords, phase, geomHeader = readCtfFile(fopen)

        info['grid'][:] = ebsdInfo['xcells'], ebsdInfo['ycells'], 1
        info['size'][:] = ebsdInfo['xcells']*ebsdInfo['xstep'], ebsdInfo['ycells']*ebsdInfo['ystep'], min(ebsdInfo['xstep'], ebsdInfo['ystep'])
    else:
        print 'unknown input file type!!'
        continue


    # only support two dimension
    # only support two dimension

#   check euler angle data
    limits = [360,180,360];  errors = []
    if any([np.any(eulerangles[:,i]>=limits[i]) for i in [0,1,2]]):
        print 'Warning: euler angles out of bound. ebsd file might contain unidexed poins.'
        for i,angle in enumerate(['phi1','PHI','phi2']):
            for n in np.nditer(np.where(eulerangles[:,i]>=limits[i]),['zerosize_ok']):
                print '%s in line %i (%4.2f %4.2f %4.2f)\n'%(angle,n,eulerangles[n,0],eulerangles[n,1],eulerangles[n,2])
                eulerangles[n,i] = eulerangles[n,i] - limits[i]


    eulerangles=np.around(eulerangles,int(options.precision))                                         # round to desired precision
    # ensure, that rounded euler angles are not out of bounds (modulo by limits)
    for i,angle in enumerate(['phi1','PHI','phi2']):
        eulerangles[:,i]%=limits[i]

#   prepare for writing <texture>
    texture = np.arange(info['grid'].prod())
    formatOut = 1+int(math.log10(len(texture)))
    textureOut =['<texture>']
    eulerFormatOut='%%%i.%if'%(int(options.precision)+4,int(options.precision))
    outStringAngles='(gauss) phi1 '+eulerFormatOut+' Phi '+eulerFormatOut+' phi2 '+eulerFormatOut+' scatter 0.0 fraction 1.0'
    for i in xrange(len(texture)):
        if options.axes:
            textureOut +=       ['[Texture%s]'%str(i+1).zfill(formatOut),
                                  'axes %s %s %s'%(options.axes[0],options.axes[1],options.axes[2]),
                                  outStringAngles%tuple(eulerangles[texture[i],...])
                                 ]
        else:
            textureOut +=       ['[Texture%s]'%str(i+1).zfill(formatOut),
                                  outStringAngles%tuple(eulerangles[texture[i],...])
                                 ]

#   prepare for writing <microstructure>
    microstructure = np.hstack( zip(texture,phase) ).reshape(info['grid'].prod(),2)                 # create texture/phase pairs
    formatOut = 1+int(math.log10(len(microstructure)))
    microstructureOut =['<microstructure>']
    for i in xrange(len(microstructure)):
        microstructureOut += ['[Grain%s]'%str(i+1).zfill(formatOut),
                             'crystallite\t%i'%options.crystallite,
                             '(constituent)\tphase %i\ttexture %i\tfraction 1.0'%(microstructure[i,1],microstructure[i,0]+1)
                             ]
    info['microstructures'] = len(microstructure)
    grid0 = info['grid'][0], info['grid'][1], info['grid'][2] # using info['grid'] then share the same memory, using info[grid][:] then different memory
    info['size'][0:2] = options.enlarge*info['size'][0:2]; info['grid'][0:2] = options.enlarge*info['grid'][0:2]
    info['homogenization'] = options.homogenization

#-- report ---------------------------------------------------------------------------------------
    damask.util.croak('grid     a b c:  %s\n'%(' x '.join(map(str,info['grid']))) +
           'size     x y z:  %s\n'%(' x '.join(map(str,info['size']))) +
           'origin   x y z:  %s\n'%(' : '.join(map(str,info['origin']))) +
           'homogenization:  %i\n'%info['homogenization'] +
           'microstructures: %i\n\n'%info['microstructures'])

    if np.any(info['grid'] < 1):
        damask.util.croak('invalid grid a b c.\n')
        continue
    if np.any(info['size'] <= 0.0):
        damask.util.croak('invalid size x y z.\n')
        continue


#--- write data/header --------------------------------------------------------------------------------
    table.info_clear()
    table.info_append([' '.join([scriptID] + sys.argv[1:]),
                     "grid\ta %i\tb %i\tc %i"%(info['grid'][0],info['grid'][1],info['grid'][2],),
                     "size\tx %f\ty %f\tz %f"%(info['size'][0],info['size'][1],info['size'][2],),
                     "origin\tx %f\ty %f\tz %f"%(info['origin'][0],info['origin'][1],info['origin'][2],),
                     "microstructures\t%i"%info['microstructures'],
                     "homogenization\t%i"%info['homogenization'],
                     ] +
                     [line for line in microstructureOut + textureOut]
                    )
    table.head_write()
    if options.compress:
        matPoints = matPoints.reshape((info['grid'][1],info['grid'][0]))
        table.data = matPoints
        table.data_writeArray('%%%ii'%(1+int(math.log10(np.amax(matPoints)))),delimiter=' ')
    else:
        if options.enlarge == 1:
            table.output_write("1 to %i\n"%(info['microstructures']))
        else:
            for irow in xrange(grid0[1]):
                grain0 = irow*grid0[0] + 1
                for i in xrange(options.enlarge):
                    table.output_write( ''.join( [ (str(jcol + grain0)+' ')*options.enlarge for jcol in xrange( grid0[0] ) ] ) )
    table.output_flush()

  # --- output finalization --------------------------------------------------------------------------

    table.close()
