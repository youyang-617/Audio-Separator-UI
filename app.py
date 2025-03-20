import os
import torch
import logging
# from yt_dlp import YoutubeDL
import gradio as gr
import argparse
from audio_separator.separator import Separator
import numpy as np
import soundfile as sf
from ensemble import ensemble_files  # ensemble.py'dan import
import json


# 设备配置
device = "cuda" if torch.cuda.is_available() else "cpu"
use_autocast = device == "cuda"

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model dictionaries organized by category
def load_models(config_path="models.json"):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
ROFORMER_MODELS = load_models()

OUTPUT_FORMATS = ['wav', 'flac', 'mp3', 'ogg', 'opus', 'm4a', 'aiff', 'ac3']


# 加载外部CSS
with open("styles.css", "r", encoding="utf-8") as f:
    CSS = f.read()
    

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
    
    all_stems = []
    total_models = len(model_keys)
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
            output_dir=out_dir,
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
        stems = [os.path.join(out_dir, file_name) for file_name in separation]
        if only_instrumental:
            instrumental_stem = next((stem for stem in stems if "instrumental" in stem.lower()), None)
            if instrumental_stem:
                all_stems.append(instrumental_stem)
        else:
            all_stems.append(stems[0])
    
    if not all_stems:
        raise ValueError("No valid stems for ensemble.")
    
    try:
        output_file = os.path.join(out_dir, f"{base_name}_ensemble_{'instrumental_' if only_instrumental else ''}{ensemble_method}.{out_format}")
        progress(0.9, desc="Creating ensemble...")
        
        # 调用ensemble_files进行实际合并
        result = ensemble_files([
            "--files"] + all_stems + [
            "--type", ensemble_method,
            "--output", output_file
        ])
        
        if result is None:
            raise ValueError("Ensemble process failed")
            
        progress(1.0, desc="Ensemble complete")
        return output_file, f"Ensemble completed with {ensemble_method}"
    except Exception as e:
        logger.error(f"Ensemble failed: {e}")
        raise RuntimeError(f"Ensemble failed: {e}")

def update_roformer_models(category):
    return gr.update(choices=list(ROFORMER_MODELS[category].keys()))

def update_ensemble_models(category):
    return gr.update(choices=list(ROFORMER_MODELS[category].keys()))

# 界面创建函数（完整UI结构）
def create_interface():
    with gr.Blocks(title="🎵 Audio-Separator 🎵", css=CSS) as app:
        gr.Markdown("<h1 class='header-text'>🎵 Audio-Separator 🎵</h1>")
        
        with gr.Tabs():
            # 设置选项卡
            with gr.Tab("⚙️ Settings"):
                model_file_dir = gr.Textbox(value="models/", label="📂 Model Cache")
                output_dir = gr.Textbox(value="output", label="📤 Output Dir")
                output_format = gr.Dropdown(value="wav", choices=['wav', 'flac', 'mp3', 'ogg', 'opus', 'm4a', 'aiff', 'ac3'], label="🎶 Format")
                norm_threshold = gr.Slider(0.1, 1, value=0.9, step=0.1, label="🔊 Norm Thresh")
                amp_threshold = gr.Slider(0.1, 1, value=0.6, step=0.1, label="📈 Amp Thresh")
                batch_size = gr.Slider(1, 16, value=1, step=1, label="⚡ Batch Size")

            # Roformer选项卡
            with gr.Tab("🎤 Roformer"):
                roformer_audio = gr.Audio(label="🎧 Input Audio", type="filepath")
                roformer_single_stem = gr.Textbox(label="🎼 Single Stem", placeholder="e.g., Instrumental")
                roformer_category = gr.Dropdown(label="📚 Category", choices=list(ROFORMER_MODELS.keys()), value="Instrumentals")
                roformer_model = gr.Dropdown(label="🛠️ Model", choices=list(ROFORMER_MODELS["Instrumentals"].keys()))
                with gr.Row():
                    roformer_seg_size = gr.Slider(32, 4000, value=256, step=32, label="📏 Seg Size")
                    roformer_overlap = gr.Slider(2, 10, value=8, step=1, label="🔄 Overlap")
                with gr.Row():
                    roformer_pitch_shift = gr.Slider(-12, 12, value=0, step=1, label="🎵 Pitch")
                    roformer_override_seg_size = gr.Checkbox(value=False, label="🔧 Override Seg")
                roformer_button = gr.Button("✂️ Separate!", variant="primary")
                with gr.Row():
                    roformer_stem1 = gr.Audio(label="🎸 Stem 1", type="filepath", interactive=False)
                    roformer_stem2 = gr.Audio(label="🥁 Stem 2", type="filepath", interactive=False)

            # Auto Ensemble选项卡
            with gr.Tab("🎚️ Auto Ensemble"):
                ensemble_audio = gr.Audio(label="🎧 Input Audio", type="filepath")
                ensemble_category = gr.Dropdown(label="📚 Category", choices=list(ROFORMER_MODELS.keys()), value="Instrumentals")
                ensemble_models = gr.Dropdown(label="🛠️ Models", choices=list(ROFORMER_MODELS["Instrumentals"].keys()), multiselect=True)
                with gr.Row():
                    ensemble_seg_size = gr.Slider(32, 4000, value=256, step=32, label="📏 Seg Size")
                    ensemble_overlap = gr.Slider(2, 10, value=8, step=1, label="🔄 Overlap")
                with gr.Row():
                    ensemble_use_tta = gr.Checkbox(value=False, label="🔍 TTA")
                    only_instrumental = gr.Checkbox(value=False, label="🎸 Only Instr")
                ensemble_method = gr.Dropdown(label="⚙️ Method (avg_wave is recommended)", choices=['avg_wave', 'median_wave', 'max_wave', 'min_wave', 'avg_fft', 'min_fft', 'max_fft'], value='avg_wave')
                ensemble_button = gr.Button("🎛️ Run Ensemble!", variant="primary")
                ensemble_output = gr.Audio(label="🎶 Output", type="filepath", interactive=False)
                ensemble_status = gr.Textbox(label="📢 Status", interactive=False)

        gr.HTML("<div class='footer'>Powered by Audio-Separator 🌟🎶</div>")

        # 事件处理（移除下载相关绑定）
        roformer_category.change(
            lambda cat: gr.Dropdown(choices=list(ROFORMER_MODELS[cat].keys())),
            inputs=[roformer_category],
            outputs=[roformer_model]
        )
        roformer_button.click(
            roformer_separator,
            inputs=[roformer_audio, roformer_model, roformer_seg_size, roformer_override_seg_size,
                    roformer_overlap, roformer_pitch_shift, model_file_dir, output_dir, output_format,
                    norm_threshold, amp_threshold, batch_size, roformer_single_stem],
            outputs=[roformer_stem1, roformer_stem2]
        )
        ensemble_category.change(
            lambda cat: gr.Dropdown(choices=list(ROFORMER_MODELS[cat].keys())),
            inputs=[ensemble_category],
            outputs=[ensemble_models]
        )
        ensemble_button.click(
            auto_ensemble_process,
            inputs=[ensemble_audio, ensemble_models, ensemble_seg_size, ensemble_overlap, output_format,
                    ensemble_use_tta, model_file_dir, output_dir, norm_threshold, amp_threshold, batch_size,
                    ensemble_method, only_instrumental],
            outputs=[ensemble_output, ensemble_status]
        )
    
    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Music Source Separation Web UI")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()

    app = create_interface()
    app.launch(
    # server_name="0.0.0.0", 
    server_port=7860,
    # share=True  # ← 添加此参数    
    )
