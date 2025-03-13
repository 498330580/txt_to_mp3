import os
import platform
import subprocess
import shutil  # 添加 shutil 模块导入
from typing import Optional

def get_base_path():
    """获取项目基础路径"""
    return os.path.dirname(os.path.abspath(__file__))

def get_ffmpeg_path() -> str:
    """获取 ffmpeg 可执行文件路径"""
    if platform.system() == 'Windows':
        return os.path.join(get_base_path(), 'ffmpeg', 'ffmpeg.exe')
    return 'ffmpeg'  # 其他系统直接使用系统安装的 ffmpeg

def create_video(mp3_path: str, image_path: str, output_path: str) -> Optional[str]:
    try:
        # 创建临时输出目录
        tmp_dir = os.path.join(os.path.dirname(output_path), "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        
        # 创建临时输出文件路径
        tmp_output = os.path.join(tmp_dir, os.path.basename(output_path))
        
        cmd = [
            get_ffmpeg_path(),
            '-loop', '1',
            '-i', image_path,
            '-i', mp3_path,
            '-c:v', 'h264',
            '-preset', 'medium',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            '-s', '1920x1080',
            '-y',
            tmp_output
        ]
        
        # 使用 CREATE_NO_WINDOW 标志来隐藏控制台窗口
        startupinfo = None
        if platform.system() == 'Windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        # 执行命令，使用 utf-8 编码
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 等待处理完成
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            # 如果失败，清理临时文件
            if os.path.exists(tmp_output):
                os.remove(tmp_output)
            return f"视频合成失败: {stderr}"
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 移动文件到最终位置
        shutil.move(tmp_output, output_path)
        print(f"完成视频合成: {os.path.basename(output_path)}")
        return None
        
    except Exception as e:
        # 确保清理临时文件
        if 'tmp_output' in locals() and os.path.exists(tmp_output):
            os.remove(tmp_output)
        return f"视频合成出错: {str(e)}"
    finally:
        # 清理空的临时目录
        if 'tmp_dir' in locals() and os.path.exists(tmp_dir) and not os.listdir(tmp_dir):
            os.rmdir(tmp_dir)

def process_novel_videos(novel_name: str) -> tuple[int, Optional[str]]:
    """
    处理指定小说的所有章节视频合成
    
    Args:
        novel_name: 小说名称
        
    Returns:
        tuple[int, Optional[str]]: (处理的章节数, 错误信息如果有)
    """
    base_path = get_base_path()
    mp3_dir = os.path.join(base_path, "data", "out_mp3", novel_name)
    out_dir = os.path.join(base_path, "data", "out_mp4", novel_name)
    
    # 检查所有支持的图片格式
    supported_formats = ['.jpg', '.jpeg', '.png']
    image_path = None
    
    for ext in supported_formats:
        temp_path = os.path.join(base_path, "data", "images", f"{novel_name}{ext}")
        if os.path.exists(temp_path):
            image_path = temp_path
            break
    
    if not image_path:
        return 0, f"找不到小说封面图片: {novel_name}"
    
    if not os.path.exists(mp3_dir):
        return 0, f"找不到小说音频目录: {novel_name}"
    
    try:
        processed_count = 0
        total_files = len([f for f in os.listdir(mp3_dir) if f.endswith('.mp3')])
        
        for mp3_file in os.listdir(mp3_dir):
            if not mp3_file.endswith('.mp3'):
                continue
                
            chapter_name = mp3_file[:-4]  # 移除 .mp3 后缀
            mp3_path = os.path.join(mp3_dir, mp3_file)
            mp4_path = os.path.join(out_dir, f"{chapter_name}.mp4")
            
            # 检查是否已经处理过
            if os.path.exists(mp4_path):
                processed_count += 1
                print(f"跳过已处理章节: {chapter_name}")
                continue
            
            print(f"正在处理章节 [{processed_count + 1}/{total_files}]: {chapter_name}")
            error = create_video(mp3_path, image_path, mp4_path)
            
            if error:
                return processed_count, error
            
            processed_count += 1
            
        # 处理完成后删除图片
        if os.path.exists(image_path):
            os.remove(image_path)
            
        return processed_count, None
        
    except Exception as e:
        return processed_count, f"处理视频时出错: {str(e)}"