"""
此脚本自动化设置conda环境、安装必要依赖、打包环境以及为Audio Separator UI应用程序创建启动脚本的过程。This script automates the process of setting up the conda environment, installing the necessary dependencies, packaging the environment, and creating startup scripts for the Audio Separator UI application.

步骤：
1. 设置环境：创建conda环境，安装依赖并修复潜在冲突。
2. 打包环境：将conda环境打包成tar.gz文件以便分发。
3. 创建启动器：创建用于启动应用程序和安装环境的批处理脚本。

用法：
运行此脚本以准备Audio Separator UI应用程序的分发。
"""

import os
import subprocess
import shutil
import sys

# 步骤1: 创建和配置conda环境
def setup_environment():
    try:
        print("Creating conda environment...")
        # 创建环境时预先指定numpy版本，避免后续冲突
        subprocess.run("conda create -n audio-separator-build python=3.11 numpy=1.26.4 -y", shell=True, check=True)
        
        # 创建pip缓存目录
        os.makedirs("pip-cache", exist_ok=True)
        
        # 1. 安装pytorch和onnxruntime
        print("Installing PyTorch and CUDA dependencies...")
        subprocess.run(
            "conda run -n audio-separator-build conda install pytorch=*=*cuda* onnxruntime=*=*cuda* --no-update-deps -c pytorch -c conda-forge -y", 
            shell=True, check=True
        )
        
        # 2. 使用pip安装最新版本的audio-separator和其他依赖
        print("Installing audio-separator and other dependencies...")
        subprocess.run(
            "conda run -n audio-separator-build pip install --cache-dir ./pip-cache -r requirements.txt", 
            shell=True, check=True
        )
        
        # 3. 验证安装
        print("Verifying installation...")
        subprocess.run("conda run -n audio-separator-build pip show audio-separator", shell=True, check=True)
        
        # 4. 修复可能的conda/pip冲突
        print("Fixing potential conda/pip conflicts...")
        subprocess.run("conda run -n audio-separator-build conda install -f numpy=1.26.4 -c conda-forge -y", shell=True, check=True)
        
        # 安装conda-pack
        subprocess.run("conda install -c conda-forge conda-pack -y", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        print(f"Command: {e.cmd}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {str(e)}")
        sys.exit(1)

# 步骤2: 打包环境
def pack_environment():
    try:
        print("Packing environment...")
        os.makedirs("dist", exist_ok=True)
        subprocess.run("conda pack -n audio-separator-build -o dist/audio-separator-env.tar.gz", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Packing environment failed with exit code {e.returncode}")
        print(f"Command: {e.cmd}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during packing: {str(e)}")
        sys.exit(1)

# 步骤3: 创建启动器和安装程序
def create_launcher():
    try:
        print("Creating launcher...")
        with open("dist/2.Start_Audio_Separator_UI.bat", "w", encoding="utf-8") as f:
            f.write('@echo off\n')
            f.write('cd %~dp0\n')
            f.write('call .\\env\\Scripts\\activate.bat\n')
            f.write('cd app\n')
            f.write('python app.py\n')
            f.write('if errorlevel 1 pause\n')
        
        # 复制项目文件
        print("Copying project files...")
        shutil.copytree(".", "dist/app", ignore=shutil.ignore_patterns('dist', 'env', '__pycache__', '*.pyc', '.git', 'pip-cache', 'models', 'output'))
        
        # 创建一键安装脚本
        with open("dist/1.Install.bat", "w", encoding="utf-8") as f:
            f.write('@echo off\n')
            f.write('echo Extracting environment package, please wait...\n')
            f.write('mkdir env\n')
            f.write('tar -xvf audio-separator-env.tar.gz -C env\n')
            f.write('echo Environment installation completed!\n')
            f.write('echo You can now close this window and click "Start_Audio_Separator_UI.bat" to run the program\n')
            f.write('pause\n')
        
        # 创建预下载模型的批处理
        with open("dist/通过代理下载模型（当且仅当实在没有办法时使用）.bat", "w", encoding="utf-8") as f:
            f.write('@echo off\n')
            f.write('cd %~dp0\n')
            f.write('call .\\env\\Scripts\\activate.bat\n')
            f.write('cd app\n')
            f.write('python model_downloader_cn.py\n')
            f.write('echo Models download completed!\n')
            f.write('pause\n')
    except Exception as e:
        print(f"ERROR: Failed to create launcher files: {str(e)}")
        sys.exit(1)

# 主函数
def main():
    try:
        setup_environment()
        pack_environment()
        create_launcher()
        
        print("=========================================")
        print("Build completed!")
        print("All files have been saved to dist directory")
        print("For distribution, please package all files in the dist directory")
        print("=========================================")
    except Exception as e:
        print(f"ERROR: Build process failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()