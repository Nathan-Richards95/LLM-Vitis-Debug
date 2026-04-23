from helpers import vitis_helper

if __name__ == "__main__":
    print("This is a test module for Vitis AI Engine tests. It is not meant to be run directly.")
    tc_name = "Debug001"
    model_name = "llama"
    helper = vitis_helper.Vitis_Helper(tc_name, model_name)
    helper.build_component("ref")