#!/bin/bash
#########################################################################
# File Name: debugCPFEMinIDB.sh
# Author: ZHANG Haiming
# mail: hm.zhang@sjtu.edu.cn
# Created Time: 2016年04月10日 星期日 22时41分52秒
#########################################################################

if [ ! $1 ]; then
  echo "please input the job name!!!"
  exit 1
fi

if [ -e "abaqus_v6.env" ]; then
  rm -f abaqus_v6.env
fi

ln -s /home/haiming/.setup/backup/debugUmatInIDB/abaqus_v6_pathOfLibs ./abaqus_v6.env

abaqus -j $1 int
