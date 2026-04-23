The bug in the provided C++ source file is a missing output token write to create a producer/consumer imbalance and potential stream deadlock. The corrected line is:

```cpp
writeincr_v8(matC, acc0);
```

Here is the full corrected source file:

```cpp
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
	v32int8 chess_