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
            
            # 按章节号排序
            audio_files.sort()
            
            # 情况一：如果只有一个音频文件，直接复制
            if len(audio_files) == 1:
                src_file = os.path.join(novel_path, audio_files[0])
                dst_file = os.path.join(novel_merge_dir, audio_files[0])
                shutil.copy2(src_file, dst_file)
                print(f"已复制单个音频文件: {audio_files[0]}")
                continue
            
            # 情况二：如果有两个音频文件，直接合并
            if len(audio_files) == 2:
                start_chapter = audio_files[0].split('.')[0]
                end_chapter = audio_files[1].split('.')[0]
                output_name = f"{start_chapter}-{end_chapter}.mp3"
                
                print(f"正在合成：{start_chapter}-{end_chapter}")
                
                # 创建临时文件列表
                temp_list = os.path.join(tmp_dir, "temp_list.txt")
                with open(temp_list, 'w', encoding='utf-8') as f:
                    for file in audio_files:
                        f.write(f"file '{os.path.join(novel_path, file)}'\n")
                
                # 合并音频文件
                temp_output = os.path.join(tmp_dir, output_name)
                final_output = os.path.join(novel_merge_dir, output_name)
                
                subprocess.run([
                    get_ffmpeg_path(),
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', temp_list,
                    '-c', 'copy',
                    temp_output
                ], capture_output=True)
                
                shutil.move(temp_output, final_output)
                print(f"合成完成：{start_chapter}-{end_chapter}")
                continue
            
            # 情况三：如果有多个音频文件
            # 检查是否存在00000文件（内容简介）
            intro_file = '00000.内容简介.mp3'
            if intro_file in audio_files:
                # 从音频文件列表中移除00000文件
                audio_files.remove(intro_file)
                # 第一步：合并第一个批次的文件（00001-00050）
                first_batch = audio_files[:chapters_per_file]
                if not first_batch:
                    continue
                
                # 获取第一个批次的起始和结束章节号
                start_chapter = first_batch[0].split('.')[0]
                end_chapter = first_batch[-1].split('.')[0]
                temp_output = os.path.join(tmp_dir, f"temp_{start_chapter}-{end_chapter}.mp3")
                
                print(f"正在合成：{start_chapter}-{end_chapter}")
                
                # 创建临时文件列表
                temp_list = os.path.join(tmp_dir, "temp_list.txt")
                with open(temp_list, 'w', encoding='utf-8') as f:
                    for file in first_batch:
                        f.write(f"file '{os.path.join(novel_path, file)}'\n")
                
                # 合并第一个批次的文件
                subprocess.run([
                    get_ffmpeg_path(),
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', temp_list,
                    '-c', 'copy',
                    temp_output
                ], capture_output=True)
                
                print(f"合成完成：{start_chapter}-{end_chapter}")
                
                # 第二步：将00000章节合并到第一段之前
                final_output = os.path.join(novel_merge_dir, f"{intro_file.split('.')[0]}-{end_chapter}.mp3")
                
                print(f"正在合成：{intro_file.split('.')[0]}-{end_chapter}")
                
                # 创建新的临时文件列表，先放00000，再放临时文件
                temp_list = os.path.join(tmp_dir, "final_list.txt")
                with open(temp_list, 'w', encoding='utf-8') as f:
                    f.write(f"file '{os.path.join(novel_path, intro_file)}'\n")
                    f.write(f"file '{temp_output}'\n")
                
                # 合并00000和临时文件
                subprocess.run([
                    get_ffmpeg_path(),
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', temp_list,
                    '-c', 'copy',
                    final_output
                ], capture_output=True)
                
                print(f"合成完成：{intro_file.split('.')[0]}-{end_chapter}")
                
                # 第三步：处理剩余的文件（00051-00100等）
                remaining_files = audio_files[chapters_per_file:]
                if remaining_files:
                    for i in range(0, len(remaining_files), chapters_per_file):
                        batch_files = remaining_files[i:i + chapters_per_file]
                        if not batch_files:
                            continue
                            
                        start_chapter = batch_files[0].split('.')[0]
                        end_chapter = batch_files[-1].split('.')[0]
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
                        
                        subprocess.run([
                            get_ffmpeg_path(),
                            '-f', 'concat',
                            '-safe', '0',
                            '-i', temp_list,
                            '-c', 'copy',
                            temp_output
                        ], capture_output=True)
                        
                        shutil.move(temp_output, final_output)
                        print(f"合成完成：{start_chapter}-{end_chapter}")
            else:
                # 如果没有00000文件，按照现有规则合并
                for i in range(0, len(audio_files), chapters_per_file):
                    batch_files = audio_files[i:i + chapters_per_file]
                    if not batch_files:
                        continue
                        
                    start_chapter = batch_files[0].split('.')[0]
                    end_chapter = batch_files[-1].split('.')[0]
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
                    
                    subprocess.run([
                        get_ffmpeg_path(),
                        '-f', 'concat',
                        '-safe', '0',
                        '-i', temp_list,
                        '-c', 'copy',
                        temp_output
                    ], capture_output=True)
                    
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