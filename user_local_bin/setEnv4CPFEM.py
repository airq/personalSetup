#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
# Makes postprocessing routines acessible from everywhere.
import os,sys
from optparse import OptionParser


#--------------------------------------------------------------------------------------------------
#                                MAIN
#--------------------------------------------------------------------------------------------------
parser = OptionParser(description = """This script is used to set the enviroment for the debugging or
        running of CPFEM for Abaqus.
""")

parser.add_option('-r', '--release',
                  dest = 'DEBUG',
                  action = 'store_false',
                  help = 'debug')
parser.set_defaults(DEBUG = True)
options = parser.parse_args()[0]

CPFEM_code_PATH=os.path.join(os.getenv('HOME'), 'CPFEM/reduce')
CPFEM_debug_PATH=os.path.join(CPFEM_code_PATH, 'debug')
CPFEM_run_PATH=os.path.join(CPFEM_code_PATH, 'run')

os.chdir(CPFEM_code_PATH)

if options.DEBUG:
    srcDir = CPFEM_debug_PATH
else:
    os.system("rm -rf Make*")
    srcDir = CPFEM_run_PATH

os.system("rm -rf *.o *.mod")
for srcFile in os.listdir(srcDir): 
    file = os.path.join(CPFEM_code_PATH, srcFile)
    print file
    if os.path.exists(file):
        os.remove(file)
    os.symlink(os.path.join(srcDir, srcFile), file)

if options.DEBUG:
    os.system("make 'DEBUG=ON'")
else:
    os.system("abaqus make -lib DAMASK_abaqus_std.f -dir ${CPFEM_LIB_PATH}")
    os.system("abaqus make -lib DAMASK_abaqus_exp.f -dir ${CPFEM_LIB_PATH}")
