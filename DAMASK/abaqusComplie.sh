#!/bin/bash
#########################################################################
# File Name: abaqusComplie.sh
# Author: Haiming Zhang
#########################################################################

myPath="/usr/local/abqlib"
myStd=DAMASK_abaqus_std.f
myExp=DAMASK_abaqus_exp.f
myDAMASKpath=/public/DAMASK

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
 echo "I did not find abaqus_v6.env in the directory $myDAMASKpath/code, exit"
 exit 1
fi

abaqus make -library "$myStd" -dir "$myPath"
abaqus make -library "$myExp" -dir "$myPath"

ls -al $myPath

