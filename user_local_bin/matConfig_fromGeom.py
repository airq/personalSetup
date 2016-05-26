#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-

import os,sys,math
import numpy as np
from optparse import OptionParser

scriptName = os.path.splitext(os.path.basename(__file__))[0]

#--------------------------------------------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser('%prog options [file[s]]', description = """
fetch <microstructure> and <texture> from a .geom file to a standlone file which is needed in material.config,
the header of the .geom will also be modified.
""", version = scriptID)

parser.add_option('-a','--append',            dest='append', action='store_true',
                  help='the generated file will be appended to the material.config')
parser.add_option('-n','--newgeom',           dest='newgeom', action='store_true',
                  help='the generated file will be appended to the material.config')

parser.set_defaults(
                    compress       = True,
                 )
(options,filenames) = parser.parse_args()


# --- loop over input files -------------------------------------------------------------------------

if filenames == []: filenames = [None]

for filename in filenames:
    if os.path.exists(filename):
        geomopen =  open(filename, 'r')
        date = geomopen.readlines()
        beginWrite = False
        for i in xrange(int(date[0]+1)):
            if not beginWrite:
                if '<microstructure>' in date[i]:
                    beginWrite = True
                    outfile.write(date[i])
                    beginLine = i-1
                else:
                    continue
            else:
                outfile.write(date[i])
        if not beginWrite: print "%s does not contain microstructure information!"%filename
        geomopen.close()

        # delete the microstructure information of .geom file
        if options.newgeom:
            geomopen = open(os.path.splitext(filename)[-2]+'_new.geom', 'r')
        else:
            geomopen = open(filename, 'r')
        header = int(data[0][1])
        date[0].replace(data[0][1], str(beginLine))
        for i in xrange(beginLine):
            geomopen.write(line(i))
        for i in xrange(len(date)):
            if i > header: geomopen.write(date[i])
    else:
        print "i can not file the file %s in current directory"%filename
        continue
