"""
优化版证件照生成器
避免重复生成，提供更清晰的测试选项
"""

import os
import requests
import base64
from datetime import datetime
from typing import Dict, Optional, List
import json


class OptimizedIDPhotoGenerator:
    """优化版证件照生成器 - 避免重复生成"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8080"):
        self.base_url = base_url
        self.output_dir = "output"
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 证件照尺寸配置
        self.photo_sizes = {
            "一寸": {"width": 295, "height": 413},
            "二寸": {"width": 413, "height": 579},
            "小二寸": {"width": 413, "height": 531},
            "护照": {"width": 390, "height": 567},
            "驾照": {"width": 260, "height": 378},
            "社保": {"width": 358, "height": 441},
        }
        
        # 背景色配置（RGB格式）
        self.background_colors = {
            "蓝色": (86, 140, 212),
            "白色": (255, 255, 255),
            "红色": (205, 50, 57),
            "灰色": (128, 128, 128),
        }
        
        # 排版尺寸配置
        self.layout_sizes = {
            "六寸": {"width": 1800, "height": 1200},
            "五寸": {"width": 1500, "height": 1050},
            "四寸": {"width": 1200, "height": 800},
        }
        
        # 已生成的文件记录（避免重复）
        self.generated_files = set()

    def decode_base64_image(self, base64_str: str) -> bytes:
        """解码base64图片数据，处理data URI前缀"""
        if base64_str.startswith('data:image'):
            base64_str = base64_str.split(',')[1]
        return base64.b64decode(base64_str)

    def save_image(self, image_data: bytes, filename: str) -> str:
        """保存图片到输出目录"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(image_data)
        return filepath

    def generate_file_key(self, size_name: str, bg_color_name: str = None, file_type: str = "transparent") -> str:
        """生成文件唯一标识符"""
        if file_type == "transparent":
            return f"{size_name}_透明底"
        elif file_type == "background":
            return f"{size_name}_{bg_color_name}背景"
        elif file_type == "layout":
            return f"{size_name}_{bg_color_name}背景_排版"
        return f"{size_name}_{file_type}"

    def step1_generate_transparent_photo(self, input_image_path: str, size_name: str = "一寸") -> Optional[Dict]:
        """步骤1：生成透明底证件照（避免重复）"""
        
        # 检查是否已生成
        file_key = self.generate_file_key(size_name, file_type="transparent")
        if file_key in self.generated_files:
            print(f"⏭️  跳过：{size_name}透明底证件照已存在")
            return {"status": True, "skipped": True}
        
        print(f"\n=== 步骤1：生成{size_name}透明底证件照 ===")
        
        if size_name not in self.photo_sizes:
            print(f"错误：不支持的证件照尺寸 - {size_name}")
            return None
            
        size_config = self.photo_sizes[size_name]
        url = f"{self.base_url}/idphoto"
        
        try:
            print(f"调用API: {url}")
            print(f"尺寸: {size_config['width']} x {size_config['height']}")
            
            with open(input_image_path, 'rb') as f:
                files = {"input_image": f}
                data = {
                    "height": size_config["height"],
                    "width": size_config["width"],
                    "human_matting_model": "modnet_photographic_portrait_matting",
                    "face_detect_model": "retinaface-resnet50",
                    "hd": True,
                    "dpi": 300,
                    "face_alignment": True,
                    "head_measure_ratio": 0.2,
                    "head_height_ratio": 0.45,
                    "top_distance_max": 0.12,
                    "top_distance_min": 0.1,
                }
                
                response = requests.post(url, files=files, data=data)
            
            if response.status_code != 200:
                print(f"API请求失败，状态码: {response.status_code}")
                return None
                
            result = response.json()
            print(f"API响应状态: {result.get('status')}")
            
            if result.get('status') == True:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # 保存标准版透明底
                if 'image_base64_standard' in result:
                    standard_data = self.decode_base64_image(result['image_base64_standard'])
                    standard_path = self.save_image(
                        standard_data, 
                        f"{size_name}_透明底_标准版_{timestamp}.png"
                    )
                    print(f"标准版透明底已保存: {standard_path}")
                
                # 保存高清版透明底
                if 'image_base64_hd' in result:
                    hd_data = self.decode_base64_image(result['image_base64_hd'])
                    hd_path = self.save_image(
                        hd_data,
                        f"{size_name}_透明底_高清版_{timestamp}.png"
                    )
                    print(f"高清版透明底已保存: {hd_path}")
                
                # 记录已生成
                self.generated_files.add(file_key)
                print("✅ 步骤1完成：透明底证件照生成成功")
                return result
                
            else:
                print(f"❌ 步骤1失败: {result.get('error', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"❌ 步骤1异常: {str(e)}")
            return None

    def step2_add_background(self, transparent_image_standard: str, transparent_image_hd: str, bg_color_name: str = "蓝色", size_name: str = "一寸") -> Optional[Dict]:
        """步骤2：添加背景色（生成标准版和高清版）"""
        
        # 检查是否已生成
        file_key = self.generate_file_key(size_name, bg_color_name, "background")
        if file_key in self.generated_files:
            print(f"⏭️  跳过：{size_name}{bg_color_name}背景证件照已存在")
            return {"status": True, "skipped": True}
        
        print(f"\n=== 步骤2：为{size_name}证件照添加{bg_color_name}背景 ===")
        
        if bg_color_name not in self.background_colors:
            print(f"错误：不支持的背景色 - {bg_color_name}")
            return None
            
        color_rgb = self.background_colors[bg_color_name]
        url = f"{self.base_url}/add_background"
        
        # 将RGB转换为十六进制格式
        color_hex = f"{color_rgb[0]:02X}{color_rgb[1]:02X}{color_rgb[2]:02X}"
        
        try:
            print(f"调用API: {url}")
            print(f"背景色RGB: {color_rgb} -> #{color_hex}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result = {"status": True}
            
            # 处理标准版
            print("🔄 处理标准版...")
            data_standard = {
                "input_image_base64": transparent_image_standard,
                "color": color_hex,
                "dpi": 300,
                "render": 0,
            }
            
            response_standard = requests.post(url, data=data_standard)
            
            if response_standard.status_code != 200:
                print(f"标准版API请求失败，状态码: {response_standard.status_code}")
                return None
                
            result_standard = response_standard.json()
            print(f"标准版API响应状态: {result_standard.get('status')}")
            
            if result_standard.get('status') == True and 'image_base64' in result_standard:
                bg_data_standard = self.decode_base64_image(result_standard['image_base64'])
                bg_path_standard = self.save_image(
                    bg_data_standard,
                    f"{size_name}_{bg_color_name}背景_标准版_{timestamp}.jpg"
                )
                print(f"标准版带背景证件照已保存: {bg_path_standard}")
                result['image_base64_standard'] = result_standard['image_base64']
            
            # 处理高清版
            print("🔄 处理高清版...")
            data_hd = {
                "input_image_base64": transparent_image_hd,
                "color": color_hex,
                "dpi": 300,
                "render": 0,
            }
            
            response_hd = requests.post(url, data=data_hd)
            
            if response_hd.status_code != 200:
                print(f"高清版API请求失败，状态码: {response_hd.status_code}")
                return None
                
            result_hd = response_hd.json()
            print(f"高清版API响应状态: {result_hd.get('status')}")
            
            if result_hd.get('status') == True and 'image_base64' in result_hd:
                bg_data_hd = self.decode_base64_image(result_hd['image_base64'])
                bg_path_hd = self.save_image(
                    bg_data_hd,
                    f"{size_name}_{bg_color_name}背景_高清版_{timestamp}.jpg"
                )
                print(f"高清版带背景证件照已保存: {bg_path_hd}")
                result['image_base64_hd'] = result_hd['image_base64']
                # 保持兼容性，默认使用高清版
                result['image_base64'] = result_hd['image_base64']
            
            # 记录已生成
            self.generated_files.add(file_key)
            print("✅ 步骤2完成：背景色添加成功（标准版+高清版）")
            return result
                
        except Exception as e:
            print(f"❌ 步骤2异常: {str(e)}")
            return None

    def step3_generate_layout(self, photo_with_bg_base64: str, layout_size_name: str = "六寸", size_name: str = "一寸", bg_color_name: str = "蓝色") -> Optional[Dict]:
        """步骤3：生成排版照（避免重复）"""
        
        # 检查是否已生成
        file_key = self.generate_file_key(size_name, bg_color_name, "layout")
        if file_key in self.generated_files:
            print(f"⏭️  跳过：{size_name}{bg_color_name}背景排版照已存在")
            return {"status": True, "skipped": True}
        
        print(f"\n=== 步骤3：生成{layout_size_name}排版照 ===")
        
        if size_name not in self.photo_sizes:
            print(f"错误：不支持的证件照尺寸 - {size_name}")
            return None
            
        # 注意：这里的height和width是证件照的尺寸，不是排版照的尺寸
        # 排版照的尺寸由API内部的generate_layout_array函数计算
        photo_size = self.photo_sizes[size_name]
        url = f"{self.base_url}/generate_layout_photos"
        
        data = {
            "input_image_base64": photo_with_bg_base64,
            "height": photo_size["height"],  # 证件照高度
            "width": photo_size["width"],    # 证件照宽度
            "dpi": 300,
        }
        
        try:
            print(f"调用API: {url}")
            print(f"证件照尺寸: {photo_size['width']} x {photo_size['height']}")
            print(f"将生成{layout_size_name}排版照")
            
            response = requests.post(url, data=data)
            
            if response.status_code != 200:
                print(f"API请求失败，状态码: {response.status_code}")
                return None
                
            result = response.json()
            print(f"API响应状态: {result.get('status')}")
            
            if result.get('status') == True:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if 'image_base64' in result:
                    layout_data = self.decode_base64_image(result['image_base64'])
                    layout_path = self.save_image(
                        layout_data,
                        f"{size_name}_{bg_color_name}背景_{layout_size_name}排版_{timestamp}.jpg"
                    )
                    print(f"排版照已保存: {layout_path}")
                
                # 记录已生成
                self.generated_files.add(file_key)
                print("✅ 步骤3完成：排版照生成成功")
                return result
                
            else:
                print(f"❌ 步骤3失败: {result.get('error', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"❌ 步骤3异常: {str(e)}")
            return None

    def generate_complete_id_photos(self, input_image_path: str, size_name: str = "一寸", bg_color_name: str = "蓝色", layout_size_name: str = "六寸") -> bool:
        """生成完整证件照（三步骤，避免重复）"""
        
        print(f"\n🚀 开始完整证件照生成流程")
        print(f"输入图片: {input_image_path}")
        print(f"证件照尺寸: {size_name}")
        print(f"背景色: {bg_color_name}")
        print(f"排版尺寸: {layout_size_name}")
        print("=" * 50)
        
        # 步骤1：生成透明底证件照
        step1_result = self.step1_generate_transparent_photo(input_image_path, size_name)
        if not step1_result or step1_result.get('status') != True:
            print("❌ 完整流程失败：步骤1失败")
            return False
        
        # 如果步骤1被跳过，需要重新生成获取数据
        if step1_result.get('skipped'):
            print("⚠️  重新生成透明底证件照以获取数据")
            # 临时移除记录，重新生成
            file_key = self.generate_file_key(size_name, file_type="transparent")
            self.generated_files.discard(file_key)
            step1_result = self.step1_generate_transparent_photo(input_image_path, size_name)
            if not step1_result:
                return False
        
        # 步骤2：添加背景色（标准版+高清版）
        transparent_standard = step1_result.get('image_base64_standard')
        transparent_hd = step1_result.get('image_base64_hd')
        
        if not transparent_standard or not transparent_hd:
            print("❌ 完整流程失败：无法获取透明底图片数据")
            return False
            
        step2_result = self.step2_add_background(transparent_standard, transparent_hd, bg_color_name, size_name)
        if not step2_result or step2_result.get('status') != True:
            print("❌ 完整流程失败：步骤2失败")
            return False
        
        # 如果步骤2被跳过，需要重新生成获取数据
        if step2_result.get('skipped'):
            print("⚠️  重新生成带背景证件照以获取数据")
            # 临时移除记录，重新生成
            file_key = self.generate_file_key(size_name, bg_color_name, "background")
            self.generated_files.discard(file_key)
            step2_result = self.step2_add_background(transparent_standard, transparent_hd, bg_color_name, size_name)
            if not step2_result:
                return False
        
        # 步骤3：生成排版照
        photo_with_bg_base64 = step2_result.get('image_base64')
        if not photo_with_bg_base64:
            print("❌ 完整流程失败：无法获取带背景图片数据")
            return False
            
        step3_result = self.step3_generate_layout(photo_with_bg_base64, layout_size_name, size_name, bg_color_name)
        if not step3_result or step3_result.get('status') != True:
            print("❌ 完整流程失败：步骤3失败")
            return False
        
        print(f"\n🎉 完整证件照生成流程成功完成！")
        print("=" * 50)
        return True

    def show_generation_summary(self):
        """显示生成总结"""
        print(f"\n📊 生成总结")
        print("=" * 30)
        print(f"已生成类型数量: {len(self.generated_files)}")
        for file_key in sorted(self.generated_files):
            print(f"✅ {file_key}")


def main():
    """主函数：优化版证件照生成演示"""
    
    #generator = OptimizedIDPhotoGenerator('http://175.178.173.138:8080')
    generator = OptimizedIDPhotoGenerator()
    input_image_path = "temp/test.jpg"
    
    if not os.path.exists(input_image_path):
        print(f"❌ 错误：输入图片不存在 - {input_image_path}")
        return
    
    print("🎯 HivisionIDPhotos 优化版证件照生成器")
    print("🔄 避免重复生成，提高效率")
    print("=" * 60)
    
    # 生成不同组合的证件照（避免重复）
    test_combinations = [
        {"size": "一寸", "bg": "蓝色", "layout": "六寸"},
        # {"size": "一寸", "bg": "白色", "layout": "六寸"},
        # {"size": "一寸", "bg": "红色", "layout": "六寸"},
        # {"size": "二寸", "bg": "蓝色", "layout": "六寸"},
        # {"size": "护照", "bg": "白色", "layout": "六寸"},
        # {"size": "驾照", "bg": "蓝色", "layout": "六寸"},
    ]
    
    success_count = 0
    for i, combo in enumerate(test_combinations, 1):
        print(f"\n📋 测试{i}：{combo['size']}{combo['bg']}背景 + {combo['layout']}排版")
        
        success = generator.generate_complete_id_photos(
            input_image_path=input_image_path,
            size_name=combo["size"],
            bg_color_name=combo["bg"],
            layout_size_name=combo["layout"]
        )
        
        if success:
            success_count += 1
    
    print(f"\n🎉 所有测试完成！成功率: {success_count}/{len(test_combinations)}")
    
    # 显示生成总结
    generator.show_generation_summary()
    
    print(f"\n📂 请查看 output 目录中的生成结果")


if __name__ == "__main__":
    main()