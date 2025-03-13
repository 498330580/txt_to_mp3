import os
import sys
import shutil
from video_process import process_novel_videos, get_base_path

def main():
    if len(sys.argv) != 2:
        print("Usage: python video_process_async.py <image_path>")
        return
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"图片文件不存在: {image_path}")
        return
    
    base_path = get_base_path()
    mp3_dir = os.path.join(base_path, "data", "out_mp3")
    
    try:
        # 确保目录存在
        os.makedirs(os.path.join(base_path, "data", "images"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "data", "out_mp4"), exist_ok=True)
        
        # 处理每个小说文件夹
        success_count = 0
        for novel_name in os.listdir(mp3_dir):
            if not os.path.isdir(os.path.join(mp3_dir, novel_name)):
                continue
            
            # 复制并重命名图片
            novel_image = os.path.join(base_path, "data", "images", f"{novel_name}.jpg")
            shutil.copy2(image_path, novel_image)
            
            # 处理视频生成
            processed_count, error = process_novel_videos(novel_name)
            if error:
                print(f"处理小说 {novel_name} 时出错: {error}")
                continue
            
            success_count += 1
            print(f"已完成小说 {novel_name} 的视频生成，共 {processed_count} 个章节")
        
        print(f"视频生成完成，共处理 {success_count} 本小说")
        
    except Exception as e:
        print(f"视频生成失败: {str(e)}")
    finally:
        # 清理临时图片
        if os.path.exists(image_path):
            os.remove(image_path)

if __name__ == "__main__":
    main()