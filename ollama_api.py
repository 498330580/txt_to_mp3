import requests
import json

def is_chapter_title(text):
    """使用 Ollama API 判断是否为章节标题"""
    url = "http://localhost:11434/api/generate"
    
    prompt = f"""请判断下面这段文字是否为小说章节标题（只返回 true 或 false）：
    {text}
    
    判断依据：
    1. 一般包含"章"、"节"、"卷"等字样
    2. 可能包含数字编号
    3. 一般较短（不超过15个字）
    4. 往往是独立成段的短句
    """
    
    data = {
        "model": "qwen2.5:3b",  # 使用中文模型
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        response_text = result.get('response', '').strip().lower()
        print(response_text)
        return response_text == 'true'
    except Exception as e:
        print(f"Ollama API 调用失败: {str(e)}")
        return False

def extract_chapter_info(text):
    """使用 Ollama API 提取章节信息"""
    url = "http://localhost:11434/api/generate"
    
    prompt = f"""请从以下文本中提取章节信息，返回 JSON 格式：
    {text}
    
    要求：
    1. 提取章节编号（数字）
    2. 提取章节标题
    3. 如果无法提取编号，返回-1
    
    返回格式：
    {{"number": 章节编号, "title": "完整标题"}}
    """
    
    data = {
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        chapter_info = json.loads(result.get('response', '{}'))
        print(chapter_info)
        return chapter_info
    except Exception as e:
        print(f"Ollama API 提取章节信息失败: {str(e)}")
        return {"number": -1, "title": text}