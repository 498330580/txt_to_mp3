import gradio as gr
import os
import shutil
import zipfile
import threading
import time
from novel_process import process_novel
from tts_process import process_tts, get_chinese_voices

# 全局变量，用于控制转换过程
conversion_running = False
conversion_progress = 0
total_chapters = 0
# 添加新的全局变量
conversion_process = None

def get_base_path():
    """获取项目基础路径"""
    return os.path.dirname(os.path.abspath(__file__))

def format_rate(rate):
    """格式化语速值"""
    if rate == 0:
        return "+0%"
    return f"{'+' if rate >= 0 else ''}{rate}%"

def save_uploaded_file(file):
    """保存上传的文件"""
    if file is None:
        return "请选择要上传的小说文件"
    
    import_dir = os.path.join(get_base_path(), "data", "import")
    os.makedirs(import_dir, exist_ok=True)
    
    try:
        file_path = os.path.join(import_dir, os.path.basename(file.name))
        shutil.copy2(file.name, file_path)
        print(f"已上传文件: {os.path.basename(file.name)}")
        return "文件上传成功"
    except Exception as e:
        print(f"文件上传失败: {str(e)}")
        return f"文件上传失败: {str(e)}"

def process_chapters():
    """处理小说分章节"""
    novel_count = process_novel()
    print(f"已处理 {novel_count} 本小说的章节分割")
    return f"章节处理完成，共处理 {novel_count} 本小说"

def count_total_chapters():
    """计算总章节数"""
    base_path = get_base_path()
    text_dir = os.path.join(base_path, "data", "out_text")
    count = 0
    
    if os.path.exists(text_dir):
        for novel_dir in os.listdir(text_dir):
            novel_path = os.path.join(text_dir, novel_dir)
            if os.path.isdir(novel_path):
                count += len([f for f in os.listdir(novel_path) if f.endswith('.txt')])
    
    return count
# 删除全局变量 conversion_running
conversion_progress = 0
total_chapters = 0
# 删除 update_progress 函数
def convert_to_speech(voice, rate, generate_subtitle):
    """转换语音"""
    global conversion_process
    try:
        # 启动新进程执行转换，显示控制台输出
        import subprocess
        cmd = f'python tts_process.py "{voice}" "{format_rate(rate)}" "{str(generate_subtitle)}"'
        conversion_process = subprocess.Popen(
            cmd, 
            shell=True,
            stdout=None,
            stderr=None
        )
        return "语音转换进程已启动"
    except Exception as e:
        print(f"转换进程启动失败: {str(e)}")
        return f"转换进程启动失败: {str(e)}"

def stop_conversion():
    """停止转换进程"""
    global conversion_process
    try:
        if conversion_process:
            print("正在停止转换进程...")
            # 在 Windows 上使用 taskkill 强制终止进程及其子进程
            import subprocess
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(conversion_process.pid)], 
                         capture_output=True)
            conversion_process = None
            print("转换进程已停止")
            return "已停止转换进程"
    except Exception as e:
        print(f"停止进程失败: {str(e)}")
        return f"停止进程失败: {str(e)}"
    return "没有正在运行的转换进程"
    try:
        chapter_count = process_tts(voice, format_rate(rate))
        print(f"已转换 {chapter_count} 个章节的语音")
        return f"语音转换完成，共转换 {chapter_count} 个章节"
    except Exception as e:
        print(f"转换过程出错: {str(e)}")
        return f"转换过程出错: {str(e)}"
# 删除 stop_conversion 函数
def package_audio():
    """打包音频文件"""
    base_path = get_base_path()
    mp3_dir = os.path.join(base_path, "data", "out_mp3")
    tmp_dir = os.path.join(base_path, "data", "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    zip_path = os.path.join(tmp_dir, "output.zip")
    
    # 创建ZIP文件
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(mp3_dir):
            # 跳过 tmp 目录
            if "tmp" in root.split(os.sep):
                continue
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, mp3_dir)
                zipf.write(file_path, arcname)
    
    print("已完成音频文件打包")
    return zip_path
def clean_files():
    """清理文件"""
    base_path = get_base_path()
    dirs_to_clean = [
        os.path.join(base_path, "data", "import"),
        os.path.join(base_path, "data", "out_text"),
        os.path.join(base_path, "data", "out_mp3"),
        os.path.join(base_path, "data", "tmp")
    ]
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            os.makedirs(dir_path)
    
    print("已清理所有文件")
    return "文件清理完成"
# 创建Gradio界面
with gr.Blocks(title="小说文本转语音工具") as demo:
    gr.Markdown("# 小说文本转语音工具")
    
    with gr.Row():
        voice_dropdown = gr.Dropdown(
            choices=get_chinese_voices(),
            value="zh-CN-YunxiNeural",
            label="选择语音"
        )
        rate_slider = gr.Slider(
            minimum=-50,
            maximum=50,
            value=0,
            step=10,
            label="语速调节（%）"
        )
        subtitle_checkbox = gr.Checkbox(
            label="输出字幕文件",
            value=False
        )
    
    # 步骤1：上传文件
    with gr.Group():
        gr.Markdown("## 步骤1：上传小说文件")
        with gr.Column():
            file_input = gr.File(
                label="选择小说文件（txt格式）",
                file_types=[".txt"],
                type="filepath"
            )
            upload_btn = gr.Button("上传文件", variant="primary")
            upload_output = gr.Textbox(label="上传结果")
    
    # 步骤2：处理章节
    with gr.Group():
        gr.Markdown("## 步骤2：处理小说分章节")
        with gr.Column():
            process_btn = gr.Button("开始处理章节", variant="primary")
            process_output = gr.Textbox(label="处理结果")
    
    # 步骤3：转换语音
    with gr.Group():
        gr.Markdown("## 步骤3：转换语音")
        with gr.Column():
            with gr.Row():
                convert_btn = gr.Button("开始转换语音", variant="primary")
                stop_btn = gr.Button("停止转换", variant="secondary")
            convert_output = gr.Textbox(label="转换结果")
    
    # 步骤4：打包下载
    with gr.Group():
        gr.Markdown("## 步骤4：打包下载")
        with gr.Column():
            package_btn = gr.Button("打包音频文件", variant="primary")
            package_output = gr.File(label="下载文件")
    
    # 步骤5：清理文件
    with gr.Group():
        gr.Markdown("## 步骤5：清理文件")
        with gr.Column():
            clean_btn = gr.Button("清理所有文件", variant="secondary")
            clean_output = gr.Textbox(label="清理结果")
    
    # 绑定事件
    upload_btn.click(
        fn=save_uploaded_file,
        inputs=[file_input],
        outputs=upload_output
    )
    
    process_btn.click(
        fn=process_chapters,
        inputs=[],
        outputs=process_output
    )
    
    convert_btn.click(
        fn=convert_to_speech,
        inputs=[voice_dropdown, rate_slider, subtitle_checkbox],
        outputs=convert_output
    )
    
    stop_btn.click(
        fn=stop_conversion,
        inputs=[],
        outputs=convert_output
    )
    
    package_btn.click(
        fn=package_audio,
        inputs=[],
        outputs=package_output
    )
    
    clean_btn.click(
        fn=clean_files,
        inputs=[],
        outputs=clean_output
    )
if __name__ == "__main__":
    # demo.launch()
    demo.launch(share=False)