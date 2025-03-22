import json
import os
import requests
from tqdm import tqdm

# 模型下载基础URL
BASE_URL = "https://gitproxy.click/https://github.com/nomadkaraoke/python-audio-separator/releases/download/model-configs/"

def load_models_info():
    """加载模型信息"""
    with open("d:/coding/Audio-Separator-UI/models_info/models.json", "r", encoding="utf-8") as f:
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

def download_model(model_filename, save_dir="models"):
    """下载模型文件"""
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    url = BASE_URL + model_filename
    save_path = os.path.join(save_dir, model_filename)
    
    print(f"正在从以下地址下载模型: {url}")
    print(f"保存路径: {save_path}")
    
    try:
        # 开始下载
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 如果响应状态不是200，将引发HTTPError异常
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        
        with open(save_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="下载进度") as pbar:
                for data in response.iter_content(block_size):
                    f.write(data)
                    pbar.update(len(data))
        
        print(f"模型 {model_filename} 下载完成！")
        return True
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return False

def main():
    try:
        # 加载模型信息
        models_info = load_models_info()
        
        # 显示模型列表并获取映射
        model_map = display_models(models_info)
        
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
                confirm = input("确认下载？ (y/n): ")
                if confirm.lower() == 'y':
                    download_model(actual_name)
                else:
                    print("下载已取消。")
            
            except ValueError:
                print("请输入有效的数字序号。")
    
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()
