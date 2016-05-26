#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-

import os,sys,string
from optparse import OptionParser
from subprocess import call
import damask

parser = OptionParser(usage='%prog options [file[s]]', description = """
post results automatically.

""", version='first version'
)

#parser.add_option('-g', '--geom_name', dest='geom_name',  type='string',
#                                       help='geom name',  metavar='string')

(options, files) = parser.parse_args()

outFileSuffix = '.spectralOut'
if files == []:
  parser.print_help()
  parser.error('no file specified...')

geom_name = files[0][:-12] if outFileSuffix in files[0] else files[0]

if not os.path.exists(geom_name+outFileSuffix):
  parser.print_help()
  parser.error('invalid file "%s" specified...'%files[0])

print 'post Results'

#postResults = 'postResults --cr f,p --split --separation x,y,z --increments --range  '+options.geom_name+'.spectralOut'
postResults = 'postResults --cr f,p --split --separation x,y,z --range 1 51 5 --dir postParaView '+geom_name+outFileSuffix
sts = call(postResults, shell=True)
os.chdir('./postParaView')

#showTable = "showTable -a "
postProc = []; postProcInfo = []
postProcInfo.append('add the Cauchy stress tensor ... ')
postProc.append('addCauchy ')
postProcInfo.append('add the logarithmic strain tensor ... ')
postProc.append("addStrainTensors -0 -v ")
postProcInfo.append('add the Mises stress and strain ... ')
postProc.append("addMises -s Cauchy -e 'ln(V)' ")
postProcInfo.append('perform 3D visulization ... ')
#postProc.append("3Dvisualize -s 'Mises(ln(V))','Mises(Cauchy)','1_ln(V)',1_Cauchy ")
postProc.append("3Dvisualize -s 'Mises(ln(V))','Mises(Cauchy)','[1-9]_ln(V)',1_Cauchy ")

print '**********************************************************'
print ''
for f in os.listdir(os.getcwd()):
    print ('post file %s'%f)
    for p in postProc:
        print p+f
        sts = call(p+f,shell=True)
    print '**********************************************************'
    print ''
