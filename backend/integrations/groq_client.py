"""
Groq SDK wrapper with fallback models and better error handling.
"""
import os
from groq import Groq
from flask import current_app


# Fallback models — try in order if primary fails
FALLBACK_MODELS = [
    'openai/gpt-oss-120b',
    'openai/gpt-oss-20b',
    'llama-3.1-8b-instant',
    'llama-3.3-70b-versatile',
]


class GroqClientError(Exception):
    pass


class GroqClient:

    def __init__(self, api_key: str, model: str = None):
        if not api_key or not api_key.strip():
            raise GroqClientError('GROQ_API_KEY is not configured.')
        self.api_key = api_key.strip()
        self.model = (model or FALLBACK_MODELS[0]).strip()
        try:
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            raise GroqClientError(f'Failed to init Groq client: {e}')

    def chat(self, messages, temperature=0.4, max_tokens=800, timeout=25):
        """
        Send chat completion. Tries primary model, then fallbacks.
        """
        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        last_error = None

        for model in models_to_try:
            try:
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout,
                )
                if not completion or not completion.choices:
                    last_error = f'Empty response from model {model}'
                    continue
                content = completion.choices[0].message.content or ''
                if content.strip():
                    if model != self.model:
                        print(f'[GroqClient] Used fallback model: {model}')
                    return content
                last_error = f'Empty content from model {model}'
            except Exception as e:
                error_str = str(e)
                print(f'[GroqClient] Model {model} failed: {error_str[:200]}')
                last_error = error_str
                # If it's a model-not-found error, try next model
                if 'not_found' in error_str.lower() or 'does not exist' in error_str.lower() or '404' in error_str:
                    continue
                # If it's auth error, no point retrying
                if '401' in error_str or 'unauthorized' in error_str.lower():
                    raise GroqClientError(f'Invalid API key: {error_str[:150]}')
                # Otherwise try next model too
                continue

        raise GroqClientError(f'All models failed. Last error: {last_error[:200] if last_error else "unknown"}')


def get_groq_client():
    api_key = (current_app.config.get('GROQ_API_KEY') or os.getenv('GROQ_API_KEY', '')).strip()
    model = (current_app.config.get('GROQ_MODEL') or os.getenv('GROQ_MODEL', FALLBACK_MODELS[0])).strip()
    return GroqClient(api_key=api_key, model=model)


def is_configured():
    try:
        key = current_app.config.get('GROQ_API_KEY') or os.getenv('GROQ_API_KEY', '')
        return bool(key and key.strip())
    except RuntimeError:
        return bool(os.getenv('GROQ_API_KEY', '').strip())