BASE_PROMPT = """
    You are given broken Vitis HLS C/C++ code.
    Repair the code so it is valid and preserves the intended behavior.
    Return only the full corrected source file.
    Do not explain your answer.
"""

FPGA_PART = "xc7z020clg400-1" #part used for synthesis and simulation

TARGET_CLOCK = 100 #target clock frequency in MHz

#Llama constants
LLAMA_BASE_URL = "http://127.0.0.1:8000/v1"
LLAMA_API_KEY = "0"
LLAMA_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
LLAMA_PATH = "/scratch/schekur2/models/llama3.3-70b-hls-trained/"