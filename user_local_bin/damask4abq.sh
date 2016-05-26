#!/bin/bash
#########################################################################
# File Name: abaqusComplie.sh
# Author: Haiming Zhang
#########################################################################

#myPath="${HOME}/local/lib/cpfem_debug"
myDAMASKpath=${HOME}/DAMASK/DAMASK/code

if [ "x$1" = "xr" ]
then
  myPath=${HOME}/local/lib/abqlib
  myStd=DAMASK_abaqus_std.f
  myDir=${myDAMASKpath}/release
  echo 'damask for release'
else
  myPath=${HOME}/local/lib/damask4abq_debug
  myStd=DAMASK_abaqus_std_debug.f
  echo 'damask for abaqus debug'
  myDir=${myDAMASKpath}/debug
fi

myExp=DAMASK_abaqus_exp.f

if [ ! -d "$myPath" ]
then
 mkdir "$myPath"
fi

cd $myPath
rm -f *.o *.so 

cd "$myDir"
for file in *
do
  if [ -e "$file" ]
  then
    rm -f $myDAMASKpath/$file
  fi
  echo "$file"
  ln -s $myDir/$file $myDAMASKpath/$file
done

cd $myDAMASKpath
abaqus make -library "$myStd" -dir "$myPath"
#abaqus make -library "$myExp" -dir "$myPath"

#ls -al $myPath

