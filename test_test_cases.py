import helpers.vitis_helper as vitis_helper

def main():
    tc_name = "Debug002"
    ref_vitis = vitis_helper.Vitis_Helper(
        tc_name = tc_name,
        mode = "ref"
    )
    ref_vitis.run_full_pipeline()

if __name__ == "__main__":
    main()