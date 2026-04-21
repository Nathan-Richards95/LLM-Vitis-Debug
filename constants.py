DEBUG_BASE_PROMPT = """
    INSTRUCTION:
    You are given broken Vitis HLS C/C++ code.
    Repair the code so it is valid and preserves the intended behavior.
    Return only the full corrected source file.
    You will only fix actual bugs in the probided code.
    If the code has no HLS-specific bugs, you will return the code as-is.
    Do not add pragmas unless they are necessary to fix a bug.
    Do not explain your answer.
    INPUT:
"""

FPGA_PART = "xc7z020clg400-1" #part used for synthesis and simulation

TARGET_CLOCK = 100 #target clock frequency in MHz

#Llama constants
LLAMA_PATH = "/scratch/schekur2/models/llama3.3-70b-hls-trained/"
LLAMA_MODEL_NAME = "llama"

VALID_VITIS_MODES = ["ref", LLAMA_MODEL_NAME, LLAMA_MODEL_NAME.lower()]