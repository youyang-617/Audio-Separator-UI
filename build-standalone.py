import os
import subprocess
import shutil
import sys

# 步骤1: 创建和配置conda环境
def setup_environment():
    print("Creating conda environment...")
    subprocess.run("conda create -n audio-separator-build python=3.11 -y", shell=True)
    
    # 创建pip缓存目录
    os.makedirs("pip-cache", exist_ok=True)
    
    # 1. 先只安装pytorch和onnxruntime (不包含audio-separator)
    print("Installing PyTorch and CUDA dependencies...")
    subprocess.run(
        "conda run -n audio-separator-build conda install pytorch=*=*cuda* onnxruntime=*=*cuda* -c pytorch -c conda-forge -y", 
        shell=True
    )
    
    # 2. 使用pip安装最新版本的audio-separator和其他依赖
    print("Installing audio-separator and other dependencies...")
    subprocess.run(
        "conda run -n audio-separator-build pip install --cache-dir ./pip-cache -r requirements.txt", 
        shell=True
    )
    
    # 3. 验证安装
    print("Verifying installation...")
    subprocess.run("conda run -n audio-separator-build pip show audio-separator", shell=True)
    
    # 安装conda-pack
    subprocess.run("conda install -c conda-forge conda-pack -y", shell=True)

# 步骤2: 打包环境
def pack_environment():
    print("Packing environment...")
    os.makedirs("dist", exist_ok=True)
    subprocess.run("conda pack -n audio-separator-build -o dist/audio-separator-env.tar.gz", shell=True)

# 步骤3: 创建启动器和安装程序
def create_launcher():
    print("Creating launcher...")
    with open("dist/Start_Audio_Separator_UI.bat", "w", encoding="utf-8") as f:
        f.write('@echo off\n')
        f.write('cd %~dp0\n')
        f.write('call .\\env\\Scripts\\activate.bat\n')
        f.write('python app\\app.py\n')
        f.write('if errorlevel 1 pause\n')
    
    # 复制项目文件
    print("Copying project files...")
    shutil.copytree(".", "dist/app", ignore=shutil.ignore_patterns('dist', 'env', '__pycache__', '*.pyc', '.git', 'pip-cache'))
    
    # 创建一键安装脚本
    with open("dist/Install.bat", "w", encoding="utf-8") as f:
        f.write('@echo off\n')
        f.write('echo Extracting environment package, please wait...\n')
        f.write('mkdir env\n')
        f.write('tar -xf audio-separator-env.tar.gz -C env\n')
        f.write('echo Environment installation completed!\n')
        f.write('echo You can now close this window and click "Start_Audio_Separator_UI.bat" to run the program\n')
        f.write('pause\n')
    
    # 创建预下载模型的批处理
    with open("dist/Download_Models.bat", "w", encoding="utf-8") as f:
        f.write('@echo off\n')
        f.write('cd %~dp0\n')
        f.write('call .\\env\\Scripts\\activate.bat\n')
        f.write('python app\\model_downloader.py\n')
        f.write('echo Models download completed!\n')
        f.write('pause\n')

# 主函数
def main():
    setup_environment()
    pack_environment()
    create_launcher()
    
    print("=========================================")
    print("Build completed!")
    print("All files have been saved to dist directory")
    print("For distribution, please package all files in the dist directory")
    print("=========================================")

if __name__ == "__main__":
    main()