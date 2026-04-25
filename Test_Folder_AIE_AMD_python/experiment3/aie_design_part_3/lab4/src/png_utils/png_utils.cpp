#include "png_utils/lodepng.h"
#include "png_utils/lodepng.cpp"

static bool load_decode_and_print_png(const char *filename,
                                      std::vector<unsigned char> &image, unsigned &width,
                                      unsigned &height) {
    lodepng::State state;

    // Request GREY8 output buffer (single channel)
    state.info_raw.colortype = LCT_GREY;
    state.info_raw.bitdepth = 8;

    // Load raw PNG file bytes, then decode with State to get metadata
    std::vector<unsigned char> png_data;
    unsigned error = lodepng::load_file(png_data, filename);
    if (error) {
        std::cerr << "file load error " << error << ": " << lodepng_error_text(error)
                  << "\n";
        return false;
    }

    error = lodepng::decode(image, width, height, state, png_data);
    if (error) {
        std::cerr << "decoder error " << error << ": " << lodepng_error_text(error)
                  << "\n";
        return false;
    }

    // Print basic output dimensions
    std::cout << "PNG image loaded with dimensions: " << width << "x" << height
              << " and Color Type: " << state.info_png.color.colortype
              << " and Bit Depth: " << state.info_png.color.bitdepth << "\n";

    return true;
}


void savePNG(const char *filenameOut, const std::vector<unsigned char> &image,
             unsigned width, unsigned height) {
    unsigned error = lodepng::encode(filenameOut, image, width, height, LCT_GREY, 8);
    if (error) {
        std::cout << "PNG encoder error " << error << ": " << lodepng_error_text(error)
                  << std::endl;
    }
}
