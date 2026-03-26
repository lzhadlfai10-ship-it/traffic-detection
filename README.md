\# 🚁 AI-Based Traffic Flow Detection System



> Real-time traffic monitoring system using YOLOv8 and ByteTrack. Detects vehicles, identifies congestion, and simulates data transmission to traffic police.



\---



\## 📋 Overview



This system analyzes traffic videos (drone or bridge footage) to:



\- 🚗 \*\*Detect \& Classify Vehicles\*\* – car, bus, truck, motorcycle

\- 🔍 \*\*Track Vehicles\*\* – assign unique IDs and track movement

\- 🚦 \*\*Detect Congestion\*\* – based on vehicle count and speed

\- 🚨 \*\*Accident Alert\*\* – detect stationary vehicles

\- 📊 \*\*Generate Reports\*\* – Excel and JSON output

\- 📡 \*\*Simulate Data Transmission\*\* – send alerts to traffic police



\---



\## 🛠️ Tech Stack



| Tool | Purpose | Version |

|------|---------|---------|

| Python | Programming | 3.14 |

| YOLOv8 | Object Detection | 8.4.27 |

| ByteTrack | Multi-Object Tracking | - |

| Supervision | Annotation \& Tracking | 0.27.0 |

| OpenCV | Video Processing | 4.13.0 |

| Pandas | Data Analysis | 3.0.1 |



\---



\## 📁 Project Structure

traffic-detection/

├── scripts/

│ ├── detect\_vehicles.py # Vehicle detection

│ ├── track\_vehicles.py # Vehicle tracking

│ ├── detect\_congestion.py # Congestion detection

│ └── generate\_report.py # Report generation

├── videos/

│ ├── traffic.mp4 # Peak hour video

│ └── light\_traffic.mp4 # Off-peak video

├── output/

│ ├── traffic\_result\_v3.mp4 # Peak result

│ ├── light\_traffic\_result\_v3.mp4 # Off-peak result

│ ├── tracked\_video.mp4 # Tracking demo

│ ├── alerts\_traffic\_v3.json # Peak alerts log

│ ├── alerts\_light\_v3.json # Off-peak alerts

│ ├── traffic\_report.xlsx # Excel report

│ ├── summary.json # Statistics summary

│ └── simulation\_log.txt # Police transmission log

└── README.md



\---



\## 🚀 Quick Start



\### Requirements

\- Python 3.8+



\### Install Dependencies

```bash

pip install ultralytics opencv-python supervision pandas numpy openpyxl



\###Run Programs

\# 1. Vehicle detection

python scripts/detect\_vehicles.py



\# 2. Vehicle tracking

python scripts/track\_vehicles.py



\# 3. Congestion detection

python scripts/detect\_congestion.py



\# 4. Generate report

python scripts/generate\_report.py



\###Output Files

File	Description

traffic\_result\_v3.mp4	Peak hour annotated video

light\_traffic\_result\_v3.mp4	Off-peak annotated video

alerts\_traffic\_v3.json	Peak hour alerts (10 records)

alerts\_light\_v3.json	Off-peak alerts (0 records)

traffic\_report.xlsx	Excel report

summary.json	Statistics summary

simulation\_log.txt	Police transmission log (11 records)





\###License

For educational purposes only

