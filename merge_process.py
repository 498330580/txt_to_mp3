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
    try:
        base_path = get_base_path()
        mp3_dir = os.path.join(base_path, "data", "out_mp3")
        merge_dir = os.path.join(base_path, "data", "out_mp3_merge")
        os.makedirs(merge_dir, exist_ok=True)
        
        # 获取ffmpeg路径
        ffmpeg_path = get_ffmpeg_path()
        if not os.path.exists(ffmpeg_path):
            print("错误：找不到ffmpeg程序")
            return
        
        # 遍历每个小说目录
        novel_dirs = [d for d in os.listdir(mp3_dir) if os.path.isdir(os.path.join(mp3_dir, d))]
        total_novels = len(novel_dirs)
        
        for novel_idx, novel_dir in enumerate(novel_dirs, 1):
            novel_path = os.path.join(mp3_dir, novel_dir)
            
            # 创建小说对应的合并目录和临时目录
            novel_merge_dir = os.path.join(merge_dir, novel_dir)
            novel_tmp_dir = os.path.join(novel_merge_dir, "tmp")
            os.makedirs(novel_merge_dir, exist_ok=True)
            os.makedirs(novel_tmp_dir, exist_ok=True)
            
            # 获取所有章节文件
            chapter_files = [f for f in os.listdir(novel_path) if f.endswith('.mp3')]
            chapter_files.sort()  # 按文件名排序
            total_chapters = len(chapter_files)
            
            print(f"\n开始处理第 {novel_idx}/{total_novels} 本小说：{novel_dir}")
            print(f"总章节数：{total_chapters}")
            
            # 检查是否存在00000章
            intro_file = next((f for f in chapter_files if f.startswith('00000')), None)
            if intro_file:
                # 移除00000章，后续单独处理
                chapter_files.remove(intro_file)
            
            # 处理每个分段
            start_idx = 0
            segment_count = 0
            while start_idx < len(chapter_files):
                # 确定当前分段的结束索引
                end_idx = min(start_idx + chapters_per_file, len(chapter_files))
                
                # 获取当前分段的文件
                current_files = chapter_files[start_idx:end_idx]
                segment_count += 1
                
                # 生成输出文件名（只使用序号）
                start_num = chapter_files[start_idx][:5]  # 获取起始章节的序号
                end_num = chapter_files[end_idx-1][:5]    # 获取结束章节的序号
                
                # 如果是第一个分段且存在00000章
                if intro_file and start_idx == 0:
                    # 先合并00001-00050
                    temp_output = os.path.join(novel_tmp_dir, f"temp_{start_num}-{end_num}.mp3")
                    final_output_name = f"00000-{end_num}.mp3"
                    temp_final_output = os.path.join(novel_tmp_dir, final_output_name)
                    final_output = os.path.join(novel_merge_dir, final_output_name)
                    
                    # 创建临时文件列表
                    list_file = os.path.join(novel_tmp_dir, "temp_list.txt")
                    with open(list_file, "w", encoding="utf-8") as f:
                        for file in current_files:
                            f.write(f"file '{os.path.join(novel_path, file)}'\n")
                    
                    # 合并00001-00050
                    print(f"\n正在合并：{start_num}-{end_num}")
                    cmd = f'"{ffmpeg_path}" -f concat -safe 0 -i "{list_file}" -c copy "{temp_output}"'
                    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"已完成合并：{start_num}-{end_num}")
                    
                    # 创建新的文件列表，包含00000章和临时文件
                    with open(list_file, "w", encoding="utf-8") as f:
                        f.write(f"file '{os.path.join(novel_path, intro_file)}'\n")
                        f.write(f"file '{temp_output}'\n")
                    
                    # 合并00000章和临时文件
                    print(f"\n正在合并：{final_output_name}")
                    cmd = f'"{ffmpeg_path}" -f concat -safe 0 -i "{list_file}" -c copy "{temp_final_output}"'
                    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    # 移动到最终位置
                    shutil.move(temp_final_output, final_output)
                    print(f"已完成合并：{final_output_name}")
                    
                    # 删除临时文件
                    os.remove(temp_output)
                    os.remove(list_file)
                else:
                    # 普通合并逻辑
                    output_name = f"{start_num}-{end_num}.mp3"
                    temp_output = os.path.join(novel_tmp_dir, output_name)
                    final_output = os.path.join(novel_merge_dir, output_name)
                    
                    # 创建临时文件列表
                    list_file = os.path.join(novel_tmp_dir, "temp_list.txt")
                    with open(list_file, "w", encoding="utf-8") as f:
                        for file in current_files:
                            f.write(f"file '{os.path.join(novel_path, file)}'\n")
                    
                    # 使用ffmpeg合并文件
                    print(f"\n正在合并：{output_name}")
                    cmd = f'"{ffmpeg_path}" -f concat -safe 0 -i "{list_file}" -c copy "{temp_output}"'
                    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    # 移动到最终位置
                    shutil.move(temp_output, final_output)
                    print(f"已完成合并：{output_name}")
                    
                    # 删除临时文件
                    os.remove(list_file)
                
                start_idx += chapters_per_file
            
            # 输出当前小说的处理进度
            print(f"\n小说《{novel_dir}》处理完成")
            print(f"总章节数：{total_chapters}，已合并为 {segment_count} 个文件")
            
            # 删除临时目录
            shutil.rmtree(novel_tmp_dir)
        
        print("\n所有音频合并完成")
    except Exception as e:
        print(f"合并音频失败: {str(e)}")

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