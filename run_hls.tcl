# ============================================================
# Generic Vitis HLS Tcl runner
#
# Example usage:
# vitis_hls -f run_hls.tcl \
#   "proj_dir=runs/Debug001/hls_proj" \
#   "src=Test_Cases/Debug001/llm_out.cpp" \
#   "tb=Test_Cases/Debug001/debug_tb.cpp" \
#   "top=vec_add" \
#   "part=xc7z020clg400-1" \
#   "clock=10.0"
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
if {![info exists proj_dir]} { error "Missing argument: proj_dir" }
if {![info exists src]}      { error "Missing argument: src" }
if {![info exists tb]}       { error "Missing argument: tb" }
if {![info exists top]}      { error "Missing argument: top" }

# ----------------------------
# Optional defaults
# ----------------------------
if {![info exists part]}  { set part "xc7z020clg400-1" }
if {![info exists clock]} { set clock "10.0" }
if {![info exists sol]}   { set sol "solution1" }

# ----------------------------
# Create/reset project
# ----------------------------
open_project -reset $proj_dir
set_top $top

# Add source under test
add_files $src

# Add testbench
add_files -tb $tb

# ----------------------------
# Solution setup
# ----------------------------
open_solution -reset $sol
set_part $part
create_clock -period $clock -name default

# ----------------------------
# Run C simulation
# ----------------------------
csim_design

# ----------------------------
# Run synthesis
# ----------------------------
csynth_design

# ----------------------------
# Optional RTL co-simulation
# Uncomment later if you want it
# ----------------------------
# cosim_design

exit