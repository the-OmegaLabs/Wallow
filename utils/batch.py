"""
批量处理工具 - 用于处理多个图像文件
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..core import WallowImage


def batch_process(file_paths, process_func, output_dir=None, threads=4, **kwargs):
    """
    批量处理图像文件

    参数:
        file_paths: 文件路径列表
        process_func: 处理函数，接收WallowImage对象并返回处理后的WallowImage
        output_dir: 输出目录 (如果未指定，则使用原目录)
        threads: 并行处理的线程数
        **kwargs: 传递给process_func的额外参数

    返回:
        成功处理的文件数量
    """
    results = {}
    processed_count = 0

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {}

        for file_path in file_paths:
            future = executor.submit(
                _process_single_file,
                file_path,
                process_func,
                output_dir,
                **kwargs
            )
            futures[future] = file_path

        for future in as_completed(futures):
            file_path = futures[future]
            try:
                result = future.result()
                results[file_path] = result
                processed_count += 1
                print(f"处理完成: {file_path}")
            except Exception as e:
                results[file_path] = e
                print(f"处理失败: {file_path} - {str(e)}")

    return processed_count


def _process_single_file(file_path, process_func, output_dir, **kwargs):
    """处理单个文件的辅助函数"""
    try:
        img = WallowImage.open(file_path)
        processed_img = process_func(img, **kwargs)

        if output_dir:
            file_name = os.path.basename(file_path)
            output_path = os.path.join(output_dir, file_name)
            os.makedirs(output_dir, exist_ok=True)
        else:
            # 在原始文件名前添加前缀
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            name_parts = file_name.split('.')
            output_path = os.path.join(
                file_dir,
                f"{name_parts[0]}_processed.{'.'.join(name_parts[1:])}"
            )

        processed_img.save(output_path)
        return True
    except Exception as e:
        raise Exception(f"处理错误: {str(e)}")


def process_folder(folder_path, process_func, output_dir=None,
                   extensions=None, recursive=False, **kwargs):
    """
    处理文件夹中的所有图像

    参数:
        folder_path: 要处理的文件夹路径
        process_func: 处理函数
        output_dir: 输出目录
        extensions: 要处理的文件扩展名列表 (如 ['.jpg', '.png'])
        recursive: 是否递归处理子文件夹
        **kwargs: 传递给process_func的额外参数

    返回:
        成功处理的文件数量
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

    extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
                  for ext in extensions]

    file_paths = []

    if recursive:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if os.path.splitext(file)[1].lower() in extensions:
                    file_paths.append(os.path.join(root, file))
    else:
        for file in os.listdir(folder_path):
            if os.path.splitext(file)[1].lower() in extensions:
                file_paths.append(os.path.join(folder_path, file))

    return batch_process(file_paths, process_func, output_dir, **kwargs)
