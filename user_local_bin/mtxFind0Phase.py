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

(options,filenames) = parser.parse_args()

# --- loop over input files -------------------------------------------------------------------------

files = []
if filenames == []:
  files.append({'name':'STDIN','input':sys.stdin,'output':sys.stdout,'croak':sys.stderr})
else:
  for name in filenames:
    if os.path.exists(name):
        outfile = os.path.splitext(name)[-2] + '_2.mtx'
        files.append({'name':name,'input':open(name),'output':open(outfile,'w'),'croak':sys.stdout})

#--- loop over input files ------------------------------------------------------------------------
for file in files:
  file['croak'].write('\033[1m' + scriptName + '\033[0m: ' + (file['name'] if file['name'] != 'STDIN' else '') + '\n')
  content = file['input'].readlines()
  file['output'].write(content[0])

  for line in content[1:]:
 
      words = line.split()
      if words[0] == 'NaN':
          words[:3] = ['0.0','0.0','0.0']
          words[3] = '0'
      else:
          words[3] = '1'

      text = '\t'.join([i for i in words])
      file['output'].write(text+'\n')
 
  file['input'].close()
  file['output'].close()
  file['croak'].close()
