#!/bin/bash
source /data/courses/class_cse494598cen571spring2026_aaror112/Vitis_2024_1/Vitis/2024.1/settings64.sh
export AIE_PLATFORM=/data/courses/class_cse494598cen571spring2026_aaror112/Vitis_2024_1/Vitis/2024.1/base_platforms/xilinx_vck190_base_202410_1/xilinx_vck190_base_202410_1.xpfm
export VITIS_ROOT=/data/courses/class_cse494598cen571spring2026_aaror112/Vitis_2024_1/Vitis/2024.1
export PYTHONPATH=$VITIS_ROOT/cli:$VITIS_ROOT/cli/proto:$PYTHONPATH
export XILINX_VITIS=/data/courses/class_cse494598cen571spring2026_aaror112/Vitis_2024_1/Vitis/2024.1
python $@