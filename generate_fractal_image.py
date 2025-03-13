from PIL import Image
import numpy as np
import colorsys
import math
import tempfile
import os

def mandelbrot(c, max_iter):
    z = 0
    n = 0
    while abs(z) <= 2 and n < max_iter:
        z = z*z + c
        n += 1
    return n, z

def generate_fractal_image(file_path, target_size_kb, image_format='jpeg'):
    """
    生成带有Mandelbrot分形图案的图片，精确控制文件大小
    :param file_path: 图片保存路径
    :param target_size_kb: 目标文件大小（单位KB）
    :param image_format: 图片格式，支持jpeg, png, gif, webp
    """
    width = 1024
    height = 768
    max_iter = 80
    quality = 95
    resize_factor = 1.0
    
    # 对于大尺寸文件，增加初始分辨率
    if target_size_kb > 500:
        resize_factor = min(2.0, target_size_kb / 500)

    if resize_factor != 1.0:
        width = int(width * resize_factor)
        height = int(height * resize_factor)
    # 创建空白图像
    img = Image.new('RGB', (width, height))
    pixels = img.load()

    # 生成分形图案
    for x in range(width):
        for y in range(height):
            # 将像素坐标映射到复平面
            re = (x - width/2.0)*4.0/width
            im = (y - height/2.0)*4.0/height
            c = complex(re, im)
            # 计算Mandelbrot值
            m, z = mandelbrot(c, max_iter)
            # 根据迭代次数设置颜色
            if m < max_iter:
                # Monochromatic blue-based coloring
                hue = 0.6  # Blue base color
                intensity = m / max_iter
                saturation = 0.3 + intensity * 0.2  # Subtle saturation variation
                value = 0.4 + intensity * 0.3  # Controlled brightness
            else:
                # Dark blue for points outside the set
                hue = 0.6
                saturation = 0.2
                value = 0.2

            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            pixels[x, y] = tuple(int(c * 255) for c in rgb)

    # 保存图片
    if resize_factor != 1.0:
        img = img.resize((width, height))
    
    current_quality = quality
    current_resize = resize_factor
    tolerance = 0.02  # 进一步降低容差以获得更精确的大小
    best_diff = float('inf')
    best_params = (current_quality, current_resize)
    temp_path = None
    max_iterations = 20  # 增加最大迭代次数
    for _ in range(max_iterations):
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmpfile:
            temp_path = tmpfile.name
            resized_width = int(width * current_resize)
            resized_height = int(height * current_resize)
            resized_img = img.resize((resized_width, resized_height))
            resized_img.save(temp_path, format=image_format, quality=current_quality, optimize=True)

        file_size = os.path.getsize(temp_path) / 1024
        size_diff = abs(file_size - target_size_kb)

        if size_diff < best_diff:
            best_diff = size_diff
            best_params = (current_quality, current_resize)

        if size_diff <= target_size_kb * tolerance:
            break

        if file_size > target_size_kb:
            # 如果文件太大，先降低质量，质量降到最低后再降低尺寸
            current_quality = max(1, current_quality - 5)
            if current_quality == 1:
                current_resize *= 0.9
                current_quality = quality
        else:  # 文件过小的情况
            # 如果文件太小，更激进地增加质量和尺寸
            # 首先尝试增加质量
            if current_quality < 100:
                current_quality = min(100, current_quality + 10)  # 更大的质量增量
            else:
                # 质量已经是最大，增加尺寸
                size_ratio = target_size_kb / max(file_size, 1)  # 避免除以零
                # 根据目标大小和当前大小的比例调整尺寸因子
                # 使用平方根来避免过度调整
                resize_multiplier = min(1.5, math.sqrt(size_ratio))
                current_resize *= resize_multiplier
                current_quality = quality  # 重置质量
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # 使用找到的最佳参数生成最终图片
    final_quality, final_resize = best_params
    final_width = int(width * final_resize)
    final_height = int(height * final_resize)
    final_img = img.resize((final_width, final_height))
    final_img.save(file_path, format=image_format, quality=final_quality, optimize=True)
    
    # 清理最后的临时文件
    if temp_path and os.path.exists(temp_path):
        os.unlink(temp_path)


generate_fractal_image('100K.webp', 100, 'webp')