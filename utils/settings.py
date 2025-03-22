import os
import json
import logging

logger = logging.getLogger(__name__)

# 默认设置
DEFAULT_SETTINGS = {
    "single_model": {
        "category": "Instrumentals",
        "model": "MelBand Roformer | INSTV7 by Gabox",
        "advanced": {
            "seg_size": 256,
            "overlap": 8,
            "pitch_shift": 0,
            "norm_threshold": 0.9,
            "amp_threshold": 0.6,
            "batch_size": 1,
            "override_seg_size": False
        }
    },
    "ensemble": {
        "category": "Instrumentals",
        "models": [],
        "method": "avg_wave",
        "only_instrumental": False,
        "advanced": {
            "seg_size": 256,
            "overlap": 8,
            "use_tta": False,
            "norm_threshold": 0.9,
            "amp_threshold": 0.6,
            "batch_size": 1
        }
    },
    "output": {
        "format": "wav",
        "model_dir": "models",
        "output_dir": "output"
    }
}

# 设置文件路径
SETTINGS_FILE = "user_settings.json"


def load_settings():
    """加载用户设置，如果不存在则返回默认设置"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                logger.info("User settings loaded successfully")
                return settings
        else:
            logger.info("No user settings found, using defaults")
            return DEFAULT_SETTINGS
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS


def save_settings(settings):
    """保存用户设置到文件"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        logger.info("Settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return False


def update_single_model_settings(category, model, **advanced_params):
    """更新单模型设置"""
    settings = load_settings()
    settings["single_model"]["category"] = category
    settings["single_model"]["model"] = model
    
    # 更新高级参数
    if advanced_params:
        for key, value in advanced_params.items():
            if key in settings["single_model"]["advanced"]:
                settings["single_model"]["advanced"][key] = value
    
    save_settings(settings)


def update_ensemble_settings(category, models, method, only_instrumental, **advanced_params):
    """更新多模型合成设置"""
    settings = load_settings()
    settings["ensemble"]["category"] = category
    settings["ensemble"]["models"] = models
    settings["ensemble"]["method"] = method
    settings["ensemble"]["only_instrumental"] = only_instrumental
    
    # 更新高级参数
    if advanced_params:
        for key, value in advanced_params.items():
            if key in settings["ensemble"]["advanced"]:
                settings["ensemble"]["advanced"][key] = value
    
    save_settings(settings)


def update_output_settings(output_format, model_dir, output_dir):
    """更新输出设置"""
    settings = load_settings()
    settings["output"]["format"] = output_format
    settings["output"]["model_dir"] = model_dir
    settings["output"]["output_dir"] = output_dir
    save_settings(settings)