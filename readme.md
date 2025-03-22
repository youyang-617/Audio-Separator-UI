[anaconda | 镜像站使用帮助 | 清华大学开源软件镜像站 | Tsinghua Open Source Mirror](https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/)

## 介绍 Introduction

一个简化、但完善了 `ensemble` 功能的 [python-audio-separator](https://github.com/nomadkaraoke/python-audio-separator/tree/main) 的UI程序。大量参考了其他开源代码

A [python-audio-separator] (https://github.com/nomadkaraoke/python-audio-separator/tree/main) UI program that simplifies but improves the'ensemble 'functionality. Extensive reference to other open source code

- 专注 `Rofomer` 系列模型 Focus on the'Rofomer 'series models
- 实现了 `ensemble` 功能 Implemented the'ensemble 'function
- 简单易用、逻辑清晰、说明详细 Simple to use, clear logic, and detailed instructions

![screenshot](assets/readme/screenshot.png)

## 安装 Installation

### Nvidia GPU with CUDA or  Google Colab

> 当前只测试了该环境，虽然理论上苹果肯定可以（pip安装 `pip install "audio-separator[cpu]==0.30.1"`）

#### By Default

Clone the repo

```bash
git clone https://github.com/youyang-617/Audio-Separator-UI.git
cd Audio-Separator-UI
```

Create a conda environment and install the dependencies

```bash
conda create -n audio-separator python=3.11
conda activate audio-separator
conda install pytorch=*=*cuda* onnxruntime=*=*cuda* audio-separator -c pytorch -c conda-forge
pip install -r requirements.txt
```

Run the app
```bash
python app.py
```

#### 大陆用户可尝试 `gitee`和清华源

克隆仓库并打开

```bash
git clone https://gitee.com/youyang-617/Audio-Separator-UI.git
cd Audio-Separator-UI
```

清华源配置请参考：[anaconda | 镜像站使用帮助 | 清华大学开源软件镜像站 | Tsinghua Open Source Mirror](https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/)

后续安装步骤同上


## 已知问题

- 模型下了一半就停止的话一定会损坏，因为模型寻找和下载用的是别人的库，要修改库非常不方便，只能麻烦大家去[this link](https://github.com/nomadkaraoke/python-audio-separator/releases/tag/model-configs)下载后手动替换了。下载可以尝试[GitHub 文件加速 | 免费公益 GitHub 文件下载加速服务 | 一个小站](https://gh-proxy.ygxz.in/)或[Github Proxy 文件代理加速](https://github.akams.cn/)等文件下载公益站点，感谢慈善家们😭
- 由于gradio框架限制，及时取消非常困难

## TO DO

- [X] 能中止处理（放弃，gradio难以完全实现）
- [X] `ensemble` 下切换模型类别后清空
- [X] `ensemble` 选择后检查所选模型是不是大于 1
- [X] 错误能在前端被渲染 而不是只显示错误
- [ ] 简化安装
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
