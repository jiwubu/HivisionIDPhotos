import cv2
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from hivision.creator.retinaface.inference import retinaface_detect_faces

now_dir = os.path.dirname(__file__)
image_path = os.path.join(os.path.dirname(now_dir), "demo", "images", "test.jpg")
output_dir = os.path.join(now_dir, "output")

# 读取图片
image = cv2.imread(image_path)

# 模型路径（使用绝对路径）
model_path = os.path.join(os.path.dirname(now_dir), "hivision", "creator", "retinaface", "weights", "retinaface-resnet50.onnx")

# 执行人脸检测
faces_dets, sess = retinaface_detect_faces(
    image=image,
    model_path=model_path,
    sess=None  # 首次调用传 None，后续可复用 sess
)

# 解析检测结果
for i, face_det in enumerate(faces_dets):
    # 人脸框坐标
    x1, y1, x2, y2 = face_det[0:4]
    confidence = face_det[4]
    
    # 5个关键点坐标 (左眼, 右眼, 鼻尖, 左嘴角, 右嘴角)
    landmarks = face_det[5:15].reshape(5, 2)
    left_eye = landmarks[0]
    right_eye = landmarks[1]
    nose = landmarks[2]
    left_mouth = landmarks[3]
    right_mouth = landmarks[4]
    
    print(f"Face {i+1}:")
    print(f"  位置: ({x1:.1f}, {y1:.1f}) - ({x2:.1f}, {y2:.1f})")
    print(f"  置信度: {confidence:.3f}")
    print(f"  左眼: {left_eye}")
    print(f"  右眼: {right_eye}")
    
    # 绘制人脸框
    cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
    
    # 绘制关键点
    for landmark in landmarks:
        cv2.circle(image, (int(landmark[0]), int(landmark[1])), 3, (0, 0, 255), -1)

# 保存结果
cv2.imwrite(os.path.join(output_dir, "test_result.jpg"), image)
print("完成！")

os._exit(0)