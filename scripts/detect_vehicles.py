# 第一个程序：检测视频里的车辆

from ultralytics import YOLO
import cv2
import os

print("=" * 50)
print("车辆检测程序开始运行")
print("=" * 50)

# 加载AI模型
print("1. 正在加载AI模型...")
model = YOLO('yolov8n.pt')
print("   模型加载完成！")

# 设置视频路径
video_path = '../videos/traffic.mp4'
output_path = '../output/detected_video.mp4'

# 检查视频是否存在
if not os.path.exists(video_path):
    print(f"错误：找不到视频文件 {video_path}")
    print("请确保你的视频在 videos 文件夹里，并且文件名是 traffic.mp4")
    input("按回车键退出...")
    exit()

print(f"2. 视频文件：{video_path}")

# 打开视频
cap = cv2.VideoCapture(video_path)

# 获取视频信息
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

print(f"   视频尺寸：{width} x {height}")
print(f"   视频帧率：{fps} FPS")

# 准备保存结果视频
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# 定义车辆类型
vehicle_classes = [2, 3, 5, 7]
class_names = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}

print("3. 开始处理视频...")
print("   (这可能需要几分钟，请耐心等待)")

frame_count = 0
vehicle_count_total = 0

# 逐帧处理
while True:
    success, frame = cap.read()
    if not success:
        break
    
    frame_count += 1
    
    if frame_count % 30 == 0:
        print(f"   已处理 {frame_count} 帧...")
    
    results = model(frame)
    boxes = results[0].boxes
    
    if boxes is not None:
        for box in boxes:
            cls = int(box.cls[0])
            if cls in vehicle_classes:
                vehicle_count_total += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{class_names[cls]} {conf:.2f}"
                cv2.putText(frame, label, (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    cv2.putText(frame, f"Vehicles: {vehicle_count_total}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    out.write(frame)

cap.release()
out.release()

print("=" * 50)
print(f"处理完成！")
print(f"总共处理了 {frame_count} 帧")
print(f"检测到车辆数量：{vehicle_count_total}")
print(f"结果视频保存在：{output_path}")
print("=" * 50)

input("按回车键退出...")