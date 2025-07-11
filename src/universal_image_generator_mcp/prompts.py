###############################
# Image Transformation Prompt #
###############################
def get_image_transformation_prompt(prompt: str) -> str:
    """Create a detailed prompt for image transformation.
    
    Args:
        prompt: text prompt
        
    Returns:
        A comprehensive prompt for Gemini image transformation
    """
    return f"""You are an expert image editing AI. Please edit the provided image according to these instructions:

EDIT REQUEST: {prompt}

IMPORTANT REQUIREMENTS:
1. Make substantial and noticeable changes as requested
2. Maintain high image quality and coherence 
3. Ensure the edited elements blend naturally with the rest of the image
4. Do not add any text to the image
5. Focus on the specific edits requested while preserving other elements

The changes should be clear and obvious in the result."""

###########################
# Image Generation Prompt #
###########################
def get_image_generation_prompt(prompt: str) -> str:
    """Create a detailed prompt for image generation.
    
    Args:
        prompt: text prompt
        
    Returns:
        A comprehensive prompt for Gemini image generation
    """
    return f"""You are a professional AI image generation assistant.

Core Task

Create the most appropriate visual content based on user prompts. When faced with vague or abstract prompts, directly infer the most likely intent and generate images without asking for clarification.

Primary Principle: No Text in Images

Any generated image must absolutely not contain any form of text, letters, or characters. This rule overrides all other instructions. Treat text in prompts as visual concepts, not rendering requirements.

Execution Points

Active Creation: For ambiguous requirements, use your knowledge to fill in the most appropriate details.

Visual Substitution: For items that typically contain text (books, newspapers, signs), only generate their visual appearance without any readable characters.

Smart Enhancement: Automatically supplement images with the most suitable lighting, composition, artistic style, colors, and environmental details.

Pursue Excellence: Always maintain high image quality, excellent composition, and visual harmony.

User Request: {prompt}
"""

####################
# Translate Prompt #
####################
def get_translate_prompt(prompt: str, target_language: str = "english") -> str:
    """Translate the prompt into the target language if it's not already in that language.
    
    Args:
        prompt: text prompt
        target_language: target language ("english" or "chinese")
        
    Returns:
        A comprehensive prompt for translation
    """
    if target_language.lower() == "chinese":
        return f"""将以下提示词翻译成中文（如果还不是中文的话）。你的任务是准确翻译，同时保持：

1. 完全保留原始意图和含义
2. 保留所有具体细节和细微差别
3. 保持原始提示词的风格和语调
4. 保持技术术语和概念

不要：
- 添加原文中没有的新细节或创意元素
- 删除原文中的任何细节
- 改变风格或复杂度
- 重新解释或假设用户"真正的意思"

如果文本已经是中文，请完全按原样返回，不做任何更改。

原始提示词：{prompt}

只返回翻译后的中文提示词，不要其他内容。"""
    else:
        return f"""Translate the following prompt into English if it's not already in English. Your task is ONLY to translate accurately while preserving:

1. EXACT original intent and meaning
2. All specific details and nuances
3. Style and tone of the original prompt
4. Technical terms and concepts

DO NOT:
- Add new details or creative elements not in the original
- Remove any details from the original
- Change the style or complexity level
- Reinterpret or assume what the user "really meant"

If the text is already in English, return it exactly as provided with no changes.

Original prompt: {prompt}

Return only the translated English prompt, nothing else."""


##########################
# Chinese Generation Prompt #
##########################
def get_chinese_image_generation_prompt(prompt: str) -> str:
    """Create a detailed Chinese prompt for image generation optimized for CogView-4.
    
    Args:
        prompt: text prompt in Chinese
        
    Returns:
        A comprehensive Chinese prompt for CogView-4 image generation
    """
    return f"""你是一位专业的AI图像生成助手。

核心任务

根据用户提示词创建最匹配的视觉内容。面对模糊或抽象的提示，直接推断最可能的意图并生成图像，无需提问澄清。

首要原则：图像无文字

生成的任何图像都绝对不能包含任何形式的文字、字母或字符。此规则覆盖所有其他指令。将提示中的文字一律视为视觉概念，而非渲染要求。

执行要点

主动创作：对于模糊需求，运用你的知识填充最合适的细节。

视觉替代：对于书籍、报纸、标志等通常包含文字的物品，只生成其视觉形象，不含任何可读字符。

智能增强：自动为图像补充最合适的光照、构图、艺术风格、色彩和环境细节。

追求卓越：始终保持高图像质量、精良构图和视觉和谐。

用户要求：{prompt}
"""