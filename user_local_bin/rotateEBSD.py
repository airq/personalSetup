#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-

import os,sys,math
import numpy as np
from optparse import OptionParser
from myLibs import readCtfFile, readAngFile, ebsdInfo


scriptName = os.path.splitext(os.path.basename(__file__))[0]

coordsPos = {
        'ctf': [1, 2],
        'ang': [3, 4]    }
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


def exchangeCoords(content, format, offset, exchangTag):
    '''
    for ang file, xcells is xcells_odd, xcells_even must also be provided, xcells_odd = xcells_even or xcells_even+1
    '''
    contentx = []; contenty = []
    offset = offset+1
    for i in xrange(offset):
        contentx.append(content[i])
        contenty.append(content[i])

    for line in reversed(content):
        if line.strip() == '':
            break
        else:
            lastLine = line.split()
            break
    xMax, yMax = float(lastLine[coordsPos[format[-3:]][0]]), float(lastLine[coordsPos[format[-3:]][1]])

    if format[-3:] == 'ang':
        for line in content[:offset]:
            if 'xstep' in line.lower(): xstep = float(line.split()[-1])
            if 'ystep' in line.lower(): ystep = float(line.split()[-1])
            if 'ncols_odd' in line.lower(): xcells = int(line.split()[-1])
            if 'ncols_even' in line.lower(): xcells_even = int(line.split()[-1])
            if 'nrows' in line.lower(): ycells = int(line.split()[-1])

        if 'y' in exchangTag:
            for jrow in reversed(xrange(ycells)):
                xstart = jrow/2 * (xcells+xcells_even) + offset; x_range = xcells
                if np.mod(jrow,2) == 1:
                    xstart = xstart + xcells; x_range = xcells_even

                for icol in xrange(x_range):
                    line = content[xstart+icol].split()
                    contenty.append('\t'.join(
                        line[:coordsPos['ang'][1]] + [str ( yMax-float(line[coordsPos['ang'][1]]) ) ] + line[coordsPos['ang'][1]+1:]
                        ))
            content = contenty
        if 'x' in exchangTag:
            for jrow in xrange(ycells):
                xstart = jrow/2 * (xcells+xcells_even) + offset; x_range = xcells
                if np.mod(jrow, 2) == 1:
                    xstart = xstart + xcells; x_range = xcells_even
                for icol in reversed(xrange(x_range)):
                    line = content[xstart+icol].split()
                    contentx.append('\t'.join(
                        line[:coordsPos['ang'][0]] + [str ( xMax-float(line[coordsPos['ang'][0]]) ) ] + line[coordsPos['ang'][0]+1:]
                        ))
            content = contentx

    elif format[-3:] == 'ctf':
        for line in content[:offset]:
            if 'xstep' in line.lower(): xstep = float(line.split()[-1])
            if 'ystep' in line.lower(): ystep = float(line.split()[-1])
            if 'xcells' in line.lower(): xcells = int(line.split()[-1])
            if 'ycells' in line.lower(): ycells = int(line.split()[-1])
        if 'y' in exchangTag:
            for jrow in reversed(xrange(ycells)):
                xstart = jrow*xcells+offset;  x_range = xcells
                for icol in xrange(x_range):
                    line = content[xstart+icol].split()
                    contenty.append('\t'.join(
                        line[:coordsPos['ctf'][1]] + [str ( yMax-float(line[coordsPos['ctf'][1]]) ) ] + line[coordsPos['ctf'][1]+1:]
                        ))
            content = contenty
        if 'x' in exchangTag:
            for jrow in xrange(ycells):
                xstart = jrow*xcells+offset;  x_range = xcells
                for icol in reversed(xrange(x_range)):
                    line = content[xstart+icol].split()
                    contentx.append('\t'.join(
                        line[:coordsPos['ctf'][0]] + [str ( xMax-float(line[coordsPos['ctf'][0]]) ) ] + line[coordsPos['ctf'][0]+1:]
                        ))
            content = contentx

    else:
        print 'unknown file format.'
    return content


#--------------------------------------------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """

Generate geometry description and material configuration from EBSD data in given square-gridded 'ang' file.
Two phases can be discriminated based on threshold value in a given data column.

""")

parser.add_option("-c",'--coords', type = 'string', metavar = 'string', dest="coords",
                  help='transform the coordinates,  [%default] ["x", "y","xy"]')
parser.add_option('-e','--euler', type='string', metavar ='string,string,string', nargs=3, dest = 'euler',
                  help='transform the euler angles [%default]')
parser.add_option('-n','--name', type = 'string', metavar ='string', dest = 'name',
                  help='the name postfix of new files [%default]')

parser.set_defaults(
                    coords = ' ',
                    euler  = ('0.0','0.0','0.0'),
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
            filesplit = os.path.splitext(name)
            outfile = filesplit[0] +'_'+options.name + filesplit[-1]
            files.append({'name':name,'input':open(name, 'r'),'output':open(outfile,'w'),'croak':sys.stdout, 'format':filesplit[-1]} )


#--- loop over input files -----------------------------------------------------------------------
pi = 3.1415926535898
for file in files:
    file['croak'].write('\033[1m' + scriptName + '\033[0m: ' + (file['name'] if file['name'] != 'STDIN' else '') + '\n')
    content = file['input'].readlines()
    #file['input'].seek(0) # wind back to the first line

    if file['format'] == '.ctf':
        for line in content:
            file['output'].write(line)
            if 'bands' in line.lower() and 'mad' in line.lower():
                offsetLineNum = content.index(line)
                break

        content = exchangeCoords(content, 'ctf', offsetLineNum, options.coords)
        for i in xrange(offsetLineNum+1, len(content)):
            words = content[i].split()
            text = '\t'.join([i for i in words[:5] +
             [str( rotate( float(words[5]), options.euler[0], True) ),
              str( rotate( float(words[6]), options.euler[1], True) ),
              str( rotate( float(words[7]), options.euler[2], True) )]
              + words[8:] ])
            file['output'].write(text+'\n')

    elif file['format'] == '.ang':
        for line in content:
            if line[0] != '#':
                offsetLineNum = content.index(line) - 1
                break
            file['output'].write(line)

        content = exchangeCoords(content, 'ang', offsetLineNum, options.coords)
        for i in xrange(offsetLineNum+1, len(content)):
            words = content[i].split()
            text = '\t'.join([i for i in [
              str( rotate( float(words[0])/pi*180.0, options.euler[0], True)*pi/180.0 ),
              str( rotate( float(words[1])/pi*180.0, options.euler[1], True)*pi/180.0 ),
              str( rotate( float(words[2])/pi*180.0, options.euler[2], True)*pi/180.0 ) ]
              + words[3:] ])
            file['output'].write(text+'\n')
    else:
        print 'unknown input file type'

    file['input'].close()
    file['output'].close()
    file['croak'].close()
