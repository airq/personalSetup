#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
'''
 Author: Haiming Zhang
 Mail: hm.zhang@sjtu.edu.cn
 Created Time: 2016年05月28日 星期六 15时47分28秒
'''

import os,sys,math
import numpy as np
from optparse import OptionParser

scriptName = os.path.splitext(os.path.basename(__file__))[0]


#-------------------------------------re-------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser(usage='%prog options [file[s]]', description = """

Generate geometry description and material configuration from EBSD data in given square-gridded 'ang' file.
Two phases can be discriminated based on threshold value in a given data column.

""")

parser.add_option('-b','--nbins',      dest='nbins', type='int', metavar = 'int',
                  help='bins for partition the euler angles [%default]')
parser.add_option('-g','--ngrains',      dest='ngrains', type='int', metavar = 'int',
                  help='number of grains [%default]')
parser.add_option('-d', dest='dreamOut', action='store_false',
                  help = '[%default]' )
parser.set_defaults(
                    nbins = 20,
                    ngrains = 20,
                    dreamOut = True
                 )
(options,args) = parser.parse_args()


# --- loop over input files -------------------------------------------------------------------------
matconfig = open('randomTextureN_' + str(options.ngrains) +  '.matconfig','w')
if options.dreamOut: 
    dreamTexture = open('dreamTextureN_' + str(options.ngrains) +  '.txt','w')
    dreamTexture.write( '# Euler0 Euler1 Euler2 Weight Sigma\n' )
    dreamTexture.write( 'Angle Count:%i\n'%options.ngrains)

nbin = options.nbins
nbin3 = nbin*nbin*nbin

eulerangles = []
det_phi = 360.0/nbin; det_Phi = 180.0/nbin
for iphi1 in xrange(nbin):
    phi1 = ( iphi1  + np.random.rand() )*det_phi
    for iPhi in xrange(nbin):
        Phi = ( iPhi  + np.random.rand() )*det_Phi
        for iphi2 in xrange(nbin):
            phi2 = ( iphi2  + np.random.rand() )*det_phi
            eulerangles.append(np.array([phi1, Phi, phi2]))
np.random.shuffle(eulerangles)

validRandomNumber = []
while len( set(validRandomNumber) ) != options.ngrains:
    for i in np.random.rand(options.ngrains):
        ig = int(i*nbin3)
        if ig  not in validRandomNumber:
            validRandomNumber.append( ig )
            if len(set(validRandomNumber)) == options.ngrains: break

print 'write material.config file'
matconfig.write('#----------------#\n')
matconfig.write('<microstructure>\n')
matconfig.write('#----------------#\n')
for i in  xrange(options.ngrains):
    matconfig.write('[Grain%s]\n'%str(i+1))
    matconfig.write('crystallite 1\n')
    matconfig.write('(constituent)  phase %s texture %s fraction 1.0\n'%(1, str(i+1)) )

matconfig.write('\n')
matconfig.write('#----------------#\n')
matconfig.write('<texture>\n')
matconfig.write('#----------------#\n')
for i in  xrange(options.ngrains):
    eulerangle = eulerangles[i]
    matconfig.write('[Texture%s]\n'%str(i+1))
    matconfig.write('(gauss)  phi1 %7.3f Phi %7.3f phi2 %7.3f scatter 0.0 fraction 1.0\n'\
       %(eulerangle[0], eulerangle[1], eulerangle[2]) )

    if options.dreamOut:
        dreamTexture.write( '%7.5f %7.5f %7.5f 1 1\n'%( eulerangle[0]*np.pi/180.0, eulerangle[1]*np.pi/180.0,
            eulerangle[2]*np.pi/180.0 ) )

matconfig.close()
if options.dreamOut:
    dreamTexture.close()
