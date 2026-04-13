import Model
import constants
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

class Llama(Model.BaseLLM):
    def __init__(self, config: Model.GenerationConfig):
        super().__init__(config)
        self.modelName = "LLaMA"
        self.model_path = constants.LLAMA_MODEL_PATH
        self.quantization_config = BitsAndBytesConfig(
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            load_in_4bit=True
        )

    
    def __post_init__(self):
        self.client = OpenAi(api_key=self.api_key, base_url=self.base_url)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token


    def generate(self, messages: list[Model.Message], **kwargs: any) -> Model.LLMResponse:
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize = True,
            add_generation_prompt = True,
            return_tensors = "pt",
            return_dict = True
        ).to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=2048,
                temperature=0.2,
                top_p=1.0,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        assistant_text = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        return Model.LLMResponse(content=assistant_text)
