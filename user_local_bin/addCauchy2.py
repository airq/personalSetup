#!/usr/bin/env python2
# -*- coding: UTF-8 no BOM -*-

import os,sys
import numpy as np
from optparse import OptionParser
import damask
from myLibs import outputPrecision, delPlusZero

scriptName = os.path.splitext(os.path.basename(__file__))[0]
scriptID   = ' '.join([scriptName,damask.version])

# --------------------------------------------------------------------
#                                MAIN
# --------------------------------------------------------------------

parser = OptionParser(option_class=damask.extendableOption, usage='%prog options [file[s]]', description = """
Add column(s) containing Cauchy stress based on given column(s) of deformation gradient and first Piola--Kirchhoff stress.

""", version = scriptID)

parser.add_option('-f','--defgrad',
                  dest = 'defgrad',
                  type = 'string', metavar = 'string',
                  help = 'heading of columns containing deformation gradient [%default]')
parser.add_option('-p','--stress',
                  dest = 'stress',
                  type = 'string', metavar = 'string',
                  help = 'heading of columns containing first Piola--Kirchhoff stress [%default]')
parser.add_option('--compress', action='store_false', dest='compress',
                  help='compress the presion of the output data [%default]')

parser.set_defaults(defgrad = 'f',
                    stress  = 'p',
                    compress = True,
                   )

(options,filenames) = parser.parse_args()

# --- loop over input files -------------------------------------------------------------------------

if filenames == []: filenames = [None]

for name in filenames:
  try:
    table = damask.ASCIItable(name = name, buffered = False)
  except:
    continue
  damask.util.report(scriptName,name)

# ------------------------------------------ read header ------------------------------------------

  table.head_read()

# ------------------------------------------ sanity checks ----------------------------------------

  errors = []
  column = {}
  
  for tensor in [options.defgrad,options.stress]:
    dim = table.label_dimension(tensor)
    if   dim <  0: errors.append('column {} not found.'.format(tensor))
    elif dim != 9: errors.append('column {} is not a tensor.'.format(tensor))
    else:
      column[tensor] = table.label_index(tensor)

  if errors != []:
    damask.util.croak(errors)
    table.close(dismiss = True)
    continue

# ------------------------------------------ assemble header --------------------------------------

  table.info_append(scriptID + '\t' + ' '.join(sys.argv[1:]))
  table.labels_append(['%i_Cauchy'%(i+1) for i in xrange(6)])                                       # extend ASCII header with new labels
  table.head_write()

# ------------------------------------------ process data ------------------------------------------
  outputAlive = True
  while outputAlive and table.data_read():                                                          # read next data line of ASCII table
    F = np.array(map(float,table.data[column[options.defgrad]:column[options.defgrad]+9]),'d').reshape(3,3)
    P = np.array(map(float,table.data[column[options.stress ]:column[options.stress ]+9]),'d').reshape(3,3)
    Cauchy = list(1.0/np.linalg.det(F)*np.dot(P,F.T).reshape(9))                                    # [Cauchy] = (1/det(F)) * [P].[F_transpose]
    # 11(0) 12(1) 13(2); 21(3) 22(4) 23(5); 31(6) 32(7) 33(8) to 11(0) 22(1) 33(2) 12(3) 23(4) 31(5)
    Cauchy = [Cauchy[0], Cauchy[4], Cauchy[8], 0.5*(Cauchy[1] + Cauchy[3]), 0.5*(Cauchy[5]+Cauchy[7]), 0.5*(Cauchy[2]+Cauchy[6])]
    if options.compress:
        precision = outputPrecision['cr_stress']
        Cauchy = [ delPlusZero(format( i, precision[2]%(precision[0]-1))  ) for i in Cauchy]
    table.data_append(Cauchy)                                                                       # [Cauchy] = (1/det(F)) * [P].[F_transpose]
    outputAlive = table.data_write()                                                                # output processed line

# ------------------------------------------ output finalization -----------------------------------

  table.close()                                                                                     # close input ASCII table (works for stdin)
