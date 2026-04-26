import Models.Model as Model
import constants
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class GPT_OSS_120b_raw(Model.BaseLLM):
    def __init__(self, config: Model.GenerationConfig):
        super().__init__(config)

        self.modelName = "GPT-OSS-120b-raw"
        self.model_path = constants.GPT_OSS_120b_PATH

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            use_fast=False,
            trust_remote_code=True
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype="auto",
            device_map="auto",
            trust_remote_code=True
        )

    def generate(self, messages: list[Model.Message], **kwargs: any) -> Model.LLMResponse:
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True
        ).to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=self.config.temperature > 0,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        assistant_text = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

        return Model.LLMResponse(text=assistant_text)