
import gradio as gr
from audio_separator.separator import Separator
import logging

# 将界面相关的函数和逻辑移动到这里
def update_roformer_models(ROFORMER_MODELS, category):
    return gr.update(choices=list(ROFORMER_MODELS[category].keys()))

def update_ensemble_models(ROFORMER_MODELS, category):
    return gr.update(choices=list(ROFORMER_MODELS[category].keys()))

def create_interface(ROFORMER_MODELS, OUTPUT_FORMATS, roformer_separator, auto_ensemble_process):
    """创建音频分离界面"""
    with gr.Blocks(theme = "NoCrypt/miku", title = "🎵 Audio-Separator 🎵") as app:
        gr.Markdown("<h1 class='header-text'>🎵 Audio-Separator 🎵</h1>")
        
        # 共享设置区域
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📁 基础设置")
                model_file_dir = gr.Textbox(value="models", label="模型缓存目录，模型将下载到项目根目录下该文件夹")
                output_dir = gr.Textbox(value="output", label="输出目录，模型分离结果将保存到该目录")
                output_format = gr.Dropdown(
                    value="wav", 
                    choices=OUTPUT_FORMATS, 
                    label="输出格式"
                )
        
        # 主要功能区域
        with gr.Tabs() as tabs:
            # 单模型分离选项卡
            with gr.Tab("🎛️ 单模型分离"):
                gr.Markdown("### 🎯 分离音频处理流程")
                
                # 步骤1
                gr.Markdown("#### 步骤 1: 上传音频")
                roformer_audio = gr.Audio(
                    label="输入音频文件", 
                    type="filepath",
                    elem_id="input_audio"
                )
                
                # 步骤2
                gr.Markdown("#### 步骤 2: 选择模型与设置")
                with gr.Row():
                    with gr.Column(scale=1):
                        roformer_category = gr.Dropdown(
                            label="模型类别", 
                            choices=list(ROFORMER_MODELS.keys()), 
                            value="Instrumentals"
                        )
                    with gr.Column(scale=1):
                        roformer_model = gr.Dropdown(
                            label="具体模型", 
                            choices=list(ROFORMER_MODELS["Instrumentals"].keys()),
                            value="MelBand Roformer | INSTV7 by Gabox"
                        )
                
                roformer_single_stem = gr.Textbox(
                    label="只输出单个轨道(可选)", 
                    placeholder="例如: Instrumental、Vocals，留空则输出所有轨道"
                )
                
                with gr.Accordion("高级参数设置", open=False):
                    with gr.Row():
                        with gr.Column(scale=1):
                            roformer_seg_size = gr.Slider(32, 4000, value=256, step=32, 
                                                        label="分段大小")
                            gr.Markdown("*较大值提高质量但增加内存占用*")
                        with gr.Column(scale=1):
                            roformer_overlap = gr.Slider(2, 10, value=8, step=1, 
                                                       label="重叠系数")
                            gr.Markdown("*较高值可减少接缝痕迹*")
                    with gr.Row():
                        with gr.Column(scale=1):
                            roformer_pitch_shift = gr.Slider(-12, 12, value=0, step=1, 
                                                          label="音高调整")
                            gr.Markdown("*调整音高，0为不调整*")
                        with gr.Column(scale=1):
                            roformer_override_seg_size = gr.Checkbox(
                                value=False, 
                                label="覆盖模型分段大小"
                            )
                            gr.Markdown("*强制使用自定义分段大小*")
                    with gr.Row():
                        with gr.Column(scale=1):
                            norm_threshold = gr.Slider(0.1, 1, value=0.9, step=0.1, 
                                                     label="归一化阈值")
                        with gr.Column(scale=1):
                            amp_threshold = gr.Slider(0.1, 1, value=0.6, step=0.1, 
                                                    label="放大阈值")
                    batch_size = gr.Slider(1, 16, value=1, step=1, 
                                          label="批处理大小")
                    gr.Markdown("*增大可提高GPU利用率，但需要更多显存*")
                
                # 步骤3
                gr.Markdown("#### 步骤 3: 开始处理")
                roformer_button = gr.Button("🚀 开始分离", variant="primary", size="lg")
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("##### 🎸 主要轨道")
                        roformer_stem1 = gr.Audio(type="filepath", interactive=False)
                    with gr.Column():
                        gr.Markdown("##### 🥁 次要轨道")
                        roformer_stem2 = gr.Audio(type="filepath", interactive=False)
            
            # 合奏选项卡
            with gr.Tab("🎚️ 模型合奏"):
                gr.Markdown("### 🔄 多模型合奏流程")
                
                # 步骤1
                gr.Markdown("#### 步骤 1: 上传音频")
                ensemble_audio = gr.Audio(label="输入音频文件", type="filepath")
                
                # 步骤2
                gr.Markdown("#### 步骤 2: 选择多个模型")
                with gr.Row():
                    with gr.Column(scale=1):
                        ensemble_category = gr.Dropdown(
                            label="模型类别", 
                            choices=list(ROFORMER_MODELS.keys()), 
                            value="Instrumentals"
                        )
                    with gr.Column(scale=1):
                        ensemble_models = gr.Dropdown(
                            label="选择多个模型", 
                            choices=list(ROFORMER_MODELS["Instrumentals"].keys()), 
                            multiselect=True
                        )
                
                with gr.Row():
                    with gr.Column(scale=1):
                        ensemble_method = gr.Dropdown(
                            label="合奏方法", 
                            choices=['avg_wave', 'median_wave', 'max_wave', 'min_wave', 
                                    'avg_fft', 'min_fft', 'max_fft'], 
                            value='avg_wave'
                        )
                        gr.Markdown("*avg_wave通常效果最佳*")
                    with gr.Column(scale=1):
                        only_instrumental = gr.Checkbox(
                            value=False, 
                            label="仅保留伴奏轨道"
                        )
                        gr.Markdown("*仅合奏伴奏轨道而忽略人声*")
                
                with gr.Accordion("高级参数设置", open=False):
                    with gr.Row():
                        with gr.Column(scale=1):
                            ensemble_seg_size = gr.Slider(32, 4000, value=256, step=32, 
                                                        label="分段大小")
                        with gr.Column(scale=1):
                            ensemble_overlap = gr.Slider(2, 10, value=8, step=1, 
                                                       label="重叠系数")
                    with gr.Row():
                        with gr.Column(scale=1):
                            ensemble_use_tta = gr.Checkbox(
                                value=False, 
                                label="使用测试时增强(TTA)"
                            )
                            gr.Markdown("*可提高质量但处理时间更长*")
                        with gr.Column(scale=1):
                            norm_threshold_ensemble = gr.Slider(0.1, 1, value=0.9, step=0.1, 
                                                              label="归一化阈值")
                            amp_threshold_ensemble = gr.Slider(0.1, 1, value=0.6, step=0.1, 
                                                             label="放大阈值")
                    batch_size_ensemble = gr.Slider(1, 16, value=1, step=1, 
                                                  label="批处理大小")
                
                # 步骤3
                gr.Markdown("#### 步骤 3: 开始合奏处理")
                ensemble_button = gr.Button("🚀 开始合奏", variant="primary", size="lg")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("##### 🎤 人声轨道")
                        ensemble_vocal = gr.Audio(label="合奏后的人声", type="filepath", interactive=False)
                    with gr.Column():
                        gr.Markdown("##### 🎸 伴奏轨道")
                        ensemble_instrumental = gr.Audio(label="合奏后的伴奏", type="filepath", interactive=False)
            
            # 帮助选项卡
            try:
                with open("help.md", "r", encoding="utf-8") as f:
                    help_content = f.read()
            except FileNotFoundError:
                help_content = "帮助文件未找到，请确保项目根目录存在help.md文件"
                
            with gr.Tab("❓ 帮助与说明"):
                gr.Markdown("""
                ### 🎵 Audio-Separator 使用指南
                
                #### 基本使用流程
                1. **单模型分离**: 上传音频 → 选择模型 → 点击分离
                2. **模型合奏**: 上传音频 → 选择多个模型 → 点击合奏
                
                #### 常见问题
                - **处理时间长**: 大文件或高级参数设置会增加处理时间
                - **内存不足**: 尝试减小分段大小或批处理大小
                - **音质问题**: 尝试不同模型或调整高级参数
                
                #### 参数说明
                - **分段大小**: 影响处理质量和内存使用
                - **重叠系数**: 影响接缝平滑度
                - **合奏方法**: 不同的信号组合方式
                
                #### 推荐模型组合
                - 人声分离: 尝试多个人声模型组合
                - 乐器分离: 使用专门的乐器分离模型
                """)
                
                with gr.Accordion("📖 点击查看模型选择帮助", open=False):
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
            update_ensemble_models,
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