import os
import torch
import logging
import gradio as gr
import argparse
import json
from audio_separator.separator import Separator  # 音频分离核心库
from utils.ensemble import ensemble_files  # 音轨合成功能
from utils.clean_up import cleanup_temp_files  # 清理临时文件
from utils.ui import create_interface  # 导入UI生成函数

# 设备配置 - 自动检测是否支持CUDA加速
device = "cuda" if torch.cuda.is_available() else "cpu"
use_autocast = device == "cuda"

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载模型配置文件
def load_models(config_path="models.json"):
    """从JSON文件加载可用的模型配置信息"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    

def roformer_separator(audio, model_key, seg_size, override_seg_size, overlap, pitch_shift, model_dir, out_dir, out_format, norm_thresh, amp_thresh, batch_size, single_stem="", progress=gr.Progress(track_tqdm=True)):
    """
    使用RoFormer模型进行音频分离
    
    参数:
        audio: 输入音频文件路径
        model_key: 选择的模型名称
        seg_size: 分段大小
        override_seg_size: 是否覆盖模型默认分段大小
        overlap: 重叠比例
        pitch_shift: 音高偏移
        model_dir: 模型文件目录
        out_dir: 输出目录
        out_format: 输出格式
        norm_thresh: 归一化阈值
        amp_thresh: 放大阈值
        batch_size: 批处理大小
        single_stem: 仅输出单个音轨(可选)
        progress: 进度条对象
        
    返回:
        分离后的音轨文件路径(主音轨, 次音轨)
    """
    if not audio:
        raise ValueError("No audio file provided.")
    base_name = os.path.splitext(os.path.basename(audio))[0]
    
    # 从模型配置中查找指定模型
    for category, models in ROFORMER_MODELS.items():
        if model_key in models:
            model = models[model_key]
            break
    else:
        raise ValueError(f"Model '{model_key}' not found.")
    
    logger.info(f"Separating {base_name} with {model_key}")
    try:
        # 配置分离器参数
        separator = Separator(
            log_level=logging.INFO,
            model_file_dir=model_dir,
            output_dir=out_dir,
            output_format=out_format,
            normalization_threshold=norm_thresh,
            amplification_threshold=amp_thresh,
            use_autocast=use_autocast,
            output_single_stem=single_stem if single_stem.strip() else None,
            mdxc_params={"segment_size": seg_size, "override_model_segment_size": override_seg_size, "batch_size": batch_size, "overlap": overlap, "pitch_shift": pitch_shift}
        )

        separator.load_model(model_filename=model)
        separation = separator.separate(audio)
        stems = [os.path.join(out_dir, file_name) for file_name in separation]
        
        # 返回结果(通常为人声和伴奏)
        return stems[0], stems[1] if len(stems) > 1 and not single_stem.strip() else None
    except Exception as e:
        logger.error(f"Separation failed: {e}")
        raise RuntimeError(f"Separation failed: {e}")


def auto_ensemble_process(audio, model_keys, seg_size, overlap, out_format, use_tta, model_dir, out_dir, norm_thresh, amp_thresh, batch_size, ensemble_method, only_instrumental, progress=gr.Progress()):
    """
    使用多个模型进行分离并合成结果
    
    参数:
        audio: 输入音频文件路径
        model_keys: 要使用的模型列表
        seg_size: 分段大小
        overlap: 重叠比例
        out_format: 输出格式
        use_tta: 是否使用测试时增强
        model_dir: 模型文件目录
        out_dir: 输出目录
        norm_thresh: 归一化阈值
        amp_thresh: 放大阈值
        batch_size: 批处理大小
        ensemble_method: 合成方法(mean/max)
        only_instrumental: 是否只输出伴奏轨道
        progress: 进度条对象
        
    返回:
        合成后的人声和伴奏文件路径
    """
    if not audio or not model_keys:
        raise ValueError("Audio or models missing.")
    base_name = os.path.splitext(os.path.basename(audio))[0]
    logger.info(f"Ensemble for {base_name} with {model_keys}")
    
    # 创建临时目录存放中间结果
    temp_dir = os.path.join(out_dir, "tmp")
    os.makedirs(temp_dir, exist_ok=True)
    logger.info(f"Created temporary directory: {temp_dir}")
    
    # 初始化存储列表
    vocal_stems = []  # 存储所有模型产生的人声轨道
    instrumental_stems = []  # 存储所有模型产生的伴奏轨道
    temp_files = []  # 用于跟踪需要清理的临时文件
    total_models = len(model_keys)
    
    try:
        # 使用每个模型分别处理音频
        for i, model_key in enumerate(model_keys):
            # 查找指定模型
            for category, models in ROFORMER_MODELS.items():
                if model_key in models:
                    model = models[model_key]
                    break
            else:
                continue
                
            # 配置分离器
            separator = Separator(
                log_level=logging.INFO,
                model_file_dir=model_dir,
                output_dir=temp_dir,
                output_format=out_format,
                normalization_threshold=norm_thresh,
                amplification_threshold=amp_thresh,
                use_autocast=use_autocast,
                mdxc_params={"segment_size": seg_size, "overlap": overlap, "use_tta": use_tta, "batch_size": batch_size}
            )
            progress(0.1 + (0.4 / total_models) * i, desc=f"Loading {model_key}")
            separator.load_model(model_filename=model)
            
            # 执行分离
            progress(0.5 + (0.4 / total_models) * i, desc=f"Separating with {model_key}")
            separation = separator.separate(audio)
            stems = [os.path.join(temp_dir, file_name) for file_name in separation]
            
            # 记录临时文件
            for stem in stems:
                temp_files.append(stem)
            
            # 根据文件名识别人声和伴奏轨道
            for stem in stems:
                stem_lower = stem.lower()
                stem_name = os.path.basename(stem_lower)
                
                logger.info(f"Classifying stem: {stem_name}")
                
                # 精确匹配伴奏关键词
                if "(instrumental)" in stem_lower or "(inst)" in stem_lower or "(accompaniment)" in stem_lower:
                    instrumental_stems.append(stem)
                    logger.info(f"  -> Classified as INSTRUMENTAL (exact match)")
                # 精确匹配人声关键词
                elif "(vocals)" in stem_lower or "(vocal)" in stem_lower or "(voice)" in stem_lower:
                    vocal_stems.append(stem)
                    logger.info(f"  -> Classified as VOCAL (exact match)")
                # 无法精确匹配时的推断策略
                else:
                    logger.warning(f"  -> Could not classify stem with certainty: {stem_name}")
                    if len(stems) > 1 and stem == stems[1]:
                        instrumental_stems.append(stem)
                        logger.info(f"  -> Assumed as INSTRUMENTAL (by position)")
                    else:
                        vocal_stems.append(stem)
                        logger.info(f"  -> Assumed as VOCAL (by position)")
        
        logger.info(f"Found {len(vocal_stems)} vocal stems and {len(instrumental_stems)} instrumental stems")
        
        # 检查是否有足够的轨道进行合成
        if (not vocal_stems and not only_instrumental) or (not instrumental_stems and only_instrumental):
            raise ValueError("No valid stems for ensemble.")
        
        vocal_output = None
        instrumental_output = None
        
        # 合成人声轨道(如果需要)
        if vocal_stems and not only_instrumental:
            progress(0.85, desc="Creating vocal ensemble...")
            vocal_output_file = os.path.join(out_dir, f"{base_name}_ensemble_vocals_{ensemble_method}.{out_format}")
            vocal_result = ensemble_files([
                "--files"] + vocal_stems + [
                "--type", ensemble_method,
                "--output", vocal_output_file
            ])
            if vocal_result:
                vocal_output = vocal_result
                logger.info(f"Vocal ensemble saved to {vocal_output}")
        
        # 合成伴奏轨道
        if instrumental_stems:
            progress(0.95, desc="Creating instrumental ensemble...")
            instrumental_output_file = os.path.join(out_dir, f"{base_name}_ensemble_instrumental_{ensemble_method}.{out_format}")
            instrumental_result = ensemble_files([
                "--files"] + instrumental_stems + [
                "--type", ensemble_method,
                "--output", instrumental_output_file
            ])
            if instrumental_result:
                instrumental_output = instrumental_result
                logger.info(f"Instrumental ensemble saved to {instrumental_output}")
        
        progress(0.98, desc="Cleaning up temporary files...")
        progress(1.0, desc="Ensemble complete")
        cleanup_temp_files(temp_files, temp_dir)
        # 返回处理结果
        return vocal_output, instrumental_output
    
    except Exception as e:
        logger.error(f"Ensemble failed: {e}")
        cleanup_temp_files(temp_files, temp_dir)
        raise RuntimeError(f"Ensemble failed: {e}")


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Music Source Separation Web UI")
    parser.add_argument("--port", type=int, default=7860, help="Web UI服务端口")
    parser.add_argument("--lang", type=str, help="Language code (e.g., zh_CN, en_US)")
    args = parser.parse_args()
    
    # 如果指定了语言，加载对应语言包
    if args.lang:
        from utils.i18n import I18n
        _ = I18n(language=args.lang)

    # 加载模型配置和输出格式选项
    ROFORMER_MODELS = load_models(config_path="models_info/models.json")
    OUTPUT_FORMATS = ['wav', 'flac', 'mp3', 'ogg', 'opus', 'm4a', 'aiff', 'ac3']
    
    # 创建Web界面并启动服务
    app = create_interface(
        ROFORMER_MODELS, 
        OUTPUT_FORMATS, 
        roformer_separator, 
        auto_ensemble_process
    )
    
    app.launch(
        server_port=args.port,
        # server_name="0.0.0.0",  # 如需外部访问
        # share=True             # 如需分享链接
    )