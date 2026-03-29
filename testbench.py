from transformers import pipeline
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
    print("Hello!")
    #1. iterate through each test case in the test cases directory
    #2. grab the broken code and send it to the LLM
    pipe = pipeline(
        task="text-generation",
        model="openai/gpt-oss-20b",     # or whatever variant you installed
        device_map="auto",              # automatically use GPU if available
        dtype="auto",
    )
    message = constants.BASE_PROMPT
    code = ""
    messages = [
        {
            "role": "system",
            "content": (constants.BASE_PROMPT),
        },
        {
            "role": "user",
            "content": f"===BEGIN BROKEN CODE===\n{code}\n===END BROKEN CODE===",  
        }
    ]
    #3. grab the output from the LLM
    out = pipe(messages, max_new_tokens=2048)
    print(f'{out}')
    fixed_code = out[0]["generated_text"][-1]["content"]
    #4. check the following from the output:
    #   - is the output empty
    #   - is the response just code
    #   - does the top level function still exist
    #   - required includes still exist
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
