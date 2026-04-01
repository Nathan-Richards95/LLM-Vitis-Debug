from Models import Model
import constants
from openai import OpenAi

class Llama(Model.BaseLLM):
    def __init__(self, config: Model.GenerationConfig):
        super().__init__(config)
        self.modelName = "LLaMA"
        self.base_url = constants.LLAMA_BASE_URL
        self.api_key = constants.LLAMA_API_KEY
        self.model = constants.LLAMA_MODEL
    
    def __post_init__(self):
        self.client = OpenAi(api_key=self.api_key, base_url=self.base_url)

    def generate(self, messages: list[Model.Message], **kwargs: any) -> Model.LLMResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 256),
        )
        return response.choices[0].message.content or ""
