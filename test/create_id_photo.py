#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
@DATE: 2024/9/5 21:39
@File: create_id_photo.py
@IDE: pycharm
@Description:
    用于测试创建证件照
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hivision.creator import IDCreator
import cv2
import os

now_dir = os.path.dirname(__file__)
image_path = os.path.join(os.path.dirname(now_dir), "demo", "images", "test.jpg")
output_dir = os.path.join(now_dir, "temp")

print(f"读取图片: {image_path}")
image = cv2.imread(image_path)
if image is None:
    print("错误：无法读取图片")
    exit(1)

print("创建 IDCreator...")
creator = IDCreator()

print("开始处理图片...")
result = creator(image)

print("保存结果...")
os.makedirs(output_dir, exist_ok=True)
cv2.imwrite(os.path.join(output_dir, "result.png"), result.standard)
cv2.imwrite(os.path.join(output_dir, "result_hd.png"), result.hd)
print("完成！")

os._exit(0)
