#!/bin/bash
#########################################################################
# File Name: abaqusComplie.sh
# Author: Haiming Zhang
#########################################################################

#myPath="${HOME}/local/lib/cpfem_debug"
myPath=${HOME}/CPFEM/reduce
myStd=DAMASK_abaqus_std_debug.f
myExp=DAMASK_abaqus_exp.f
myDAMASKpath=${HOME}/CPFEM/reduce

if [ ! -d "$myPath" ]
then
 mkdir "$myPath"
fi

cd $myPath
rm -f *.o *.so 

cd "$myDAMASKpath"

rm -f *.mod *.o
for file in abaqus_v6.env $myStd commercialFEM_fileList.f90
do
  if [ -e "$file" ]
  then
    rm -f $file
  fi
done

ln -s ${HOME}/.setup/backup/debugUmatInIDB/abaqus_v6_forDebuggingInIDB ./abaqus_v6.env
for file in $myStd commercialFEM_fileList.f90
do
  ln -s ${HOME}/.setup/backup/debugUmatInIDB/$file $file
done

abaqus make -library "$myStd" -dir "$myPath"
#abaqus make -library "$myExp" -dir "$myPath"

#ls -al $myPath

