

if __name__ == "__main__":
    data = {
        "name": "test_case_name",
        "meta": {
            "top_function": "top_function_name",
            "required_includes": ["include1.h", "include2.h"]
        },
        "broken_code": "broken_code"
    }
    output = "output"
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
