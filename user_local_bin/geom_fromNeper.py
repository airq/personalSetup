#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-

import os,sys,math,string
import numpy as np
import multiprocessing
from optparse import OptionParser
from subprocess import call
sys.path.append("F:\\ABAQUS_JOB_files")
reload(sys)
sys.setdefaultencoding('utf8')

scriptID   = string.replace('$Id: geom_fromVoronoiTessellation.py 4549 2015-10-12 18:10:26Z SJTU\hm.zhang $','\n','\\n')
scriptName = os.path.splitext(scriptID.split()[1])[0]



# --------------------------------------------------------------------
#                                MAIN
# --------------------------------------------------------------------

parser = OptionParser(usage='%prog options [file[s]]', description = """
Generate geometry description and material configuration by standard Voronoi tessellation of given seeds file.

""", version = scriptID)
parser.add_option('-s', '--size', dest = 'size', type = 'float', nargs = 3, metavar=' '.join(['float']*3),
                  help = '''x,y,z size of hexahedral box, x,y size of square (the 3rd is zero); 
                          diameter and height of a cylinder (the 3rd is zero), diameter of a circle (the 2nd and 3rd are zero)''')
parser.add_option('--minsize', dest = 'minsize', type = 'float', metavar= 'float',
                  help = 'minimum element size')
parser.add_option('-n', '--number', dest = 'ngrains', type = 'int', metavar = 'int',
                  help = 'number of grains [%default]')
parser.add_option('-m', '--morpho', dest = 'morpho', type = 'string', metavar = 'string',
                  help = '''Type of morphology of the cells. For random tessellations, it can be either equiaxed (‘equiaxed’), 
                            columnar (‘columnar(dir)’, where dir is the columnar direction and can be (‘x’, ‘y’ or ‘z’) or 
                            bamboo-like (‘bamboo(dir)’, where dir is the bamboo direction and can be (‘x’, ‘y’ or ‘z’). 
                            To get a lamella morphology, provide ‘lamella’. Regular morphologies also are available: 
                            squares (‘square’) in 2D, and cubes (‘cube’) and truncated octahedra (‘tocta’) in 3D. [%default]''')
parser.add_option('-o','--output', dest='output', type='string', metavar='string',
                  help='name of the output file [%default]')
parser.add_option('-c', '--circle', dest='circle', action='store_true',
                  help ='the shape of geometrical models: False (cuboid, rectangular) or True (cylindrical or circle) [%default]')   
parser.add_option('-t', '--three', dest = 'threeD', action='store_true',
                  help = 'dimension: True (3d), Flase (2d) [%default]')
parser.add_option('--tet', dest = 'tetrahedral', action='store_true',
                  help = 'element type: True (tetrahedral), False (hexahedral) [%default]')
parser.add_option('-p',  '--periodic', dest='periodic', action='store_true',
                  help='Specify the type of tessellation, standard (False) or periodic (True) [%default]')

parser.set_defaults(
                    size        = None,
                    ngrains     = 20,
                    morpho      = 'equiaxed',
                    output      = 'myPloyTesslation',
                    threeD      = False, 
                    circle      = False,
                    periodic    = False,
                    tetrahedral = False,
                  )
(options,args) = parser.parse_args()

ttype   = 'periodic' if options.periodic    else 'standard'
dim     = '3'        if options.threeD      else '2'
elttype = 'tet'      if options.tetrahedral else 'hex'
ngrains = str(options.ngrains)
morpho  = options.morpho
minsize = str(options.minsize)
outfilename = options.output
geomfile,meshfile = outfilename+'.tess',outfilename+'.msh'

if options.threeD:
  if options.circle: domain  = "'cylinder(%s,%s)'"%(options.size[0],options.size[1]) #cylinder(height,diameter)
  else:              domain  = "'cube(%s,%s,%s)'"%(options.size[0],options.size[1],options.size[2]) #cube(size_x,size_y,size_z)
else:
  if options.circle: domain  = "'circle(%s)'"%(options.size[0]/2.0) #circle(radius)
  else:              domain  = "'square(%s,%s)'"%(options.size[0],options.size[1]) #square(size_x,size_y)

generateTess = 'neper -T -n '+ngrains+' -id 1 -dim '+dim+' -domain '+domain+' -morpho '+morpho+ \
               ' -regularization 1 -mloop 5 -ttype '+ttype+' -o '+geomfile
generateMesh = 'neper -M '+geomfile+' -elttype '+elttype+' -cl '+minsize+' -o '+meshfile


print 'generating tesselation'
print generateTess
sts = call(generateTess, shell=True)
print 'meshing'
print generateMesh
sts = call(generateMesh, shell=True)
