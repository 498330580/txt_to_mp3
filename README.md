# 小说文本转语音工具

一个将小说文本转换为语音的工具，支持章节分割和批量转换。

## 功能特点

- 自动分割小说章节
- 支持多种中文语音选择
- 语速可调节（-50% 到 +50%）
- 支持断点续传，避免重复转换
- 图形化界面操作
- 支持转换过程中停止
- 支持批量打包下载
- 支持临时文件管理，确保输出文件完整性

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
- 步骤1：上传小说文件
- 步骤2：处理小说分章节
- 步骤3：转换语音（可随时停止）
- 步骤4：打包下载
- 步骤5：清理文件

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
- 可以随时停止转换过程

## 许可证

本项目采用 [GNU General Public License v3.0](LICENSE) 开源许可证。

- 允许任何人免费使用、修改和分发本项目
- 修改后的项目必须继续使用 GPL-3.0 许可证开源
- 修改后的项目必须标明原项目出处

## 致谢

如果您觉得这个项目对您有帮助，欢迎：
- 在 GitHub 上给项目点个 Star
- Fork 项目并贡献代码
- 在使用中提出宝贵意见
