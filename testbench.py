from sys import argv

from transformers import pipeline
import constants
import json
from pathlib import Path
#import Models.Model
#from Models.Llama import Llama
import platform
import subprocess
import re
from Models.Model import GenerationConfig
from Models.Llama import Llama

TEST_CASES_DIR = Path("Test_Cases")

def get_testCases():
    testCase = []
    
    for item in TEST_CASES_DIR.iterdir():
        #print (TEST_CASES_DIR.iterdir())
        if item.is_dir():
            testCase.append(item)

    return testCase
    
def load_testCases(tc_path):
    broken_path = tc_path / "broken.cpp"
    meta_path = tc_path / "meta.json"
    tb_path = tc_path / "debug_tb.cpp"
    ref_path = tc_path / "ref.cpp"

    testcase_data = {
        "name": tc_path.name,
        "broken_code": "",
        "meta": {},
        "tb_code": "",
        "ref_code": ""
    }
    if broken_path.exists():
        testcase_data["broken_code"] = broken_path.read_text(encoding="utf-8")

    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            testcase_data["meta"] = json.load(f)

    if tb_path.exists():
        testcase_data["tb_code"] = tb_path.read_text(encoding="utf-8")

    if ref_path.exists():
        testcase_data["ref_code"] = ref_path.read_text(encoding="utf-8")

    return testcase_data

def extract_code(llm_response):
    """
    Removes markdown code fences if the LLM returns:
    ```cpp
    ...
    ```
    """
    text = llm_response.strip()

    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 3:
            return parts[1].replace("cpp", "", 1).strip()

    return text


def write_llm_output(tc_path, llm_response):
    """
    Save the LLM's returned code into llm_out.cpp inside the testcase folder.
    """
    cleaned_code = extract_code(llm_response)
    output_path = tc_path / "llm_out.cpp"
    output_path.write_text(cleaned_code, encoding="utf-8")
    return output_path

def run_vitis_case(tc_path, meta, llm_out_path):
    proj_dir = Path("runs") / tc_path.name / "hls_proj"
    proj_dir.parent.mkdir(parents=True, exist_ok=True)

    top = meta.get("top_function", "")
    part = meta.get("part", "xc7z020clg400-1")
    clock = str(meta.get("clock_period", 10.0))

    cmd = [
        "vitis_hls",
        "-f", "run_hls.tcl",
        f"proj_dir={proj_dir}",
        f"src={llm_out_path}",
        f"tb={tc_path / 'debug_tb.cpp'}",
        f"top={top}",
        f"part={part}",
        f"clock={clock}",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    (proj_dir.parent / "vitis_stdout.txt").write_text(result.stdout)
    (proj_dir.parent / "vitis_stderr.txt").write_text(result.stderr)

    return result
def has_top_level_cpp_function(code: str, function_name: str) -> bool:
    # Matches return type + function name + (
    pattern = rf"""
        ^\s*                                  # start of line
        (?:[\w:<>\*&]+\s+)+                   # return type (very flexible)
        {function_name}\s*                    # function name
        \([^;]*\)\s*                          # arguments
        \{{                                   # opening brace (definition, not declaration)
    """

    return re.search(pattern, code, re.MULTILINE | re.VERBOSE) is not None

if __name__ == '__main__':
    #1. iterate through each test case in the test cases directory
    #2. grab the broken code and send it to the LLM
    testcases = get_testCases()        
    model_type = argv[1] if len(argv) > 1 else "llama"
    model = None
    match model_type:
        case "llama":
            config = GenerationConfig(
                model_name=constants.LLAMA_MODEL_NAME,
                temperature=0.2,
                max_tokens=2048,
                top_p=1.0
            )
            model = Llama(config=config)
        case "gpt5":
            pass  # Handle GPT-5 case
    if model is None:
        print(f"Unsupported model type: {model_type}")
        exit(1)
    testcases = get_testCases()
    for tc in testcases:
        data = load_testCases(tc)
        code = f"{data['broken_code']}"
        messages = [
            {"role": "system", "content": constants.DEBUG_BASE_PROMPT},
            {"role": "user", "content": f"{code}"}
        ]
        output = model.generate(messages=messages)
        print(f"LLM output for test case {data['name']}:\n{output.text}\n")
        #3. grab the output from the LLM
        #4. check the following from the output:
        #   - is the output empty
        #   - is the response just code (are comments ok?)
        #   - does the top level function still exist
        #   - required includes still exist
        parseable_output = True
        error = ""
        if vars(output)['text'].strip() == "":
            parseable_output = False
            error = "LLM returned an empty response."
            print(f"Error for test case {data['name']}: {error}")
        
        if has_top_level_cpp_function(vars(output)['text'], data['meta']['top_function']) == False:
            print(f"Top level function is missing in the output for test case {data['name']}.")
            error = "Missing top level function."
            parseable_output = False
        #5. Attempt to run the tcl file to see if it synthesizes and simulates without error
        #6. Grab the output json and record the following:
        #   - csim success
        #   - csynth success
        #   - correctness pass
        #   - compiler errors
        #   - compiler warnings
        #   - synthesis errors
        #   - synthesis warnings
        #   - runtime metrics (clock frequency, resource usage, etc.)
        #7. Write the output json to a file. Store using the following schema:
        # {
        #     "run_id": "modelA_debug_001",
        #     "model": "modelA",
        #     "benchmark_id": "debug_001",
        #     "bug_type": "missing_semicolon",
        #     "parseable_output": true,
        #     "error_types": [],
        #     "top_function_present": true,
        #     "csim_success": true,
        #     "correctness_pass": true,
        #     "csynth_success": true,
        #     "compiler_errors": [],
        #     "compiler_warnings": [],
        #     "synthesis_errors": [],
        #     "synthesis_warnings": [],
        #     "final_status": "success"
        # }

       

