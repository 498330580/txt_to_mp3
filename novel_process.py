import os
import re
from ollama_api import is_chapter_title, extract_chapter_info

def get_base_path():
    """获取项目基础路径"""
    return os.path.dirname(os.path.abspath(__file__))

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

def identify_potential_titles(lines):
    """识别可能的章节标题行"""
    potential_titles = []
    for i, line in enumerate(lines):
        # 清理空格
        cleaned_line = line.strip()
        # 检查长度是否小于15个字
        if len(cleaned_line) > 0 and len(cleaned_line) <= 15:
            potential_titles.append((i, cleaned_line))
    return potential_titles

def split_chapters(content):
    """分割章节内容"""
    # 处理文本内容（去除空行和分隔符）
    cleaned_lines = process_content(content)
    
    # 识别可能的章节标题
    potential_titles = identify_potential_titles(cleaned_lines)
    
    # 使用 AI 识别真实的章节标题
    chapter_positions = []
    for pos, title in potential_titles:
        if is_chapter_title(title):
            chapter_info = extract_chapter_info(title)
            chapter_positions.append({
                'position': pos,
                'number': chapter_info['number'],
                'title': chapter_info['title']
            })
    
    # 分割章节
    chapters = []
    current_content = []
    
    # 处理内容简介
    if chapter_positions and chapter_positions[0]['position'] > 0:
        intro_content = cleaned_lines[:chapter_positions[0]['position']]
        if intro_content:
            chapters.append({
                'number': 0,
                'title': '内容简介',
                'content': '\n'.join(intro_content)
            })
    
    # 处理各个章节
    for i, chapter_pos in enumerate(chapter_positions):
        # 如果不是第一个章节，保存前一章节的内容
        if i > 0:
            prev_pos = chapter_positions[i-1]['position']
            chapters.append({
                'number': chapter_positions[i-1]['number'],
                'title': chapter_positions[i-1]['title'],
                'content': '\n'.join(cleaned_lines[prev_pos:chapter_pos['position']])
            })
        
        # 如果是最后一个章节
        if i == len(chapter_positions) - 1:
            chapters.append({
                'number': chapter_pos['number'],
                'title': chapter_pos['title'],
                'content': '\n'.join(cleaned_lines[chapter_pos['position']:])
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