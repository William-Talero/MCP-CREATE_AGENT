from enum import Enum
from typing import NamedTuple

class AIModelProvider(str, Enum):
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    META = "meta"
    MISTRAL = "mistral"
    COHERE = "cohere"
    GOOGLE = "google"

class AIModelInfo(NamedTuple):
    provider: AIModelProvider
    model: str
    display_name: str
    description: str
    max_tokens: int
    supports_tools: bool
    supports_vision: bool

class AIModel:
    # OpenAI Models
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4_32K = "gpt-4-32k"
    GPT_35_TURBO = "gpt-35-turbo"
    GPT_35_TURBO_16K = "gpt-35-turbo-16k"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"

    # Anthropic Models
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    CLAUDE_35_SONNET = "claude-3-5-sonnet"

    # Meta Models
    LLAMA_2_7B = "llama-2-7b"
    LLAMA_2_13B = "llama-2-13b"
    LLAMA_2_70B = "llama-2-70b"
    LLAMA_3_8B = "llama-3-8b"
    LLAMA_3_70B = "llama-3-70b"
    LLAMA_31_8B = "llama-3.1-8b"
    LLAMA_31_70B = "llama-3.1-70b"
    LLAMA_31_405B = "llama-3.1-405b"

    # Mistral Models
    MISTRAL_7B = "mistral-7b"
    MISTRAL_8X7B = "mistral-8x7b"
    MISTRAL_LARGE = "mistral-large"
    MISTRAL_SMALL = "mistral-small"

    # Cohere Models
    COMMAND = "command"
    COMMAND_LIGHT = "command-light"
    COMMAND_R = "command-r"
    COMMAND_R_PLUS = "command-r-plus"

    # Google Models
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    GEMINI_15_PRO = "gemini-1.5-pro"
    GEMINI_15_FLASH = "gemini-1.5-flash"

    _MODELS: dict[str, AIModelInfo] = {
        # OpenAI Models
        GPT_4: AIModelInfo(
            provider=AIModelProvider.AZURE_OPENAI,
            model=GPT_4,
            display_name="GPT-4",
            description="Modelo más capaz de OpenAI",
            max_tokens=8192,
            supports_tools=True,
            supports_vision=False,
        ),
        GPT_4_TURBO: AIModelInfo(
            provider=AIModelProvider.AZURE_OPENAI,
            model=GPT_4_TURBO,
            display_name="GPT-4 Turbo",
            description="GPT-4 optimizado y más rápido",
            max_tokens=128000,
            supports_tools=True,
            supports_vision=True,
        ),
        GPT_4O: AIModelInfo(
            provider=AIModelProvider.AZURE_OPENAI,
            model=GPT_4O,
            display_name="GPT-4o",
            description="GPT-4 optimizado multimodal",
            max_tokens=128000,
            supports_tools=True,
            supports_vision=True,
        ),
        GPT_35_TURBO: AIModelInfo(
            provider=AIModelProvider.AZURE_OPENAI,
            model=GPT_35_TURBO,
            display_name="GPT-3.5 Turbo",
            description="Modelo rápido y eficiente",
            max_tokens=4096,
            supports_tools=True,
            supports_vision=False,
        ),
        # Anthropic Models
        CLAUDE_35_SONNET: AIModelInfo(
            provider=AIModelProvider.ANTHROPIC,
            model=CLAUDE_35_SONNET,
            display_name="Claude 3.5 Sonnet",
            description="Último modelo de Anthropic, equilibrio perfecto",
            max_tokens=200000,
            supports_tools=True,
            supports_vision=True,
        ),
        CLAUDE_3_OPUS: AIModelInfo(
            provider=AIModelProvider.ANTHROPIC,
            model=CLAUDE_3_OPUS,
            display_name="Claude 3 Opus",
            description="Modelo más potente de Anthropic",
            max_tokens=200000,
            supports_tools=True,
            supports_vision=True,
        ),
        CLAUDE_3_SONNET: AIModelInfo(
            provider=AIModelProvider.ANTHROPIC,
            model=CLAUDE_3_SONNET,
            display_name="Claude 3 Sonnet",
            description="Equilibrio entre capacidad y velocidad",
            max_tokens=200000,
            supports_tools=True,
            supports_vision=True,
        ),
        # Meta Models
        LLAMA_31_405B: AIModelInfo(
            provider=AIModelProvider.META,
            model=LLAMA_31_405B,
            display_name="Llama 3.1 405B",
            description="Modelo más grande de Meta",
            max_tokens=128000,
            supports_tools=True,
            supports_vision=False,
        ),
        LLAMA_31_70B: AIModelInfo(
            provider=AIModelProvider.META,
            model=LLAMA_31_70B,
            display_name="Llama 3.1 70B",
            description="Equilibrio entre tamaño y rendimiento",
            max_tokens=128000,
            supports_tools=True,
            supports_vision=False,
        ),
        # Mistral Models
        MISTRAL_LARGE: AIModelInfo(
            provider=AIModelProvider.MISTRAL,
            model=MISTRAL_LARGE,
            display_name="Mistral Large",
            description="Modelo grande de Mistral",
            max_tokens=32000,
            supports_tools=True,
            supports_vision=False,
        ),
        MISTRAL_SMALL: AIModelInfo(
            provider=AIModelProvider.MISTRAL,
            model=MISTRAL_SMALL,
            display_name="Mistral Small",
            description="Modelo pequeño y rápido de Mistral",
            max_tokens=32000,
            supports_tools=True,
            supports_vision=False,
        ),
        # Google Models
        GEMINI_15_PRO: AIModelInfo(
            provider=AIModelProvider.GOOGLE,
            model=GEMINI_15_PRO,
            display_name="Gemini 1.5 Pro",
            description="Modelo multimodal avanzado de Google",
            max_tokens=1000000,
            supports_tools=True,
            supports_vision=True,
        ),
        GEMINI_15_FLASH: AIModelInfo(
            provider=AIModelProvider.GOOGLE,
            model=GEMINI_15_FLASH,
            display_name="Gemini 1.5 Flash",
            description="Versión rápida de Gemini",
            max_tokens=1000000,
            supports_tools=True,
            supports_vision=True,
        ),
        # Cohere Models
        COMMAND_R_PLUS: AIModelInfo(
            provider=AIModelProvider.COHERE,
            model=COMMAND_R_PLUS,
            display_name="Command R+",
            description="Modelo más avanzado de Cohere",
            max_tokens=128000,
            supports_tools=True,
            supports_vision=False,
        ),
    }

    @classmethod
    def get_model_info(cls, model_name: str) -> AIModelInfo | None:
        return cls._MODELS.get(model_name)

    @classmethod
    def get_all_models(cls) -> dict[str, AIModelInfo]:
        return cls._MODELS.copy()

    @classmethod
    def get_models_by_provider(cls, provider: AIModelProvider) -> dict[str, AIModelInfo]:
        return {k: v for k, v in cls._MODELS.items() if v.provider == provider}

    @classmethod
    def detect_provider(cls, model_name: str) -> AIModelProvider | None:
        model_info = cls.get_model_info(model_name)
        return model_info.provider if model_info else None
