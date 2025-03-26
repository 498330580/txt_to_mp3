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
        
        if not os.path.exists(mp3_dir):
            print("没有找到音频文件目录")
            return
            
        # 遍历每个小说目录
        for novel_dir in os.listdir(mp3_dir):
            novel_path = os.path.join(mp3_dir, novel_dir)
            if not os.path.isdir(novel_path):
                continue
                
            print(f"\n处理小说: {novel_dir}")
            
            # 创建小说对应的合并目录
            novel_merge_dir = os.path.join(merge_dir, novel_dir)
            os.makedirs(novel_merge_dir, exist_ok=True)
            
            # 创建临时目录
            tmp_dir = os.path.join(novel_merge_dir, "tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            
            # 获取所有音频文件
            audio_files = [f for f in os.listdir(novel_path) if f.endswith('.mp3')]
            if not audio_files:
                print(f"小说 {novel_dir} 没有音频文件")
                continue
                
            # 如果只有一个音频文件，直接复制
            if len(audio_files) == 1:
                src_file = os.path.join(novel_path, audio_files[0])
                dst_file = os.path.join(novel_merge_dir, audio_files[0])
                shutil.copy2(src_file, dst_file)
                print(f"已复制单个音频文件: {audio_files[0]}")
                continue
            
            # 处理多个音频文件
            # 首先处理00000文件（内容简介）
            intro_file = "00000.mp3"
            if intro_file in audio_files:
                audio_files.remove(intro_file)
                src_file = os.path.join(novel_path, intro_file)
                dst_file = os.path.join(novel_merge_dir, intro_file)
                shutil.copy2(src_file, dst_file)
                print(f"已复制内容简介: {intro_file}")
            
            # 按章节号排序
            audio_files.sort()
            
            # 分批合并文件
            for i in range(0, len(audio_files), chapters_per_file):
                batch_files = audio_files[i:i + chapters_per_file]
                if not batch_files:
                    continue
                    
                # 获取当前批次的起始和结束章节号
                start_chapter = batch_files[0].split('.')[0]  # 只取章节序号部分
                end_chapter = batch_files[-1].split('.')[0]   # 只取章节序号部分
                output_name = f"{start_chapter}-{end_chapter}.mp3"
                
                print(f"正在合成：{start_chapter}-{end_chapter}")
                
                # 创建临时文件列表
                temp_list = os.path.join(tmp_dir, "temp_list.txt")
                with open(temp_list, 'w', encoding='utf-8') as f:
                    for file in batch_files:
                        f.write(f"file '{os.path.join(novel_path, file)}'\n")
                
                # 合并音频文件
                temp_output = os.path.join(tmp_dir, output_name)
                final_output = os.path.join(novel_merge_dir, output_name)
                
                # 使用ffmpeg合并音频
                subprocess.run([
                    get_ffmpeg_path(),
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', temp_list,
                    '-c', 'copy',
                    temp_output
                ], capture_output=True)
                
                # 移动合并后的文件到最终位置
                shutil.move(temp_output, final_output)
                print(f"合成完成：{start_chapter}-{end_chapter}")
            
            # 清理临时目录
            shutil.rmtree(tmp_dir)
            
        print("\n所有小说处理完成")
    except Exception as e:
        print(f"合并音频文件时出错: {str(e)}")
        raise

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