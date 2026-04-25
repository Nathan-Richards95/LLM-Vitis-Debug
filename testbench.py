# standard library imports
from sys import argv
import json
from pathlib import Path
import subprocess
import os
import platform
import re
from datetime import datetime

# our file imports
import constants
import Models.Model
from Models.Model import GenerationConfig
from Models.Llama import Llama
from datetime import datetime
from helpers import general_helper
from helpers import vitis_helper

def initialize_model(model_type):
    try:
        model = None
        try:
            if model_type == "llama":
                config = GenerationConfig(
                            model_name=constants.LLAMA_MODEL_NAME,
                            temperature=0.2,
                            max_tokens=2048,
                            top_p=1.0
                        )
                model = Llama(config=config)
        except Exception as e:
            print(f"An error occurred while initializing the model: {e}")
            exit(1)
        #case for if the model is not implemented
        if model is None:
            print(f"Unsupported model type: {model_type}")
            exit(1)
        return model
    except Exception as e:
        print(f"An error occurred while initializing the model: {e}")
        exit(1)

def initialize_results_file(model_type):
    try:
        #create a json file to store the results, with a timestamp in the name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = Path("Results") / f"{model_type}_results_{timestamp}.json"
        if not results_path.exists():
            with open(results_path, "w", encoding="utf-8") as f:
                json.dump(constants.GET_BASE_RESULTS_FORMAT(), f)  # initialize with the blank structure
        return results_path, timestamp
    except Exception as e:
        print(f"An error occurred while initializing the results file: {e}")
        exit(1)

def generate_message(tc, model_type, model):
    try:
        #1. iterate through each test case in the test cases directory
        #2. grab the broken code and send it to the LLM
        print(f"Processing test case: {tc.name}")
        data = general_helper.load_testCases(tc, model_type)
        code = data["broken_code"]
        messages = [
            {"role": "system", "content": constants.DEBUG_BASE_PROMPT},
            {"role": "user", "content": f"{code}"}
        ]
        #TODO: Check if the code if fully generated, and if the full code is not there,
        #then keep sending it back in until we get a full response or 
        #we hit a max number of retries.
        #TODO: Also, try to strip any non code from the response
        #TODO: Make sure to keep track if the LLM required trimming and the number of retries it needed
        output = model.generate(messages=messages)
        print(f"LLM output for test case {data['name']}:\n{output.text}\n")
        return data, output
    except Exception as e:
        print(f"An error occurred while generating the message: {e}")
        exit(1)

def validate_output(output, data):
    try:
        #3. grab the output from the LLM
        #4. check the following from the output:
        #   - is the output empty
        #   - is the response just code (are comments ok?)
        #   - does the top level function still exist
        #   - required includes still exist
        parseable_output = True
        error = []
        empty = False
        if output.text.strip() == "":
            parseable_output = False
            error.append("LLM returned an empty response.")
            empty = True
            print(f"Error for test case {data['name']}: {error}")
        print(f'{data["name"]} is not empty') if not empty else print(f'{data["name"]} is empty')
        
        has_top = True
        if general_helper.has_top_level_cpp_function(output.text, data['meta']['top_function']) == False:
            print(f"Top level function is missing in the output for test case {data['name']}.")
            error.append("Missing top level function.")
            parseable_output = False
            has_top = False
        print(f'{data["name"]} has top level function {data["meta"]["top_function"]}') if has_top else print(f'{data["name"]} is missing top level function {data["meta"]["top_function"]}')
        return error, parseable_output, has_top 
    except Exception as e:
        print(f"An error occurred while validating the output: {e}")
        return ["Error validating output."], False, False

def build_ref(tc, data):
    try:
        #5. Attempt to build in x86 and hw for ref
        # check if the hw build report is already in the test case folder. If it is, skip the build step and just read the report.
        report_path = Path(f"Test_Cases/{tc.name}/workspace/aie_ref/build/hw/Work/reports/complexity.csv")
        if report_path.exists():
            print(f"HW build report already exists for test case {data['name']}. Skipping build step.")
        else:
            print(f'Building reference implementation for test case {data["name"]}...')
            ref_vitis = vitis_helper.Vitis_Helper(
                tc_name = tc.name,
                mode = "ref"
            )
            ref_vitis.run_full_pipeline()
    except Exception as e:
        print(f"An error occurred while building the reference implementation: {e}")

def build_model(tc, model_type, data):
    try:
        #5. Attempt to build in x86 and hw for the model
        print(f'Building LLM output for test case {data["name"]}...')
        model_vitis = vitis_helper.Vitis_Helper(
            tc_name = tc.name,
            mode = model_type
        )
        model_vitis.run_full_pipeline()
    except Exception as e:
        print(f"An error occurred while building the model: {e}")

def compare_outputs(tc, model_type, data):
    try:
        #6. Grab the ref output and the llm output and compare them for correctness. Will only check for correctness and not for performance for now
        ref_output_path = Path(f"Test_Cases/{tc.name}/ref/output.txt")
        llm_output_path = Path(f"Test_Cases/{tc.name}/{model_type}/output.txt")
        llm_output_correct = False
        if ref_output_path.exists() and llm_output_path.exists():
            # Compare the outputs for correctness
            with open(ref_output_path, "r", encoding="utf-8") as f:
                ref_output = f.read().strip()
            with open(llm_output_path, "r", encoding="utf-8") as f:
                llm_output = f.read().strip()
            llm_output_correct = (ref_output == llm_output)
            print(f"LLM output correctness for test case {data['name']}: {llm_output_correct}")
        else:
            if not ref_output_path.exists():
                print(f"Reference output file not found for test case {data['name']}. Expected at: {ref_output_path}")
            if not llm_output_path.exists():
                print(f"LLM output file not found for test case {data['name']}. Expected at: {llm_output_path}")
        return llm_output_correct
    except Exception as e:
        print(f"An error occurred while comparing the outputs: {e}")
        return False

def write_results(model_type, timestamp, data, error, has_top, llm_output_correct, parseable_output, results_path):
    try:
        #open a json file in the results folder and append the results for this test case
        results_data = {
            "run_id": f"{model_type}_{data['name']}_{timestamp}",
            "model": model_type,
            "benchmark_id": data['name'],
            "bug_type": data['meta']['bug_type'],
            "parseable_output": parseable_output,
            "error_types": error,
            "top_function_present": has_top,
            "correctness_pass": llm_output_correct,
            "difficulty": data['meta']['difficulty']
        }
        with open(results_path, "r+", encoding="utf-8") as f:
            existing_data = json.load(f)
            existing_data["test_results"].append(results_data)
            f.seek(0)
            json.dump(existing_data, f, indent=4)
    except Exception as e:
        print(f"An error occurred while writing the results: {e}")

def main():

    testcases = general_helper.get_testCases()
    model_type = argv[1] if len(argv) > 1 else "llama"
    model = initialize_model(model_type)
    results_path, timestamp = initialize_results_file(model_type)
    for tc in testcases:
        try:
            data, output = generate_message(tc, model_type, model)
            errors, parseable_output, has_top = validate_output(output, data)
            general_helper.write_llm_output(tc, model_type, output.text)
            build_ref(tc, data)
            build_model(tc, model_type, data)
            llm_output_correct = compare_outputs(tc, model_type, data)
            write_results(model_type, timestamp, data, errors, has_top, llm_output_correct, parseable_output, results_path)
        except Exception as e:
            print(f"An error occurred while processing test case {tc.name}: {e}")
            continue
    general_helper.score_model(results_path)

if __name__ == "__main__":
    main()       

