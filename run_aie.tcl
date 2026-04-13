# ============================================================
# Generic Vitis AIE Tcl runner for Lab 4 style projects
#
# Example usage:
# vitis -s run_aie.tcl -- \
#   "work_dir=runs/Debug001/aie_work" \
#   "src_dir=Test_Cases/Debug001" \
#   "top_file=aie_top_all.cpp" \
#   "platform=Xilinx_vek280_base_202410_1" \
#   "target=x86sim" \
#   "run_sim=1"
#
# This script is intended for AIE projects, not HLS.
# It compiles an AI Engine component using Vitis/AIE flow and
# optionally runs x86sim or aiesim.
# ============================================================

# ----------------------------
# Parse command-line arguments
# ----------------------------
foreach arg $argv {
    set kv [split $arg "="]
    set key [lindex $kv 0]
    set value [join [lrange $kv 1 end] "="]
    set $key $value
}

# ----------------------------
# Required arguments
# ----------------------------
if {![info exists work_dir]}  { error "Missing argument: work_dir" }
if {![info exists src_dir]}   { error "Missing argument: src_dir" }
if {![info exists top_file]}  { error "Missing argument: top_file" }

# ----------------------------
# Optional defaults
# ----------------------------
if {![info exists platform]}  { set platform "Xilinx_vek280_base_202410_1" }
if {![info exists target]}    { set target "x86sim" }
if {![info exists run_sim]}   { set run_sim 1 }

# Build paths
set top_path [file join $src_dir $top_file]
set cfg_path [file join $work_dir "aiecompiler.cfg"]

# ----------------------------
# Prepare work directory
# ----------------------------
file mkdir $work_dir

# ----------------------------
# Generate aiecompiler.cfg
# Lab 4 explicitly expects these include dirs:
#   src/kernels
#   src/png_utils
# ----------------------------
set cfg_fd [open $cfg_path "w"]
puts $cfg_fd "include=src/kernels"
puts $cfg_fd "include=src/png_utils"
close $cfg_fd

puts "Generated AIE compiler config at: $cfg_path"

# ----------------------------
# Compile AIE design
# ----------------------------
# The lab uses aie_top_all.cpp as the top file.
# target = x86sim or hw
# For functional correctness, start with x86sim.
set compile_cmd [list v++ -c --mode aie \
    --config $cfg_path \
    --target $target \
    --platform $platform \
    --work_dir $work_dir \
    $top_path]

puts "Running AIE compile command:"
puts $compile_cmd

if {[catch {exec {*}$compile_cmd} result]} {
    puts "AIE compile failed:"
    puts $result
    exit 1
} else {
    puts "AIE compile completed successfully."
    puts $result
}

# ----------------------------
# Optional simulation
# ----------------------------
if {$run_sim} {
    if {$target eq "x86sim"} {
        puts "Running x86 simulation..."
        if {[catch {exec sh -c "cd $work_dir && x86simulator"} sim_result]} {
            puts "x86sim failed:"
            puts $sim_result
            exit 2
        } else {
            puts "x86sim completed successfully."
            puts $sim_result
        }
    } elseif {$target eq "aiesim"} {
        puts "Running AI Engine simulation..."
        if {[catch {exec sh -c "cd $work_dir && aiesimulator"} sim_result]} {
            puts "aiesim failed:"
            puts $sim_result
            exit 3
        } else {
            puts "aiesim completed successfully."
            puts $sim_result
        }
    } else {
        puts "Simulation skipped: unsupported simulation target '$target'"
    }
}

puts "AIE Tcl flow finished."
exit 0