import os
import subprocess
import shutil
import sys

# 步骤1: 创建和配置conda环境
def setup_environment():
    print("正在创建conda环境...")
    subprocess.run("conda create -n audio-separator-build python=3.11 -y", shell=True)
    
    # 安装依赖
    print("正在安装依赖...")
    subprocess.run(
        "conda run -n audio-separator-build conda install pytorch=*=*cuda* onnxruntime=*=*cuda* audio-separator -c pytorch -c conda-forge -y", 
        shell=True
    )
    subprocess.run(
        "conda run -n audio-separator-build pip install -r requirements.txt", 
        shell=True
    )
    
    # 安装conda-pack
    subprocess.run("conda install -c conda-forge conda-pack -y", shell=True)

# 步骤2: 打包环境
def pack_environment():
    print("正在打包环境...")
    os.makedirs("dist", exist_ok=True)
    subprocess.run("conda pack -n audio-separator-build -o dist/audio-separator-env.tar.gz", shell=True)

# 步骤3: 创建启动器和安装程序
def create_launcher():
    print("正在创建启动器...")
    with open("dist/启动 Audio-Separator-UI.bat", "w") as f:
        f.write('@echo off\n')
        f.write('cd %~dp0\n')
        f.write('call .\\env\\Scripts\\activate.bat\n')
        f.write('python app.py\n')
        f.write('if errorlevel 1 pause\n')
    
    # 复制项目文件
    print("正在复制项目文件...")
    shutil.copytree(".", "dist/app", ignore=shutil.ignore_patterns('dist', 'env', '__pycache__', '*.pyc', '.git'))
    
    # 创建一键安装脚本
    with open("dist/安装.bat", "w") as f:
        f.write('@echo off\n')
        f.write('echo 正在解压环境包，请稍候...\n')
        f.write('mkdir env\n')
        f.write('tar -xf audio-separator-env.tar.gz -C env\n')
        f.write('echo 环境安装完成！\n')
        f.write('echo 现在可以关闭此窗口，并点击"启动 Audio-Separator-UI.bat"运行程序\n')
        f.write('pause\n')
    
    # 创建预下载模型的批处理
    with open("dist/下载常用模型.bat", "w") as f:
        f.write('@echo off\n')
        f.write('cd %~dp0\n')
        f.write('call .\\env\\Scripts\\activate.bat\n')
        f.write('python app\\download_models.py\n')
        f.write('echo 模型下载完成！\n')
        f.write('pause\n')

# 主函数
def main():
    setup_environment()
    pack_environment()
    create_launcher()
    
    print("=========================================")
    print("构建完成！")
    print("所有文件已保存到 dist 目录")
    print("分发时，请打包 dist 目录下的所有文件")
    print("=========================================")

if __name__ == "__main__":
    main()