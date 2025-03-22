import gradio as gr
from utils.error_handler import catch_errors # 错误处理装饰器
from utils.i18n import _  # i18n函数
from utils.settings import load_settings, update_single_model_settings, update_ensemble_settings, update_output_settings


def update_roformer_models(ROFORMER_MODELS, category):
    return gr.update(choices=list(ROFORMER_MODELS[category].keys()))


def update_ensemble_models(ROFORMER_MODELS, category):
    return gr.update(
        choices=list(ROFORMER_MODELS[category].keys()), value=[]
    )  # 切换后清空选择

@catch_errors
def validate_ensemble_inputs(ensemble_func, audio, model_keys, *args):
    """
    验证ensemble输入参数，确保至少选择两个模型

    Args:
        ensemble_func: 原始的ensemble处理函数
        audio: 输入音频文件
        model_keys: 选择的模型列表
        *args: 其他参数将原样传递给原始函数
    """

    # 检查模型选择 - 确保至少选择了2个模型
    if not model_keys or len(model_keys) <= 1:
        raise gr.Error(_("Please select at least 2 model for ensemble processing"))

    # 验证通过后，调用原始处理函数
    return ensemble_func(audio, model_keys, *args)


def create_interface(
    ROFORMER_MODELS, OUTPUT_FORMATS, roformer_separator, auto_ensemble_process
):
    """创建音频分离界面"""
    # 加载用户设置
    user_settings = load_settings()
    
    with gr.Blocks(
        theme="NoCrypt/miku", title="🎵Roformor-based Audio-Separator 🎵"
        # title="🎵Roformor-based Audio-Separator 🎵"
    ) as app:
        gr.Markdown("<h1 class='header-text'>🎵 Audio-Separator 🎵</h1>")
        
        # 共享设置区域
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown(f"### 📁 {_('Basic Settings')}")
                model_file_dir = gr.Textbox(
                    value=user_settings["output"]["model_dir"], 
                    label=_("Model Cache Directory")
                )
                output_dir = gr.Textbox(
                    value=user_settings["output"]["output_dir"], 
                    label=_("Output Directory")
                )
                output_format = gr.Dropdown(
                    value=user_settings["output"]["format"], 
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
                    label=_("Input Audio File"), type="filepath", elem_id="input_audio"
                )

                # 步骤2
                gr.Markdown(f"#### {_('Step 2: Select Model')}")
                with gr.Row():
                    with gr.Column(scale=1):
                        roformer_category = gr.Dropdown(
                            label=_("Model Category"),
                            choices=list(ROFORMER_MODELS.keys()),
                            value=user_settings["single_model"]["category"],
                        )
                    with gr.Column(scale=1):
                        # 使用保存的类别获取模型列表
                        initial_category = user_settings["single_model"]["category"]
                        roformer_model = gr.Dropdown(
                            label=_("Specific Model"),
                            choices=list(ROFORMER_MODELS[initial_category].keys()),
                            value=user_settings["single_model"]["model"] if user_settings["single_model"]["model"] in ROFORMER_MODELS[initial_category] else list(ROFORMER_MODELS[initial_category].keys())[0],
                        )

                roformer_single_stem = gr.Textbox(
                    label=_("Single Track Output"),
                    placeholder=_(
                        "Example: Instrumental, Vocals. Leave empty for all tracks"
                    ),
                )

                with gr.Accordion(_("Advanced Parameters"), open=False):
                    with gr.Row():
                        with gr.Column(scale=1):
                            roformer_seg_size = gr.Slider(
                                32, 4000, 
                                value=user_settings["single_model"]["advanced"]["seg_size"],
                                step=32, 
                                label=_("Segment Size")
                            )
                            gr.Markdown(
                                _("*Larger values improve quality but increase memory usage*")
                            )
                        with gr.Column(scale=1):
                            roformer_overlap = gr.Slider(
                                2, 10, 
                                value=user_settings["single_model"]["advanced"]["overlap"],
                                step=1, 
                                label=_("Overlap Factor")
                            )
                            gr.Markdown(_("*Higher values reduce seam artifacts*"))
                    with gr.Row():
                        with gr.Column(scale=1):
                            roformer_pitch_shift = gr.Slider(
                                -12, 12, 
                                value=user_settings["single_model"]["advanced"]["pitch_shift"],
                                step=1, 
                                label=_("Pitch Adjustment")
                            )
                            gr.Markdown(_("*Adjust pitch, 0 for no change*"))
                        with gr.Column(scale=1):
                            roformer_override_seg_size = gr.Checkbox(
                                value=user_settings["single_model"]["advanced"]["override_seg_size"],
                                label=_("Override Model Segment Size")
                            )
                            gr.Markdown(_("*Force using custom segment size*"))
                    with gr.Row():
                        with gr.Column(scale=1):
                            norm_threshold = gr.Slider(
                                0.1, 1,
                                value=user_settings["single_model"]["advanced"]["norm_threshold"],
                                step=0.1,
                                label=_("Normalization Threshold"),
                            )
                        with gr.Column(scale=1):
                            amp_threshold = gr.Slider(
                                0.1, 1,
                                value=user_settings["single_model"]["advanced"]["amp_threshold"],
                                step=0.1,
                                label=_("Amplification Threshold"),
                            )
                    batch_size = gr.Slider(
                        1, 16, 
                        value=user_settings["single_model"]["advanced"]["batch_size"],
                        step=1, 
                        label=_("Batch Size")
                    )

                # 步骤3
                gr.Markdown(f"#### {_('Step 3: Start Processing')}")
                roformer_button = gr.Button(
                    f"🚀 {_('Start Separation')}", variant="primary", size="lg"
                )
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
                gr.Markdown("> " + _("It is recommended to choose 2-5 models for integration. Integrating multiple good models can improve the separation effect. On the contrary, a poor model will drag down the overall effect."))
                with gr.Row():
                    with gr.Column(scale=1):
                        ensemble_category = gr.Dropdown(
                            label=_("Model Category"),
                            choices=list(ROFORMER_MODELS.keys()),
                            value=user_settings["ensemble"]["category"],
                        )
                    with gr.Column(scale=1):
                        ensemble_models = gr.Dropdown(
                            label=_("Select Multiple Models"),
                            choices=list(ROFORMER_MODELS[user_settings["ensemble"]["category"]].keys()),
                            value=user_settings["ensemble"]["models"],
                            multiselect=True,
                        )

                with gr.Row():
                    with gr.Column(scale=1):
                        ensemble_method = gr.Dropdown(
                            label=_("Ensemble Method"),
                            choices=[
                                "avg_wave",
                                "median_wave",
                                "max_wave",
                                "min_wave",
                                "avg_fft",
                                "min_fft",
                                "max_fft",
                            ],
                            value=user_settings["ensemble"]["method"],
                        )
                        gr.Markdown(_("*avg_wave usually works best*"))
                    with gr.Column(scale=1):
                        only_instrumental = gr.Checkbox(
                            value=user_settings["ensemble"]["only_instrumental"],
                            label=_("Instrumental Only")
                        )
                        gr.Markdown(
                            _("*Only create instrumental track and ignore vocals*")
                        )

                with gr.Accordion(_("Advanced Parameters"), open=False):
                    with gr.Row():
                        with gr.Column(scale=1):
                            ensemble_seg_size = gr.Slider(
                                32, 4000, 
                                value=user_settings["ensemble"]["advanced"]["seg_size"],
                                step=32, 
                                label=_("Segment Size")
                            )
                        with gr.Column(scale=1):
                            ensemble_overlap = gr.Slider(
                                2, 10, 
                                value=user_settings["ensemble"]["advanced"]["overlap"],
                                step=1, 
                                label=_("Overlap Factor")
                            )
                    with gr.Row():
                        with gr.Column(scale=1):
                            ensemble_use_tta = gr.Checkbox(
                                value=user_settings["ensemble"]["advanced"]["use_tta"],
                                label=_("Use Test Time Augmentation")
                            )
                            gr.Markdown(_("*Can improve quality but takes longer*"))
                        with gr.Column(scale=1):
                            norm_threshold_ensemble = gr.Slider(
                                0.1, 1,
                                value=user_settings["ensemble"]["advanced"]["norm_threshold"],
                                step=0.1,
                                label=_("Normalization Threshold"),
                            )
                            amp_threshold_ensemble = gr.Slider(
                                0.1, 1,
                                value=user_settings["ensemble"]["advanced"]["amp_threshold"],
                                step=0.1,
                                label=_("Amplification Threshold"),
                            )
                    batch_size_ensemble = gr.Slider(
                        1, 16, 
                        value=user_settings["ensemble"]["advanced"]["batch_size"],
                        step=1, 
                        label=_("Batch Size")
                    )

                # 步骤3
                gr.Markdown(f"#### {_('Step 3: Start Processing')}")
                ensemble_button = gr.Button(
                    f"🚀 {_('Start Ensemble')}", variant="primary", size="lg"
                )

                with gr.Row():
                    with gr.Column():
                        gr.Markdown(f"##### 🎤 {_('Vocals Track')}")
                        ensemble_vocal = gr.Audio(
                            label=_("Ensemble Vocals"),
                            type="filepath",
                            interactive=False,
                        )
                    with gr.Column():
                        gr.Markdown(f"##### 🎸 {_('Instrumental Track')}")
                        ensemble_instrumental = gr.Audio(
                            label=_("Ensemble Instrumental"),
                            type="filepath",
                            interactive=False,
                        )

            # 帮助选项卡
            try:
                with open("docs/help.md", "r", encoding="utf-8") as f:
                    help_content = f.read()
            except FileNotFoundError:
                help_content = _(
                    "Help file not found, please ensure help.md exists in the project directory"
                )

            with gr.Tab(f"❓ {_('Help & Instructions')}"):
                gr.Markdown(
                    f"""
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
                
                > 大陆下载模型可以通过尝试[GitHub 文件加速 | 免费公益 GitHub 文件下载加速服务 | 一个小站](https://gh-proxy.ygxz.in/)或[Github Proxy 文件代理加速](https://github.akams.cn/)等文件下载公益站点下载[this link](https://github.com/nomadkaraoke/python-audio-separator/releases/tag/model-configs)这里的模型，感谢慈善家们😭（右键所选模型→复制链接→粘贴到代理站）
                """
                )

                with gr.Accordion(
                    f"📖 {_('Click to view model selection help')}", open=False
                ):
                    gr.Markdown(help_content)

        # 底部信息
        gr.HTML("<div class='footer'>Powered by Audio-Separator 🌟🎶</div>")

        # 绑定事件处理
        def on_roformer_change(category, model, seg_size, override_seg_size, 
                              overlap, pitch_shift, norm_thresh, amp_thresh, batch_size):
            update_single_model_settings(
                category, model, 
                seg_size=seg_size,
                override_seg_size=override_seg_size,
                overlap=overlap,
                pitch_shift=pitch_shift,
                norm_threshold=norm_thresh,
                amp_threshold=amp_thresh,
                batch_size=batch_size
            )
            return

        def on_ensemble_change(category, models, method, only_instrumental, seg_size, 
                              overlap, use_tta, norm_thresh, amp_thresh, batch_size):
            update_ensemble_settings(
                category, models, method, only_instrumental,
                seg_size=seg_size,
                overlap=overlap,
                use_tta=use_tta,
                norm_threshold=norm_thresh,
                amp_threshold=amp_thresh,
                batch_size=batch_size
            )
            return

        def on_output_change(format, model_dir, output_dir):
            update_output_settings(format, model_dir, output_dir)
            return

        # 绑定各种UI元素的change事件
        roformer_model.change(
            on_roformer_change,
            inputs=[
                roformer_category, roformer_model, roformer_seg_size,
                roformer_override_seg_size, roformer_overlap, roformer_pitch_shift,
                norm_threshold, amp_threshold, batch_size
            ],
            outputs=[]
        )
        
        roformer_category.change(
            lambda category: update_roformer_models(ROFORMER_MODELS, category),
            inputs=[roformer_category],
            outputs=[roformer_model]
        )

        # 绑定高级参数的变更事件
        for param in [roformer_seg_size, roformer_override_seg_size, roformer_overlap, 
                    roformer_pitch_shift, norm_threshold, amp_threshold, batch_size]:
            param.change(
                on_roformer_change,
                inputs=[
                    roformer_category, roformer_model, roformer_seg_size,
                    roformer_override_seg_size, roformer_overlap, roformer_pitch_shift,
                    norm_threshold, amp_threshold, batch_size
                ],
                outputs=[]
            )

        # 绑定ensemble相关的变更事件
        ensemble_category.change(
            lambda category: update_ensemble_models(ROFORMER_MODELS, category),
            inputs=[ensemble_category],
            outputs=[ensemble_models]
        )

        ensemble_models.change(
            on_ensemble_change,
            inputs=[
                ensemble_category, ensemble_models, ensemble_method, only_instrumental,
                ensemble_seg_size, ensemble_overlap, ensemble_use_tta, 
                norm_threshold_ensemble, amp_threshold_ensemble, batch_size_ensemble
            ],
            outputs=[]
        )

        # 绑定ensemble的其他设置变更事件
        for param in [ensemble_method, only_instrumental, ensemble_seg_size, ensemble_overlap,
                    ensemble_use_tta, norm_threshold_ensemble, amp_threshold_ensemble, 
                    batch_size_ensemble]:
            param.change(
                on_ensemble_change,
                inputs=[
                    ensemble_category, ensemble_models, ensemble_method, only_instrumental,
                    ensemble_seg_size, ensemble_overlap, ensemble_use_tta, 
                    norm_threshold_ensemble, amp_threshold_ensemble, batch_size_ensemble
                ],
                outputs=[]
            )

        # 绑定输出设置变更事件
        for param in [output_format, model_file_dir, output_dir]:
            param.change(
                on_output_change,
                inputs=[output_format, model_file_dir, output_dir],
                outputs=[]
            )

        roformer_button.click(
            roformer_separator,
            inputs=[
                roformer_audio,
                roformer_model,
                roformer_seg_size,
                roformer_override_seg_size,
                roformer_overlap,
                roformer_pitch_shift,
                model_file_dir,
                output_dir,
                output_format,
                norm_threshold,
                amp_threshold,
                batch_size,
                roformer_single_stem,
            ],
            outputs=[roformer_stem1, roformer_stem2],
        )


        ensemble_button.click(
            lambda audio, models, *args: validate_ensemble_inputs(
                auto_ensemble_process, audio, models, *args
            ),
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
