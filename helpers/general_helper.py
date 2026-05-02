import json
import constants
from pathlib import Path
import re
import shutil
import subprocess

def score_model(results_data_path: str):
    #Iterates through all of the results from the json file and calculates a score
    #based on whether the output was correct. Later, will add the number of retries,
    #whether non code text was generated.
    #Afterwards, will add in the performance metrics and use those to calculate a final score.
    results_data = []
    with open(results_data_path, "r", encoding="utf-8") as f:
        results_data = json.load(f)["test_results"]

    score = 0
    for result in results_data:
        print(f'Result: {result}')
        if result["correctness_pass"]:
            difficulty = result["difficulty"]
            if difficulty == "easy":
                score += constants.EASY_MULTIPLIER
            elif difficulty == "medium":
                score += constants.MEDIUM_MULTIPLIER
            elif difficulty == "hard":
                score += constants.HARD_MULTIPLIER
        #add in other factors here later, such as parseable output, number of retries, etc.

    print(f"Final Score: {score}/{len(results_data)}")
    #put the score at the top of the json
    with open(results_data_path, "r+", encoding="utf-8") as f:
        existing_data = json.load(f)
        #can add other statistics such as which bugs were good at fixing, which were hard, etc.
        output_data = {
            "score": score,
            "total_cases": len(results_data),
        }
        f.seek(0)
        json.dump(output_data, f, indent=4)



def get_testCases():
    testCase = []
    TEST_CASES_DIR = Path("Test_Cases")
    for item in TEST_CASES_DIR.iterdir():
        #print (TEST_CASES_DIR.iterdir())
        if item.is_dir():
            testCase.append(item)

    return testCase
    
def load_testCases(tc_path, model_type):
    broken_path = tc_path / "broken" / "broken.cpp"
    meta_path = tc_path / "meta.json"
    model_graph_path = tc_path / model_type / "graph.cpp"
    ref_graph_path = tc_path / "ref" / "graph.cpp"
    ref_path = tc_path / "ref" / "ref.cpp"
    host_path = tc_path / "shared" / "host.cpp"

    testcase_data = {
        "name": tc_path.name,
        "broken_code": "",
        "meta": {},
        "model_graph_code": "",
        "ref_graph_code": "",
        "ref_code": "",
        "host_code": ""
    }
    if broken_path.exists():
        testcase_data["broken_code"] = broken_path.read_text(encoding="utf-8")
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            testcase_data["meta"] = json.load(f)
    if model_graph_path.exists():
        testcase_data["model_graph_code"] = model_graph_path.read_text(encoding="utf-8")
    if ref_graph_path.exists():
        testcase_data["ref_graph_code"] = ref_graph_path.read_text(encoding="utf-8")
    if ref_path.exists():
        testcase_data["ref_code"] = ref_path.read_text(encoding="utf-8")
    if host_path.exists():
        testcase_data["host_code"] = host_path.read_text(encoding="utf-8")
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


def write_llm_output(tc_path, model_type, llm_response):
    """
    Save the LLM's returned code into llm_out.cpp inside the testcase folder.
    """
    cleaned_code = extract_code(llm_response)
    output_dir = tc_path / model_type 
    output_path = output_dir / "broken.cpp"
    if not output_dir.exists():
        broken_dir = tc_path / "broken"
        shutil.copytree(broken_dir, output_dir)
    output_path.write_text(cleaned_code, encoding="utf-8")
    return output_path

def clean_patch(llm_response):
    llm_returned_patch = False
    cleaned_code = llm_response #TODO: Change this to be the properly cleaned code
    return cleaned_code, llm_returned_patch

def apply_git_patch(tc_path, model_type, llm_response):
    cleaned_code, llm_returned_patch = clean_patch(llm_response) #TODO: Change this to be the properly cleaned code
    output_dir = tc_path / model_type 
    output_path = output_dir / "broken.cpp"
    patch_path = output_dir / "patch.diff"
    if not output_dir.exists():
        broken_dir = tc_path / "broken"
        shutil.copytree(broken_dir, output_dir)
    # Apply git patch
    patch_applied = False
    patch_path.write_text(cleaned_code, encoding="utf-8")
    check = subprocess.run(
        ["git", "apply", "--check", str(patch_path.name)],
        cwd=output_dir
    )
    if check.returncode == 0:
        apply_result = subprocess.run(
            ["git", "apply", patch_path.name],
            cwd=output_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE    
        )
        if apply_result.returncode == 0:
            patch_applied = True

    return output_path, patch_applied, llm_returned_patch

def has_top_level_cpp_function(code: str, function_name: str) -> bool:
    # Matches return type + function name + (
    pattern = rf"""
        ^\s*                                  
        (?:[\w:<>\*&]+\s+)+                   
        {re.escape(function_name)}\s*         
        \([^;]*\)\s*                          
        \{{                                   
    """
    return re.search(pattern, code, re.MULTILINE | re.VERBOSE) is not None
