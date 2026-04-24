#include <adf.h>
#include <stdio.h>
#include "para_L3.h"
#include "parameter_L3_B0_A0_C3.h"

void mm3_kernel0_L3_B0_A0_C3(input_window_int8* __restrict matA, 
		output_stream_acc48* __restrict matC){
    
    v32int8 *restrict matB = (v32int8 *)matB_LUT0;

	v64int8 chess_storage(xa) buf_matA0=undef_v64int8(); //
	v64int8 chess_storage(xb) buf_matA1=undef_v64int8(); //
			
	v32int8 chess_storage(wc0) buf_matB0=undef_v32int8(); // 
	v32int8 chess_storage(wc1) buf_matB1=undef_v32int8(); // 

    for (int seq=0;seq<L3_bound_seq;seq++)
	    chess_prepare_for_pipelining
	    chess_loop_range(L3_bound_seq,)
    {// SEQ/4
        
        for (int oc=0;oc<L3_bound_oc;oc++)
	    chess_prepare_for_pipelining
	    chess_loop_range(L3_bound_oc,)
        { //OC/4
            v8acc48 acc0=null_v8acc48();
            v8acc48 acc1=null_v8acc48();

            buf_mat