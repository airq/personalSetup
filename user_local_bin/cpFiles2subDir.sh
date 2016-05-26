#!/bin/bash
#########################################################################
# File Name: cpFiles2subDir.sh
# Author: Haiming Zhang

for i in $(ls)
do
  echo $i
  if [ -d $i ]
  then
     cp postParaView.py $i
  fi
done

