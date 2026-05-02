import os
from pathlib import Path


OUTPUT_DEBUG_BASE_PROMPT = f"""INSTRUCTION:

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

PATCH_DEBUG_BASE_PROMPT = f"""
INSTRUCTION:

You are a compiler-like patch generation system.

Your task is to take the provided broken Vitis HLS / Versal AIE C/C++ code and output a corrected git diff patch that fixes the code while preserving the intended behavior.

STRICT OUTPUT RULES (MANDATORY):
- Output ONLY a valid unified git diff patch.
- Do NOT output the full corrected source file.
- Do NOT include explanations, comments, markdown, or extra text.
- Do NOT wrap the output in ``` or any formatting.
- Do NOT prepend or append anything outside the patch.
- The output must begin with: diff --git
- The output must be directly usable with: git apply patch.diff
- If you violate any of these rules, the output is invalid.

PATCH FORMAT RULES:
- Use unified git diff format.
- Use paths relative to the directory where the patch will be applied.
- Do NOT include absolute paths.
- Do NOT include parent directory paths such as Test_Cases/... unless those paths are present from the patch application directory.
- For a file named broken.cpp, use:
  diff --git a/broken.cpp b/broken.cpp
  --- a/broken.cpp
  +++ b/broken.cpp
- For a file named vector_add.cpp, use:
  diff --git a/vector_add.cpp b/vector_add.cpp
  --- a/vector_add.cpp
  +++ b/vector_add.cpp
- Every hunk must include a valid @@ line with correct line numbers and line counts.
- Include enough unchanged context lines before and after each change for git apply to match the file.
- Do NOT indent patch header lines.
- Lines removed from the original file must begin with "-".
- Lines added to the new file must begin with "+".
- Unchanged context lines must begin with a single space.
- Do NOT omit required closing braces or context lines from a hunk.
- The patch must apply cleanly with git apply.

REPAIR RULES:
- Fix ONLY real syntax, semantic, API, or compilation errors.
- Preserve original structure and intent as much as possible.
- Make the smallest change necessary to fix the problem.
- Do NOT rewrite the program unless necessary for correctness.
- Do NOT add optimizations or unnecessary pragmas.
- ONLY add pragmas if required for correctness or compilation.
- Maintain compatibility with Vitis HLS / Versal AIE APIs.
- Do not create, delete, or rename files unless required to fix the issue.

EDGE CASE RULE:
- If the input code is already valid and has no HLS/AIE-related issues, output an empty patch exactly as:
diff --git a/NO_CHANGES b/NO_CHANGES
--- a/NO_CHANGES
+++ b/NO_CHANGES
@@ -0,0 +0,0 @@

SELF-CHECK BEFORE OUTPUT:
- Ensure the output is a valid unified git diff patch.
- Ensure the output starts with diff --git.
- Ensure all file paths are relative to the patch application directory.
- Ensure the patch modifies the correct filename from the input.
- Ensure every hunk has correct line counts.
- Ensure there is NO natural language in the output.
- Ensure there are NO markdown code fences.
- Ensure the patch can be saved as patch.diff and applied using git apply patch.diff.

OUTPUT FORMAT RULES:
- Return the final patch using the exact markers below.
- Prefer no text before or after the markers.
- If any text appears outside the markers, it will be ignored.
- The text between the markers must contain ONLY a valid unified git diff patch.
- Do NOT put explanations, markdown, comments, or code fences between the markers.
- After removing the marker lines, the patch must be directly usable with:
  git apply patch.diff

===PATCH STARTS HERE===
<valid git diff patch only>
===PATCH ENDS HERE===

Any output that contains text outside of the git diff patch will be discarded.

INPUT FILE NAME:
broken.cpp
"""

#TODO: Make this prompt able to toggle between git patch and output
# also make it put the error into the prompt
# also make it put the code into the prompt
# then make it return the whole prompt
def GENERATE_PROMPT(error):
    prompt = OUTPUT_DEBUG_BASE_PROMPT if USE_GIT_PATCH else PATCH_DEBUG_BASE_PROMPT
    prompt += f"""
        Bug description:
        {error}
    """
    return prompt

FPGA_PART = "xc7z020clg400-1" #part used for synthesis and simulation

TARGET_CLOCK = 100 #target clock frequency in MHz

#Llama constants
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Model names
LLAMA_MODEL_NAME = "qwen"
GPT_OSS_120b_MODEL_NAME = "GPT-OSS-120b-raw"
CODESTRAL_V6_MODEL_NAME = "codestral-v6" # the semi working model
CODESTRAL_MODEL_NAME = "codestral-22b-aie-merged"
QWEN_MODEL_NAME = "qwen2.5-32b-aie-merged"
QWEN_QLORA_MODEL_NAME = "qwen2.5-32b-aie-qlora"

# Model paths
CODESTRAL_V6_PATH = os.path.join(REPO_ROOT, "Collab_Models", "codestral-22b-aie-v6-merged")
CODESTRAL_PATH = os.path.join(REPO_ROOT, "Collab_Models", "codestral-22b-aie-merged")
QWEN_PATH = os.path.join(REPO_ROOT, "Collab_Models", "qwen2.5-32b-aie-merged")
LLAMA_PATH = QWEN_PATH
GPT_OSS_120b_PATH = "/scratch/nrricha2/Versal_Project/Models/GPT_OSS_120b"

# Model repo id's for hugging face
CODESTRAL_V6_REPO_ID = "SiddharthaChekuri/codestral-22b-aie-v6-merged"
CODESTRAL_REPO_ID = "SiddharthaChekuri/codestral-22b-aie-merged"
QWEN_REPO_ID = "SiddharthaChekuri/qwen2.5-32b-aie-merged"
QWEN_QLORA_REPO_ID = "theonevk/qwen2.5-32b-aie-qlora"
LLAMA_REPO_ID = QWEN_REPO_ID


#GPT OSS 120b constants
VALID_GPT_OSS_120b_INPUTS = ["gpt_oss_120b_raw", "120r"]

VALID_VITIS_MODES = [
    "ref", 
    LLAMA_MODEL_NAME,
    LLAMA_MODEL_NAME.lower(),
    GPT_OSS_120b_MODEL_NAME, 
    GPT_OSS_120b_MODEL_NAME.lower()
]

# Model downloading stuff
MODEL_DIR = Path("/scratch") / os.environ["USER"] / "models"


AVAILABLE_MODELS = {
    "1": {
        "name": CODESTRAL_MODEL_NAME,
        "repo_id": CODESTRAL_REPO_ID
    },
    "2": {
        "name": QWEN_MODEL_NAME, 
        "repo_id": QWEN_REPO_ID
    },
    "3": {
        "name": QWEN_QLORA_MODEL_NAME,
        "repo_id": QWEN_QLORA_REPO_ID
    },
    "4": {
        "name": CODESTRAL_V6_MODEL_NAME,
        "repo_id": CODESTRAL_V6_REPO_ID
    }
}

#scoring stuff
EASY_MULTIPLIER = 1
MEDIUM_MULTIPLIER = 2
HARD_MULTIPLIER = 3

def GET_BASE_RESULTS_FORMAT():
    return {
        "score": {},
        "test_results": []
    }


# constant for whether we use git patch or output write
USE_GIT_PATCH = True