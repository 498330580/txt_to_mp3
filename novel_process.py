import os
import re
import json
from typing import List, Tuple, Dict, Optional

def get_base_path() -> str:
    """获取项目根目录"""
    return os.path.dirname(os.path.abspath(__file__))

def chinese_to_arabic(chinese_str: str) -> int:
    """将中文数字转换为阿拉伯数字"""
    chinese_nums = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        '十': 10, '百': 100, '千': 1000, '万': 10000
    }
    
    result = 0
    temp = 0
    
    for char in chinese_str:
        if char in chinese_nums:
            num = chinese_nums[char]
            if num >= 10:
                if temp == 0:
                    temp = 1
                result += temp * num
                temp = 0
            else:
                temp = num
                
    if temp > 0:
        result += temp
        
    return result

def traditional_to_arabic(traditional_str: str) -> int:
    """将繁体数字转换为阿拉伯数字"""
    traditional_nums = {
        '零': 0, '壹': 1, '贰': 2, '叁': 3, '肆': 4,
        '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9,
        '拾': 10, '佰': 100, '仟': 1000, '萬': 10000
    }
    
    result = 0
    temp = 0
    
    for char in traditional_str:
        if char in traditional_nums:
            num = traditional_nums[char]
            if num >= 10:
                if temp == 0:
                    temp = 1
                result += temp * num
                temp = 0
            else:
                temp = num
                
    if temp > 0:
        result += temp
        
    return result

def load_chapter_patterns() -> List[Tuple[str, str]]:
    """从配置文件加载章节识别模式"""
    config_path = os.path.join(get_base_path(), "data", "config", "config.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            patterns = config.get('chapter_patterns', [])
            return [(p['pattern'], p['description']) for p in patterns]
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        # 返回默认模式
        return [
            (r'^第([0-9零一二三四五六七八九十百千万]+)章.*', '数字/中文数字'),
            (r'^第([壹贰叁肆伍陆柒捌玖拾佰仟萬]+)章.*', '繁体数字')
        ]

def extract_chapter_number(title: str) -> Optional[int]:
    """从章节标题中提取章节号"""
    patterns = load_chapter_patterns()
    for pattern, _ in patterns:
        match = re.match(pattern, title)
        if match:
            num_str = match.group(1)
            # 转换中文数字为阿拉伯数字
            if any(c in num_str for c in '零一二三四五六七八九十百千万'):
                return chinese_to_arabic(num_str)
            # 转换繁体数字为阿拉伯数字
            elif any(c in num_str for c in '壹贰叁肆伍陆柒捌玖拾佰仟萬'):
                return traditional_to_arabic(num_str)
            # 直接返回阿拉伯数字
            else:
                return int(num_str)
    return None

def get_novel_files():
    """获取导入目录下的所有txt文件"""
    import_path = os.path.join(get_base_path(), "data", "import")
    novel_files = []
    for file in os.listdir(import_path):
        if file.endswith('.txt'):
            novel_files.append({
                'name': file,
                'path': os.path.join(import_path, file)
            })
    return novel_files

def detect_encoding(file_path):
    """检测文件编码"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except UnicodeDecodeError:
            continue
    return None

def process_content(content):
    """处理文本内容"""
    # 1. 去除空行
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # 2. 清理分隔符行，替换为单个回车
    cleaned_lines = []
    punctuation_marks = set('-=*~#@$%^&_+<>.,;:!?/\\|')
    
    for line in lines:
        # 检查是否是分隔符行
        first_char = line[0]
        if (first_char in punctuation_marks and 
            len(line) >= 5 and 
            all(c == first_char for c in line)):
            # 遇到分隔符行时添加一个空字符串，join时会转换为单个回车
            cleaned_lines.append('')
            continue
        cleaned_lines.append(line)
    
    return cleaned_lines

def get_chapter_info(line):
    """识别章节标题和章节号"""
    number = extract_chapter_number(line)
    if number is not None:
        return number, line
    
    return None, None

def split_chapters(content):
    """分割章节内容"""
    # 处理文本内容（去除空行和分隔符）
    cleaned_lines = process_content(content)
    
    # 查找所有章节标题
    chapters = []
    current_content = []
    current_title = None
    current_number = None
    intro_content = []
    used_numbers = set()  # 用于记录已使用的章节号
    
    for line in cleaned_lines:
        # 查找章节标题
        number, title = get_chapter_info(line)
        if number is not None:
            # 检查章节号是否已使用
            if number in used_numbers:
                # 如果章节号已使用，将内容添加到当前章节
                if current_title:
                    current_content.append(line)
                continue
                
            used_numbers.add(number)  # 记录已使用的章节号
            
            # 如果有内容简介，先保存为第一章
            if intro_content and not chapters:
                chapters.append({
                    'number': 0,
                    'title': '内容简介',
                    'content': '\n'.join(intro_content)
                })
            
            # 如果已有章节内容，保存前一章节
            if current_title and current_content:
                chapters.append({
                    'number': current_number,
                    'title': current_title,
                    'content': '\n'.join(current_content)
                })
            
            # 开始新章节
            current_title = title
            current_number = number
            current_content = [line]
        else:
            # 如果还没遇到第一个章节标题，就是内容简介
            if not current_title:
                if line.strip():  # 只添加非空行
                    intro_content.append(line)
            else:
                current_content.append(line)
    
    # 保存最后一章
    if current_title and current_content:
        chapters.append({
            'number': current_number,
            'title': current_title,
            'content': '\n'.join(current_content)
        })
    
    return chapters

def process_novel():
    """处理小说文件的主函数"""
    novels = get_novel_files()
    processed_count = 0
    
    for novel in novels:
        try:
            # 检测文件编码
            encoding = detect_encoding(novel['path'])
            if not encoding:
                print(f"无法识别文件编码: {novel['name']}")
                continue
                
            # 读取小说内容
            with open(novel['path'], 'r', encoding=encoding) as f:
                content = f.read()
            
            # 分割章节
            chapters = split_chapters(content)
            
            # 保存章节
            save_chapters(novel['name'], chapters)
            processed_count += 1
            
        except Exception as e:
            print(f"处理文件失败 {novel['name']}: {str(e)}")
            continue
    
    return processed_count

def save_chapters(novel_name, chapters):
    """保存分割后的章节"""
    # 使用绝对路径
    base_path = get_base_path()
    output_dir = os.path.join(base_path, "data", "out_text", novel_name.replace('.txt', ''))
    
    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存每个章节
    for chapter in chapters:
        # 清理文件名中的非法字符
        title = re.sub(r'[<>:"/\\|?*]', '_', chapter['title'])
        # 使用五位数字格式化章节号
        filename = f"{chapter['number']:05d}.{title}.txt"
        filepath = os.path.join(output_dir, filename)
        
        # 确保父目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(chapter['content'])