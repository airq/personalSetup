#!/bin/bash
#########################################################################
# File Name: abaqusComplie.sh
# Author: Haiming Zhang
#########################################################################

myPath="${HOME}/local/lib/abqlib"
myStd=DAMASK_abaqus_std.f
myExp=DAMASK_abaqus_exp.f
myDAMASKpath=${HOME}/DAMASK/DAMASK

if [ ! -d "$myPath" ]
then
 mkdir "$myPath"
fi

cd $myPath
rm -f *

cd "$myDAMASKpath"/code

if [ -e "abaqus_v6.env" ]
then
 echo "'abaqus_v6.env' exists"
else
 echo "'abaqus_v6.env' does not exist, new symbolic is created"
 ln -s ${HOME}/.setup/DAMASK_abaqus_v6_for_compilation.env ./abaqus_v6.env
 exit 1
fi

abaqus make -library "$myStd" -dir "$myPath"
abaqus make -library "$myExp" -dir "$myPath"

ls -al $myPath

