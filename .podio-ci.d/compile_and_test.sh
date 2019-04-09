#!/bin/bash

source /podio/.podio-ci.d/init_x86_64.sh

cd /podio
source init.sh
mkdir build install
cd build
cmake -DCMAKE_INSTALL_PREFIX=../install .. && \
make -j4 && \
make test && \
make install
