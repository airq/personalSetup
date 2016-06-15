#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-
import os
'''
 File Name: generateCycli.py
 Author: Haiming Zhang
 Mail: hm.zhang@sjtu.edu.cn
 Created Time: 2016年04月27日 星期三 10时17分26秒
'''

tension0 = "fdot 4.0e-4 0 0  0 * 0   0 0 *  stress  * * *   * 0 *   * * 0  time 10  incs 20 freq 40 \n"
compress= "fdot -4.0e-4 0 0  0 * 0   0 0 *  stress  * * *   * 0 *   * * 0  time 20  incs 40 freq 50 \n"
tension= "fdot 4.0e-4 0 0  0 * 0   0 0 *  stress  * * *   * 0 *   * * 0  time 20  incs 40 freq 50 \n"

Ocompress= "fdot -4.0e-4 0 0  0 * 0   0 0 *  stress  * * *   * 0 *   * * 0  time 20  incs 40 freq 4 \n"
Otension= "fdot 4.0e-4 0 0  0 * 0   0 0 *  stress  * * *   * 0 *   * * 0  time 20  incs 40 freq 4 \n"


loadfile = open('cycle20160531.load', 'w')
loadfile.write(tension0)
for i in xrange(5):
    for j in xrange(200):
        loadfile.write(compress)
        loadfile.write(tension)
    loadfile.write(Ocompress)
    loadfile.write(Otension)

