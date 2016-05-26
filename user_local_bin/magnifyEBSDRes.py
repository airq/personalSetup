#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-

import os,sys,math
import numpy as np
from optparse import OptionParser

def allAreDigit(string):
    results = True
    if string[0] == '#':
        results = False
    else:
        for ele in string.split():
            for beta in ele: 
                if beta.isalpha(): 
                    results= False
                    break
    return results

scriptName = os.path.splitext(os.path.basename(__file__))[0]

#--------------------------------------------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """

magnify the resolution of EBSD data files, supporting .ctf and .ang format, must be carefull about
the default columex when .ang file is being processed ***.
""")

parser.add_option('-c','--columex',
                  dest = 'columex',
                  type = 'int', metavar = 'int',
                  help='the colume number of x coordinate, must be careful about the default value, if .ang is processed [%default]')

parser.add_option('-t','--times',
                  dest = 'times',
                  type = 'int', metavar = 'int',
                  help='the magnifing times [%default]')

parser.set_defaults(
                    columex = 2,
                    times = 2,
                 )
(options,filenames) = parser.parse_args()

xcol = options.columex - 1

# --- loop over input files -------------------------------------------------------------------------
files = []
if filenames == []:
  files.append({'name':'STDIN','input':sys.stdin,'output':sys.stdout,'croak':sys.stderr})
else:
  for name in filenames:
    if os.path.exists(name):
        outfile = os.path.splitext(name)[-2] + '_magnify_' + str(options.times)+ '_times' + os.path.splitext(name)[-1] 
        files.append({'name':name,'input':open(name),'output':open(outfile,'w'),'croak':sys.stdout, 'format':os.path.splitext(name)[-1]})
    else:
        print 'file not found'


#--- loop over input files ------------------------------------------------------------------------
for file in files:
  file['croak'].write('\033[1m' + scriptName + '\033[0m: ' + (file['name'] if file['name'] != 'STDIN' else '') + '\n')
  content = file['input'].readlines()

  lineTemp = []
  stepIndex = {}; dimenIndex = {}
  for line in content:
      for text in ['xstep', 'ystep']:
          if text in line.lower():
              X = line.split()[-1]
              stepIndex[text] = float(X)
              line = line.replace(X, str(float(X)/options.times))

      textlist = ['xcells', 'ycells'] if file['format'] == '.ctf' else ['ncols_odd', 'ncols_even', 'nrows']
      for text in textlist:
          if text in line.lower(): 
              X = line.split()[-1]
              dimenIndex[text] = int(X)
              line = line.replace(X, str(int(X)*options.times))
      
      if allAreDigit(line):
          offsetLine = content.index(line)
          break
      file['output'].write(line)

  xstep, ystep = stepIndex['xstep']/options.times, stepIndex['ystep']/options.times
  xcells, ycells = (dimenIndex['xcells'], dimenIndex['ycells']) if file['format'] == '.ctf' else \
                   (dimenIndex['ncols_odd'], dimenIndex['nrows'])

  splitSign = '\t' if file['format'] == '.ctf' else '    '

# begin write data
  for i, line in enumerate(content[offsetLine:]):
      lineSplit = line.split()
      X = lineSplit[xcol]
      lineTemp.append(splitSign.join((ele) for ele in lineSplit))
      for iextend in xrange(options.times-1):
          lineSplit[xcol] = str(float(X) + xstep*(iextend+1))
          lineTemp.append( splitSign.join( (ele) for ele in lineSplit ) )
      
      if np.mod( (i+1), xcells ) == 0:
          for subline in lineTemp: file['output'].write(subline + '\n')
          for jextend in xrange(options.times-1):
              lineSplit = lineTemp[0].split()
              Y = str( float(lineSplit[xcol + 1]) + ystep*(jextend+1))
              for subline in lineTemp:
                  lineSplit = subline.split()
                  lineSplit[xcol+1] = Y 
                  file['output'].write( splitSign.join( (ele) for ele in lineSplit ) + '\n' )

          lineTemp = []

  file['input'].close()
  file['output'].close()
  file['croak'].close()
