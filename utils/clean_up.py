import os
from venv import logger

def cleanup_temp_files(temp_files, temp_dir=None):
    """
    清理临时文件和目录
    
    参数:
        temp_files: 需要删除的临时文件列表
        temp_dir: 临时目录路径（可选）
    """
    # 清理临时文件
    for file_path in temp_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Removed temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {file_path}: {e}")
    
    # 如果指定了临时目录，尝试删除它
    if temp_dir and os.path.exists(temp_dir):
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