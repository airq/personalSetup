sudo apt-get install libblas3gf libblas-doc libblas-dev liblapack3gf liblapack-doc liblapack-dev -y
sudo apt-get install libhdf5-mpich-dev openmpi*
sudo apt-get install libfftw3-3 libfftw3-dev libfftw3-mpi3 libfftw3-mpi-dev 
use root account
./configure --prefix=/usr/local --with-blas-lapack-dir=$MKLROOT/lib/intel64 --download-fftw --download-hdf5 --with-fc=mpif90 --with-cc=mpicc --with-cxx=mpicxx --with-c2html=0 --with-x=0 --with-ssl=0 --with-debugging=0 FFLAGS="${FFLAGS} -stand f08 -standard-semantics" COPTFLAGS="-O3 -xHost -no-prec-div" CXXOPTFLAGS="-O3 -xHost -no-prec-div" FOPTFLAGS="-O3 -xHost -no-prec-div" PETSC_ARCH=ifort PETSC_DIR=`pwd`
sudo apt-get install cython python-f2py flvstreamer
