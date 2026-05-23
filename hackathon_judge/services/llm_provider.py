from deepeval.models import DeepEvalBaseLLM
import litellm


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


def get_litellm_model(model_name: str) -> LiteLLMModel:
    return LiteLLMModel(model_name)
