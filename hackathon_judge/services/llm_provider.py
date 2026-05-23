import os

from hackathon_judge.config.settings import get_settings


def get_litellm_model(model_name: str):
    from deepeval.models import DeepEvalBaseLLM
    import litellm

    settings = get_settings()

    if settings.openai_api_key:
        os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
    if settings.anthropic_api_key:
        os.environ.setdefault("ANTHROPIC_API_KEY", settings.anthropic_api_key)
    if settings.deepseek_api_key:
        os.environ.setdefault("DEEPSEEK_API_KEY", settings.deepseek_api_key)
    if settings.gemini_api_key:
        os.environ.setdefault("GEMINI_API_KEY", settings.gemini_api_key)

    class LiteLLMModel(DeepEvalBaseLLM):
        def __init__(self, model: str):
            self._model_name = model

        def load_model(self):
            return self._model_name

        def generate(self, prompt: str, schema=None) -> str:
            kwargs = {"model": self._model_name, "messages": [{"role": "user", "content": prompt}]}
            if schema:
                kwargs["response_format"] = schema
            resp = litellm.completion(**kwargs)
            return resp.choices[0].message.content

        async def a_generate(self, prompt: str, schema=None) -> str:
            kwargs = {"model": self._model_name, "messages": [{"role": "user", "content": prompt}]}
            if schema:
                kwargs["response_format"] = schema
            resp = await litellm.acompletion(**kwargs)
            return resp.choices[0].message.content

        def get_model_name(self) -> str:
            return self._model_name

    return LiteLLMModel(model_name)
