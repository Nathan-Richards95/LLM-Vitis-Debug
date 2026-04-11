import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import constants

if __name__ == "__main__":
    model_path = "/scratch/schekur2/models/llama3.3-70b-hls-trained/"
    quantization_config = BitsAndBytesConfig(
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        load_in_4bit=True
    )

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=False
    )

    prompt = constants.BASE_PROMPT + "\n===BEGIN BROKEN CODE===\n" + "int main() { int i = 1 }\n" + "===END BROKEN CODE==="
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=2048,
            temperature=0.2,
            top_p=1.0
        )

    print(tokenizer.decode(outputs[0], skip_special_tokens=True))