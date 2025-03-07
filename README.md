# 小说文本转语音工具

一个将小说文本转换为语音的工具，支持章节分割和批量转换。

## 功能特点

- 自动分割小说章节
- 支持多种中文语音选择
- 语速可调节
- 支持断点续传，避免重复转换
- 图形化界面操作

## 目录结构

```plaintext
txt_to_mp3/
├── app.py              # 主程序入口和GUI界面
├── novel_process.py    # 小说文本处理模块
├── tts_process.py      # 语音转换处理模块
└── data/
    ├── import/        # 导入的小说文本文件
    ├── out_text/      # 分章节后的文本文件
    └── out_mp3/       # 生成的语音文件
```

## 使用方法

1. 安装依赖
```bash
pip install edge-tts gradio
```

2. 准备小说文件
- 将小说文本文件(.txt格式)放入 `data/import` 目录

3. 运行程序
```bash
python app.py
```

4. 使用界面
- 选择语音：支持多种中文语音
- 调节语速：-50% 到 +50%
- 点击"开始处理"按钮开始转换

## 支持的语音

- zh-CN-XiaoxiaoNeural
- zh-CN-XiaoyiNeural
- zh-CN-YunjianNeural
- zh-CN-YunxiNeural
- zh-CN-YunxiaNeural
- zh-CN-YunyangNeural

## 注意事项

- 小说文本需要是UTF-8编码
- 章节分隔符支持 `---` 和 `***` 格式
- 转换过程中请保持网络连接
- 已转换的章节会自动跳过，支持断点续传
