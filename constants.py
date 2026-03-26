BASE_PROMPT = """
    You are given broken Vitis HLS C/C++ code.
    Repair the code so it is valid and preserves the intended behavior.
    Return only the full corrected source file.
    Do not explain your answer."""