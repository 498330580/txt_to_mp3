# 📚 小说文本转语音工具

✨ **Version: 1.4.0** ✨

一个将小说文本转换为语音的工具，支持章节分割、音频合并和视频生成功能。本工具旨在帮助用户将小说文本转换为语音，方便用户阅读和收听。

## 🎯 功能特点

- ✅ **自动分割**小说章节
- 🎙️ 支持**多种中文语音**选择
- ⏩ 语速可调节（-50% 到 +50%）
- 🔄 支持**断点续传**，避免重复转换
- 🖥️ 图形化界面操作
- ⏸️ 支持转换过程中停止
- 📦 支持批量打包下载
- 🎬 支持视频生成功能
- 🔊 支持音频合并功能
- 🖼️ 支持自定义视频封面

## 🏗️ 目录结构

```plaintext
txt_to_mp3/
├── 📄 app.py              # 主程序入口和GUI界面
├── 📄 novel_process.py    # 小说文本处理模块
├── 📄 tts_process.py      # 语音转换处理模块
├── 📄 merge_process.py    # 音频合并处理模块
├── 📄 video_process_async.py # 异步视频生成模块
└── 📂 data/
    ├── 📂 import/        # 导入的小说文本文件
    ├── 📂 out_text/      # 分章节后的文本文件
    ├── 📂 out_mp3/       # 生成的语音文件
    ├── 📂 out_mp3_merge/ # 合并后的音频文件
    ├── 📂 out_mp4/       # 生成的视频文件
    ├── 📂 images/        # 视频封面图片
    └── 📂 tmp/          # 临时文件目录


## 🚀 使用方法

### 方式一：本地运行

1. **安装Python** 🐍
   - 下载并安装 Python 3.10+
   - 勾选"Add Python to PATH"

2. **安装依赖** 📦
```bash
pip install -r requirements.txt
```

3. **运行程序** ▶️
```bash
python app.py
```

### 方式二：Docker运行 🐳

1. **拉取镜像**
```bash
docker pull 498330580/txt_to_mp3:latest
```

2. **运行容器** (推荐使用docker-compose)
```bash
docker-compose up -d
```

3. **访问界面** 🌐
   - 打开浏览器访问 http://localhost:7860

## ⚠️ 注意事项

- 📝 小说文本建议使用UTF-8编码
- 🔌 转换过程中请保持网络连接
- ⏳ 已转换的章节会自动跳过
- 🗑️ 完成后可清理临时文件释放空间

## 📜 许可证

本项目采用 [GNU General Public License v3.0](LICENSE) 开源许可证。

## 🙏 致谢

如果您觉得这个项目对您有帮助，欢迎：
- ⭐ 在 GitHub 上给项目点个 Star
- 🍴 Fork 项目并贡献代码
- 💬 在使用中提出宝贵意见
```


## 🙏 赞助支持
如果您觉得本项目对您有帮助，欢迎赞助支持。
![./doc/img/收款码.jpg](./doc/img/收款码.jpg)
