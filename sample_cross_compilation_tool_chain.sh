#!/bin/sh

echo "||=========================================||"
echo "||Sample Cross Compilation tool chain shell v0.1 ||"
echo "||=========================================||"
export LC_CTYPE=C.UTF-8

EXTERN_LIB_CMAKE=extern_lib.cmake

HOST=aarch64-linux-gnu
VENDOR_TOP_DIR=/home/jwwang/tc1c_cross_compile/gcc-linaro-7.3.1-2018.05-i686_aarch64-linux-gnu/
TOOL_CHAIN_TOP_DIR=${VENDOR_TOP_DIR}


TOOL_CHAIN_PATH=${TOOL_CHAIN_TOP_DIR}/bin
C_COMPILER_PATH=${TOOL_CHAIN_PATH}/${HOST}-gcc
CXX_COMPILER_PATH=${TOOL_CHAIN_PATH}/${HOST}-gcc
FIND_ROOT_PATH=${VENDOR_TOP_DIR} ${TOOL_CHAIN_TOP_DIR}

PREFIX_PATH=.
#CFLAGS="-I${VENDOR_TOP_DIR}/include"
#LDFLAGS="-L${VENDOR_TOP_DIR}/lib"

export PATH=$PATH:$TOOL_CHAIN_PATH
echo $TOP_DIR



echo "generate ${EXTERN_LIB_CMAKE}..."
echo "set(CMAKE_SYSTEM_NAME Linux)" > $EXTERN_LIB_CMAKE
echo "set(TOOLCHAIN_PATH ${TOOL_CHAIN_PATH})" >> $EXTERN_LIB_CMAKE
echo "set(CMAKE_C_COMPILER ${C_COMPILER_PATH})" >> $EXTERN_LIB_CMAKE
echo "set(CMAKE_CXX_COMPILER ${CXX_COMPILER_PATH})" >> $EXTERN_LIB_CMAKE
#echo "set(CMAKE_FIND_ROOT_PATH ${FIND_ROOT_PATH})" >> $EXTERN_LIB_CMAKE

echo "list(APPEND CMAKE_PREFIX_PATH ${PREFIX_PATH})" >> $EXTERN_LIB_CMAKE

rm -rf "build_${HOST}"
mkdir "build_${HOST}"
cd "build_${HOST}"
cmake ..
make


