from Models.Llama import Llama
import Models.Model as Model

config = Model.GenerationConfig(
    model_name="codestral",
    max_tokens=50,
    temperature=0.7,
    top_p=0.9
)

model = Llama(config)

response = model.generate([
    {"role": "user", "content": "Say hello briefly"}
])

print("MODEL OUTPUT:")
print(response.text)