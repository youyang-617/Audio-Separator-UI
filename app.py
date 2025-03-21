import os
import torch
import logging
import gradio as gr
import argparse
from audio_separator.separator import Separator
from core.ensemble import ensemble_files  # ensemble.py'dan import
import json
from core.ui import create_interface

# 设备配置
device = "cuda" if torch.cuda.is_available() else "cpu"
use_autocast = device == "cuda"

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载模型配置
def load_models(config_path="models.json"):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    

def roformer_separator(audio, model_key, seg_size, override_seg_size, overlap, pitch_shift, model_dir, out_dir, out_format, norm_thresh, amp_thresh, batch_size, single_stem="", progress=gr.Progress(track_tqdm=True)):
    if not audio:
        raise ValueError("No audio file provided.")
    base_name = os.path.splitext(os.path.basename(audio))[0]
    for category, models in ROFORMER_MODELS.items():
        if model_key in models:
            model = models[model_key]
            break
    else:
        raise ValueError(f"Model '{model_key}' not found.")
    
    logger.info(f"Separating {base_name} with {model_key}")
    try:
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
        progress(0.2, desc="Loading model...")
        separator.load_model(model_filename=model)
        progress(0.7, desc="Separating audio...")
        separation = separator.separate(audio)
        stems = [os.path.join(out_dir, file_name) for file_name in separation]
        return stems[0], stems[1] if len(stems) > 1 and not single_stem.strip() else None
    except Exception as e:
        logger.error(f"Separation failed: {e}")
        raise RuntimeError(f"Separation failed: {e}")


def auto_ensemble_process(audio, model_keys, seg_size, overlap, out_format, use_tta, model_dir, out_dir, norm_thresh, amp_thresh, batch_size, ensemble_method, only_instrumental, progress=gr.Progress()):
    if not audio or not model_keys:
        raise ValueError("Audio or models missing.")
    base_name = os.path.splitext(os.path.basename(audio))[0]
    logger.info(f"Ensemble for {base_name} with {model_keys}")
    
    # 创建临时目录
    import tempfile
    temp_dir = os.path.join(out_dir, "tmp")
    os.makedirs(temp_dir, exist_ok=True)
    logger.info(f"Created temporary directory: {temp_dir}")
    
    # 分别创建两个列表存储人声和伴奏轨道
    vocal_stems = []
    instrumental_stems = []
    # 记录所有中间文件以便后续清理
    temp_files = []
    total_models = len(model_keys)
    
    try:
        for i, model_key in enumerate(model_keys):
            for category, models in ROFORMER_MODELS.items():
                if model_key in models:
                    model = models[model_key]
                    break
            else:
                continue
            separator = Separator(
                log_level=logging.INFO,
                model_file_dir=model_dir,
                output_dir=temp_dir,  # 使用临时目录
                output_format=out_format,
                normalization_threshold=norm_thresh,
                amplification_threshold=amp_thresh,
                use_autocast=use_autocast,
                mdxc_params={"segment_size": seg_size, "overlap": overlap, "use_tta": use_tta, "batch_size": batch_size}
            )
            progress(0.1 + (0.4 / total_models) * i, desc=f"Loading {model_key}")
            separator.load_model(model_filename=model)
            progress(0.5 + (0.4 / total_models) * i, desc=f"Separating with {model_key}")
            separation = separator.separate(audio)
            stems = [os.path.join(temp_dir, file_name) for file_name in separation]
            
            # 记录所有生成的中间文件
            for stem in stems:
                temp_files.append(stem)
            
            # 优先匹配明确的标记
            for stem in stems:
                stem_lower = stem.lower()
                stem_name = os.path.basename(stem_lower)
                
                logger.info(f"Classifying stem: {stem_name}")
                
                if "(instrumental)" in stem_lower or "(inst)" in stem_lower or "(accompaniment)" in stem_lower:
                    instrumental_stems.append(stem)
                    logger.info(f"  -> Classified as INSTRUMENTAL (exact match)")
                elif "(vocals)" in stem_lower or "(vocal)" in stem_lower or "(voice)" in stem_lower:
                    vocal_stems.append(stem)
                    logger.info(f"  -> Classified as VOCAL (exact match)")
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
        
        # 处理人声轨道合成（如果不是只要伴奏）
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
        
        # 处理伴奏轨道合成
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
            
        progress(1.0, desc="Ensemble complete")
        
        # 清理临时文件
        for file_path in temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Removed temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {file_path}: {e}")
        
        # 尝试删除临时目录
        try:
            # 检查目录是否为空
            remaining_files = os.listdir(temp_dir)
            if not remaining_files:
                os.rmdir(temp_dir)
                logger.info(f"Removed temporary directory: {temp_dir}")
            else:
                logger.warning(f"Could not remove temporary directory, {len(remaining_files)} files remain")
        except Exception as e:
            logger.warning(f"Failed to remove temporary directory: {e}")
        
        # 构建返回结果
        return vocal_output, instrumental_output
    
    except Exception as e:
        logger.error(f"Ensemble failed: {e}")
        # 发生错误时也尝试清理文件
        for file_path in temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        raise RuntimeError(f"Ensemble failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Music Source Separation Web UI")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--lang", type=str, help="Language code (e.g., zh_CN, en_US)")
    args = parser.parse_args()
    
    # 如果指定了语言
    if args.lang:
        from core.i18n import I18n
        # 重新加载指定语言
        _ = I18n(language=args.lang)

    # 加载配置和资源
    ROFORMER_MODELS = load_models(config_path="models_info/models.json")
    OUTPUT_FORMATS = ['wav', 'flac', 'mp3', 'ogg', 'opus', 'm4a', 'aiff', 'ac3']
    
    # 创建界面并启动
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
