# 第三个程序：检测拥堵和事故
# 文件名：detect_congestion.py
# 功能：检测交通拥堵，自动报警
# 最后更新：2026-03-26

from ultralytics import YOLO
import cv2
import supervision as sv
import numpy as np
import os
import time
from collections import deque
import json

print("=" * 60)
print("交通拥堵检测程序开始运行")
print("=" * 60)

# 第1步：加载AI模型
print("1. 正在加载AI模型...")
model = YOLO('yolov8n.pt')
print("   模型加载完成！")

# 第2步：设置视频路径
video_path = '../videos/traffic.mp4'
output_path = '../output/congestion_detected.mp4'
alert_log_path = '../output/alerts.json'

# 检查视频是否存在
if not os.path.exists(video_path):
    print(f"错误：找不到视频文件 {video_path}")
    input("按回车键退出...")
    exit()

print(f"2. 视频文件：{video_path}")

# 第3步：打开视频
cap = cv2.VideoCapture(video_path)
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

# 第6步：定义车辆类型
vehicle_classes = [2, 3, 5, 7]
class_names = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}

# 第7步：拥堵检测参数
CONGESTION_THRESHOLD = 15  # 如果当前画面车辆超过15辆，视为拥堵
SPEED_THRESHOLD = 5        # 如果车辆速度低于5像素/帧，视为慢速
ALERT_COOLDOWN = 30        # 两次报警之间的最小帧数（避免重复报警）

# 第8步：记录车辆位置和速度
# 用字典存储每辆车的上一帧位置和速度
vehicle_positions = {}
vehicle_speeds = {}

# 报警记录
alerts = []
last_alert_frame = 0
congestion_start_frame = None
congestion_alert_active = False

# 用于计算平均速度的队列
speed_history = deque(maxlen=30)

print("3. 开始分析交通状况...")
print("   (程序会检测拥堵和事故，自动报警)")

frame_count = 0
congestion_frames = 0

# 第9步：逐帧处理
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
    detections = sv.Detections.from_ultralytics(results[0])
    
    # 过滤车辆
    if len(detections) > 0:
        vehicle_mask = np.isin(detections.class_id, vehicle_classes)
        detections = detections[vehicle_mask]
        
        # 更新跟踪
        detections = tracker.update_with_detections(detections)
        
        # ========== 计算车辆速度 ==========
        current_vehicle_count = len(detections)
        avg_speed = 0
        
        if len(detections) > 0:
            speeds = []
            for i in range(len(detections)):
                tracker_id = int(detections.tracker_id[i]) if detections.tracker_id is not None else None
                if tracker_id is not None:
                    # 获取当前车辆中心点
                    x1, y1, x2, y2 = detections.xyxy[i]
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)
                    
                    # 如果之前记录过这辆车的位置，计算速度
                    if tracker_id in vehicle_positions:
                        prev_x, prev_y = vehicle_positions[tracker_id]
                        # 计算移动距离（欧氏距离）
                        distance = np.sqrt((center_x - prev_x)**2 + (center_y - prev_y)**2)
                        speed = distance  # 每帧移动的像素距离
                        speeds.append(speed)
                        vehicle_speeds[tracker_id] = speed
                    
                    # 更新位置
                    vehicle_positions[tracker_id] = (center_x, center_y)
            
            # 计算平均速度
            if speeds:
                avg_speed = sum(speeds) / len(speeds)
                speed_history.append(avg_speed)
        
        # 清理已经不存在的车辆
        current_ids = set()
        if detections.tracker_id is not None:
            current_ids = set(detections.tracker_id)
        for tid in list(vehicle_positions.keys()):
            if tid not in current_ids:
                del vehicle_positions[tid]
                if tid in vehicle_speeds:
                    del vehicle_speeds[tid]
        
        # ========== 拥堵检测 ==========
        is_congested = False
        congestion_reason = ""
        
        # 条件1：车辆数量过多
        if current_vehicle_count > CONGESTION_THRESHOLD:
            is_congested = True
            congestion_reason = f"车辆过多 ({current_vehicle_count}辆 > {CONGESTION_THRESHOLD}辆)"
        
        # 条件2：平均速度过慢
        elif avg_speed < SPEED_THRESHOLD and avg_speed > 0:
            is_congested = True
            congestion_reason = f"车速过慢 ({avg_speed:.1f}像素/帧 < {SPEED_THRESHOLD}像素/帧)"
        
        # ========== 事故检测（静止车辆） ==========
        accident_detected = False
        stationary_vehicles = []
        
        for tracker_id, speed in vehicle_speeds.items():
            # 如果车辆速度接近0超过一段时间，可能是事故
            if speed < 1:
                stationary_vehicles.append(tracker_id)
        
        if len(stationary_vehicles) > 5:  # 如果超过5辆车静止
            accident_detected = True
        
        # ========== 报警处理 ==========
        current_time = frame_count / fps  # 转换为秒
        
        if is_congested and (frame_count - last_alert_frame) > ALERT_COOLDOWN:
            alert = {
                "timestamp": current_time,
                "frame": frame_count,
                "type": "congestion",
                "reason": congestion_reason,
                "vehicle_count": current_vehicle_count,
                "avg_speed": avg_speed,
                "message": f"⚠️ 交通拥堵警报！{congestion_reason}"
            }
            alerts.append(alert)
            last_alert_frame = frame_count
            print(f"   🚨 第{frame_count}帧：{alert['message']}")
            
            if not congestion_alert_active:
                congestion_start_frame = frame_count
                congestion_alert_active = True
        elif not is_congested and congestion_alert_active:
            # 拥堵结束
            congestion_end_frame = frame_count
            duration = (congestion_end_frame - congestion_start_frame) / fps
            alert = {
                "timestamp": current_time,
                "frame": frame_count,
                "type": "congestion_end",
                "duration_seconds": duration,
                "message": f"✅ 拥堵解除，持续了 {duration:.1f} 秒"
            }
            alerts.append(alert)
            print(f"   ✅ 第{frame_count}帧：{alert['message']}")
            congestion_alert_active = False
        
        if accident_detected and (frame_count - last_alert_frame) > ALERT_COOLDOWN:
            alert = {
                "timestamp": current_time,
                "frame": frame_count,
                "type": "accident",
                "stationary_vehicles": len(stationary_vehicles),
                "message": f"🚨 事故警报！检测到 {len(stationary_vehicles)} 辆静止车辆"
            }
            alerts.append(alert)
            last_alert_frame = frame_count
            print(f"   🚨 第{frame_count}帧：{alert['message']}")
        
        # ========== 在画面上标注 ==========
        # 画框和标签
        box_annotator = sv.BoxAnnotator()
        label_annotator = sv.LabelAnnotator()
        
        labels = []
        for i in range(len(detections)):
            tracker_id = int(detections.tracker_id[i]) if detections.tracker_id is not None else "?"
            class_id = detections.class_id[i]
            vehicle_type = class_names.get(class_id, "vehicle")
            speed = vehicle_speeds.get(tracker_id, 0)
            labels.append(f"#{tracker_id} {vehicle_type} {speed:.1f}")
        
        annotated_frame = box_annotator.annotate(frame, detections)
        annotated_frame = label_annotator.annotate(annotated_frame, detections, labels)
        
        # 显示拥堵状态
        if is_congested:
            cv2.rectangle(annotated_frame, (0, 0), (width, 80), (0, 0, 255), -1)
            cv2.putText(annotated_frame, "CONGESTION DETECTED!", 
                        (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(annotated_frame, congestion_reason, 
                        (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        elif accident_detected:
            cv2.rectangle(annotated_frame, (0, 0), (width, 80), (0, 0, 255), -1)
            cv2.putText(annotated_frame, "ACCIDENT DETECTED!", 
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 显示统计信息
        cv2.putText(annotated_frame, f"Vehicles: {current_vehicle_count}", 
                    (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"Avg Speed: {avg_speed:.1f} px/frame", 
                    (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
    else:
        annotated_frame = frame
        cv2.putText(annotated_frame, "No vehicles detected", 
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # 保存这一帧
    out.write(annotated_frame)

# 第10步：释放资源
cap.release()
out.release()

# 第11步：保存报警日志
with open(alert_log_path, 'w', encoding='utf-8') as f:
    json.dump(alerts, f, ensure_ascii=False, indent=2)

# 第12步：打印统计报告
print("=" * 60)
print("检测完成！")
print("=" * 60)
print(f"总共处理了 {frame_count} 帧")
print(f"检测到拥堵报警：{len([a for a in alerts if a['type']=='congestion'])} 次")
print(f"检测到事故报警：{len([a for a in alerts if a['type']=='accident'])} 次")
print(f"报警日志保存在：{alert_log_path}")
print(f"结果视频保存在：{output_path}")
print("=" * 60)

# 打印详细报警记录
if alerts:
    print("\n报警记录：")
    for alert in alerts:
        print(f"  [{alert['timestamp']:.1f}秒] {alert['message']}")

input("\n按回车键退出...")