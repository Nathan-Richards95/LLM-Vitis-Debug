import os
DEBUG_BASE_PROMPT = f"""You are fixing a broken C++ source file for AMD Vitis/AIE.

Requirements:
- Return the COMPLETE corrected source file
- Do NOT return partial code
- Do NOT omit unchanged code
- Do NOT add explanations
- Do NOT use markdown fences
- Preserve all includes, declarations, and unchanged functions
- Only fix the bug(s) needed
"""


"""
    INSTRUCTION:

You are a compiler-like transformation system.

Your task is to take the provided broken Vitis HLS / Versal AIE C/C++ code and output a corrected version that compiles and preserves the intended behavior.

STRICT OUTPUT RULES (MANDATORY):
- Output ONLY the full corrected source code file.
- Do NOT include any explanations, comments, markdown, or extra text.
- Do NOT wrap the output in ``` or any formatting.
- Do NOT prepend or append anything.
- The output must begin with the first character of valid C/C++ code.
- The output must end with the final character of the source file.
- If you violate any of these rules, the output is invalid.

REPAIR RULES:
- Fix ONLY real syntax, semantic, or API errors.
- Preserve original structure and intent as much as possible.
- Do NOT rewrite the program unless necessary to fix correctness.
- Do NOT add optimizations or unnecessary pragmas.
- ONLY add pragmas if required for correctness or compilation.
- Maintain compatibility with Vitis HLS / Versal AIE APIs.

EDGE CASE RULE:
- If the input code is already valid and has no HLS/AIE-related issues, output it EXACTLY unchanged.

SELF-CHECK BEFORE OUTPUT:
- Ensure the output is valid C/C++ code.
- Ensure there is NO natural language in the output.
- Ensure there are NO explanations or comments added.
- Ensure the output is a single complete file.

Any output that contains text outside of valid C/C++ code will be discarded.

INPUT:
"""

FPGA_PART = "xc7z020clg400-1" #part used for synthesis and simulation

TARGET_CLOCK = 100 #target clock frequency in MHz

#Llama constants
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Model paths
CODESTRAL_PATH = os.path.join(REPO_ROOT, "Collab_Models", "codestral-22b-aie-merged")
QWEN_PATH = os.path.join(REPO_ROOT, "Collab_Models", "qwen2.5-32b-aie-merged")

# Default model (change this to switch models)
LLAMA_PATH = QWEN_PATH

LLAMA_MODEL_NAME = "qwen"

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