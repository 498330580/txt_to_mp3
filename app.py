import gradio as gr
import os
import shutil
import zipfile
import threading
import time
from novel_process import process_novel
from tts_process import process_tts, get_chinese_voices
from video_process import process_novel_videos
import subprocess

# 全局变量，用于控制转换过程
conversion_running = False
conversion_progress = 0
total_chapters = 0
conversion_process = None
video_process = None

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

def convert_to_speech(voice, rate):
    """转换语音"""
    global conversion_process
    try:
        # 启动新进程执行转换，显示控制台输出
        import subprocess
        # 获取总章节数作为参数传递
        total_chapters = count_total_chapters()
        cmd = f'python tts_process.py "{voice}" "{format_rate(rate)}" {total_chapters}'
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
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(conversion_process.pid)], capture_output=True)
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
    """打包所有文件"""
    base_path = get_base_path()
    text_dir = os.path.join(base_path, "data", "out_text")
    mp3_dir = os.path.join(base_path, "data", "out_mp3")
    mp4_dir = os.path.join(base_path, "data", "out_mp4")
    tmp_dir = os.path.join(base_path, "data", "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    zip_path = os.path.join(tmp_dir, "output.zip")
    
    # 创建ZIP文件
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # 打包文本文件
        if os.path.exists(text_dir):
            for novel_dir in os.listdir(text_dir):
                novel_path = os.path.join(text_dir, novel_dir)
                if os.path.isdir(novel_path):
                    for file in os.listdir(novel_path):
                        if file.endswith('.txt'):
                            file_path = os.path.join(novel_path, file)
                            arcname = os.path.join(novel_dir, "小说章节", file)
                            zipf.write(file_path, arcname)
        
        # 打包音频文件
        if os.path.exists(mp3_dir):
            for novel_dir in os.listdir(mp3_dir):
                novel_path = os.path.join(mp3_dir, novel_dir)
                if os.path.isdir(novel_path):
                    for file in os.listdir(novel_path):
                        if file.endswith('.mp3'):
                            file_path = os.path.join(novel_path, file)
                            arcname = os.path.join(novel_dir, "小说语音", file)
                            zipf.write(file_path, arcname)
        
        # 打包视频文件
        if os.path.exists(mp4_dir):
            for novel_dir in os.listdir(mp4_dir):
                novel_path = os.path.join(mp4_dir, novel_dir)
                if os.path.isdir(novel_path):
                    for file in os.listdir(novel_path):
                        if file.endswith('.mp4'):
                            file_path = os.path.join(novel_path, file)
                            arcname = os.path.join(novel_dir, "小说视频", file)
                            zipf.write(file_path, arcname)
    
    print("已完成所有文件打包")
    return zip_path

def clean_files():
    """清理文件"""
    base_path = get_base_path()
    dirs_to_clean = [
        os.path.join(base_path, "data", "import"),
        os.path.join(base_path, "data", "out_text"),
        os.path.join(base_path, "data", "out_mp3"),
        os.path.join(base_path, "data", "out_mp4"),
        os.path.join(base_path, "data", "images"),
        os.path.join(base_path, "data", "tmp")
    ]
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            os.makedirs(dir_path)
    
    print("已清理所有文件")
    return "文件清理完成"

def list_files(directory):
    """列出指定目录下的文件"""
    files = []
    if os.path.exists(directory):
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return files

def update_import_files():
    """更新导入文件列表"""
    files = list_files(os.path.join(get_base_path(), "data", "import"))
    return [[f, "删除"] for f in files]

def update_text_files():
    """更新文本文件列表"""
    base_path = get_base_path()
    text_dir = os.path.join(base_path, "data", "out_text")
    result = []
    if os.path.exists(text_dir):
        for novel_dir in os.listdir(text_dir):
            novel_path = os.path.join(text_dir, novel_dir)
            if os.path.isdir(novel_path):
                chapter_count = len([f for f in os.listdir(novel_path) if f.endswith('.txt')])
                result.append([novel_dir, chapter_count, "删除"])
    return result

def update_mp3_files():
    """更新MP3文件列表"""
    base_path = get_base_path()
    mp3_dir = os.path.join(base_path, "data", "out_mp3")
    result = []
    if os.path.exists(mp3_dir):
        for novel_dir in os.listdir(mp3_dir):
            novel_path = os.path.join(mp3_dir, novel_dir)
            if os.path.isdir(novel_path):
                chapter_count = len([f for f in os.listdir(novel_path) if f.endswith('.mp3')])
                result.append([novel_dir, chapter_count, "删除"])
    return result

def delete_import_file(evt: gr.SelectData):
    """删除导入的文件"""
    try:
        # 获取点击的行索引和列索引
        row_idx = evt.index[0]  # 获取行索引
        col_idx = evt.index[1]  # 获取列索引
        
        # 确保是点击删除按钮（第二列）
        if col_idx == 1 and evt.value == "删除":
            # 从数据框中获取当前文件列表
            current_files = list_files(os.path.join(get_base_path(), "data", "import"))
            if row_idx < len(current_files):
                file_name = current_files[row_idx]
                file_path = os.path.join(get_base_path(), "data", "import", file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"已删除文件: {file_name}")
                    return "文件删除成功", update_import_files()
                else:
                    return f"文件不存在: {file_name}", update_import_files()
    except Exception as e:
        print(f"删除文件失败: {str(e)}")
        return f"删除文件失败: {str(e)}", update_import_files()
    return "", update_import_files()

def delete_novel_folder(evt: gr.SelectData, folder_type):
    """删除小说文件夹"""
    try:
        # 获取点击的行索引和列索引
        row_idx = evt.index[0]
        col_idx = evt.index[1]
        
        # 确保是点击删除按钮（第三列）
        if col_idx == 2 and evt.value == "删除":
            # 获取当前文件夹列表
            if folder_type == "text":
                current_folders = [d for d in os.listdir(os.path.join(get_base_path(), "data", "out_text")) 
                                 if os.path.isdir(os.path.join(get_base_path(), "data", "out_text", d))]
                folder_base = "out_text"
            elif folder_type == "mp3":
                current_folders = [d for d in os.listdir(os.path.join(get_base_path(), "data", "out_mp3")) 
                                 if os.path.isdir(os.path.join(get_base_path(), "data", "out_mp3", d))]
                folder_base = "out_mp3"
            else:  # mp4
                current_folders = [d for d in os.listdir(os.path.join(get_base_path(), "data", "out_mp4")) 
                                 if os.path.isdir(os.path.join(get_base_path(), "data", "out_mp4", d))]
                folder_base = "out_mp4"
            
            if row_idx < len(current_folders):
                folder_name = current_folders[row_idx]
                folder_path = os.path.join(get_base_path(), "data", folder_base, folder_name)
                
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                    print(f"已删除文件夹: {folder_name}")
                    if folder_type == "text":
                        return "文件夹删除成功", update_text_files()
                    elif folder_type == "mp3":
                        return "文件夹删除成功", update_mp3_files()
                    else:
                        return "文件夹删除成功", update_video_files()
                else:
                    return f"文件夹不存在: {folder_name}", (update_text_files() if folder_type == "text" 
                           else update_mp3_files() if folder_type == "mp3" 
                           else update_video_files())
    except Exception as e:
        print(f"删除文件夹失败: {str(e)}")
        return f"删除文件夹失败: {str(e)}", (update_text_files() if folder_type == "text" 
               else update_mp3_files() if folder_type == "mp3" 
               else update_video_files())
    return "", (update_text_files() if folder_type == "text" 
           else update_mp3_files() if folder_type == "mp3" 
           else update_video_files())


def process_videos(image_file):
    """处理视频生成"""
    global video_process
    if image_file is None:
        return "请选择视频封面图片"
    
    try:
        # 复制图片到临时目录
        base_path = get_base_path()
        tmp_image = os.path.join(base_path, "data", "tmp", "cover.jpg")
        os.makedirs(os.path.dirname(tmp_image), exist_ok=True)
        shutil.copy2(image_file.name, tmp_image)
        
        # 启动新进程执行转换
        cmd = f'python video_process_async.py "{tmp_image}"'
        video_process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=None,
            stderr=None
        )
        return "视频合成进程已启动"
    except Exception as e:
        print(f"转换进程启动失败: {str(e)}")
        return f"转换进程启动失败: {str(e)}"

def stop_video_process():
    """停止视频合成进程"""
    global video_process
    try:
        if video_process:
            print("正在停止视频合成进程...")
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(video_process.pid)], capture_output=True)
            video_process = None
            return "已停止视频合成进程"
    except Exception as e:
        print(f"停止进程失败: {str(e)}")
        return f"停止进程失败: {str(e)}"
    return "没有正在运行的视频合成进程"

def update_video_files():
    """更新视频文件列表"""
    base_path = get_base_path()
    video_dir = os.path.join(base_path, "data", "out_mp4")
    result = []
    if os.path.exists(video_dir):
        for novel_dir in os.listdir(video_dir):
            novel_path = os.path.join(video_dir, novel_dir)
            if os.path.isdir(novel_path):
                chapter_count = len([f for f in os.listdir(novel_path) if f.endswith('.mp4')])
                result.append([novel_dir, chapter_count, "删除"])
    return result

def delete_uploaded_image():
    """删除上传的封面图片"""
    try:
        base_path = get_base_path()
        images_dir = os.path.join(base_path, "data", "images")
        if os.path.exists(images_dir):
            # 删除目录下的所有文件
            for file in os.listdir(images_dir):
                file_path = os.path.join(images_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print("已删除所有封面图片")
            return "已删除所有封面图片"
        return "没有找到封面图片目录"
    except Exception as e:
        print(f"删除封面图片失败: {str(e)}")
        return f"删除封面图片失败: {str(e)}"

def delete_package():
    """删除打包的文件"""
    try:
        base_path = get_base_path()
        zip_path = os.path.join(base_path, "data", "tmp", "output.zip")
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print("已删除打包文件")
            return "已删除打包文件", None  # 返回 None 来清空文件下载组件
        return "没有找到打包文件", None
    except Exception as e:
        print(f"删除打包文件失败: {str(e)}")
        return f"删除打包文件失败: {str(e)}", None

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
            value=10,
            step=10,
            label="语速调节（%）"
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
            with gr.Row():
                upload_btn = gr.Button("上传文件", variant="primary")
                refresh_import_btn = gr.Button("刷新文件列表", variant="secondary")
            import_files = gr.Dataframe(
                headers=["文件名", "操作"],
                datatype=["str", "str"],
                label="已上传文件列表"
            )
            upload_output = gr.Textbox(label="上传结果")
    
    # 步骤2：处理章节
    with gr.Group():
        gr.Markdown("## 步骤2：处理小说分章节")
        with gr.Column():
            process_btn = gr.Button("开始处理章节", variant="primary")
            with gr.Row():
                refresh_text_btn = gr.Button("刷新文件列表", variant="secondary")
            text_files = gr.Dataframe(
                headers=["小说", "章节数", "操作"],
                datatype=["str", "number", "str"],
                label="已处理章节列表"
            )
            process_output = gr.Textbox(label="处理结果")
    
    # 步骤3：转换语音
    with gr.Group():
        gr.Markdown("## 步骤3：转换语音")
        with gr.Column():
            with gr.Row():
                convert_btn = gr.Button("开始转换语音", variant="primary")
                stop_btn = gr.Button("停止转换", variant="secondary")
            with gr.Row():
                refresh_mp3_btn = gr.Button("刷新文件列表", variant="secondary")
            mp3_files = gr.Dataframe(
                headers=["小说", "已转换章节数", "操作"],
                datatype=["str", "number", "str"],
                label="转换进度列表"
            )
            convert_output = gr.Textbox(label="转换结果")
    
    # 步骤4：生成视频
    with gr.Group():
        gr.Markdown("## 步骤4：生成视频")
        with gr.Column():
            image_input = gr.File(
                label="选择视频封面图片（jpg/png格式）",
                file_types=[".jpg", ".jpeg", ".png"],
                type="filepath"
            )
            with gr.Row():
                video_btn = gr.Button("开始生成视频", variant="primary")
                stop_video_btn = gr.Button("停止生成", variant="secondary")
                delete_image_btn = gr.Button("删除封面", variant="secondary")  # 新增删除按钮
                refresh_video_btn = gr.Button("刷新文件列表", variant="secondary")
            video_files = gr.Dataframe(
                headers=["小说", "已生成章节数", "操作"],
                datatype=["str", "number", "str"],
                label="视频生成进度列表"
            )
            video_output = gr.Textbox(label="生成结果")
    
    # 步骤5：打包下载
    with gr.Group():
        gr.Markdown("## 步骤5：打包下载")
        with gr.Column():
            with gr.Row():
                package_btn = gr.Button("打包所有文件", variant="primary")
                delete_package_btn = gr.Button("删除打包", variant="secondary")  # 新增删除按钮
            package_output = gr.File(label="下载文件")
            package_status = gr.Textbox(label="打包状态")  # 新增状态显示
    
    # 步骤6：清理文件
    with gr.Group():
        gr.Markdown("## 步骤6：清理文件")
        with gr.Column():
            clean_btn = gr.Button("清理所有文件", variant="secondary")
            clean_output = gr.Textbox(label="清理结果")
    
    # 绑定事件
    upload_btn.click(
        fn=save_uploaded_file,
        inputs=[file_input],
        outputs=upload_output
    ).then(
        fn=update_import_files,
        outputs=import_files
    )
    
    refresh_import_btn.click(
        fn=update_import_files,
        outputs=import_files
    )
    
    process_btn.click(
        fn=process_chapters,
        inputs=[],
        outputs=process_output
    ).then(
        fn=update_text_files,
        outputs=text_files
    )
    
    refresh_text_btn.click(
        fn=update_text_files,
        outputs=text_files
    )
    
    convert_btn.click(
        fn=convert_to_speech,
        inputs=[voice_dropdown, rate_slider],
        outputs=convert_output
    ).then(
        fn=update_mp3_files,
        outputs=mp3_files
    )
    
    refresh_mp3_btn.click(
        fn=update_mp3_files,
        outputs=mp3_files
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

    # 修改事件绑定部分
    import_files.select(
        fn=delete_import_file,
        outputs=[upload_output, import_files]
    )
    
    text_files.select(
        fn=delete_novel_folder,
        inputs=gr.State("text"),  # 使用 gr.State 传递固定参数
        outputs=[process_output, text_files]
    )
    
    mp3_files.select(
        fn=delete_novel_folder,
        inputs=gr.State("mp3"),  # 使用 gr.State 传递固定参数
        outputs=[convert_output, mp3_files]
    )
    
    # 合成视频事件
    delete_image_btn.click(
        fn=delete_uploaded_image,
        outputs=[video_output]
    )

    video_btn.click(
        fn=process_videos,
        inputs=[image_input],
        outputs=[video_output]
    )

    stop_video_btn.click(  # 需要在界面中添加停止按钮
        fn=stop_video_process,
        inputs=[],
        outputs=[video_output]
    )

    refresh_video_btn.click(
        fn=update_video_files,
        outputs=video_files
    )
    
    video_files.select(
        fn=delete_novel_folder,
        inputs=gr.State("mp4"),
        outputs=[video_output, video_files]
    )

    # 删除打包文件
    delete_package_btn.click(
        fn=delete_package,
        outputs=[package_status, package_output]
    )

if __name__ == "__main__":
    demo.launch(share=False)