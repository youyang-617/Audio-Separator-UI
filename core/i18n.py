# Original author: https://github.com/Eddycrack864/UVR5-UI/blob/main/assets/i18n/i18n.py
# Modified by uy: https://github.com/youyang-617
import os
import json
import logging
from pathlib import Path
from locale import getdefaultlocale

logger = logging.getLogger(__name__)

class I18n:
    """音频分离器国际化类"""
    
    def __init__(self, language=None, config_path=None):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.language_dir = os.path.join(self.base_dir, "i18n")
        
        # 尝试从配置文件加载语言设置
        if config_path:
            try:
                with open(config_path, "r", encoding="utf8") as file:
                    config = json.load(file)
                    override = config.get("language", {}).get("override", False)
                    selected_lang = config.get("language", {}).get("selected", None)
                    
                    if override and selected_lang:
                        self.language = selected_lang
                        logger.info(f"Using language from config: {self.language}")
                    else:
                        self.language = self._detect_language(language)
            except Exception as e:
                logger.warning(f"Failed to load language from config: {e}")
                self.language = self._detect_language(language)
        else:
            self.language = self._detect_language(language)
            
        # 确保语言目录存在
        os.makedirs(self.language_dir, exist_ok=True)
        
        # 加载语言文件
        self.translations = self._load_translations()
        logger.info(f"Loaded translations for {self.language}")
    
    def _detect_language(self, language):
        """检测系统语言或使用指定语言"""
        language = language or getdefaultlocale()[0]
        lang_prefix = language[:2] if language is not None else "en"
        
        # 获取可用语言列表
        available_languages = self._get_available_languages()
        
        # 查找匹配的语言
        matching_languages = [
            lang for lang in available_languages if lang.startswith(lang_prefix)
        ]
        
        # 如果找到匹配的语言，使用第一个；否则回退到英语
        selected_language = matching_languages[0] if matching_languages else "en_US"
        logger.info(f"Detected language: {selected_language}")
        return selected_language
    
    def _get_available_languages(self):
        """获取可用的语言列表"""
        try:
            language_files = [path.stem for path in Path(self.language_dir).glob("*.json")]
            return language_files
        except Exception:
            logger.warning("Failed to get available languages")
            return ["en_US"]
    
    def _load_translations(self):
        """加载翻译文件"""
        try:
            file_path = os.path.join(self.language_dir, f"{self.language}.json")
            
            # 如果文件不存在，尝试创建一个空的翻译文件
            if not os.path.exists(file_path):
                logger.warning(f"Translation file not found: {file_path}, creating an empty one")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
                return {}
                
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Failed to load language file: {e}")
            return {}
    
    def __call__(self, key):
        """翻译函数，使用方式: _('key')"""
        return self.translations.get(key, key)
    
    def get_languages(self):
        """获取所有可用语言"""
        return self._get_available_languages()

# 创建全局翻译实例
_ = I18n()