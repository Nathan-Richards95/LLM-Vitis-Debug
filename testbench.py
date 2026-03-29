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
