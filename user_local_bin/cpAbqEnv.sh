#!/bin/bash
#########################################################################
# File Name: /home/haiming/.setup/user_local_bin/cpAbqEnv.sh
# Author: ZHANG Haiming
# mail: hm.zhang@sjtu.edu.cn
# Created Time: 2016年04月08日 星期五 22时39分30秒
#########################################################################

if [ "$1" != "cpfem-std" -a "$1" != "cpfem-exp" ]; then
  echo "CPFEM for ABAQUS Standard used? you can use keywords 'cpfem-std' or 'cpfem-exp' to specify the solver!"
  solver="cpfem-std"
else
  solver=$1
fi

for file in abaqus_v6.env numerics.config
do
  if [ -e "$file" ]; then
    rm $file
  fi
done

cp ${HOME}/.setup/abaqus/abaqus_v6_for_cpfem.env ${PWD}/abaqus_v6.env

if [ "$solver" == "cpfem-std" ]
then
  cp ${HOME}/.setup/DAMASK/numerics_for_std ${PWD}/numerics.config
else
  cp ${HOME}/.setup/DAMASK/numerics_for_exp ${PWD}/numerics.config
fi
