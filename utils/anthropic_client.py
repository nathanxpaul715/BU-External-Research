import anthropic  
from config.auth_manager import get_api_key
from config.settings import ANTHROPIC_MODEL  
from loguru import logger

  
def get_anthropic_client(force_refresh: bool = False) -> anthropic.Anthropic:  
    """  
    Get configured Anthropic client with valid API key
      
    Args:  
        force_refresh: Force fetching a new token
      
    Returns:  
        Configured Anthropic client  
    """  
    api_key = get_api_key(force_refresh)
    logger.info(f"Creating Anthropic client with model: {ANTHROPIC_MODEL}") 
    return anthropic.Anthropic(api_key=api_key)

def get_langchain_chat_model(force_refresh: bool = False):  
    """  
    Get LangChain ChatAnthropic model configured with TR authentication
      
    Args:  
        force_refresh: Force fetching a new token
      
    Returns:  
        Configured ChatAnthropic model  
    """  
    from langchain_anthropic import ChatAnthropic  
    from config.settings import MAX_TOKENS, TEMPERATURE
      
    api_key = get_api_key(force_refresh)
      
    return ChatAnthropic(  
        model=ANTHROPIC_MODEL,  
        anthropic_api_key=api_key,  
        temperature=TEMPERATURE,  
        max_tokens=MAX_TOKENS  
    )