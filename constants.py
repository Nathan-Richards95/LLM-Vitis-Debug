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
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Model paths
CODESTRAL_PATH = os.path.join(REPO_ROOT, "Collab_Models", "codestral-22b-aie-merged")
QWEN_PATH = os.path.join(REPO_ROOT, "Collab_Models", "qwen2.5-32b-aie-merged")

# Default model (change this to switch models)
LLAMA_PATH = QWEN_PATH

LLAMA_MODEL_NAME = "qwen"

VALID_VITIS_MODES = ["ref", LLAMA_MODEL_NAME, LLAMA_MODEL_NAME.lower()]

#scoring stuff
EASY_MULTIPLIER = 1
MEDIUM_MULTIPLIER = 2
HARD_MULTIPLIER = 3

def GET_BASE_RESULTS_FORMAT():
    return {
        "score": {},
        "test_results": []
    }