import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import constants

if __name__ == "__main__":
    model_path = "/scratch/schekur2/models/llama3.3-70b-hls-trained/"
    print(f'Model path: {model_path}')
    quantization_config = BitsAndBytesConfig(
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        load_in_4bit=True
    )

    print("loading tokenizer")
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    print("loading model")
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("tokenizing")
    messages = [
        {"role": "system", "content": constants.DEBUG_BASE_PROMPT},
        {"role": "user", "content": "int main() { int i = 1 }"}
    ]
    print("generating")
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize = True,
        add_generation_prompt = True,
        return_tensors = "pt",
        return_dict = True
    ).to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=2048,
            temperature=0.2,
            top_p=1.0,
            pad_token_id=tokenizer.pad_token_id,
        )

    new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
    assistant_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
    print("done")
    print("Assistant response:")
    print(assistant_text)
    with open("test_output.txt", "w") as f:
        f.write(assistant_text)