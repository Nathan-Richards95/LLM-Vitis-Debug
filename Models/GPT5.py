from openai import OpenAI

class GPT5:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_code(self, prompt, max_tokens=100):
        response = self.client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()