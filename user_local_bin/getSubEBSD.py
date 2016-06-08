#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-

import os,sys,math
import numpy as np
from optparse import OptionParser


scriptName = os.path.splitext(os.path.basename(__file__))[0]

#--------------------------------------------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """

Generate geometry description and material configuration from EBSD data in given square-gridded 'ang' file.
Two phases can be discriminated based on threshold value in a given data column.

""")

parser.add_option('-o','--origin',
                  dest = 'origin',
                  type = 'int', nargs = 2, metavar = 'int int',
                  help='the left-lower corner of the sub ebsd')

parser.add_option('-g','--grid',
                  dest = 'grid',
                  type = 'int', nargs = 2, metavar = 'int int',
                  help='min a,b grid of square %default')

parser.set_defaults(
                    grid = (100,100),
                    origin = (0,0),
                 )
(options,filenames) = parser.parse_args()



# --- loop over input files -------------------------------------------------------------------------

files = []
if filenames == []:
  files.append({'name':'STDIN','input':sys.stdin,'output':sys.stdout,'croak':sys.stderr})
else:
  for name in filenames:
    if os.path.exists(name):
        outfile = os.path.splitext(name)[-2] + '_Ox' + str(options.origin[0])+ 'y'+str(options.origin[1]) + '.ctf'
        files.append({'name':name,'input':open(name),'output':open(outfile,'w'),'croak':sys.stdout})

#--- loop over input files ------------------------------------------------------------------------
for file in files:
  file['croak'].write('\033[1m' + scriptName + '\033[0m: ' + (file['name'] if file['name'] != 'STDIN' else '') + '\n')
  content = file['input'].readlines()

  for line in content:
      if 'xcells' in line.lower(): 
          XCells = int(line.split()[1])
          line = line.replace(str(XCells), str(options.grid[0]))
      if 'ycells' in line.lower(): 
          YCells = int(line.split()[1])
          line = line.replace(str(YCells), str(options.grid[1]))

      if 'xstep' in line.lower(): XStep  = float(line.split()[1])
      if 'ystep' in line.lower(): YStep  = float(line.split()[1])

      file['output'].write(line)
      if 'bands' in line.lower() and 'mad' in line.lower():
          offsetLineNum = content.index(line) + 1
          break

  if options.grid[0] + options.origin[0] > XCells: 
      print "%s + %s is out of range, XCells is %s!"%(options.grid[0], options.origin[0], XCells)
  if options.grid[1] + options.origin[1] > YCells: 
      print "%s + %s is out of range, YCells is %s!"%(options.grid[1], options.origin[1], YCells)

  for iy in xrange(options.grid[1]):
      istart = offsetLineNum + (options.origin[1] + iy) * XCells + options.origin[0]
      for ix in xrange(options.grid[0]):
          line = content[istart + ix]
          words = line.split()
          text = '\t'.join([i for i in [words[0], str(float(words[1])-XStep*options.origin[0]), 
              str(float(words[2])-YStep*options.origin[1])] + words[3:] ])
          file['output'].write(text+'\n')
          #file['output'].write(line.replace(linesplit[1], str(float(linesplit[1])-XStep*options.origin[0]) ). 
                                    #replace(linesplit[2], str(float(linesplit[2])-YStep*options.origin[1]) ) )
  file['input'].close()
  file['output'].close()
  file['croak'].close()
