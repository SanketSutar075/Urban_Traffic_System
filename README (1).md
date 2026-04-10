# TrafficIQ v7.0 — Smart Traffic Signalling + AQI Prediction
**Prepared by: Sanket Sutar | B.E. Final Year Project 2025-26**

## 🚀 Run Locally
```bash
pip install -r requirements.txt
streamlit run Deep_Learning_Demo.py
```

## ☁️ Deploy on Streamlit Cloud
1. Push all files to GitHub
2. Go to share.streamlit.io
3. Connect GitHub repo
4. Main file: `Deep_Learning_Demo.py`
5. Deploy!

## 📦 Files Required
```
Deep_Learning_Demo.py   ← Main app
requirements.txt        ← Python packages
packages.txt            ← System packages (ffmpeg, libgl1)
.streamlit/config.toml  ← Upload size config
```

## 🎯 Features
- YOLOv8 CNN Vehicle Detection
- RNN + LSTM Forecasting  
- ANN / KNN / KMeans / Random Forest / GBM
- AQI Prediction + Weather Correction
- Emergency Vehicle Override
- Speed Estimator + Congestion Index
- Route Advisory + Incident Log
- CO2 Tracker + Density Heatmap
- Download Annotated Video

## ⚙️ Modes
- **Demo Mode** — Animated traffic (no camera needed)
- **Webcam** — Browser camera via st.camera_input
- **Upload Video** — MP4/AVI/MOV with YOLO detection

## 💡 Notes
- First run downloads YOLOv8n.pt (~6MB) automatically
- Streamlit Cloud free tier: 1GB RAM (use frame_skip=3 for videos)
- Video upload max: 200MB (set in config.toml)
