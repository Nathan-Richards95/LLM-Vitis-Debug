from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_PATH = "/scratch/schekur2/models/llama3.3-70b-hls-trained/"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="auto"
)

system_prompt = (
    "You are an expert Vitis HLS debugging assistant. "
    "Given broken HLS C/C++ code, return only the corrected code."
)

chat_history = [
    {"role": "system", "content": system_prompt}
]

print("\nModel loaded. Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.strip().lower() == "exit":
        break

    chat_history.append({"role": "user", "content": user_input})

    prompt = tokenizer.apply_chat_template(
        chat_history,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.95,
            do_sample=True
        )

    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True
    )

    print(f"\nModel:\n{response}\n")

    chat_history.append({"role": "assistant", "content": response})