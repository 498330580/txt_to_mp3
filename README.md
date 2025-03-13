# 小说文本转语音工具

Version: 1.2.1

一个将小说文本转换为语音的工具，支持章节分割和批量转换。
本工具旨在帮助用户将小说文本转换为语音，方便用户阅读和收听。它支持章节分割和批量转换，以确保输出文件的完整性。

## 介绍

开发本项目主要是因为自己在听小说的时候，经常会遇到一些章节需要反复听，但是听着听着就会忘记，所以就想着能不能将小说转换为语音，这样就可以随时听了。网上有很多工具可以将小说转换为语音，但是都不太方便或者需要钱，所以就想着能不能自己写一个。

## 开发环境要求

- Python 版本: 3.10 或更高
- 操作系统: Windows 10/11
- 内存: 建议 4GB 或更高
- 磁盘空间: 根据小说数量，建议预留 1GB 以上

## 功能特点

- 自动分割小说章节
- 支持多种中文语音选择
- 语速可调节（-50% 到 +50%）
- 支持断点续传，避免重复转换
- 图形化界面操作
- 支持转换过程中停止
- 支持批量打包下载
- 支持临时文件管理，确保输出文件完整性
- 支持视频生成功能

## 目录结构

```plaintext
txt_to_mp3/
├── app.py              # 主程序入口和GUI界面
├── novel_process.py    # 小说文本处理模块
├── tts_process.py      # 语音转换处理模块
├── video_process.py    # 视频生成处理模块
└── data/
    ├── import/        # 导入的小说文本文件
    ├── out_text/      # 分章节后的文本文件
    ├── out_mp3/       # 生成的语音文件
    ├── out_mp4/       # 生成的视频文件
    └── images/        # 视频封面图片
```

## 计划

- [x] 自动分割小说章节
- [x] 支持多种中文章节标题识别
- [x] 语速可调节（-50% 到 +50%）
- [x] 支持断点续传，避免重复转换
- [x] 图形化界面操作
- [x] 支持转换过程中停止
- [x] 支持批量打包下载
- [x] 支持临时文件管理，确保输出文件完整性
- [x] 支持视频生成功能
- [x] docker容器化

## 使用方法

### 方式一：本地运行

#### 1. 环境准备

1. 安装 Python
   
   - 下载并安装 Python 3.8 或更高版本
   - 安装时勾选"Add Python to PATH"
2. 安装依赖包
```bash
pip install -r requirements.txt
 ```

3. 运行程序
```bash
python app.py
```

### 方式二：docker运行

#### 1. 环境准备

1. 安装 Docker
2. 拉取镜像
```bash
docker pull 498330580/txt_to_mp3:latest
```
3. 运行容器
```bash
docker run -d \
  --name txt_to_mp3 \
  -p 7860:7860 \
  -v %cd%/data/import:/app/data/import \
  -v %cd%/data/out_text:/app/data/out_text \
  -v %cd%/data/out_mp3:/app/data/out_mp3 \
  -v %cd%/data/tmp:/app/data/tmp \
  498330580/txt_to_mp3:latest
```
4. 访问界面
    - 打开浏览器访问 http://localhost:7860
5. 停止容器
```bash
docker stop txt_to_mp3
```
6. 删除容器
```bash
docker rm txt_to_mp3
```

### 使用步骤

1. 准备小说文件
    - 将小说文本文件(.txt格式)放入 data/import 目录
    - 支持的文件编码：UTF-8、GBK、GB2312、UTF-16
    - 建议使用 UTF-8 编码以获得最佳兼容性

2. 使用界面
    - 步骤1：上传小说文件
        - 点击"上传文件"按钮选择小说文件
        - 支持批量上传多个文件
    - 步骤2：处理小说分章节
        - 点击"处理章节"按钮
        - 程序会自动识别章节并分割
        - 支持多种章节标题格式
    - 步骤3：转换语音
        - 选择语音角色（支持多个中文语音）
        - 调整语速（-50% 到 +50%）
        - 点击"开始转换"
        - 可随时点击"停止转换"暂停
    - 步骤4：打包下载
        - 转换完成后点击"打包下载"
        - 将生成包含所有MP3文件的ZIP压缩包
    - 步骤5：清理文件
        - 完成后可点击"清理文件"释放空间

## 支持的语音

- zh-CN-XiaoxiaoNeural
- zh-CN-XiaoyiNeural
- zh-CN-YunjianNeural
- zh-CN-YunxiNeural
- zh-CN-YunxiaNeural
- zh-CN-YunyangNeural

## 注意事项

- 小说文本需要是UTF-8编码
- 章节分隔符支持 `---` 和 `***` 等格式
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

## 赞助支持
如果您觉得本项目对您有帮助，欢迎赞助支持。
![./doc/img/收款码.jpg](./doc/img/收款码.jpg)
