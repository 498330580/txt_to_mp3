import os
import sys
import subprocess
import shutil

def get_base_path():
    """获取项目基础路径"""
    return os.path.dirname(os.path.abspath(__file__))

def get_ffmpeg_path():
    """获取ffmpeg路径"""
    base_path = get_base_path()
    return os.path.join(base_path, "ffmpeg", "ffmpeg.exe")

def merge_audio_files(chapters_per_file):
    """合并音频文件"""
    # 使用绝对路径
    base_path = get_base_path()
    mp3_dir = os.path.join(base_path, "data", "out_mp3")
    merge_dir = os.path.join(base_path, "data", "out_mp3_merge")
    
    # 确保合并目录存在
    os.makedirs(merge_dir, exist_ok=True)
    
    # 获取所有小说目录
    novel_dirs = [d for d in os.listdir(mp3_dir) if os.path.isdir(os.path.join(mp3_dir, d))]
    
    for novel_dir in novel_dirs:
        try:
            print(f"\n正在处理小说：{novel_dir}")
            novel_mp3_dir = os.path.join(mp3_dir, novel_dir)
            novel_merge_dir = os.path.join(merge_dir, novel_dir)
            
            # 确保小说合并目录存在
            os.makedirs(novel_merge_dir, exist_ok=True)
            
            # 获取所有mp3文件
            mp3_files = [f for f in os.listdir(novel_mp3_dir) if f.endswith('.mp3')]
            mp3_files.sort()  # 按文件名排序
            
            if not mp3_files:
                print(f"未找到音频文件: {novel_dir}")
                continue
                
            # 如果只有一个文件，直接复制
            if len(mp3_files) == 1:
                src_file = os.path.join(novel_mp3_dir, mp3_files[0])
                dst_file = os.path.join(novel_merge_dir, mp3_files[0])
                shutil.copy2(src_file, dst_file)
                print(f"单章节文件，已直接复制：{mp3_files[0]}")
                continue
            
            # 创建小说对应的临时目录
            novel_tmp_dir = os.path.join(novel_merge_dir, "tmp")
            os.makedirs(novel_tmp_dir, exist_ok=True)
            
            try:
                # 检查是否存在00000文件
                intro_file = next((f for f in mp3_files if f.startswith('00000')), None)
                if intro_file:
                    # 移除00000文件，后续单独处理
                    mp3_files.remove(intro_file)
                
                # 处理每个分段
                start_idx = 0
                while start_idx < len(mp3_files):
                    # 确定当前分段的结束索引
                    end_idx = min(start_idx + chapters_per_file, len(mp3_files))
                    
                    # 获取当前分段的文件
                    current_files = mp3_files[start_idx:end_idx]
                    
                    # 生成输出文件名
                    start_num = current_files[0][:5]  # 获取起始章节的序号
                    end_num = current_files[-1][:5]   # 获取结束章节的序号
                    output_name = f"{start_num}-{end_num}.mp3"
                    
                    # 创建临时文件列表
                    list_file = os.path.join(novel_tmp_dir, "temp_list.txt")
                    with open(list_file, 'w', encoding='utf-8') as f:
                        for file in current_files:
                            f.write(f"file '{os.path.join(novel_mp3_dir, file)}'\n")
                    
                    # 合并文件到临时目录
                    temp_output = os.path.join(novel_tmp_dir, output_name)
                    subprocess.run([
                        'ffmpeg', '-f', 'concat', '-safe', '0',
                        '-i', list_file, '-c', 'copy',
                        temp_output
                    ], capture_output=True)
                    
                    # 移动到最终位置
                    final_output = os.path.join(novel_merge_dir, output_name)
                    shutil.move(temp_output, final_output)
                    
                    print(f"已合并: {output_name}")
                    start_idx += chapters_per_file
                
                # 如果存在00000文件，最后处理
                if intro_file:
                    # 创建新的文件列表，包含所有合并后的文件和00000文件
                    final_list_file = os.path.join(novel_tmp_dir, "final_list.txt")
                    with open(final_list_file, 'w', encoding='utf-8') as f:
                        f.write(f"file '{os.path.join(novel_mp3_dir, intro_file)}'\n")
                        # 添加所有合并后的文件
                        for file in os.listdir(novel_merge_dir):
                            if file.endswith('.mp3'):
                                f.write(f"file '{os.path.join(novel_merge_dir, file)}'\n")
                    
                    # 合并到临时目录
                    temp_output = os.path.join(novel_tmp_dir, intro_file)
                    subprocess.run([
                        'ffmpeg', '-f', 'concat', '-safe', '0',
                        '-i', final_list_file, '-c', 'copy',
                        temp_output
                    ], capture_output=True)
                    
                    # 移动到最终位置
                    final_output = os.path.join(novel_merge_dir, intro_file)
                    shutil.move(temp_output, final_output)
                    
                    print(f"已处理: {intro_file}")
                
                print(f"小说 {novel_dir} 处理完成")
                
            finally:
                # 清理临时目录
                if os.path.exists(novel_tmp_dir):
                    shutil.rmtree(novel_tmp_dir)
                    
        except Exception as e:
            print(f"处理小说失败 {novel_dir}: {str(e)}")
            continue

if __name__ == "__main__":
    # 获取命令行参数
    if len(sys.argv) > 1:
        try:
            chapters_per_file = int(sys.argv[1])
            merge_audio_files(chapters_per_file)
        except ValueError:
            print(f"参数错误: {sys.argv[1]} 不是一个有效的整数")
    else:
        print("请提供每段章节数参数") 