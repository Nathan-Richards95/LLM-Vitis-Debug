from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    role: str   # "system", "user", "assistant"
    content: str


@dataclass
class GenerationConfig:
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 512
    top_p: float = 1.0
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    text: str
    raw: Any = None
    usage: Optional[Dict[str, Any]] = None


class BaseLLM(ABC):
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.model_name = config.model_name

    @abstractmethod
    def generate(self, messages: List[Message]) -> LLMResponse:
        """Run the model on a chat-style prompt."""
        raise NotImplementedError

    def generate_from_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        messages: List[Message] = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=prompt))
        return self.generate(messages)