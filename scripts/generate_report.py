# 第四个程序：生成统计报告并模拟发送数据到交警部门
# 文件名：generate_report.py

import json
import pandas as pd
import os
from datetime import datetime
import time

# 函数：根据报警类型生成建议方案
def generate_recommendation(alert):
    """根据报警类型生成建议方案"""
    if alert['type'] == 'congestion':
        vehicle_count = alert.get('vehicle_count', 0)
        if vehicle_count > 25:
            return "建议：立即增派警力疏导，考虑临时交通管制"
        elif vehicle_count > 20:
            return "建议：增派警力到现场疏导，通知前方路口分流"
        else:
            return "建议：加强监控，准备启动疏导预案"
    elif alert['type'] == 'accident':
        return "建议：立即通知交警和救护车前往处理，设置警示标志"
    elif alert['type'] == 'congestion_end':
        return "建议：恢复正常监控，继续保持关注"
    return "建议：加强监控"

print("=" * 60)
print("交通流量分析报告生成程序")
print("=" * 60)

# 第1步：读取报警日志
alert_log_path = '../output/alerts_traffic_v3.json'
report_path = '../output/traffic_report.xlsx'
simulation_log_path = '../output/simulation_log.txt'

print("1. 正在读取报警日志...")

if not os.path.exists(alert_log_path):
    print(f"错误：找不到报警日志文件 {alert_log_path}")
    print("请先运行 detect_congestion.py 生成报警日志")
    input("按回车键退出...")
    exit()

with open(alert_log_path, 'r', encoding='utf-8') as f:
    alerts = json.load(f)

print(f"   读取成功！共有 {len(alerts)} 条报警记录")

# 第2步：分析报警数据
print("\n2. 正在分析报警数据...")

congestion_alerts = [a for a in alerts if a['type'] == 'congestion']
accident_alerts = [a for a in alerts if a['type'] == 'accident']
congestion_end_alerts = [a for a in alerts if a['type'] == 'congestion_end']

print(f"   拥堵报警：{len(congestion_alerts)} 次")
print(f"   事故报警：{len(accident_alerts)} 次")
print(f"   拥堵解除：{len(congestion_end_alerts)} 次")

# 第3步：计算统计数据
print("\n3. 正在计算统计数据...")

if congestion_alerts:
    avg_vehicle_count = sum(a.get('vehicle_count', 0) for a in congestion_alerts) / len(congestion_alerts)
    avg_speed = sum(a.get('avg_speed', 0) for a in congestion_alerts) / len(congestion_alerts)
    print(f"   平均拥堵时车辆数：{avg_vehicle_count:.1f} 辆")
    print(f"   平均车速：{avg_speed:.2f} 像素/帧")
    
    worst_congestion = max(congestion_alerts, key=lambda x: x.get('vehicle_count', 0))
    print(f"   最严重拥堵：{worst_congestion['vehicle_count']} 辆车")
else:
    avg_vehicle_count = 0
    avg_speed = 0
    worst_congestion = {}

# 第4步：生成Excel报告
print("\n4. 正在生成Excel报告...")

report_data = []
for alert in alerts:
    report_data.append({
        '时间(秒)': alert.get('timestamp', 0),
        '帧数': alert.get('frame', 0),
        '报警类型': alert.get('type', ''),
        '原因': alert.get('reason', ''),
        '车辆数': alert.get('vehicle_count', ''),
        '平均速度': alert.get('avg_speed', ''),
        '静止车辆数': alert.get('stationary_vehicles', ''),
        '持续时间(秒)': alert.get('duration_seconds', ''),
        '详细信息': alert.get('message', '')
    })

df = pd.DataFrame(report_data)
df.to_excel(report_path, index=False, sheet_name='交通报警记录')
print(f"   Excel报告已保存到：{report_path}")

# 第5步：生成统计摘要
print("\n5. 正在生成统计摘要...")

summary = {
    '分析时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    '总报警次数': len(alerts),
    '拥堵报警次数': len(congestion_alerts),
    '事故报警次数': len(accident_alerts),
    '拥堵解除次数': len(congestion_end_alerts),
    '平均拥堵车辆数': avg_vehicle_count,
    '平均拥堵车速': avg_speed,
    '最严重拥堵车辆数': worst_congestion.get('vehicle_count', 0) if congestion_alerts else 0,
    '最严重拥堵时间': worst_congestion.get('timestamp', 0) if congestion_alerts else 0
}

summary_path = '../output/summary.json'
with open(summary_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"   统计摘要已保存到：{summary_path}")

# 第6步：模拟发送数据到交警部门
print("\n6. 正在模拟发送数据到交警部门...")
print("   " + "-" * 50)

class PoliceDepartmentAPI:
    def __init__(self):
        self.received_alerts = []
    
    def send_alert(self, alert_data):
        self.received_alerts.append(alert_data)
        time.sleep(0.2)  # 模拟网络延迟
        return {"status": "success", "code": 200}

api = PoliceDepartmentAPI()

sent_count = 0
for alert in alerts:
    data_packet = {
        "alert_id": f"ALERT_{alert['timestamp']}_{alert['frame']}",
        "timestamp": alert['timestamp'],
        "alert_type": alert['type'],
        "location": "天桥观测点 - 东行方向",
        "details": alert['message'],
        "severity": "高" if alert['type'] == 'congestion' and alert.get('vehicle_count', 0) > 20 else "中",
        "recommendation": generate_recommendation(alert)
    }
    
    api.send_alert(data_packet)
    sent_count += 1
    print(f"   已发送报警 #{sent_count}: {data_packet['alert_type']}")

print("\n" + "=" * 60)
print("数据发送完成！")
print("=" * 60)
print(f"总共发送报警：{sent_count} 条")
print(f"发送状态：成功")
print(f"接收方：交警部门模拟系统")

# 保存模拟发送日志
with open(simulation_log_path, 'w', encoding='utf-8') as f:
    f.write("=" * 60 + "\n")
    f.write("交警部门数据发送模拟日志\n")
    f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 60 + "\n\n")
    
    for i, alert in enumerate(api.received_alerts, 1):
        f.write(f"报警 #{i}\n")
        f.write(f"  ID: {alert['alert_id']}\n")
        f.write(f"  时间: {alert['timestamp']:.1f} 秒\n")
        f.write(f"  类型: {alert['alert_type']}\n")
        f.write(f"  位置: {alert['location']}\n")
        f.write(f"  详情: {alert['details']}\n")
        f.write(f"  严重程度: {alert['severity']}\n")
        f.write(f"  建议方案: {alert['recommendation']}\n")
        f.write("-" * 40 + "\n")

print(f"模拟发送日志已保存到：{simulation_log_path}")

# 第7步：打印最终报告
print("\n" + "=" * 60)
print("最终分析报告")
print("=" * 60)
if alerts:
    print(f"分析时间段：0-{alerts[-1]['timestamp']:.1f} 秒")
print(f"总报警次数：{len(alerts)} 次")
print(f"拥堵报警：{len(congestion_alerts)} 次")
print(f"事故报警：{len(accident_alerts)} 次")
print("\n生成的报告文件：")
print(f"  - 详细报告：{report_path}")
print(f"  - 统计摘要：{summary_path}")
print(f"  - 发送日志：{simulation_log_path}")
print("\n✅ 系统已向交警部门发送所有报警数据")
print("=" * 60)

input("\n按回车键退出...")