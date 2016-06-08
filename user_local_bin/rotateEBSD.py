#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-

import os,sys,math
import numpy as np
from optparse import OptionParser


scriptName = os.path.splitext(os.path.basename(__file__))[0]


def period2Pi(phi):
    if phi<0:
        return 360. + phi
    elif phi>360.:
        return phi - 360.
    else:
        return phi

def rotate(y,string, p):
    '''
    get a specific operation according to the string
    string = 'x-', return x-y, string = '-x', return y-x; string='x', return x+y
    p - means period
    '''
    if string[-1].isdigit() and string[0].isdigit():
        return period2Pi(y+float(string)) if p else y+float(string)
    elif string[-1] == '-':
        return period2Pi(float(string[:-1]) - y) if p else float(string[-1]) - y
    elif string[0]  == '-':
        return period2Pi(y - float(string[1:])) if p else y - float(string[1:])

#--------------------------------------------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """

Generate geometry description and material configuration from EBSD data in given square-gridded 'ang' file.
Two phases can be discriminated based on threshold value in a given data column.

""")

parser.add_option("-c",'--coords', metavar = '<string LIST>', dest="coords",
                  help='transform the coordinates [%default]')
parser.add_option('-e','--euler', metavar ='<string LIST>', dest = 'euler',
                  help='transform the euler angles [%default]')
parser.add_option('-n','--name', type = 'string', metavar ='string', dest = 'name',
                  help='the name postfix of new files [%default]')

parser.set_defaults(
                    coords = ('0.0', '0.0'),
                    euler  = ('0.0', '0.0', '0.0'),
                    name   = 'rot'
                 )
(options,filenames) = parser.parse_args()



# --- loop over input files -------------------------------------------------------------------------

files = []
if filenames == []:
    files.append({'name':'STDIN','input':sys.stdin,'output':sys.stdout,'croak':sys.stderr})
else:
    for name in filenames:
        if os.path.exists(name):
            filesplit = os.path.split(name)
            outfile = filesplit[-2] +options.name +'rot' + filesplit[-1]
            files.append({'name':name,'input':open(name),'output':open(outfile,'w'),'croak':sys.stdout, 'format':filesplit[-1]} )


#--- loop over input files -----------------------------------------------------------------------
pi = 3.1415926535898
for file in files:
    file['croak'].write('\033[1m' + scriptName + '\033[0m: ' + (file['name'] if file['name'] != 'STDIN' else '') + '\n')
    content = file['input'].readlines()

    if file['format'] == '.ctf':
        file['output'].write(line)
        for line in content:
            if 'bands' in line.lower() and 'mad' in line.lower():
                offsetLineNum = content.index(line)
                break

        for i in xrange(offsetLineNum, len(content)):
            words = content[i].split()
            text = '\t'.join([i for i in [words[0], 
              str( rotate( float(words[1]), options.coords[0], False) ),
              str( rotate( float(words[2]), options.coords[1], False) ),
              word[3], word[4],
              str( rotate( float(words[5]), options.euler[0], True) ),
              str( rotate( float(words[6]), options.euler[1], True) ),
              str( rotate( float(words[7]), options.euler[2], True) )]
              + words[8:] ])
            file['output'].write(text+'\n')

    elif file['format'] == '.ang'
        file['output'].write(line)
        for line in content:
            if line[0] != '#':
                offsetLineNum = content.index(line)
                break

        for i in xrange(offsetLineNum, len(content)):
            words = content[i].split()
            text = '\t'.join([i for i in [
              str( rotate( float(words[0])/pi*180.0, options.euler[0], True) ),
              str( rotate( float(words[1])/pi*180.0, options.euler[1], True) ),
              str( rotate( float(words[2])/pi*180.0, options.euler[2], True) ),
              str( rotate( float(words[3]), options.coords[0], False) ),
              str( rotate( float(words[4]), options.euler[1], False) ),
              + words[5:] ])
            file['output'].write(text+'\n')

    file['input'].close()
    file['output'].close()
    file['croak'].close()
