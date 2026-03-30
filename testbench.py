import constants
import json
from pathlib import Path

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
    testcases = get_testCases()
    #print("Hello!")
    #1. 


    for tc in testcases:
        print("DEBUG: iterating ->", tc.name)
        #print(tc.name)  testing if it pulls from the right place

        data = load_testCases(tc)


        print("Testcase:", data["name"])
        print("Broken code:")
        print(data["broken_code"])
        print("Meta:")
        print(data["meta"])
        print("-" * 40)

        # TEMPORARY TEST:
        # pretend the LLM returned the reference code
        fake_llm_response = data["ref_code"]

        llm_out_path = write_llm_output(tc, fake_llm_response)
        print("Wrote LLM output to:", llm_out_path)
    
    
