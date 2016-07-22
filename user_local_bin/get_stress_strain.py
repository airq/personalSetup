#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-

import os
from subprocess import call
from optparse import OptionParser
import damask

parser = OptionParser(option_class=damask.extendableOption, usage='', description = """
""")

parser.add_option('-d', '--direct', dest='direct',  type='string',
                  help='The directory where the post results are stored',  metavar='string')
parser.set_defaults( direct = 'stress_strain',
        )
(options,filename) = parser.parse_args()

for geom_name in filename:
    postResults = 'postResults --cr f,p --dir '+options.direct+' '+geom_name+'.spectralOut'

    sts = call(postResults, shell=True)
    #
    os.chdir('./%s/'%options.direct)
    addCauchy = 'addCauchy '
    addStrainTensors = "addStrainTensors -0 -v "
    addMises = "addMises -s Cauchy -e 'ln(V)' "
    #
    #
    postProc = [addCauchy, addStrainTensors, addMises]
    #
    #
    file = geom_name+'.txt'
    for p in postProc:
        p = p+file
        print p
        sts = call(p,shell=True)

