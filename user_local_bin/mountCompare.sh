#!/bin/bash
#########################################################################
# File Name: mountCompare.sh
# Author: ZHANG Haiming
# mail: hm.zhang@sjtu.edu.cn
# Created Time: 2016年04月11日 星期一 21时25分44秒
#########################################################################

mount -o loop /dev/sda5 /mnt/one
mount -o loop /dev/sdb1 /mnt/two
bcompare
