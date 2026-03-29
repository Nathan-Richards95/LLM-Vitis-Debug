from transformers import pipeline
import constants

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