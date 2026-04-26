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

#GPT OSS 120b constants
GPT_OSS_120b_PATH = "/scratch/nrricha2/Versal_Project/Models/GPT_OSS_120b"
VALID_GPT_OSS_120b_INPUTS = ["gpt_oss_120b_raw", "120r"]
GPT_OSS_120b_MODEL_NAME = "GPT-OSS-120b-raw"

VALID_VITIS_MODES = [
    "ref", 
    LLAMA_MODEL_NAME,
    LLAMA_MODEL_NAME.lower(),
    GPT_OSS_120b_MODEL_NAME, 
    GPT_OSS_120b_MODEL_NAME.lower()
]


#scoring stuff
EASY_MULTIPLIER = 1
MEDIUM_MULTIPLIER = 2
HARD_MULTIPLIER = 3

def GET_BASE_RESULTS_FORMAT():
    return {
        "score": {},
        "test_results": []
    }