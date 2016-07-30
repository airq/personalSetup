#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-

import os,re,sys,numpy,string,optparse 
import damask


# --------------------------------------------------------------------
# rotate sample vector into lattice frame
def rotateToLattice(p1,P,p2,x):
  
  def s(alpha): return numpy.sin(alpha)
  def c(alpha): return numpy.cos(alpha)

  R = numpy.array([
                    [ c(p1)*c(p2)-c(P)*s(p1)*s(p2), -c(p1)*s(p2)-c(P)*c(p2)*s(p1),  s(P)*s(p1) ], 
                    [ c(p2)*s(p1)+c(P)*c(p1)*s(p2), -s(p1)*s(p2)+c(P)*c(p1)*c(p2), -s(P)*c(p1) ], 
                    [             s(P)      *s(p2),              s(P)      *c(p2),  c(P)       ],
                  ]).T
  
  return numpy.dot(R,x)


# -----------------------------
def getHeader(scale,std):
  cmds = '\\begin{tikzpicture}\n\\begin{scope}'
  if std:
    myscale = float(scale) / (numpy.sqrt(2.0) - 1.0)
    cmds += '[x=%fcm,y=%fcm]'%(myscale,myscale)
  else: 
    cmds += '[x=%fcm,y=%fcm]'%(0.5*float(scale),0.5*float(scale))
  return cmds


# -----------------------------
def getFooter():
  return '\n\\end{scope}\n\\end{tikzpicture}'



# -----------------------------
def lines(levels,std):

  # ---
  def rot2d(angle):
    x = numpy.radians(float(angle))
    return numpy.array([[numpy.cos(x), -numpy.sin(x)],
                        [numpy.sin(x),  numpy.cos(x)]])

  # ---
  def grosskreis(ratio,angle):
    cmds = ''
    alpha = numpy.arctan(ratio)
    rad = 1.0 / numpy.cos(alpha)
    startPoint = numpy.dot(rot2d(angle),numpy.array([0,-1]))
    startAngle = -(90.0 - numpy.degrees(alpha)) + angle
    endAngle = +(90.0 - numpy.degrees(alpha)) + angle
    R90 = rot2d(90)
    for i in range(4):
      startPoint = numpy.dot(R90,startPoint) 
      startAngle += 90.0
      endAngle += 90.0
      cmds += '\n\\draw[gray,line width=0.5pt] (%f,%f) arc(%f:%f:%f);'%(startPoint[0],startPoint[1],startAngle,endAngle,rad)
    return cmds

  # ---
  def basics():
    cmds = ''
    startPoint = numpy.array([-1,0])
    endPoint = numpy.array([1,0])
    R45 = rot2d(45)
    for i in range(8):
      startPoint = numpy.dot(R45,startPoint) 
      endPoint = numpy.dot(R45,endPoint) 
      cmds += '\n\\draw[gray,line width=0.5pt] (%f,%f) -- (%f,%f);'%(startPoint[0],startPoint[1],endPoint[0],endPoint[1])
    cmds += '\n\\draw[line width=1.0pt] (0,0) circle(1);'
    return cmds
  
  # ---
  cmds = ''
  if levels >= 0:
    if std: 
      x = numpy.sqrt(2.0) - 1.0
      cmds += '\n\\draw[line width=1.0pt] (0,0) -- (%f,0);'%x
      cmds += '\n\\draw[line width=1.0pt] (%f,0) arc(0:15:%f);'%(x,numpy.sqrt(2.0))
      x = (numpy.sqrt(3.0) - 1.0) / 2.0
      cmds += '\n\\draw[line width=1.0pt] (0,0) -- (%f,%f);'%(x,x)
    else:
      cmds += basics()
      if levels > 0:
        angle = 0.0
        cmds += grosskreis(1.0,angle)
        for level in range(2,levels+1):
          for ratio in [1.0 / float(level), float(level)]:
            cmds += grosskreis(ratio,angle)
      if levels > 1:
        angle = 45.0
        ratio = numpy.sqrt(2.0)
        cmds += grosskreis(ratio,angle)
      if levels > 2:
        angle = 45.0
        ratio = 1.0 / numpy.sqrt(2.0)
        cmds += grosskreis(ratio,angle)
        ratio = 0.5
        cmds += grosskreis(ratio,angle)
  return cmds



# --------------------------
def points(levels,inversion,std):
  
  # ---
  def getPointPos(p,std):
    return project(p['hkl'],False,std)

  # ---
  def getPointLabel(p,invert,std):
    h,k,l = map(lambda x: {True: -x, False: x}[invert],p['hkl'])
    if std:
      cmds = '{%s:\\small\\hkl<%d%d%d>}'%(p['label'],h,k,l)
    else:
      cmds = '{%s:\\scriptsize\\hkl[%d%d%d]}'%(p['label'],h,k,l)
    return cmds

  # ---
  if std:
    labels = '\n\\begin{scope}[inner sep=0pt]'
    mypoints = [
                [
                  {'hkl':[0,0,1], 'label':'below left',  'shape':'fill,rectangle,minimum height=6pt,minimum width=6pt'},
                  {'hkl':[0,1,1], 'label':'below right', 'shape':'fill,diamond,minimum height=12pt,minimum width=6pt'},
                  {'hkl':[1,1,1], 'label':'above right', 'shape':'fill,isosceles triangle,isosceles triangle apex angle=60,shape border rotate=105,minimum height=7pt'},
                  {'hkl':[1,1,2], 'label':'above left',  'shape':'fill,circle,minimum height=4pt'},
                ]
               ]
  else:
    labels = '\n\\begin{scope}[label distance=-2mm]'
    mypoints = [
                [
                  {'hkl':[0,0,1],   'label':'below',        'shape':''}, # shape could be 'draw,rectangle' or 'fill,circle'
                  {'hkl':[0,1,0],   'label':'right',        'shape':''},
                  {'hkl':[0,-1,0],  'label':'left',         'shape':''},
                  {'hkl':[1,0,0],   'label':'below',        'shape':''},
                  {'hkl':[-1,0,0],  'label':'above',        'shape':''},
                ],
                [
                  {'hkl':[ 0, 1,1], 'label':'right',        'shape':''},
                  {'hkl':[ 0,-1,1], 'label':'left',         'shape':''},
                  {'hkl':[ 1, 0,1], 'label':'below',        'shape':''},
                  {'hkl':[-1, 0,1], 'label':'above',        'shape':''},
                  {'hkl':[-1, 1,1], 'label':'right',        'shape':''},
                  {'hkl':[ 1, 1,1], 'label':'right',        'shape':''},
                  {'hkl':[-1,-1,1], 'label':'left',         'shape':''},
                  {'hkl':[ 1,-1,1], 'label':'left',         'shape':''},
                  {'hkl':[-1, 1,0], 'label':'above right',  'shape':''},
                  {'hkl':[ 1, 1,0], 'label':'below right',  'shape':''},
                  {'hkl':[-1,-1,0], 'label':'above left',   'shape':''},
                  {'hkl':[ 1,-1,0], 'label':'below left',   'shape':''},
                ]
               ]
  levels = min(levels+1,len(mypoints))
  if levels > 0:
    for level in range(levels):
      for p in mypoints[level]:
        x,y = getPointPos(p,std)
        labels += '\n\\node[%s,label=%s] at (%f,%f) {};'%(p['shape'],getPointLabel(p,inversion,std),x,y)
  labels += '\n\end{scope}'
  return labels



# --------------------------
def project(p,invert,std):
  x,y,z = map(float,p)
  norm = numpy.linalg.norm([x,y,z])
  xProj = y / (norm + abs(z))
  yProj = -x / (norm + abs(z))
  if std:
    a = abs(xProj)
    b = abs(yProj)
    xProj = max(a,b)
    yProj = min(a,b) 
  elif invert:
    xProj = -xProj
    yProj = -yProj
  return [xProj, yProj]


# --------------------------
def getSymbolsize(s,a,b):
  return 0.1 + max(0.0,min(1.0,((float(s)-float(a))/(float(b)-float(a))))) * 1.9


# --------------------------
def datapoints(dataset,line,symbol,symbolsize):
  if isinstance(symbolsize,list):
    cmds = '\n\\begin{scope}[every node/.style={fill,shape=%s}]'%(symbol)
  else: 
    cmds = '\n\\begin{scope}[every node/.style={fill,shape=%s,inner sep=%fpt}]'%(symbol,0.5*symbolsize)
  cmds += '\n\\path'
  if line: cmds += '[draw]'
  for i,p in enumerate(dataset[:-1]):
    if isinstance(symbolsize,list):
      cmds += '\n(%f,%f) node[inner sep=%fpt] {} -- '%(p[0],p[1],symbolsize[i])
    else:
      cmds += '\n(%f,%f) node {} -- '%(p[0],p[1])
  if isinstance(symbolsize,list):
    cmds += '\n(%f,%f) node[inner sep=%fpt] {};'%(dataset[-1][0],dataset[-1][1],symbolsize[-1])
  else:
    cmds += '\n(%f,%f) node {};'%(dataset[-1][0],dataset[-1][1])
  cmds += '\n\\end{scope}'
  return cmds


# -----------------------------
class extendableOption(optparse.Option):
# used for definition of new option parser action 'extend', which enables to take multiple option arguments
# taken from online tutorial http://docs.python.org/library/optparse.html
  
  ACTIONS = optparse.Option.ACTIONS + ("extend",)
  STORE_ACTIONS = optparse.Option.STORE_ACTIONS + ("extend",)
  TYPED_ACTIONS = optparse.Option.TYPED_ACTIONS + ("extend",)
  ALWAYS_TYPED_ACTIONS = optparse.Option.ALWAYS_TYPED_ACTIONS + ("extend",)

  def take_action(self, action, dest, opt, value, values, parser):
    if action == "extend":
      lvalue = value.split(",")
      values.ensure_value(dest, []).extend(lvalue)
    else:
      optparse.Option.take_action(self, action, dest, opt, value, values, parser)



###############################
# -----------------------------
# MAIN STARTS HERE

# --- input parsing

parser = optparse.OptionParser(option_class=extendableOption, 
                               usage='%prog [options] x y z filename [x2 y2 z2 filename2 ...]', description = """
Generate inverse polefigure for direct use in latex. 
""" + string.replace('$Id: $','\n','\\n')
)

parser.add_option('-s','--size', dest='size', type='float',
                  help='size of inverse polefigure [%default]')
parser.add_option('-d','--detail', dest='detail', type='int',
                  help='level of detail [%default]')
parser.add_option('-l','--label', nargs=3, dest='eulerlabel', type='string',
                  help='label of euler angles in ascii table [%default]')
parser.add_option('--symbolscaling', nargs=3, dest='symbolscaling', type='string',
                  help='scaling of points: label,minval,maxval [%default]')
parser.add_option('--symbol', action='extend', dest='symbol', type='string',
                  help="symbols used for printing ['circle']")
parser.add_option('--symbolsize', dest='symbolsize', type='float',
                  help="symbol size in points [%default]")
parser.add_option('--line', action='store_true', dest='line',
                  help='connect symbols by line [%default]')
parser.add_option('-i','--invert', action='store_true', dest='invert',
                  help='inverse pole figure with -100 pole in the center [%default]')
parser.add_option('--std', action='store_true', dest='standardtriangle',
                  help='project all points into the standard triangle [%default]')
parser.add_option('-o','--output', dest='outfilename', type='string',
                  help='output filename')

parser.set_defaults(size = 8.0)
parser.set_defaults(detail = 1)
parser.set_defaults(eulerlabel = ['1_eulerangles','2_eulerangles','3_eulerangles'])
parser.set_defaults(symbol = [])
parser.set_defaults(symbolsize = 2.0)
parser.set_defaults(symbolscaling = None)
parser.set_defaults(line = False)
parser.set_defaults(invert = False)
parser.set_defaults(standardtriangle = False)

(options, args) = parser.parse_args()


# --- sanity checks

if len(args)%4 > 0:
  parser.error('wrong number of iunput arguments')
else:
  Nfiles = len(args)/4

datafilenames = []
vectors = []
for i in range(Nfiles):
  try:
    vectors.append(map(float,args[4*i:4*i+3]))
  except:
    parser.error('could not understand input arguments')
  if os.path.isfile(args[4*i+3]):
    datafilenames.append(args[4*i+3])
  else: 
    parser.error('could not find filename %s'%args[4*i+3])

if len(options.symbol) < Nfiles:
  options.symbol += ['circle']*(Nfiles-len(options.symbol))
for symbol in options.symbol:
  if symbol not in ['circle','rectangle','ellipse']:
    parser.error('symbol "%s" not supported'%symbol)




# --- get header and footer of tex file

header = getHeader(options.size, options.standardtriangle)
footer = getFooter()


# --- get inverse pole figure planes and directions

lineCommands = lines(options.detail, options.standardtriangle)
pointCommands = points(options.detail,  options.invert, options.standardtriangle)


# --- read data from datafile
print 'read data'

datasets = []
symbolsizes = []
for i in range(Nfiles):
  datasets.append([])
  symbolsizes.append([])
  vector = vectors[i]
  with open(datafilenames[i],'r') as datafile:                                       # open datafile in read mode
    table = damask.ASCIItable(fileIn=datafile)                                       # use ASCIItable class to read data file
    table.head_read()                                                                # read ASCII header info
    datacolumns = []
    for label in options.eulerlabel:                                                 # check if euler angle label can be found
      if label not in table.labels:
        parser.error('column %s not found...\n'%label)
      datacolumns.append(table.labels.index(label))                                  # remember column of euler angle data of euler angle data
    if options.symbolscaling:
      if options.symbolscaling[0] not in table.labels:
        parser.error('column %s not found...\n'%options.symbolscaling[0])
      symbolsizeColumn = table.labels.index(options.symbolscaling[0])
    print 'reading data'
    while table.data_read():                                                         # read line in datafile
      eulerangles = numpy.array([float(table.data[col]) for col in datacolumns])     # get euler angles from current datarow
      p1,P,p2 = map(numpy.radians,eulerangles)                                       # convert to radians
      print 'rotating'
      rotatedVector = rotateToLattice(p1,P,p2,vector)                                # rotate vector into lattice frame
      datasets[-1].append(project(rotatedVector, options.invert, 
                                  options.standardtriangle))                         # project vector onto stereographic plane and append point to data structure
      if options.symbolscaling:
        symbolsizes[-1].append(getSymbolsize(float(table.data[symbolsizeColumn]),0.0,0.1))


# --- get data points on inverse pole figure

print 'get data points'
datapointCommands = ''
for i,dataset in enumerate(datasets):
  if options.symbolscaling:
    datapointCommands += datapoints(dataset, options.line, 
                                    options.symbol[i], symbolsizes[i])
  else:
    datapointCommands += datapoints(dataset, options.line, 
                                    options.symbol[i], options.symbolsize)


# --- write to standard out or file

print 'writing out'
if options.outfilename:
  with open(options.outfilename,'w') as outfile:
    outfile.write(header + lineCommands + pointCommands + datapointCommands + footer)
else:
  sys.stdout.write(header + lineCommands + pointCommands + datapointCommands + footer)

