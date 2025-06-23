import os
from config.settings import settings

def call_ai(prompt, provider=None, **kwargs):
    provider = provider or settings.AI_PROVIDER
    if provider == 'openai':
        return call_openai(prompt, api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL, **kwargs)
    elif provider == 'deepseek':
        return call_openai(
            prompt,
            api_key=settings.DEEPSEEK_API_KEY,
            model=settings.DEEPSEEK_MODEL,
            base_url="https://api.deepseek.com/v1",
            **kwargs
        )
    elif provider == 'anthropic':
        return call_anthropic(prompt, **kwargs)
    else:
        raise ValueError(f"Unknown AI provider: {provider}")


def call_openai(prompt, api_key, model, base_url=None, **kwargs):
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    return response.choices[0].message.content


def call_anthropic(prompt, **kwargs):
    import anthropic
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    model = kwargs.get('model', settings.ANTHROPIC_MODEL)
    response = client.messages.create(
        model=model,
        max_tokens=kwargs.get('max_tokens', 1024),
        temperature=kwargs.get('temperature', 0.7),
        messages=[{"role": "user", "content": prompt}]
    )
    if hasattr(response, 'content') and isinstance(response.content, list):
        return response.content[0].text
    elif hasattr(response, 'completion'):
        return response.completion
    else:
        return str(response) 