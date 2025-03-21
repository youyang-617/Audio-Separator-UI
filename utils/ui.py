
import gradio as gr
from audio_separator.separator import Separator
import logging
from utils.i18n import _  # 导入翻译函数


def update_roformer_models(ROFORMER_MODELS, category):
    return gr.update(choices=list(ROFORMER_MODELS[category].keys()))

def update_ensemble_models(ROFORMER_MODELS, category):
    return gr.update(choices=list(ROFORMER_MODELS[category].keys()), value =[])  # 切换后清空选择

def create_interface(ROFORMER_MODELS, OUTPUT_FORMATS, roformer_separator, auto_ensemble_process):
    """创建音频分离界面"""
    with gr.Blocks(theme = "NoCrypt/miku", title = "🎵Roformor-based Audio-Separator 🎵") as app:
        gr.Markdown("<h1 class='header-text'>🎵 Audio-Separator 🎵</h1>")
        
        # 共享设置区域
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown(f"### 📁 {_('Basic Settings')}")
                model_file_dir = gr.Textbox(value="models", label=_("Model Cache Directory"))
                output_dir = gr.Textbox(value="output", label=_("Output Directory"))
                output_format = gr.Dropdown(
                    value="wav", 
                    choices=OUTPUT_FORMATS, 
                    label=_("Output Format")
                )
        
        # 主要功能区域
        with gr.Tabs() as tabs:
            # 单模型分离选项卡
            with gr.Tab(f"🎛️ {_('Single Model Separation')}"):
                gr.Markdown(f"### 🎯 {_('Audio Separation Process')}")
                
                # 步骤1
                gr.Markdown(f"#### {_('Step 1: Upload Audio')}")
                roformer_audio = gr.Audio(
                    label=_("Input Audio File"), 
                    type="filepath",
                    elem_id="input_audio"
                )
                
                # 步骤2
                gr.Markdown(f"#### {_('Step 2: Select Model')}")
                with gr.Row():
                    with gr.Column(scale=1):
                        roformer_category = gr.Dropdown(
                            label=_("Model Category"), 
                            choices=list(ROFORMER_MODELS.keys()), 
                            value="Instrumentals"
                        )
                    with gr.Column(scale=1):
                        roformer_model = gr.Dropdown(
                            label=_("Specific Model"), 
                            choices=list(ROFORMER_MODELS["Instrumentals"].keys()),
                            value="MelBand Roformer | INSTV7 by Gabox"
                        )
                
                roformer_single_stem = gr.Textbox(
                    label=_("Single Track Output"), 
                    placeholder=_("Example: Instrumental, Vocals. Leave empty for all tracks")
                )
                
                with gr.Accordion(_("Advanced Parameters"), open=False):
                    with gr.Row():
                        with gr.Column(scale=1):
                            roformer_seg_size = gr.Slider(32, 4000, value=256, step=32, 
                                                        label=_("Segment Size"))
                            gr.Markdown(_("*Larger values improve quality but increase memory usage*"))
                        with gr.Column(scale=1):
                            roformer_overlap = gr.Slider(2, 10, value=8, step=1, 
                                                       label=_("Overlap Factor"))
                            gr.Markdown(_("*Higher values reduce seam artifacts*"))
                    with gr.Row():
                        with gr.Column(scale=1):
                            roformer_pitch_shift = gr.Slider(-12, 12, value=0, step=1, 
                                                          label=_("Pitch Adjustment"))
                            gr.Markdown(_("*Adjust pitch, 0 for no change*"))
                        with gr.Column(scale=1):
                            roformer_override_seg_size = gr.Checkbox(
                                value=False, 
                                label=_("Override Model Segment Size")
                            )
                            gr.Markdown(_("*Force using custom segment size*"))
                    with gr.Row():
                        with gr.Column(scale=1):
                            norm_threshold = gr.Slider(0.1, 1, value=0.9, step=0.1, 
                                                     label=_("Normalization Threshold"))
                        with gr.Column(scale=1):
                            amp_threshold = gr.Slider(0.1, 1, value=0.6, step=0.1, 
                                                    label=_("Amplification Threshold"))
                    batch_size = gr.Slider(1, 16, value=1, step=1, 
                                          label=_("Batch Size"))
                    gr.Markdown(_("*Increase to improve GPU utilization, requires more VRAM*"))
                
                # 步骤3
                gr.Markdown(f"#### {_('Step 3: Start Processing')}")
                roformer_button = gr.Button(f"🚀 {_('Start Separation')}", variant="primary", size="lg")
                with gr.Row():
                    with gr.Column():
                        gr.Markdown(f"##### 🎸 {_('Main Track')}")
                        roformer_stem1 = gr.Audio(type="filepath", interactive=False)
                    with gr.Column():
                        gr.Markdown(f"##### 🥁 {_('Secondary Track')}")
                        roformer_stem2 = gr.Audio(type="filepath", interactive=False)
            
            # Ensemble选项卡
            with gr.Tab(f"🎚️ {_('Multi-model Ensemble')}"):
                gr.Markdown(f"### 🔄 {_('Multi-model Ensemble Process')}")
                
                # 步骤1
                gr.Markdown(f"#### {_('Step 1: Upload Audio')}")
                ensemble_audio = gr.Audio(label=_("Input Audio File"), type="filepath")
                
                # 步骤2
                gr.Markdown(f"#### {_('Step 2: Select Multiple Models')}")
                with gr.Row():
                    with gr.Column(scale=1):
                        ensemble_category = gr.Dropdown(
                            label=_("Model Category"), 
                            choices=list(ROFORMER_MODELS.keys()), 
                            value="Instrumentals"
                        )
                    with gr.Column(scale=1):
                        ensemble_models = gr.Dropdown(
                            label=_("Select Multiple Models"), 
                            choices=list(ROFORMER_MODELS["Instrumentals"].keys()), 
                            multiselect=True
                        )
                
                with gr.Row():
                    with gr.Column(scale=1):
                        ensemble_method = gr.Dropdown(
                            label=_("Ensemble Method"), 
                            choices=['avg_wave', 'median_wave', 'max_wave', 'min_wave', 
                                    'avg_fft', 'min_fft', 'max_fft'], 
                            value='avg_wave'
                        )
                        gr.Markdown(_("*avg_wave usually works best*"))
                    with gr.Column(scale=1):
                        only_instrumental = gr.Checkbox(
                            value=False, 
                            label=_("Instrumental Only")
                        )
                        gr.Markdown(_("*Only create instrumental track and ignore vocals*"))
                
                with gr.Accordion(_("Advanced Parameters"), open=False):
                    with gr.Row():
                        with gr.Column(scale=1):
                            ensemble_seg_size = gr.Slider(32, 4000, value=256, step=32, 
                                                        label=_("Segment Size"))
                        with gr.Column(scale=1):
                            ensemble_overlap = gr.Slider(2, 10, value=8, step=1, 
                                                       label=_("Overlap Factor"))
                    with gr.Row():
                        with gr.Column(scale=1):
                            ensemble_use_tta = gr.Checkbox(
                                value=False, 
                                label=_("Use Test Time Augmentation")
                            )
                            gr.Markdown(_("*Can improve quality but takes longer*"))
                        with gr.Column(scale=1):
                            norm_threshold_ensemble = gr.Slider(0.1, 1, value=0.9, step=0.1, 
                                                              label=_("Normalization Threshold"))
                            amp_threshold_ensemble = gr.Slider(0.1, 1, value=0.6, step=0.1, 
                                                             label=_("Amplification Threshold"))
                    batch_size_ensemble = gr.Slider(1, 16, value=1, step=1, 
                                                  label=_("Batch Size"))
                
                # 步骤3
                gr.Markdown(f"#### {_('Step 3: Start Processing')}")
                ensemble_button = gr.Button(f"🚀 {_('Start Ensemble')}", variant="primary", size="lg")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown(f"##### 🎤 {_('Vocals Track')}")
                        ensemble_vocal = gr.Audio(label=_("Ensemble Vocals"), type="filepath", interactive=False)
                    with gr.Column():
                        gr.Markdown(f"##### 🎸 {_('Instrumental Track')}")
                        ensemble_instrumental = gr.Audio(label=_("Ensemble Instrumental"), type="filepath", interactive=False)
            
            
            # 帮助选项卡
            try:
                with open("help.md", "r", encoding="utf-8") as f:
                    help_content = f.read()
            except FileNotFoundError:
                help_content = _("Help file not found, please ensure help.md exists in the project directory")
                
            with gr.Tab(f"❓ {_('Help & Instructions')}"):
                gr.Markdown(f"""
                ### 🎵 {_('Audio-Separator User Guide')}
                
                > {_('The models can be manually downloaded from : ')} [this link](https://github.com/nomadkaraoke/python-audio-separator/releases/tag/model-configs)
                
                #### {_('Basic Workflow')}
                1. **{_('Single Model Separation')}**: {_('Upload audio → Select model → Click separate')}
                2. **{_('Multi-model Ensemble')}**: {_('Upload audio → Select multiple models → Click ensemble')}
                
                #### {_('Common Issues')}
                - **{_('Long processing time')}**: {_('Large files or advanced settings increase processing time')}
                - **{_('Memory issues')}**: {_('Try reducing segment size or batch size')}
                - **{_('Sound quality issues')}**: {_('Try different models or adjust advanced parameters')}
                
                #### {_('Parameter Descriptions')}
                - **{_('Segment Size')}**: {_('Affects processing quality and memory usage')}
                - **{_('Overlap Factor')}**: {_('Affects seam smoothness')}
                - **{_('Ensemble Method')}**: {_('Different ways to combine signals')}
                
                #### {_('Recommended Model Combinations')}
                - {_('Vocal separation')}: {_('Try combinations of vocal models')}
                - {_('Instrument separation')}: {_('Use specialized instrument models')}
                """)
                
                with gr.Accordion(f"📖 {_('Click to view model selection help')}", open=False):
                    gr.Markdown(help_content)
        
        # 底部信息
        gr.HTML("<div class='footer'>Powered by Audio-Separator 🌟🎶</div>")
        
        # 绑定事件处理
        roformer_category.change(
            lambda cat: update_roformer_models(ROFORMER_MODELS, cat),
            inputs=[roformer_category],
            outputs=[roformer_model]
        )
        
        roformer_button.click(
            roformer_separator,
            inputs=[
                roformer_audio, roformer_model, roformer_seg_size, 
                roformer_override_seg_size, roformer_overlap, roformer_pitch_shift, 
                model_file_dir, output_dir, output_format, norm_threshold, 
                amp_threshold, batch_size, roformer_single_stem
            ],
            outputs=[roformer_stem1, roformer_stem2]
        )
        
        ensemble_category.change(
            lambda cat: update_ensemble_models(ROFORMER_MODELS, cat),
            inputs=[ensemble_category],
            outputs=[ensemble_models]
        )
        
        ensemble_button.click(
            auto_ensemble_process,
            inputs=[
                ensemble_audio, ensemble_models, ensemble_seg_size, 
                ensemble_overlap, output_format, ensemble_use_tta, 
                model_file_dir, output_dir, norm_threshold_ensemble, 
                amp_threshold_ensemble, batch_size_ensemble, 
                ensemble_method, only_instrumental
            ],
             outputs=[ensemble_vocal, ensemble_instrumental]
        )
    
    return app