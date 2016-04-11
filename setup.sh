#!/bin/bash
#########################################################################
# File Name: setup.sh
# Author: ZHANG Haiming
# mail: hm.zhang@sjtu.edu.cn
# Created Time: 2016年04月10日 星期日 22时16分03秒
#########################################################################

#-----------creat link----------
for file in debugCPFEMinIDB.sh rmAbaqusFiles.sh
do
  ln -s ${HOME}/.setup/usr_local/bin/$file /usr/local/bin/$file
done

#-----------creat dirs----------
local_dir=${HOME}/local
for dir in ${local_dir}/lib ${local_dir}/bin
do
  if [ -d "$dir" ]
  then
    echo "$dir exists"
  elif
    mkdir -p $dir
  fi
done
