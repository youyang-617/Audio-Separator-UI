"""
模型下载器 / Model Downloader

此脚本用于从 GitHub 上下载音频分离模型。用户可以选择要下载的模型，脚本会生成下载链接并在浏览器中打开。
This script is used to download audio separation models from GitHub. Users can select the model to download, and the script will generate a download link and open it in the browser.

功能 / Features:
1. 加载模型信息 / Load model information
2. 显示可用模型列表 / Display available model list
3. 生成下载链接并在浏览器中打开 / Generate download link and open in browser

使用方法 / Usage:
1. 运行脚本 / Run the script
2. 选择要下载的模型 / Select the model to download
3. 在浏览器中完成下载并将文件保存到指定目录 / Complete the download in the browser and save the file to the specified directory
"""
import json
import os
import webbrowser
from tqdm import tqdm

# 模型下载基础URL
BASE_URL = "https://gitproxy.click/https://github.com/nomadkaraoke/python-audio-separator/releases/download/model-configs/"

def load_models_info():
    """加载模型信息"""
    with open("models_info/models.json", "r", encoding="utf-8") as f:
        return json.load(f)

def display_models(models_info):
    """显示所有模型并返回模型索引映射"""
    model_index = 1
    model_map = {}
    print("使用 gitproxy.click 访问 GitHub 上的模型文件")
    print("可用模型列表：")
    print("-" * 80)
    
    for category, models in models_info.items():
        print(f"\n{category}:")
        for display_name, actual_name in models.items():
            print(f"  [{model_index}] {display_name}")
            model_map[model_index] = (display_name, actual_name, category)
            model_index += 1
    
    return model_map

def open_download_link(model_filename, save_dir="models"):
    """生成下载链接并使用浏览器打开"""
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    url = BASE_URL + model_filename
    save_path = os.path.join(save_dir, model_filename)
    
    print(f"正在打开浏览器下载链接: {url}")
    print(f"请将下载的文件保存到: {os.path.abspath(save_dir)} 目录")
    
    # 打开浏览器下载
    webbrowser.open(url)
    
    print(f"已打开浏览器，请在浏览器中完成下载。")
    return True

def main():
    try:
        # 加载模型信息
        models_info = load_models_info()
        
        # 显示模型列表并获取映射
        model_map = display_models(models_info)
        
        # 创建模型目录提示
        models_dir = os.path.abspath("models")
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        print(f"\n下载的模型应保存在: {models_dir}")
        print("下载后请确保模型文件放在上述目录中，以便程序正确加载")
        
        while True:
            # 用户输入
            print("\n" + "-" * 80)
            choice = input("请输入要下载的模型序号 (输入q退出): ")
            
            if choice.lower() == 'q':
                print("程序已退出。")
                break
            
            try:
                choice = int(choice)
                if choice not in model_map:
                    print(f"无效的选择: {choice}，请输入有效的序号。")
                    continue
                
                display_name, actual_name, category = model_map[choice]
                print(f"\n您选择了: {display_name} (类别: {category})")
                print(f"对应的模型文件: {actual_name}")
                
                # 下载确认
                confirm = input("确认使用浏览器下载？ (y/n): ")
                if confirm.lower() == 'y':
                    open_download_link(actual_name)
                    print("\n请等待浏览器下载完成。下载后请确认文件名正确，并将文件放入模型目录。")
                    input("按回车键继续...")
                else:
                    print("下载已取消。")
            
            except ValueError:
                print("请输入有效的数字序号。")
    
    except Exception as e:
        print(f"发生错误: {str(e)}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()