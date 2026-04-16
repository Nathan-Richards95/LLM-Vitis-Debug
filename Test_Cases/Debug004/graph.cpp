
extern void add_one(input_buffer<int> &, output_buffer<int> &);

class my_graph : public graph
{
public:
    kernel k;

    input_plio in;
    output_plio out;

    my_graph()
    {
        k = kernel::create(add_one);

        in = input_plio::create("input", plio_32_bits, "data/input.txt");
        out = output_plio::create("output", plio_32_bits, "data/output.txt");

        connect<>(in.out[0], k.in[0]);
        connect<>(k.out[0], out.in[0]);

        runtime<ratio>(k) = 1.0;
    }
};