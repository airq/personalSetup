#!/bin/bash

if [ 'X$1' = 'Xr' ]
then
  ln -s /home/haiming/.setup/DAMASK/Makefile_debug_out /home/haiming/DAMASK/DAMASK/Makefile
  ln -s /home/haiming/.setup/DAMASK/DAMASK_spectral_debug.f90 /home/haiming/DAMASK/DAMASK/code/DAMASK_spectral.f90
  make OPTIMIZATION=OFF DEBUG=ON OPEMMP=OFF
  make install
else
  ln -s /home/haiming/.setup/DAMASK/Makefile_release_out /home/haiming/DAMASK/DAMASK/Makefile
  ln -s /home/haiming/DAMASK/DAMASK/code/release/DAMASK_spectral.f90 /home/haiming/DAMASK/DAMASK/code/DAMASK_spectral.f90
  make 
  make install
fi
