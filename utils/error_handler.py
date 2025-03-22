import functools
import traceback
import logging
import gradio as gr

logger = logging.getLogger(__name__)

def catch_errors(func):
    """
    装饰器：捕获函数执行过程中的所有错误，并转换为gr.Error
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except gr.Error:
            # 如果已经是gr.Error，直接传递
            raise
        except Exception as e:
            # 记录详细错误到日志
            error_details = traceback.format_exc()
            logger.error(f"处理错误: {error_details}")
            
            # 构建友好的错误信息
            error_message = f"Error Happened: {str(e)}"
            raise gr.Error(error_message)
    return wrapper