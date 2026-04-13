# ============================================================
# Generic Vitis AIE Tcl runner for AIE code debugging
#
# Example usage:
# vitis -s run_aie.tcl -- \
#   "work_dir=runs/Debug001/aie_work" \
#   "graph_src=Test_Cases/Debug001/llm_graph.cpp" \
#   "platform=Xilinx_vek280_base_202410_1" \
#   "target=x86sim" \
#   "include_dirs=Test_Cases/Debug001"
#
# This script is for AIE graph/kernel compilation and optional sim.
# No host PNG/image utilities are included.
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
if {![info exists work_dir]}     { error "Missing argument: work_dir" }
if {![info exists graph_src]}    { error "Missing argument: graph_src" }

# ----------------------------
# Optional defaults
# ----------------------------
if {![info exists platform]}     { set platform "Xilinx_vek280_base_202410_1" }
if {![info exists target]}       { set target "x86sim" }
if {![info exists include_dirs]} { set include_dirs "." }
if {![info exists run_sim]}      { set run_sim 0 }

file mkdir $work_dir

# ----------------------------
# Generate aiecompiler.cfg
# ----------------------------
set cfg_path [file join $work_dir "aiecompiler.cfg"]
set cfg_fd [open $cfg_path "w"]

# include_dirs may be a comma-separated list
foreach dir [split $include_dirs ","] {
    if {$dir ne ""} {
        puts $cfg_fd "include=$dir"
    }
}

close $cfg_fd

puts "Generated config: $cfg_path"

# ----------------------------
# Compile AIE graph
# ----------------------------
set compile_cmd [list v++ -c --mode aie \
    --config $cfg_path \
    --target $target \
    --platform $platform \
    --work_dir $work_dir \
    $graph_src]

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
        puts "Running x86simulator..."
        if {[catch {exec sh -c "cd $work_dir && x86simulator"} sim_result]} {
            puts "x86sim failed:"
            puts $sim_result
            exit 2
        } else {
            puts "x86sim completed successfully."
            puts $sim_result
        }
    } elseif {$target eq "aiesim"} {
        puts "Running aiesimulator..."
        if {[catch {exec sh -c "cd $work_dir && aiesimulator"} sim_result]} {
            puts "aiesim failed:"
            puts $sim_result
            exit 3
        } else {
            puts "aiesim completed successfully."
            puts $sim_result
        }
    }
}

puts "AIE debug flow finished."
exit 0