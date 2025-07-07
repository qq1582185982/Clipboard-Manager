#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图标创建脚本
为应用程序创建ICO格式的图标文件
"""

from PIL import Image, ImageDraw
import os

def create_icon():
    """创建应用程序图标"""
    print('Creating application icon...')
    
    # 确保目录存在
    os.makedirs('assets', exist_ok=True)
    
    # 创建图标
    size = (64, 64)
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 绘制剪贴板图标
    # 外框
    draw.rectangle([8, 6, 56, 58], outline='black', fill='white', width=2)
    
    # 夹子
    draw.rectangle([20, 2, 44, 10], outline='black', fill='silver', width=1)
    draw.rectangle([22, 4, 42, 8], outline='black', fill='white', width=1)
    
    # 文本线条
    draw.line([14, 18, 50, 18], fill='black', width=2)
    draw.line([14, 26, 47, 26], fill='black', width=2)
    draw.line([14, 34, 44, 34], fill='black', width=2)
    draw.line([14, 42, 40, 42], fill='black', width=2)
    
    # 保存为ICO格式
    icon_path = 'assets/icon.ico'
    image.save(icon_path, format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
    
    print(f'Icon created successfully: {icon_path}')
    return True

if __name__ == "__main__":
    try:
        create_icon()
        print("图标创建完成！")
    except Exception as e:
        print(f"图标创建失败: {e}")
        exit(1)