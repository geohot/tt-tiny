#!/bin/bash
clang -std=c++20 -I. \
  -I/home/billy/build/tt-metal/tt_metal/api \
  -I/home/billy/build/tt-metal/tt_metal/hostdevcommon/api \
  -I/home/billy/build/tt-metal/build_Release/include \
  -L/home/billy/build/tt-metal/build/lib -ltt_metal \
  main.cc -lstdc++
export TT_METAL_HOME="/home/billy/build/tt-metal"
export LD_LIBRARY_PATH="/home/billy/build/tt-metal/build/lib"
./a.out
