# 第二个程序：跟踪车辆，给每辆车一个ID
# 文件名：track_vehicles.py
# 最后更新：2026-03-26

from ultralytics import YOLO
import cv2
import supervision as sv
import numpy as np
import os

print("=" * 60)
print("车辆跟踪程序开始运行")
print("=" * 60)

# 第1步：加载AI模型
print("1. 正在加载AI模型...")
model = YOLO('yolov8n.pt')
print("   模型加载完成！")

# 第2步：设置视频路径
video_path = '../videos/traffic.mp4'
output_path = '../output/tracked_video.mp4'

# 检查视频是否存在
if not os.path.exists(video_path):
    print(f"错误：找不到视频文件 {video_path}")
    print("请确保你的视频在 videos 文件夹里，并且文件名是 traffic.mp4")
    input("按回车键退出...")
    exit()

print(f"2. 视频文件：{video_path}")

# 第3步：打开视频
cap = cv2.VideoCapture(video_path)

# 获取视频信息
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

print(f"   视频尺寸：{width} x {height}")
print(f"   视频帧率：{fps} FPS")

# 第4步：准备保存结果视频
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# 第5步：创建跟踪器
tracker = sv.ByteTrack()

# 第6步：创建画框和标签的工具（修正后的版本）
# 使用正确的 supervision 函数
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

# 第7步：定义车辆类型
vehicle_classes = [2, 3, 5, 7]  # 2=car, 3=motorcycle, 5=bus, 7=truck
class_names = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}

print("3. 开始处理视频...")
print("   (这可能需要几分钟，请耐心等待)")

frame_count = 0
# 用来记录每辆车通过计数线
crossed_vehicles = set()
total_vehicle_count = 0

# 定义计数线（在画面中间画一条横线）
count_line_y = height // 2  # 画面中间的位置
print(f"   计数线位置：Y = {count_line_y}")

# 第8步：逐帧处理
while True:
    success, frame = cap.read()
    if not success:
        break
    
    frame_count += 1
    
    # 每30帧显示一次进度
    if frame_count % 30 == 0:
        print(f"   已处理 {frame_count} 帧...")
    
    # 用AI检测这一帧
    results = model(frame)
    
    # 只保留车辆的检测结果
    detections = sv.Detections.from_ultralytics(results[0])
    
    # 过滤掉非车辆
    if len(detections) > 0:
        vehicle_mask = np.isin(detections.class_id, vehicle_classes)
        detections = detections[vehicle_mask]
        
        # 更新跟踪（给每辆车分配ID）
        detections = tracker.update_with_detections(detections)
        
        # 准备标签（显示车辆ID和类型）
        labels = []
        for i in range(len(detections)):
            if detections.tracker_id is not None:
                tracker_id = int(detections.tracker_id[i])
            else:
                tracker_id = "?"
            
            class_id = detections.class_id[i]
            vehicle_type = class_names.get(class_id, "vehicle")
            labels.append(f"#{tracker_id} {vehicle_type}")
            
            # 检查车辆是否通过计数线
            # 获取车辆中心点Y坐标
            x1, y1, x2, y2 = detections.xyxy[i]
            center_y = int((y1 + y2) / 2)
            
            # 如果车辆通过计数线，并且之前没被计数过
            if tracker_id not in crossed_vehicles:
                # 判断是否跨过线
                if abs(center_y - count_line_y) < 15:
                    crossed_vehicles.add(tracker_id)
                    total_vehicle_count += 1
                    print(f"   车辆 #{tracker_id} 通过计数线，当前总数：{total_vehicle_count}")
        
        # 在画面上画框和标签
        annotated_frame = box_annotator.annotate(frame, detections)
        annotated_frame = label_annotator.annotate(annotated_frame, detections, labels)
    else:
        annotated_frame = frame
    
    # 在画面顶部显示统计信息
    cv2.putText(annotated_frame, f"Total Vehicles Passed: {total_vehicle_count}", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    # 显示当前帧的车辆数
    if len(detections) > 0:
        cv2.putText(annotated_frame, f"Current Vehicles: {len(detections)}", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # 画计数线
    cv2.line(annotated_frame, (0, count_line_y), (width, count_line_y), 
             (255, 0, 0), 3)
    cv2.putText(annotated_frame, "COUNT LINE", (width // 2 - 60, count_line_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    
    # 保存这一帧
    out.write(annotated_frame)

# 第9步：释放资源
cap.release()
out.release()

print("=" * 60)
print(f"处理完成！")
print(f"总共处理了 {frame_count} 帧")
print(f"通过计数线的车辆总数：{total_vehicle_count} 辆")
print(f"结果视频保存在：{output_path}")
print("=" * 60)

input("按回车键退出...")