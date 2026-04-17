# /*
# Copyright (C) 2023, Advanced Micro Devices, Inc. All rights reserved.
# SPDX-License-Identifier: X11
# */


############################### Make file input options ############################## 
# Default GAMA scaling parameters (can be overridden by user)
Y ?= 1
G ?= 4
X ?= 1

# Makefile input options
TARGET := sw_emu
DEVICE_DEBUG := OFF
BUFF_OPT := 0
STACK ?= 1024

############################### Design source files ############################## 
AIE_SRC := no_aie
PL_SRC := no_pl
HOST_SRC := no_host
# Configuration files #revisit
CONFIG := conn.cfg
CONFIG_FILE := ./connectivity_config/$(CONFIG)
EMCONFIG_FILE := emconfig.json

############################### Platform and sysroot information ######################
PLATFORM_NAME := xilinx_vek280_base_202410_1
BASE_PLATFORM ?= ${PLATFORM_REPO_PATHS}/$(PLATFORM_NAME)/$(PLATFORM_NAME).xpfm
# Sysroot and rootfs (set via environment)
SDKTARGETSYSROOT ?= ${SYSROOT}
# ROOTFS ?= ${PLATFORM_REPO_PATHS}/sw/versal/xilinx-versal-common-v2024.1/rootfs.ext4
# IMAGE ?= ${PLATFORM_REPO_PATHS}/sw/versal/xilinx-versal-common-v2024.1/Image


############################### Directory structure creation ######################
# Directory structure (directory structure focused on AIE directory)
DESIGN_NAME := $(AIE_SRC)_P_$(PL_SRC)_H_$(HOST_SRC)_BufOpt$(BUFF_OPT)_Y$(Y)_G$(G)_X$(X)
BUILD_DIR_MAIN := build/$(DESIGN_NAME)_$(TARGET)
EXEC_DIR := output/$(DESIGN_NAME)_$(TARGET)

ifeq ($(DEVICE_DEBUG),ON)
	EXEC_DIR := output/$(DESIGN_NAME)_$(TARGET)_debug
endif

TEMP_DIR := ./$(BUILD_DIR_MAIN)/pl_kernel.$(TARGET).$(PLATFORM_NAME) # revisit
AIE_WORK_DIR := $(BUILD_DIR_MAIN)/Work_AIE
AIE_SIM_DIR := sim/$(DESIGN_NAME)_$(TARGET)

PACKAGE_OUT := ./package.$(TARGET)


############################### Source files ######################

# Source files
GRAPH_FILE := $(AIE_SRC)/aie_top_all.cpp
PL_FILE := ./pl/$(PL_SRC)/dma0.cpp ./pl/$(PL_SRC)/dma0.hpp #revisit
# Single-file compatibility variable (kept for backward compatibility)
HOST_FILE := ./host/$(HOST_SRC)/host.cpp
# Detect all host C++ sources so SW emulation host build can compile multiple files
HOST_FILES := $(wildcard ./host/$(HOST_SRC)/*.cpp)

# Output files
GRAPH_EXE := libadf.a
PFM := gama_Y$(Y)_G$(G)_X$(X)
HOST_EXE := host.exe
XCLBIN := gama_$(TARGET).xclbin

#revisit
ifeq ($(TARGET),sw_emu)
	KERNEL_XO := $(EXEC_DIR)/dma0.xo
else
	KERNEL_XO := $(EXEC_DIR)/dma0.xo
endif


############################## Setting up Compilers and simulators ##############################

# Compiler executables
VPP := v++
AIECC := v++ -c --mode aie
AIESIM := aiesimulator
X86SIM := x86simulator

############################## AIE Compiler Flags ##############################
AIE_INCLUDES := --include "$(XILINX_VITIS)/aietools/include" \
				--include "./$(AIE_SRC)" \
				--include "./data" \
				--include "./$(AIE_SRC)/kernels" \
				--include "./"

AIE_FLAGS := $(AIE_INCLUDES) \
			 --platform $(BASE_PLATFORM) \
			 --aie.xlopt=1 \
			 --aie.stacksize=$(STACK) \
			 --aie.pl-register-threshold=350 \
			 --aie.pl-freq=300 \
			 --work_dir ./$(AIE_WORK_DIR) \
			 --output=$(EXEC_DIR)/$(GRAPH_EXE)

ifeq ($(BUFF_OPT),8)
	AIE_FLAGS += --aie.Xmapper=BufferOptLevel8
else
	AIE_FLAGS += --aie.Xmapper=BufferOptLevel$(BUFF_OPT)
endif

ifeq ($(TARGET),sw_emu)
	AIE_FLAGS += --target x86sim
else
	AIE_FLAGS += --target hw
endif

AIE_FLAGS += --aie.Xpreproc -Dmult_Y=$(Y) \
			 --aie.Xpreproc -Dmult_G=$(G) \
			 --aie.Xpreproc -Dmult_X=$(X)

############################## HLS Kernel Compiler Flags ############################## #revisit
ifeq ($(TARGET),sw_emu)
	VPP_XO_FLAGS := -c \
					--platform $(BASE_PLATFORM) \
					-t $(TARGET) \
					--save-temps \
					-g \
					-I ./pl/$(PL_SRC)
else
	VPP_XO_FLAGS := -c \
					--mode hls \
					--platform $(BASE_PLATFORM)
endif

############################## Linker XSA Flags ##############################
VPP_XSA_LINK_FLAGS := -l \
				  -t $(TARGET) \
				  --platform $(BASE_PLATFORM) \
				  --save-temps \
				  -g \
				  --temp_dir $(BUILD_DIR_MAIN)/xsa_link_temp \
				  -o $(EXEC_DIR)/$(PFM).xsa \
				  $(EXEC_DIR)/$(GRAPH_EXE) \
				  --verbose

ifeq ($(DEVICE_DEBUG),ON)
	VPP_XSA_LINK_FLAGS += --profile.data all:all:all
endif

############################## Host Compiler Flags ##############################
GCC_FLAGS := -Wall \
			 -c \
			 -std=c++17 \
			 -g

ifeq ($(TARGET),sw_emu)
	GCC_INCLUDES := -I${XILINX_XRT}/include
	GCC_LIB := -lxrt_coreutil 
	GCC_LIB += -L${XILINX_XRT}/lib
else
	GCC_INCLUDES := -I$(SDKTARGETSYSROOT)/usr/include/xrt \
					-I./$(AIE_SRC) \
					-I./$(AIE_SRC)/kernels \
					-I${XILINX_VITIS}/aietools/include
	GCC_LIB := -lxrt_coreutil
endif

############################## Emulation Commands ##############################
SW_EMU_CMD := ./$(HOST_EXE) $(XCLBIN) 
HW_EMU_CMD := ./launch_hw_emu.sh 

############################## Guard Checks ############################## #revisit
check_defined = \
	$(strip $(foreach 1,$1, \
		$(call __check_defined,$1,$(strip $(value 2)))))

__check_defined = \
	$(if $(value $1),, \
		$(error Undefined $1$(if $2, ($2))))

guard-PLATFORM_REPO_PATHS:
	$(call check_defined, PLATFORM_REPO_PATHS, Set to where you downloaded $(PLATFORM_NAME))

guard-ROOTFS:
	$(call check_defined, ROOTFS, Set to: xilinx-versal-common-v2024.1/rootfs.ext4)

guard-IMAGE:
	$(call check_defined, IMAGE, Set to: xilinx-versal-common-v2024.1/Image)

guard-CXX:
	$(call check_defined, CXX, Run: xilinx-versal-common-v2024.1/environment-setup-aarch64-xilinx-linux)

guard-SDKTARGETSYSROOT:
	$(call check_defined, SDKTARGETSYSROOT, Run: xilinx-versal-common-v2024.1/environment-setup-aarch64-xilinx-linux)

############################## Setting Rules of Compilation ##############################
.ONESHELL:
.PHONY: all clean cleanall aie aiesim pl_kernels xsa host package run run_emu sd_card

all: aie xsa host package
sd_card: all

############################## AIE Compilation ##############################
aie: $(EXEC_DIR)/$(GRAPH_EXE)

$(EXEC_DIR)/$(GRAPH_EXE): $(GRAPH_FILE)
	@echo "INFO: Compiling AIE graph..."
	@mkdir -p $(EXEC_DIR)
	$(AIECC) $(AIE_FLAGS) $(GRAPH_FILE)
	@echo "COMPLETE: AIE graph compiled."

############################## AIE Simulation ##############################
aiesim: $(EXEC_DIR)/$(GRAPH_EXE)
	@echo "INFO: Running AIE simulation..."
ifeq ($(TARGET),sw_emu)
	export X86SIM_OPTIONSPATH=./$(AIE_WORK_DIR)/options/x86sim.options && \
	$(X86SIM) --pkg-dir=./$(AIE_WORK_DIR) \
			  --output-dir=$(AIE_SIM_DIR) \
			  --input-dir=aie/$(AIE_SRC)/data 
else
	$(AIESIM) --profile \
			  --dump-vcd=$(AIE_SIM_DIR)/trace \
			  --pkg-dir=./$(AIE_WORK_DIR) \
			  --output-dir=$(AIE_SIM_DIR) \
			  --input-dir=$(AIE_SRC)/data
endif
	@echo "COMPLETE: AIE simulation finished."

############################## PL Kernel Compilation ############################## #revisit
pl_kernels: guard-PLATFORM_REPO_PATHS
	@echo "INFO: Compiling PL kernels..."
ifeq ($(TARGET),sw_emu)
	$(VPP) $(VPP_XO_FLAGS) \
		   -k dma0 \
		   pl/$(PL_SRC)/dma0.cpp \
		   -D__SW_EMU__ \
		   -o $(KERNEL_XO) \
		   --temp_dir $(TEMP_DIR)/hls_kernel_temp/
else
	@sed -i '9c\package.output.file=../../$(EXEC_DIR)/dma0.xo' pl/$(PL_SRC)/dma0.cfg
	$(VPP) $(VPP_XO_FLAGS) \
		   --config pl/$(PL_SRC)/dma0.cfg \
		   --work_dir $(BUILD_DIR_MAIN)/pl_kernel
endif
	@echo "COMPLETE: PL kernels compiled."

############################## XSA Generation ##############################
xsa: guard-PLATFORM_REPO_PATHS $(EXEC_DIR)/$(GRAPH_EXE)
	@echo "INFO: Generating XSA..."
	$(VPP) $(VPP_XSA_LINK_FLAGS) || (echo "ERROR: XSA generation failed with code $$?"; exit 1)
	@echo "COMPLETE: XSA created."

############################## Host Compilation ##############################
ifeq ($(TARGET),sw_emu)
host: guard-CXX guard-SDKTARGETSYSROOT
	@echo "INFO: Compiling host application for SW emulation..."
	@mkdir -p $(EXEC_DIR)
	# Compile each host .cpp into its own object file in $(EXEC_DIR)
	for src in $(HOST_FILES); do \
		obj=$(EXEC_DIR)/$$(basename $$src .cpp).o; \
		echo "Compiling $$src -> $$obj"; \
		g++ -g -Wall -c -std=c++17 \
			-D__PS_ENABLE_AIE__ \
			-D__SW_EMU__ \
			-Wno-int-to-pointer-cast \
			-I${XILINX_XRT}/include \
			-I./ \
			-I./aie/$(AIE_SRC)/kernels \
			-I./aie/$(AIE_SRC) \
			-I$(SDKTARGETSYSROOT)/usr/include/xrt \
			-I${XILINX_VITIS}/aietools/include \
			-I./$(AIE_SRC) \
			-I./$(AIE_SRC)/kernels \
			-o $$obj $$src; \
	done
	g++ -g $(EXEC_DIR)/*.o \
		-lxrt_coreutil \
		-std=c++17 \
		-L${XILINX_XRT}/lib \
		-o ./$(EXEC_DIR)/$(HOST_EXE)
	@echo "COMPLETE: Host application created."
else
host: guard-CXX guard-SDKTARGETSYSROOT
	@echo "INFO: Compiling host application..."
	@mkdir -p $(EXEC_DIR)
	for src in $(HOST_FILES); do \
		obj=$(EXEC_DIR)/$$(basename $$src .cpp).o; \
		echo "Compiling $$src -> $$obj"; \
		$(CXX) $(GCC_FLAGS) $(GCC_INCLUDES) \
			   -D__AIE_ARCH__=20 \
			   -o $$obj $$src; \
	done
# 	$(CXX) $(GCC_FLAGS) $(GCC_INCLUDES) \
# 		   -D__AIE_ARCH__=20 \
# 		   -o $(EXEC_DIR)/host.o $(HOST_FILE)
	$(CXX) $(EXEC_DIR)/*.o \
		   $(GCC_LIB) \
		   -std=c++17 \
		   -o $(EXEC_DIR)/$(HOST_EXE)
	@echo "COMPLETE: Host application created."
endif

############################## Package Generation ##############################
ifeq ($(TARGET),sw_emu)
package: guard-PLATFORM_REPO_PATHS guard-IMAGE guard-ROOTFS
	@echo "INFO: Creating SW emulation package..."
	emconfigutil --platform $(BASE_PLATFORM) \
				 --nd 1 \
				 --od $(EXEC_DIR)
	v++ -p -t $(TARGET) \
		--platform $(BASE_PLATFORM) \
		--package.out_dir $(EXEC_DIR)/$(PACKAGE_OUT) \
		--package.defer_aie_run \
		-o $(EXEC_DIR)/$(XCLBIN) \
		--temp_dir $(BUILD_DIR_MAIN)/package_temp \
		./$(EXEC_DIR)/$(PFM).xsa \
		./$(EXEC_DIR)/$(GRAPH_EXE)
	@echo "COMPLETE: SW emulation package created."
else
package: guard-PLATFORM_REPO_PATHS guard-IMAGE guard-ROOTFS
	@echo "INFO: Creating emulation/hardware package..."
	v++ -p -t $(TARGET) \
		-f $(BASE_PLATFORM) \
		--package.rootfs=$(ROOTFS) \
		--package.image_format=ext4 \
		--package.boot_mode=sd \
		--package.kernel_image=$(IMAGE) \
		--package.out_dir $(EXEC_DIR) \
		--output $(EXEC_DIR)/$(XCLBIN) \
		--temp_dir $(BUILD_DIR_MAIN)/package_temp \
		--package.sd_file $(EXEC_DIR)/host.exe \
		$(EXEC_DIR)/$(PFM).xsa \
		$(EXEC_DIR)/libadf.a
	@echo "COMPLETE: Emulation/hardware package created."
endif

############################## Run Application ##############################
run: all run_emu

run_emu:
	@echo "INFO: Running emulation..."
ifeq ($(TARGET),sw_emu)
	sed -i 's/dump=no/dump=yes/g' ./$(AIE_WORK_DIR)/options/x86sim.options
	cd ./$(EXEC_DIR) && \
	export XCL_EMULATION_MODE=$(TARGET) && \
	export X86SIM_OPTIONSPATH=../../$(AIE_WORK_DIR)/options/x86sim.options && \	
	$(SW_EMU_CMD)
else ifeq ($(TARGET),hw_emu)
	cd ./$(EXEC_DIR) && \
	$(HW_EMU_CMD)
else
	@echo "INFO: Hardware build, no emulation executed."
endif

############################## Cleaning Rules ##############################
clean:
	@echo "INFO: Cleaning TARGET specific files..."
	rm -rf $(BUILD_DIR_MAIN) $(EXEC_DIR)
	@echo "COMPLETE: Clean finished."

cleanall: clean
	@echo "INFO: Cleaning all files including simulation outputs..."
	rm -rf _x v++* *.o *.compile_summary* *.xpe xnwOut *.log *.xsa Work *.db *.csv *.jou .Xil
	rm -rf x86simulator_output/ aiesimulator_output/ sim/
	@echo "COMPLETE: Cleanall finished."

cleanresidue: 
	@echo "INFO: Cleaning residue files..."
	rm -rf _x v++* *.o *.compile_summary* *.xpe *.log *.xsa *.db *.csv *.jou .Xil
	@echo "COMPLETE: Clean residue finished."

############################## Help Section ##############################
.PHONY: help
help::
	@echo "Makefile Usage:"
	@echo ""
	@echo "  make all TARGET=<sw_emu/hw_emu/hw> PLATFORM=<FPGA platform>"
	@echo "	  Command to generate the design for specified Target and Shell."
	@echo ""
	@echo "  make clean"
	@echo "	  Command to remove the generated non-hardware files."
	@echo ""
	@echo "  make cleanall"
	@echo "	  Command to remove all the generated files."
	@echo ""
	@echo "  make run TARGET=<sw_emu/hw_emu/hw>"
	@echo "	  Command to run application in emulation or hardware."
	@echo ""
	@echo "  make aie"
	@echo "	  Command to compile AIE graph."
	@echo ""
	@echo "  make aiesim"
	@echo "	  Command to run AIE simulation."
	@echo ""

############################## Setting up Project Variables ##############################


############################## Usage Examples ##############################
# Sample compilation commands with required flags:
# make -f Makefile_exp AIE_SRC=aie/aie_constr_buf_array_scaling/aie_MKN_64x96x64_MMUL_8x8x4_bf16_bf16_memtile HOST_SRC=YGX_444 TARGET=hw Y=4 G=4 X=4 BUFF_OPT=0 package &> compile.log
#
# SW emulation AI engine option file:
# export X86SIM_OPTIONSPATH ./build/aie_maxeva_pl_maxeva_host_maxeva_sw_emu/Work_AIE_aie_maxeva_sw_emu/options/x86sim.options
# export XCL_EMULATION_MODE=sw_emu