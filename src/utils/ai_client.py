import os
from config.settings import settings

def call_ai(prompt, **kwargs):
    """
    调用DeepSeek AI API
    
    Args:
        prompt: 提示词
        **kwargs: 其他参数
        
    Returns:
        AI响应内容
    """
    return call_deepseek(prompt, **kwargs)


def call_deepseek(prompt, **kwargs):
    """
    调用DeepSeek API
    
    Args:
        prompt: 提示词
        **kwargs: 其他参数
        
    Returns:
        AI响应内容
    """
    from openai import OpenAI
    from loguru import logger
    
    try:
        logger.info(f"调用DeepSeek API，模型: {settings.DEEPSEEK_MODEL}")
        
        client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )

        response = client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=kwargs.get('max_tokens', settings.DEEPSEEK_MAX_TOKENS),
            temperature=kwargs.get('temperature', settings.DEEPSEEK_TEMPERATURE),
            stream=False
        )
        
        result = response.choices[0].message.content
        logger.info(f"API调用成功，返回内容长度: {len(result) if result else 0}")
        return result
        
    except Exception as e:
        logger.error(f"DeepSeek API调用失败: {e}")
        logger.error(f"错误类型: {type(e).__name__}")
        raise e 