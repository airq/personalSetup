#!/usr/bin/env python2
# -*- coding: UTF-8 no BOM -*-

import os,sys,time,copy
import numpy as np
import damask
from optparse import OptionParser
from scipy import spatial

scriptName = os.path.splitext(os.path.basename(__file__))[0]
scriptID   = ' '.join([scriptName,damask.version])


parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [ASCIItable(s)]', description = """
Add grain index based on similiarity of crystal lattice orientation.

""", version = scriptID)

parser.add_option('-p',
                  '--phase',
                  dest = 'phase',
                  type = 'int', metavar = 'int',
                  help = 'the disoriention of this phase is 0, i.e, no rotation [%default]')
parser.add_option('-s',
                  '--symmetry',
                  dest = 'symmetry',
                  type = 'string', metavar = 'string',
                  help = 'crystal symmetry [%default]')
parser.add_option('-r',
                  '--reference',
                  dest = 'reference',
                  type = 'string', metavar = 'string',
                  help = 'reference file')
parser.add_option('-e',
                  '--eulers',
                  dest = 'eulers',
                  type = 'string', metavar = 'string',
                  help = 'label of Euler angles')
parser.add_option('--degrees',
                  dest = 'degrees',
                  action = 'store_false',
                  help = 'Euler angles are given in degrees [%default]')
parser.add_option('-m',
                  '--matrix',
                  dest = 'matrix',
                  type = 'string', metavar = 'string',
                  help = 'label of orientation matrix')
parser.add_option('-a',
                  dest = 'a',
                  type = 'string', metavar = 'string',
                  help = 'label of crystal frame a vector')
parser.add_option('-b',
                  dest = 'b',
                  type = 'string', metavar = 'string',
                  help = 'label of crystal frame b vector')
parser.add_option('-c',
                  dest = 'c',
                  type = 'string', metavar = 'string',
                  help = 'label of crystal frame c vector')
parser.add_option('-q',
                  '--quaternion',
                  dest = 'quaternion',
                  type = 'string', metavar = 'string',
                  help = 'label of quaternion')

parser.set_defaults(
                    phase = 0,
                    symmetry = 'cubic',
                    #pos      = 'pos',
                    degrees  = True,
                   )

(options, filenames) = parser.parse_args()

input = [options.eulers     is not None,
         options.a          is not None and \
         options.b          is not None and \
         options.c          is not None,
         options.matrix     is not None,
         options.quaternion is not None,
        ]

if np.sum(input) != 1: parser.error('needs exactly one input format.')

(label,dim,inputtype) = [(options.eulers,3,'eulers'),
                         ([options.a,options.b,options.c],[3,3,3],'frame'),
                         (options.matrix,9,'matrix'),
                         (options.quaternion,4,'quaternion'),
                        ][np.where(input)[0][0]]                                                    # select input label that was requested
toRadians = np.pi/180.0 if options.degrees else 1.0                                                 # rescale degrees to radians

# ----------------------------------------- loop reference file
if os.path.exists(options.reference):
    table = damask.ASCIItable(name = options.reference,buffered = False)
    table.head_read()
    errors  = []
  
    if not np.all(table.label_dimension(label) == dim):
        errors.append('input "{}" does not have dimension {}.'.format(label,dim))
    else:  column = table.label_index(label)

    if errors  != []:
        damask.util.croak(errors)
        table.close(dismiss = True)

# ------------------------------------------ process data ------------------------------------------ 
    print 'read the orientaion of the initial file'
    o0 = []
    while table.data_read():                                                                          # read next data line of ASCII table

        if inputtype == 'eulers':
            o = damask.Orientation(Eulers   = np.array(map(float,table.data[column:column+3]))*toRadians,
                             symmetry = options.symmetry).reduced()
        elif inputtype == 'matrix':
            o = damask.Orientation(matrix   = np.array(map(float,table.data[column:column+9])).reshape(3,3).transpose(),
                             symmetry = options.symmetry).reduced()
        elif inputtype == 'frame':
            o = damask.Orientation(matrix = np.array(map(float,table.data[column[0]:column[0]+3] + \
                                                         table.data[column[1]:column[1]+3] + \
                                                         table.data[column[2]:column[2]+3])).reshape(3,3),
                             symmetry = options.symmetry).reduced()
        elif inputtype == 'quaternion':
            o = damask.Orientation(quaternion = np.array(map(float,table.data[column:column+4])),
                             symmetry   = options.symmetry).reduced()
        o0.append(o)

# --- loop over input files -------------------------------------------------------------------------
if filenames == []: filenames = [None]

for name in filenames:
    try:    table = damask.ASCIItable(name = name,
                                      buffered = False)
    except: continue
    damask.util.report(scriptName,name)

# ------------------------------------------ read header -------------------------------------------  
    table.head_read()

# ------------------------------------------ sanity checks -----------------------------------------
    errors  = []
    if not np.all(table.label_dimension(label) == dim):
        errors.append('input "{}" does not have dimension {}.'.format(label,dim))
    else:  column = table.label_index(label)
    if options.phase > 0:
        phase_column = table.label_index('phase')
    else:
        phase_column = 0

    if errors  != []:
        damask.util.croak(errors)
        table.close(dismiss = True)
        continue

# ------------------------------------------ assemble header ---------------------------------------
    table.info_append(scriptID + '\t' + ' '.join(sys.argv[1:]))
    table.labels_append('disOrientation')                        # report orientation source and disorientation
    table.head_write()

# ------------------------------------------ process data ------------------------------------------
    table.data_rewind()
    igrid = 0; disOrient = []
    print 'processing the current file'
    while table.data_read():                                                                          # read next data line of ASCII table

        if options.phase > 0 and int( float( table.data[phase_column] ) ) == options.phase:
            disOrient.append(0.0)
        else:
            if inputtype == 'eulers':
                o = damask.Orientation(Eulers   = np.array(map(float,table.data[column:column+3]))*toRadians,
                                 symmetry = options.symmetry).reduced()
            elif inputtype == 'matrix':
                o = damask.Orientation(matrix   = np.array(map(float,table.data[column:column+9])).reshape(3,3).transpose(),
                                 symmetry = options.symmetry).reduced()
            elif inputtype == 'frame':
                o = damask.Orientation(matrix = np.array(map(float,table.data[column[0]:column[0]+3] + \
                                                                 table.data[column[1]:column[1]+3] + \
                                                                 table.data[column[2]:column[2]+3])).reshape(3,3),
                                 symmetry = options.symmetry).reduced()
            elif inputtype == 'quaternion':
                o = damask.Orientation(quaternion = np.array(map(float,table.data[column:column+4])),
                                     symmetry   = options.symmetry).reduced()

            disorientation = o.disorientation(o0[igrid], SST = False)[0]
            disOrient.append(np.arccos(disorientation.quaternion.w)/np.pi*180.0)

        outputAlive = True
        table.data_append(disOrient[igrid])                                                     # add (condensed) grain ID
        outputAlive = table.data_write()
        igrid += 1

# ------------------------------------------ output finalization -----------------------------------  
    table.close()                                                                                     # close ASCII tables
