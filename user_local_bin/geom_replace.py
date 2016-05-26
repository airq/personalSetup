#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
import os
from optparse import OptionParser

def allAreDigit(string):
    results = True
    for ele in string.split():
        if ele.isalpha(): results= False
    return results


#--------------------------------------------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser( usage='%prog options [file[s]]', description = """

generate a mix-grain geom file from xxx
""")

parser.add_option('-f','--filename',              dest='filename', type='string', metavar = 'string',
                  help='input file name')

(options,args) = parser.parse_args()
print options
filein = options.filename

if os.path.exists(filein):
    fileout = open(os.path.splitext(filein)[-2] + '_replace'+os.path.splitext(filein)[-1], 'w')
    for line in open(filein, 'r').readlines():

        if allAreDigit(line):
            fileout.write(line.replace('10','5'))
        else:
            fileout.write(line)

else:
    print 'we can not find the file, please confirm!!'
