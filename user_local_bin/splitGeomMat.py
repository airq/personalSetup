#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
'''
 Author: Haiming Zhang
 Mail: hm.zhang@sjtu.edu.cn
 Created Time: 2016年05月28日 星期六 15时47分28秒
'''

from optparse import OptionParser
import os,sys,math,string
import numpy as np


def allIsDigit(line):
    return all(i.isdigit() for i in line.split())


# --------------------------------------------------------------------
#                                MAIN
# --------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """
Transform linear binned data into Euler angles. ***This script does not support the case that one CRYSTALLITE contains
more than one (constituent).***

""")

parser.add_option('-n', '--new', dest='newGeomFile', action='store_true',
                  help = "write the geom model into a new geom file [%default]")   
parser.add_option('--homo', dest='homoWrite', action='store_false',
                  help = "write '<homogenization>' into to the material.config file [%default]")   
parser.add_option('-e', '--ebsd', dest='ebsd', action='store_true',
                  help = "write 'ebsd_ngrains' into to homogenization [%default]")   

parser.set_defaults( newGeomFile = False,
                     homoWrite   = True,
                     ebsd        = False
                 )

(options,filenames) = parser.parse_args()

if filenames == []:
    print 'missing the input file, please specify a geom file!'
else:
    matConfigComment = '#-----------------------\n'
    for filename in filenames:
        if os.path.exists(filename):
            fopen = open(filename, 'r')
            content = fopen.readlines()
            fopen.close()

            geomcontent = [];  matcontent = []

            recordMat = False
            newHeader = 0
            for i,line in enumerate(content):
                if line:
                    if line.split()[0] == '<microstructure>':
                        recordMat = True
                        newHeader = i
                    elif allIsDigit(line) or 'to' in line:
                        recordMat = False
                    elif line.split()[0] == 'microstructures':
                        nOrientation = line.split()[1]

                    if recordMat:
                        matcontent.append(line)
                    else:
                        if i > 0: geomcontent.append(line)

            geomOpen = open(os.path.splitext(filename)[0]+'_rmMat.geom', 'w') if options.newGeomFile else open(filename, 'w')
            matOpen  = open(os.path.splitext(filename)[0]+'_mat.config', 'w') 

            geomOpen.write(str(newHeader-1)+'  header\n')
            for line in geomcontent: geomOpen.write(line)

            if options.homoWrite:
                for text in [ matConfigComment, '<homogenization>\n', matConfigComment, '[oneGrain]\n', 'type isostrain\n', \
                        'Ngrains  1\n', '(output)  ipcoords \n']:
                    matOpen.write(text)
                if options.ebsd:
                    matOpen.write('ebsd_ngrains  '+str(nOrientation)+' \n')

                matOpen.write('\n')
                matOpen.write(matConfigComment)
                for line in matcontent: matOpen.write(line)

            geomOpen.close(); matOpen.close()

        else:
            print 'the geom file %s is not found'%options.geomfile
