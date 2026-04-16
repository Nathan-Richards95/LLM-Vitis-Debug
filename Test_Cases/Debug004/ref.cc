#include <aie_api/aie.hpp>
#include <adf.h>

void add_one(adf::input_buffer<int> &in,
             adf::output_buffer<int> &out)
{
    auto in_ptr = in.data();
    auto out_ptr = out.data();

    for (int i = 0; i < 256; i++)
    {
        out_ptr[i] = in_ptr[i] + 1;
    }
}