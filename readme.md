## 介绍 Introduction

一个简化、但完善了 `ensemble` 功能的 [python-audio-separator](https://github.com/nomadkaraoke/python-audio-separator/tree/main) 的UI程序。大量参考了其他开源代码

A [python-audio-separator] (https://github.com/nomadkaraoke/python-audio-separator/tree/main) UI program that simplifies but improves the'ensemble 'functionality. Extensive reference to other open source code

- 专注 `Rofomer` 系列模型 Focus on the'Rofomer 'series models
- 实现了 `ensemble` 功能 Implemented the'ensemble 'function
- 简单易用、逻辑清晰、说明详细 Simple to use, clear logic, and detailed instructions

本程序暂时只能在 `Nvidia GPU with CUDA` 或 `Google Colab` 上运行，其他平台可能会有问题 This program can only run on `Nvidia GPU with CUDA` or `Google Colab` for now, other platforms may have issues

![screenshot](assets/readme/screenshot.png)

## 手动安装并运行 Installation and Run

### Nvidia GPU with CUDA or Google Colab

> 当前只测试了该环境，虽然理论上苹果肯定可以（pip安装 `pip install "audio-separator[cpu]==0.30.1"`）

#### 安装 (Installation)

> 小白请下载预构建版本

**克隆仓库 Clone the repo**

```bash
git clone https://github.com/youyang-617/Audio-Separator-UI.git
cd Audio-Separator-UI
```

**创建 conda 环境并安装依赖 Create a conda environment and install the dependencies**

```bash
# 创建环境
conda create -n audio-separator python=3.11
conda activate audio-separator

# 安装 PyTorch 和 CUDA 依赖
conda install pytorch=*=*cuda* onnxruntime=*=*cuda* -c pytorch -c conda-forge

# 安装最新版本的 audio-separator 和其他依赖
pip install -r requirements.txt
```

**运行 Run the app**

```bash
python app.py
```

**退出 Quit**

按下 `Ctrl + C` 或关闭终端窗口 Press `Ctrl + C` in the terminal or close the terminal window.

## 大陆用户请看

如果一直连不上，可尝试 `gitee`和清华源

克隆仓库并打开

```bash
git clone https://gitee.com/youyang-617/Audio-Separator-UI.git
cd Audio-Separator-UI
```

清华源配置请参考：[anaconda | 镜像站使用帮助 | 清华大学开源软件镜像站 | Tsinghua Open Source Mirror](https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/)

后续安装步骤同上；

另外，我写了个模型下载器，如果实在太慢，可以尝试用这个下载器下载（需要能运行python）

依赖 `gitproxy.click` 的代理服务😭😭感恩佬们

```bash
python model_downloader_cn.py
```

使用方法：

1. 运行脚本 `python model_downloader_cn.py`
2. 从列表中选择想要下载的模型序号
3. 确认下载后，模型会自动保存到 `models` 目录

## 预构建版本 Pre-built Version

==只用于 `Windows` 系统，其他系统可能会有问题 Only for `Windows` system, other systems may have issues==

### 下载预构建包 Download Pre-built Package

1. 前往项目的 [Releases 页面](https://github.com/youyang-617/Audio-Separator-UI/releases)  
   Visit the project's [Releases page](https://github.com/youyang-617/Audio-Separator-UI/releases)
2. 下载最新版本的压缩包（通常命名为 `Audio-Separator-UI-vX.X.X.zip`）  
   Download the latest version of the package (typically named `Audio-Separator-UI-vX.X.X.zip`)

### 安装步骤 Installation Steps

1. 将下载的压缩包解压到一个没有中文路径、没有空格的目录中（如 `D:\Programs\Audio-Separator-UI`）  
   Extract the downloaded package to a directory without spaces in the path (e.g., `D:\Programs\Audio-Separator-UI`)
2. 打开解压后的文件夹，按顺序执行批处理文件：  
   Open the extracted folder and execute the batch files in sequence:
   - 双击运行 `1.Install.bat`  
     Double-click to run `1.Install.bat`
   - 此脚本会解压环境包并配置必要的运行环境  
     This script will extract the environment package and configure the necessary runtime environment
   - **注意**：解压过程可能需要几分钟，请耐心等待。如提示中所述，解压完成后可能会卡住，这是正常现象  
     **Note**: The extraction process may take several minutes, please be patient. As mentioned in the prompt, it might appear to hang after completion, which is normal

### 启动应用程序 Launch the Application

1. 环境安装完成后，双击运行 `2.Start_Audio_Separator_UI.bat` 启动应用程序  
   After the environment installation is complete, double-click `2.Start_Audio_Separator_UI.bat` to launch the application
2. 应用程序将在浏览器中打开，默认地址为 http://127.0.0.1:7860  
   The application will open in your browser at the default address http://127.0.0.1:7860

### 模型下载 Model Download

首次使用时，程序会自动下载所需模型。如果下载速度过慢或失败可以双击运行 `通过代理下载模型（当且仅当实在没有办法时使用）.bat`  

或者，手动下载模型到 `models` 目录下。模型文件名必须与下载的文件名一致。[请到这里下载](https://github.com/nomadkaraoke/python-audio-separator/releases/tag/model-configs)，若下载到一半可能会损坏，需要手动替换。大陆用户可以尝试[GitHub 文件加速 | 免费公益 GitHub 文件下载加速服务 | 一个小站](https://gh-proxy.ygxz.in/)或[Github Proxy 文件代理加速](https://github.akams.cn/)等文件下载公益站点

You can manually download the model to the 'models' directory. The model file name must be the same as the downloaded file name. [Please go here to download](https://github.com/nomadkaraoke/python-audio-separator/releases/tag/model-configs), if you download half of it, it may be damaged and need to be replaced manually

### 常见问题解决 Troubleshooting Common Issues

1. **环境解压卡住**：环境包较大，解压可能需要较长时间。如果长时间无响应，可以关闭窗口并重新运行 `1.Install.bat`  
   **Environment extraction hanging**: The environment package is large and extraction may take a long time. If there is no response for a long time, you can close the window and run `1.Install.bat` again

2. **模型下载中断**：如果模型下载中断，建议：  
   **Model download interrupted**: If the model download is interrupted, it is recommended to:
   - 使用代理下载批处理文件重新下载  
     Use the proxy download batch file to download again
   - 或参考这篇文档手动下载替换模型（上一节或已知问题）
     Or manually download and replace models

3. **启动失败**：请检查：  
   **Launch failure**: If the launch fails, please check:
   - 是否按顺序执行了安装步骤  
     Whether the installation steps were executed in order
   - 安装路径是否包含中文或空格  
     Whether the installation path contains Chinese characters or spaces
   - 是否有其他实例正在运行  
     Whether there are other instances running
   - 大陆用户建议挂个梯子


### 卸载方法 Uninstallation Method

直接删除整个程序文件夹即可完成卸载，预构建版本不会修改系统注册表  
Simply delete the entire program folder to complete the uninstallation. The pre-built version does not modify the system registry

## 已知问题

- 模型下了一半就停止的话一定会损坏，因为模型寻找和下载用的是别人的库，要修改库非常不方便，只能麻烦大家去[this link](https://github.com/nomadkaraoke/python-audio-separator/releases/tag/model-configs)下载后手动替换了。下载可以尝试[GitHub 文件加速 | 免费公益 GitHub 文件下载加速服务 | 一个小站](https://gh-proxy.ygxz.in/)或[Github Proxy 文件代理加速](https://github.akams.cn/)等文件下载公益站点，或者参看[这里](####大陆用户模型下载可选方式)，感谢慈善家们😭
- 由于gradio框架限制，及时取消非常困难，必须等待处理完，或者在命令行 `crtl + c` 强行退出服务
- 预构建包解压完大概率卡住
- 建议始终科学上网运行，不然不知道会有什么bug

## TO DO

- [X] 能中止处理（放弃，gradio难以完全实现）
- [X] `ensemble` 模式
- [X] 错误能在前端被渲染 而不是只显示错误
- [X] 简化安装
- [X] 大陆的models一键下载
- [ ] 教程/文档
- [X] 保存会话信息，保存用户上一次使用的模型和参数
- [ ] 模型分数展示（leader board）
- [X] 多语言支持

## Credits 🙏🙏🙏🙏

- python-audio-separator by [beveradb](https://github.com/beveradb).
- Thanks to [UVR5 UI](https://github.com/Eddycrack864/UVR5-UI), this project is basically a imitation of it.
- Thanks to [dgfsfxc-tgsacxs-otyhrhs](https://huggingface.co/spaces/ASesYusuf1/dgfsfxc-tgsacxs-otyhrhs/blob/main/gui.py), which many of the code in this repo was copied from.
- Thanks to [Anjok07](https://github.com/Anjok07) and [Ultimate Vocal Remover GUI](https://github.com/Anjok07/ultimatevocalremovergui), which is the beginning of everything.
- Thank you to all the authors of the open-source model involved!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
