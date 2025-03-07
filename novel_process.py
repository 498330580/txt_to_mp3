import os
import re

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

def split_chapters(content):
    """分割章节内容"""
    # 使用正则表达式匹配分隔符
    separators = [r'-+\n', r'\*+\n']
    # 合并所有分隔符模式
    pattern = '|'.join(separators)
    
    # 分割内容
    chapters = re.split(pattern, content)
    # 去除空白章节
    chapters = [ch.strip() for ch in chapters if ch.strip()]
    
    # 提取章节信息
    processed_chapters = []
    for chapter in chapters:
        # 查找章节标题
        match = re.search(r'第\d+章.*?\n', chapter)
        if match:
            title = match.group().strip()
            # 提取章节号
            num_match = re.search(r'第(\d+)章', title)
            if num_match:
                chapter_num = int(num_match.group(1))
                processed_chapters.append({
                    'number': chapter_num,
                    'title': title,
                    'content': chapter.strip()
                })
    
    return processed_chapters

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
        filename = f"{chapter['number']}.{title}.txt"
        filepath = os.path.join(output_dir, filename)
        
        # 确保父目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(chapter['content'])

def process_novel():
    """处理小说文件的主函数"""
    novels = get_novel_files()
    for novel in novels:
        # 读取小说内容
        with open(novel['path'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割章节
        chapters = split_chapters(content)
        
        # 保存章节
        save_chapters(novel['name'], chapters)
    
    return len(novels)