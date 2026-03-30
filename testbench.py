from sys import argv

from transformers import pipeline
import constants
import json
from pathlib import Path
import Models.Model
from Models.Llama import Llama
import platform

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



if __name__ == '__main__':
    #1. iterate through each test case in the test cases directory
    #2. grab the broken code and send it to the LLM
    model_type = argv[1] if len(argv) > 1 else "gpt5"
    model = None
    match model_type:
        case "llama":
            config = Models.Model.GenerationConfig(
                model_name=constants.LLAMA_MODEL,
                temperature=0.7,
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
        code = f"===BEGIN BROKEN CODE===\n{code}\n===END BROKEN CODE==="
        output = model.generate_from_text(code, system_prompt=constants.BASE_PROMPT)
        #3. grab the output from the LLM
        #4. check the following from the output:
        #   - is the output empty
        #   - is the response just code
        #   - does the top level function still exist
        #   - required includes still exist
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

       

