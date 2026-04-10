import gc
import os
import tempfile
"""
TrafficIQ v7.0 - Smart Traffic Signalling + AQI Prediction
ULTRA REVAMP — Cyberpunk Dark HUD + 6 New Features
Prepared by: Sanket Sutar
Run: streamlit run app.py
pip install streamlit opencv-python ultralytics scikit-learn psutil matplotlib pandas numpy
"""

import streamlit as st
import cv2, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import time, random, math, base64, json
from datetime import datetime, timedelta
from collections import deque

st.set_page_config(
    page_title="TrafficIQ v7.0 | Sanket Sutar",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except: YOLO_AVAILABLE = False

try:
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.cluster import KMeans
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    SK_AVAILABLE = True
except: SK_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except: PSUTIL_AVAILABLE = False

# ─── CYBERPUNK DARK THEME ────────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&family=Exo+2:ital,wght@0,300;0,400;0,600;0,700;0,800;1,400&display=swap');

:root {
  --bg:#070b14;--bg2:#0d1421;--bg3:#111827;
  --glass:rgba(255,107,0,0.04);--glass2:rgba(0,212,255,0.04);
  --or:#ff6b00;--or2:#ff8c00;--or3:#ffb347;--or-glow:rgba(255,107,0,0.35);
  --cy:#00d4ff;--cy2:#00a8cc;--cy-glow:rgba(0,212,255,0.3);
  --gr:#00ff88;--gr-glow:rgba(0,255,136,0.3);
  --re:#ff2244;--re-glow:rgba(255,34,68,0.3);
  --ye:#ffd700;--ye-glow:rgba(255,215,0,0.3);
  --pu:#bf5fff;--pu-glow:rgba(191,95,255,0.25);
  --border:rgba(255,107,0,0.18);--border2:rgba(0,212,255,0.15);
  --text:#e8ecf1;--text2:#a0aec0;--text3:#4a5568;
  --card-bg:rgba(13,20,33,0.85);
  --grid-line:rgba(255,107,0,0.06);
}

html,body,[class*="css"]{
  font-family:'Rajdhani',sans-serif;
  background:var(--bg)!important;
  color:var(--text)!important;
}
.stApp{background:var(--bg)!important;}
.stApp::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background:
    repeating-linear-gradient(0deg,transparent,transparent 59px,var(--grid-line) 59px,var(--grid-line) 60px),
    repeating-linear-gradient(90deg,transparent,transparent 59px,var(--grid-line) 59px,var(--grid-line) 60px);
}

/* SIDEBAR */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#0a0f1e,#0d1421)!important;
  border-right:1px solid var(--border)!important;
}
[data-testid="stSidebar"] *{color:var(--text2)!important;}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{
  color:var(--or)!important;font-family:'Orbitron',monospace!important;
}
[data-testid="stSidebar"] .stSlider>div>div>div{background:var(--or)!important;}
[data-testid="stSidebar"] .stRadio label{color:var(--text2)!important;}
[data-testid="stSidebar"] .stToggle>div{background:var(--or)!important;}

/* HERO */
.hero-wrap{
  position:relative;overflow:hidden;border-radius:20px;
  background:linear-gradient(135deg,#0d1421 0%,#111827 50%,#0d1421 100%);
  border:1px solid var(--border);
  padding:0;margin-bottom:20px;
  box-shadow:0 0 60px rgba(255,107,0,0.12),0 0 120px rgba(0,212,255,0.06),inset 0 0 80px rgba(255,107,0,0.03);
}
.hero-bg{
  position:absolute;inset:0;
  background:
    radial-gradient(ellipse 60% 80% at 85% 50%,rgba(255,107,0,0.08) 0%,transparent 70%),
    radial-gradient(ellipse 40% 60% at 15% 50%,rgba(0,212,255,0.06) 0%,transparent 70%);
  pointer-events:none;
}
.hero-inner{position:relative;z-index:1;padding:2.4rem 3rem 2rem;}
.hero-eyebrow{
  font-family:'Share Tech Mono',monospace;font-size:.68rem;
  color:var(--cy);letter-spacing:4px;margin-bottom:10px;
  text-shadow:0 0 10px var(--cy-glow);
}
.hero-title{
  font-family:'Orbitron',monospace;font-size:3.2rem;font-weight:900;
  color:var(--text);line-height:1.05;margin:0;
  text-shadow:0 0 40px rgba(255,107,0,0.3);
}
.hero-title .or{color:var(--or);text-shadow:0 0 20px var(--or-glow);}
.hero-title .cy{color:var(--cy);text-shadow:0 0 20px var(--cy-glow);}
.hero-sub{
  font-family:'Exo 2',sans-serif;font-size:1.05rem;color:var(--text2);
  margin-top:10px;line-height:1.6;max-width:700px;
}
.hero-author{
  display:inline-flex;align-items:center;gap:12px;
  background:rgba(255,107,0,0.08);border:1px solid rgba(255,107,0,0.25);
  border-radius:40px;padding:8px 22px;margin-top:16px;
  backdrop-filter:blur(10px);
}
.author-dot{width:8px;height:8px;background:var(--or);border-radius:50%;box-shadow:0 0 8px var(--or);animation:pulse-dot 2s infinite;}
@keyframes pulse-dot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.6;transform:scale(1.4)}}
.author-name{font-family:'Orbitron',monospace;font-size:.85rem;font-weight:700;color:var(--or);}
.author-role{font-family:'Share Tech Mono',monospace;font-size:.62rem;color:var(--text3);letter-spacing:1px;}
.hero-badges{display:flex;flex-wrap:wrap;gap:7px;margin-top:16px;}
.hbadge{
  font-family:'Share Tech Mono',monospace;font-size:.62rem;letter-spacing:1.5px;
  padding:5px 14px;border-radius:4px;
  background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
  color:var(--text2);transition:all .3s;
}
.hbadge:hover{border-color:var(--or);color:var(--or);}
.hb-new{background:rgba(0,255,136,0.08);border-color:rgba(0,255,136,0.3);color:var(--gr);text-shadow:0 0 8px var(--gr-glow);}
.hb-live{
  background:rgba(255,34,68,0.12);border-color:rgba(255,34,68,0.4);color:var(--re);
  animation:live-blink 1.5s infinite;text-shadow:0 0 8px var(--re-glow);
}
@keyframes live-blink{0%,100%{opacity:1}50%{opacity:.4}}
.hero-ver{
  position:absolute;right:2.5rem;top:50%;transform:translateY(-50%);
  font-family:'Orbitron',monospace;font-size:5rem;font-weight:900;
  color:rgba(255,107,0,0.06);letter-spacing:-5px;line-height:1;user-select:none;
}

/* SECTION TITLE */
.stitle{
  font-family:'Orbitron',monospace;font-size:.75rem;font-weight:700;letter-spacing:3px;
  color:var(--cy);margin:8px 0 14px;padding:0 0 8px 14px;
  border-bottom:1px solid var(--border2);position:relative;
}
.stitle::before{
  content:'';position:absolute;left:0;top:50%;transform:translateY(-50%);
  width:4px;height:70%;background:var(--cy);border-radius:2px;
  box-shadow:0 0 8px var(--cy-glow);
}

/* METRIC CARDS */
.mgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px;}
.mgrid2{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:12px;}
.mgrid3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px;}
.mcard{
  background:var(--card-bg);border:1px solid var(--border);border-radius:12px;
  padding:16px 12px;text-align:center;position:relative;overflow:hidden;
  backdrop-filter:blur(12px);transition:all .3s;
  box-shadow:0 4px 24px rgba(0,0,0,0.4);
}
.mcard::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--card-top,var(--or));}
.mcard::after{
  content:'';position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(ellipse at 50% 0%,rgba(255,107,0,0.06),transparent 70%);
}
.mcard:hover{transform:translateY(-3px);border-color:var(--or);box-shadow:0 8px 32px rgba(255,107,0,0.15);}
.mval{
  font-family:'Orbitron',monospace;font-size:2.2rem;font-weight:800;
  color:var(--card-color,var(--or));line-height:1;
  text-shadow:0 0 15px var(--card-glow,var(--or-glow));
}
.mlbl{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--text3);letter-spacing:2px;margin-top:5px;}
.mc-car{--card-color:var(--gr);--card-top:var(--gr);--card-glow:var(--gr-glow);}
.mc-bike{--card-color:var(--or);--card-top:var(--or);--card-glow:var(--or-glow);}
.mc-tot{--card-color:var(--cy);--card-top:var(--cy);--card-glow:var(--cy-glow);}
.mc-aqi{--card-color:var(--re);--card-top:var(--re);--card-glow:var(--re-glow);}
.mc-eff{--card-color:var(--pu);--card-top:var(--pu);--card-glow:var(--pu-glow);}
.mc-co2{--card-color:var(--gr);--card-top:var(--gr);--card-glow:var(--gr-glow);}
.mc-spd{--card-color:var(--ye);--card-top:var(--ye);--card-glow:var(--ye-glow);}
.mc-flow{--card-color:var(--cy);--card-top:var(--cy);--card-glow:var(--cy-glow);}

/* AQI PANEL */
.aqi-panel{
  background:var(--card-bg);border:1px solid var(--border);border-radius:12px;
  padding:18px 16px;margin-bottom:12px;backdrop-filter:blur(12px);
  box-shadow:0 4px 24px rgba(0,0,0,0.4);
}
.aqi-big{font-family:'Orbitron',monospace;font-size:3rem;font-weight:900;line-height:1;}
.aqi-tag{
  display:inline-block;border-radius:4px;padding:4px 14px;
  font-family:'Share Tech Mono',monospace;font-size:.65rem;font-weight:700;
  margin-top:6px;letter-spacing:2px;
}

/* SIGNAL PANEL */
.sig-panel{
  border-radius:12px;padding:18px;margin-bottom:12px;
  backdrop-filter:blur(12px);position:relative;overflow:hidden;
  box-shadow:0 4px 24px rgba(0,0,0,0.4);
}
.sig-green{background:rgba(0,255,136,0.06);border:1px solid rgba(0,255,136,0.25);}
.sig-yellow{background:rgba(255,215,0,0.06);border:1px solid rgba(255,215,0,0.25);}
.sig-red{background:rgba(255,34,68,0.06);border:1px solid rgba(255,34,68,0.25);}
.sig-emergency{
  background:rgba(255,34,68,0.12);border:2px solid rgba(255,34,68,0.6);
  animation:emergency-pulse 0.8s infinite;
}
@keyframes emergency-pulse{
  0%,100%{box-shadow:0 0 0 0 rgba(255,34,68,0.4)}
  50%{box-shadow:0 0 0 16px rgba(255,34,68,0)}
}
.sig-lbl{font-family:'Share Tech Mono',monospace;font-size:.62rem;color:var(--text3);letter-spacing:2px;}
.sig-time{font-family:'Orbitron',monospace;font-size:3.2rem;font-weight:900;line-height:1;margin:5px 0;}
.sig-green .sig-time{color:var(--gr);text-shadow:0 0 20px var(--gr-glow);}
.sig-yellow .sig-time{color:var(--ye);text-shadow:0 0 20px var(--ye-glow);}
.sig-red .sig-time,.sig-emergency .sig-time{color:var(--re);text-shadow:0 0 20px var(--re-glow);}
.sig-desc{font-size:.88rem;color:var(--text2);margin-top:8px;line-height:1.5;}

/* TRAFFIC LIGHT VISUAL */
.tl-wrap{display:flex;justify-content:center;align-items:center;gap:24px;margin:12px 0;}
.tl-housing{
  background:#0a0f1e;border:2px solid rgba(255,255,255,0.08);border-radius:30px;
  padding:14px 10px;display:flex;flex-direction:column;gap:10px;
  box-shadow:0 8px 32px rgba(0,0,0,0.6);
}
.tl-light{width:30px;height:30px;border-radius:50%;transition:all .4s;}
.tl-red-off{background:#3a0a0a;box-shadow:none;}
.tl-red-on{background:var(--re);box-shadow:0 0 16px var(--re),0 0 40px rgba(255,34,68,0.4);}
.tl-yellow-off{background:#2a1a00;}
.tl-yellow-on{background:var(--ye);box-shadow:0 0 16px var(--ye),0 0 40px rgba(255,215,0,0.4);}
.tl-green-off{background:#002a12;}
.tl-green-on{background:var(--gr);box-shadow:0 0 16px var(--gr),0 0 40px rgba(0,255,136,0.4);}
.tl-info{text-align:center;}

/* INTERSECTION GRID */
.intersection-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:8px 0;}
.int-card{
  background:var(--card-bg);border:1px solid var(--border);border-radius:10px;
  padding:12px;text-align:center;backdrop-filter:blur(8px);transition:all .3s;
}
.int-card.active-green{border-color:rgba(0,255,136,0.4);background:rgba(0,255,136,0.04);}
.int-card.active-red{border-color:rgba(255,34,68,0.4);background:rgba(255,34,68,0.04);}
.int-card.active-yellow{border-color:rgba(255,215,0,0.4);background:rgba(255,215,0,0.04);}
.int-card.emergency{border-color:rgba(255,34,68,0.7);animation:emergency-pulse 0.8s infinite;}
.int-name{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--text3);letter-spacing:1.5px;}
.int-signal{font-size:1.5rem;margin:4px 0;}
.int-time{font-family:'Orbitron',monospace;font-size:1.3rem;font-weight:700;}

/* ALERTS */
.al-crit{
  background:rgba(255,34,68,0.08);border-left:3px solid var(--re);
  border-radius:0 8px 8px 0;padding:10px 14px;margin:5px 0;
  font-family:'Rajdhani',sans-serif;font-size:.9rem;color:#ff6688;
}
.al-warn{
  background:rgba(255,107,0,0.08);border-left:3px solid var(--or);
  border-radius:0 8px 8px 0;padding:10px 14px;margin:5px 0;
  font-family:'Rajdhani',sans-serif;font-size:.9rem;color:var(--or);
}
.al-ok{
  background:rgba(0,255,136,0.06);border-left:3px solid var(--gr);
  border-radius:0 8px 8px 0;padding:10px 14px;margin:5px 0;
  font-family:'Rajdhani',sans-serif;font-size:.9rem;color:var(--gr);
}
.al-info{
  background:rgba(0,212,255,0.06);border-left:3px solid var(--cy);
  border-radius:0 8px 8px 0;padding:10px 14px;margin:5px 0;
  font-family:'Rajdhani',sans-serif;font-size:.9rem;color:var(--cy);
}
.anomaly-card{
  background:rgba(255,107,0,0.1);border:1px solid rgba(255,107,0,0.3);
  border-radius:8px;padding:10px 14px;margin:6px 0;font-size:.88rem;color:var(--or);
  animation:flicker 2s infinite;
}
@keyframes flicker{0%,100%{opacity:1}92%,96%{opacity:.7}}
.anomaly-card.critical{background:rgba(255,34,68,0.12);border-color:rgba(255,34,68,0.4);color:#ff6688;}

/* EMERGENCY BANNER */
.emergency-banner{
  background:linear-gradient(135deg,rgba(183,0,30,0.9),rgba(230,0,50,0.85));
  border:1px solid rgba(255,34,68,0.6);border-radius:10px;
  padding:14px 20px;margin:8px 0;
  font-family:'Orbitron',monospace;font-size:.9rem;font-weight:700;
  color:#fff;text-align:center;letter-spacing:2px;
  box-shadow:0 0 30px rgba(255,34,68,0.4);
  animation:emergency-pulse 0.8s infinite;
}

/* ML ROWS */
.mlrow{
  background:var(--card-bg);border:1px solid var(--border);border-radius:8px;
  padding:10px 14px;transition:all .3s;
}
.mlrow:hover{border-color:var(--or);box-shadow:0 0 12px var(--or-glow);}
.mlrow-lbl{font-family:'Share Tech Mono',monospace;font-size:.6rem;color:var(--text3);letter-spacing:1.5px;}
.mlrow-val{font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;margin-top:2px;}

/* LANE BARS */
.lane-wrap{margin:6px 0;}
.lane-label{font-family:'Share Tech Mono',monospace;font-size:.62rem;color:var(--text3);letter-spacing:1.5px;margin-bottom:4px;}
.lane-track{height:12px;background:rgba(255,255,255,0.05);border-radius:6px;border:1px solid var(--border);overflow:hidden;position:relative;}
.lane-fill{height:100%;border-radius:6px;transition:width .6s ease;position:relative;}
.lane-fill::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.15),transparent);animation:shimmer 2s infinite;}
@keyframes shimmer{0%{transform:translateX(-100%)}100%{transform:translateX(100%)}}
.lane-pct{font-family:'Orbitron',monospace;font-size:.8rem;font-weight:700;margin-top:3px;}

/* SPEED GAUGE */
.speed-gauge{
  background:var(--card-bg);border:1px solid var(--border);border-radius:12px;
  padding:16px;text-align:center;backdrop-filter:blur(12px);
}
.speed-val{font-family:'Orbitron',monospace;font-size:2.4rem;font-weight:900;color:var(--ye);text-shadow:0 0 15px var(--ye-glow);}
.speed-unit{font-family:'Share Tech Mono',monospace;font-size:.65rem;color:var(--text3);letter-spacing:2px;}

/* CONGESTION INDEX */
.congestion-ring{position:relative;width:90px;height:90px;margin:0 auto;}
.cring-svg{transform:rotate(-90deg);}
.cring-val{
  position:absolute;inset:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center;
}
.cring-num{font-family:'Orbitron',monospace;font-size:1.4rem;font-weight:900;}
.cring-lbl{font-family:'Share Tech Mono',monospace;font-size:.5rem;color:var(--text3);letter-spacing:1px;}

/* INCIDENT LOG */
.incident-log{
  background:var(--card-bg);border:1px solid var(--border);border-radius:12px;
  padding:14px;max-height:200px;overflow-y:auto;
}
.incident-item{
  display:flex;gap:10px;align-items:flex-start;
  padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04);
  font-family:'Rajdhani',sans-serif;font-size:.85rem;
}
.incident-time{font-family:'Share Tech Mono',monospace;font-size:.6rem;color:var(--text3);min-width:55px;padding-top:2px;}
.incident-icon{font-size:1rem;min-width:20px;}
.incident-text{color:var(--text2);line-height:1.4;}
.incident-log::-webkit-scrollbar{width:3px;}
.incident-log::-webkit-scrollbar-track{background:transparent;}
.incident-log::-webkit-scrollbar-thumb{background:var(--or);border-radius:2px;}

/* ROUTE ADVISORY */
.route-card{
  background:var(--card-bg);border:1px solid var(--border);border-radius:12px;
  padding:14px;backdrop-filter:blur(12px);
}
.route-item{
  display:flex;justify-content:space-between;align-items:center;
  padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);
}
.route-item:last-child{border-bottom:none;}
.route-name{font-family:'Rajdhani',sans-serif;font-size:.95rem;font-weight:600;color:var(--text);}
.route-status{
  font-family:'Share Tech Mono',monospace;font-size:.62rem;
  padding:3px 10px;border-radius:4px;letter-spacing:1px;
}
.route-free{background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.25);color:var(--gr);}
.route-mod{background:rgba(255,215,0,0.1);border:1px solid rgba(255,215,0,0.25);color:var(--ye);}
.route-jam{background:rgba(255,34,68,0.1);border:1px solid rgba(255,34,68,0.25);color:var(--re);}
.route-time{font-family:'Orbitron',monospace;font-size:.85rem;font-weight:700;color:var(--cy);}

/* STATS */
.stat-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.stat-item{
  background:var(--card-bg);border:1px solid var(--border);border-radius:10px;
  padding:14px;text-align:center;backdrop-filter:blur(8px);
}
.stat-val{font-family:'Orbitron',monospace;font-size:1.6rem;font-weight:800;}
.stat-lbl{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--text3);letter-spacing:1.5px;margin-top:4px;}

/* EFFICIENCY */
.eff-card{
  background:var(--card-bg);border:1px solid var(--border);border-radius:12px;
  padding:18px;backdrop-filter:blur(12px);
}
.eff-score{font-family:'Orbitron',monospace;font-size:3rem;font-weight:900;color:var(--pu);text-shadow:0 0 20px var(--pu-glow);}
.eff-bar{height:8px;border-radius:4px;background:rgba(255,255,255,0.06);margin:8px 0;overflow:hidden;}
.eff-fill{height:100%;border-radius:4px;transition:width .6s ease;}

/* PREDICTION ACCURACY */
.acc-bar{
  background:var(--card-bg);border:1px solid var(--border);border-radius:10px;
  padding:12px 14px;margin:5px 0;
}
.acc-name{font-family:'Share Tech Mono',monospace;font-size:.62rem;color:var(--text3);letter-spacing:1px;margin-bottom:6px;}
.acc-track{height:8px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden;margin-bottom:4px;}
.acc-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,var(--cy),var(--or));}
.acc-pct{font-family:'Orbitron',monospace;font-size:.72rem;font-weight:700;color:var(--cy);}

/* ALGO SECTION */
.algo-card{
  background:var(--card-bg);border:1px solid var(--border);border-radius:14px;
  padding:20px 22px;margin:8px 0;backdrop-filter:blur(12px);
  box-shadow:0 4px 24px rgba(0,0,0,0.4);
}
.algo-name{font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;color:var(--or);margin-bottom:2px;text-shadow:0 0 10px var(--or-glow);}
.algo-type{font-family:'Share Tech Mono',monospace;font-size:.62rem;color:var(--cy);letter-spacing:2px;margin-bottom:10px;}
.algo-desc{font-family:'Rajdhani',sans-serif;font-size:.9rem;color:var(--text2);line-height:1.7;}
.algo-formula{
  background:rgba(0,212,255,0.04);border:1px solid var(--border2);border-radius:6px;
  padding:9px 13px;margin:10px 0;font-family:'Share Tech Mono',monospace;
  font-size:.72rem;color:var(--cy);line-height:1.6;
}
.algo-role{
  background:rgba(0,255,136,0.04);border:1px solid rgba(0,255,136,0.15);
  border-radius:6px;padding:9px 13px;
  font-family:'Rajdhani',sans-serif;font-size:.85rem;color:var(--gr);
}
.algo-row{
  display:grid;grid-template-columns:145px 120px 1fr;gap:10px;align-items:start;
  border-bottom:1px solid var(--border);padding:12px 0;
}
.algo-row:last-child{border-bottom:none;}
.ar-name{font-family:'Orbitron',monospace;font-size:.82rem;font-weight:700;color:var(--or);}
.ar-type{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--bg);background:var(--cy);border-radius:4px;padding:3px 8px;text-align:center;}
.ar-why{font-family:'Rajdhani',sans-serif;font-size:.88rem;color:var(--text2);line-height:1.55;}
.ar-why b{color:var(--text);}

/* SUMMARY */
.summary-card{
  background:var(--card-bg);border:1px solid var(--border);border-radius:14px;
  padding:22px 24px;margin:10px 0;backdrop-filter:blur(12px);
}
.summary-title{font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;color:var(--or);margin-bottom:10px;}
.summary-text{font-family:'Rajdhani',sans-serif;font-size:.95rem;color:var(--text2);line-height:1.8;}
.summary-text b{color:var(--or);}

/* INFO CARD */
.info-card{
  background:rgba(0,212,255,0.04);border:1px solid var(--border2);border-radius:10px;
  padding:12px 16px;margin:8px 0;
  font-family:'Rajdhani',sans-serif;font-size:.88rem;color:var(--text2);line-height:1.65;
}
.info-card b{color:var(--cy);}

/* STATUSBAR */
.statusbar{
  background:rgba(7,11,20,0.9);border:1px solid var(--border);border-radius:6px;
  padding:7px 14px;font-family:'Share Tech Mono',monospace;font-size:.64rem;
  color:var(--text3);display:flex;justify-content:space-between;
  margin-top:6px;backdrop-filter:blur(8px);
}
.statusbar span b{color:var(--or);}

/* BUTTONS */
.stButton>button{
  font-family:'Orbitron',monospace!important;font-size:.72rem!important;
  font-weight:700!important;letter-spacing:2px!important;border-radius:6px!important;
  transition:all .3s!important;
}
.stButton>button[kind="primary"]{
  background:linear-gradient(135deg,#ff6b00,#ff8c00)!important;
  border:none!important;color:#000!important;
  box-shadow:0 4px 20px rgba(255,107,0,0.4)!important;
}
.stButton>button[kind="primary"]:hover{
  box-shadow:0 6px 32px rgba(255,107,0,0.7)!important;
  transform:translateY(-2px)!important;
}
.stButton>button:not([kind="primary"]){
  background:rgba(13,20,33,0.9)!important;
  border:1px solid var(--border)!important;color:var(--text2)!important;
}
.stButton>button:not([kind="primary"]):hover{border-color:var(--or)!important;color:var(--or)!important;}

/* TABS */
.stTabs [data-baseweb="tab-list"]{
  background:var(--card-bg);border-radius:8px;padding:5px;
  border:1px solid var(--border);backdrop-filter:blur(12px);
}
.stTabs [data-baseweb="tab"]{
  font-family:'Orbitron',monospace!important;font-size:.65rem!important;
  font-weight:600!important;color:var(--text3)!important;border-radius:6px!important;
  letter-spacing:1px!important;
}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,var(--or),var(--or2))!important;
  color:#000!important;
}

/* CHARTS */
.stProgress>div>div>div{background:linear-gradient(90deg,var(--or),var(--cy))!important;}
.streamlit-expanderHeader{
  font-family:'Orbitron',monospace!important;font-weight:700!important;
  color:var(--or)!important;background:var(--card-bg)!important;
  border-radius:8px!important;letter-spacing:1px!important;
}

/* FOOTER */
.footer{
  text-align:center;padding:24px;
  font-family:'Share Tech Mono',monospace;font-size:.66rem;
  color:var(--text3);border-top:1px solid var(--border);margin-top:24px;
  background:rgba(7,11,20,0.8);
}
.footer span{color:var(--or);text-shadow:0 0 8px var(--or-glow);}

hr{border-color:var(--border)!important;opacity:1!important;}
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:var(--bg2);}
::-webkit-scrollbar-thumb{background:rgba(255,107,0,0.3);border-radius:2px;}
::-webkit-scrollbar-thumb:hover{background:var(--or);}

/* SIDEBAR INPUTS */
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"]{
  background:var(--or)!important;box-shadow:0 0 8px var(--or-glow)!important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] div[data-testid]{
  background:var(--or)!important;
}
</style>""", unsafe_allow_html=True)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
INTERSECTIONS = ["North Junction", "South Gate", "East Cross", "West Hub"]
INT_COLORS = ["#00ff88", "#ff2244", "#ffd700", "#00d4ff"]
CO2_PER_IDLE_SEC = 0.0025
EMERGENCY_TYPES = ["🚑 AMBULANCE", "🚒 FIRE ENGINE", "🚓 POLICE UNIT"]
ROUTES = ["Via Highway NH-48", "Via Ring Road", "Via Bypass MH-4", "Via City Centre"]

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
def _init():
    D = dict(
        history=deque(maxlen=300), running=False, frame_no=0, yolo_model=None, cap=None,
        prev_c=0, prev_b=0, peak=0, frames_done=0, cnn_feats=deque(maxlen=80),
        lstm_last=120.0, rnn_last=8.0, frame_skip=3,
        emergency_active=False, emergency_type="", emergency_countdown=0, emergency_intersection=0,
        green_wave_mode=False, co2_saved=0.0, efficiency_scores=deque(maxlen=120),
        total_vehicles_cleared=0, idle_time_saved=0.0, incident_detected=False, prev_total=0,
        session_start=datetime.now(),
        vid_path=None, out_path=None, vid_done=False,
        vid_bytes=None, vid_stats=None,
        # NEW v7.0
        speed_history=deque(maxlen=100), avg_speed=42.0,
        flow_rate=0.0, congestion_index=0,
        incident_log=deque(maxlen=50),
        pred_accuracy={"KNN": 87.2, "RF": 91.4, "GBM": 93.1, "ANN": 82.6},
        route_status={r: "FREE" for r in ROUTES},
        sound_alert=False, total_alerts=0,
        heatmap_data=np.zeros((10, 14), dtype=float),
    )
    for k, v in D.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()

# ─── MODEL LOADERS ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading YOLOv8n...")
def _load_yolo():
    if not YOLO_AVAILABLE: return None
    try: return YOLO("yolov8n.pt")
    except: return None

CAR_IDS = {2}; BIKE_IDS = {1, 3}
CAR_IDS_EX = {2,5,7}; BIKE_IDS_EX = {1,3}; ALL_VEH_IDS = CAR_IDS_EX | BIKE_IDS_EX

# ─── VEHICLE DETECTION ───────────────────────────────────────────────────────

def _run_yolo_on_tile(model, tile, conf=0.20):
    try:
        res = model(tile, verbose=False, conf=conf, iou=0.40, imgsz=640, max_det=300, agnostic_nms=True)[0]
        return [(int(b.cls[0]),float(b.conf[0]),*map(int,b.xyxy[0].cpu().numpy()))
                for b in res.boxes if int(b.cls[0]) in ALL_VEH_IDS]
    except: return []

def _nms_boxes(boxes, iou_thr=0.45):
    if not boxes: return []
    boxes = sorted(boxes, key=lambda b: b[1], reverse=True)
    sup=[False]*len(boxes); kept=[]
    for i in range(len(boxes)):
        if sup[i]: continue
        kept.append(boxes[i]); _,_,x1i,y1i,x2i,y2i=boxes[i]; ai=max(0,x2i-x1i)*max(0,y2i-y1i)
        for j in range(i+1,len(boxes)):
            if sup[j]: continue
            _,_,x1j,y1j,x2j,y2j=boxes[j]
            inter=max(0,min(x2i,x2j)-max(x1i,x1j))*max(0,min(y2i,y2j)-max(y1i,y1j))
            if inter>0 and inter/(max(1,ai+max(0,x2j-x1j)*max(0,y2j-y1j)-inter))>iou_thr: sup[j]=True
    return kept

def detect_vehicles(model, frame):
    small = cv2.resize(frame, (416, 416))
    res = model(small, verbose=False, conf=0.40, imgsz=416)[0]
    cars = bikes = 0; out = frame.copy(); H0, W0 = frame.shape[:2]; sx, sy = W0/416, H0/416
    for box in res.boxes:
        cid = int(box.cls[0]); cf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = int(x1*sx), int(y1*sy), int(x2*sx), int(y2*sy)
        if cid in CAR_IDS: cars += 1; col, lb = (0, 220, 100), f"CAR {cf:.2f}"
        elif cid in BIKE_IDS: bikes += 1; col, lb = (255, 140, 0), f"BIKE {cf:.2f}"
        else: continue
        cv2.rectangle(out, (x1, y1), (x2, y2), col, 2)
        cv2.rectangle(out, (x1, y1-20), (x1+len(lb)*8+4, y1), col, -1)
        cv2.putText(out, lb, (x1+2, y1-4), cv2.FONT_HERSHEY_SIMPLEX, .45, (0, 0, 0), 1)
    _hud(out, cars, bikes); return out, cars, bikes


def detect_vehicles_fast(model, frame):
    """Lightweight single-pass detection for webcam — no tiling, low latency."""
    H0, W0 = frame.shape[:2]; out = frame.copy()
    res = model(frame, verbose=False, conf=0.25, iou=0.45,
                imgsz=640, max_det=200, agnostic_nms=True)[0]
    cars = bikes = 0
    for box in res.boxes:
        cid = int(box.cls[0])
        if cid not in ALL_VEH_IDS: continue
        cf = float(box.conf[0])
        x1,y1,x2,y2 = map(int, box.xyxy[0].cpu().numpy())
        x1,y1 = max(0,x1),max(0,y1); x2,y2 = min(W0-1,x2),min(H0-1,y2)
        if cid in CAR_IDS_EX: cars+=1
        elif cid in BIKE_IDS_EX: bikes+=1
        col=VEH_COLORS.get(cid,(200,200,200)); lb=f"{VEH_LABELS.get(cid,'VEH')} {cf:.2f}"
        area=max(1,(x2-x1))*max(1,(y2-y1)); thick=1 if area<2000 else 2
        cv2.rectangle(out,(x1,y1),(x2,y2),col,thick)
        if area>500:
            ly=max(y1-4,14)
            cv2.rectangle(out,(x1,ly-12),(x1+len(lb)*7+4,ly+2),col,-1)
            cv2.putText(out,lb,(x1+2,ly),cv2.FONT_HERSHEY_SIMPLEX,.38,(0,0,0),1)
    _hud(out,cars,bikes); return out,cars,bikes

# ─── DEMO FRAME ───────────────────────────────────────────────────────────────
_vpool = []
class _V:
    def __init__(self, night=False):
        self.t = "car" if random.random() < .68 else "bike"
        self.lane = random.randint(0, 1)
        self.w = random.randint(54, 72) if self.t == "car" else random.randint(22, 32)
        self.h = random.randint(28, 36) if self.t == "car" else random.randint(16, 24)
        self.spd = random.uniform(4, 7) if self.t == "car" else random.uniform(5.5, 10)
        if night:
            self.col = random.choice([(60,60,80),(80,60,60),(50,70,100)] if self.t=="car" else [(20,60,120),(120,50,20)])
        else:
            self.col = random.choice([(180,50,50),(50,50,180),(80,80,80),(50,130,50),(150,100,0)] if self.t=="car" else [(0,100,200),(200,80,0),(140,0,140)])
        self.x = -self.w-5 if self.lane == 0 else 565
        self.y = random.randint(155, 185) if self.lane == 0 else random.randint(220, 250)
    def update(self): self.x += (self.spd if self.lane == 0 else -self.spd)
    def dead(self): return self.x > 580 or self.x < -90

def demo_frame(tc, tb, night=False, emergency=False):
    global _vpool
    H, W = 400, 560
    # Cyberpunk palette
    if night:
        sky = (8, 12, 20); grnd = (12, 18, 10); road = (20, 22, 28); divdr = (0, 200, 100)
        edge = (0, 150, 200); bld = (15, 22, 35); win_c = (80, 120, 200); txt = (0, 180, 100)
    else:
        sky = (180, 200, 230); grnd = (160, 180, 150); road = (70, 72, 80); divdr = (255, 140, 0)
        edge = (220, 220, 220); bld = (210, 205, 195); win_c = (170, 200, 240); txt = (160, 90, 0)

    img = np.full((H, W, 3), 200, dtype=np.uint8)
    img[:, :] = sky; img[H//2:, :] = grnd
    ry = int(H * .42); cv2.rectangle(img, (0, ry), (W, H), road, -1)
    cy2 = int(H * .54)
    for x in range(0, W, 32): cv2.line(img, (x, cy2), (x+18, cy2), divdr, 3)
    cv2.line(img, (0, ry), (W, ry), edge, 2); cv2.line(img, (0, H-3), (W, H-3), edge, 2)

    blds = [(15,45,48,120),(72,58,55,120),(140,38,60,120),(220,50,52,120),(290,42,60,120),(368,55,50,120),(430,40,56,120),(496,48,52,120)]
    for bx, by, bw2, bh2 in blds:
        bc = (40, 50, 70) if night else (140, 130, 120)
        cv2.rectangle(img, (bx, by), (bx+bw2, by+bh2), bld, -1)
        cv2.rectangle(img, (bx, by), (bx+bw2, by+bh2), bc, 1)
        for wy2 in range(by+8, by+bh2-8, 16):
            for wx2 in range(bx+5, bx+bw2-5, 11):
                wc = (200, 230, 255) if night and random.random() > .35 else win_c
                cv2.rectangle(img, (wx2, wy2), (wx2+7, wy2+8), wc, -1)

    if night:
        for _ in range(50):
            sx2, sy2 = random.randint(0, W), random.randint(0, ry-10)
            br = random.randint(160, 255)
            cv2.circle(img, (sx2, sy2), 1, (br, br, br), -1)
        cv2.circle(img, (490, 40), 16, (200, 220, 160), -1)
        cv2.circle(img, (498, 35), 11, (8, 12, 20), -1)
        # Neon glow effect on road
        overlay = img.copy()
        cv2.rectangle(overlay, (0, ry), (W, H), (0, 30, 50), -1)
        cv2.addWeighted(overlay, .25, img, .75, 0, img)
    else:
        cv2.circle(img, (510, 45), 22, (255, 220, 60), -1)

    for tx in [8, 68, 132, 210, 282, 360, 422, 490]:
        ty2 = ry - 2
        cv2.rectangle(img, (tx, ty2-14), (tx+5, ty2), (100, 70, 30), -1)
        cv2.circle(img, (tx+2, ty2-16), 9, (15, 40, 15) if night else (30, 110, 30), -1)

    for pole_x in [130, 420]:
        cv2.line(img, (pole_x, ry-65), (pole_x, ry+5), (60, 60, 65), 3)
        cv2.rectangle(img, (pole_x-6, ry-65), (pole_x+6, ry-30), (30, 32, 38), -1)
        col_r = (220, 0, 30) if night else (180, 20, 20)
        col_y_t = (180, 160, 0) if night else (160, 140, 0)
        col_g = (0, 220, 80) if night else (20, 160, 40)
        cv2.circle(img, (pole_x, ry-61), 5, col_r, -1)
        if night: cv2.circle(img, (pole_x, ry-61), 8, (220, 0, 30, 0), -1)
        cv2.circle(img, (pole_x, ry-49), 5, col_y_t, -1)
        cv2.circle(img, (pole_x, ry-37), 5, col_g, -1)
        if night:
            cv2.circle(img, (pole_x, ry-61), 12, (80, 0, 10), 1)
            cv2.circle(img, (pole_x, ry-37), 12, (0, 80, 30), 1)

    if emergency:
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (W, H), (120, 0, 0), -1)
        cv2.addWeighted(overlay, .2, img, .8, 0, img)
        cv2.putText(img, "! EMERGENCY OVERRIDE ACTIVE !", (20, H-18), cv2.FONT_HERSHEY_SIMPLEX, .44, (255, 60, 60), 2)

    _vpool = [v for v in _vpool if not v.dead()]
    cc = sum(1 for v in _vpool if v.t == "car"); cb = sum(1 for v in _vpool if v.t == "bike")
    if cc < tc and random.random() < .28: v = _V(night); v.t = "car"; _vpool.append(v)
    if cb < tb and random.random() < .35: v = _V(night); v.t = "bike"; _vpool.append(v)

    for lane in [1, 0]:
        for v in _vpool:
            if v.lane != lane: continue
            v.update(); x1, y1 = int(v.x), int(v.y); x2, y2 = x1+v.w, y1+v.h
            cv2.rectangle(img, (x1+3, y1+3), (x2+3, y2+3), (10, 10, 15), -1)
            cv2.rectangle(img, (x1, y1), (x2, y2), v.col, -1)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), 1)
            if night:
                hl = (255, 255, 220) if v.lane == 0 else (255, 100, 80)
                hx = x2-2 if v.lane == 0 else x1+2
                cv2.circle(img, (hx, y1+int(v.h*.28)), 5, hl, -1)
                cv2.circle(img, (hx, y2-int(v.h*.28)), 5, hl, -1)
                # headlight glow
                cv2.circle(img, (hx, y1+int(v.h*.28)), 9, (hl[0]//3, hl[1]//3, hl[2]//3), -1)
            g = (min(255, v.col[0]+80), min(255, v.col[1]+80), min(255, v.col[2]+80))
            cv2.rectangle(img, (x1+int(v.w*.18), y1+3), (x1+int(v.w*.82), y1+int(v.h*.5)), g, -1)
            wr = max(4, int(v.h*.22))
            cv2.circle(img, (x1+int(v.w*.2), y2), wr, (20, 20, 20), -1)
            cv2.circle(img, (x1+int(v.w*.8), y2), wr, (20, 20, 20), -1)
            lb = "CAR" if v.t == "car" else "BIKE"
            lc = (0, 160, 60) if v.t == "car" else (200, 90, 0)
            cv2.rectangle(img, (x1, y1-15), (x1+len(lb)*7+5, y1), lc, -1)
            cv2.putText(img, lb, (x1+2, y1-3), cv2.FONT_HERSHEY_SIMPLEX, .36, (255, 255, 255), 1)

    cars = sum(1 for v in _vpool if v.t == "car"); bikes = sum(1 for v in _vpool if v.t == "bike")
    _hud_light(img, cars, bikes, night)
    cv2.putText(img, f"TrafficIQ v7.0 | Sanket Sutar", (6, H-6), cv2.FONT_HERSHEY_SIMPLEX, .28, txt, 1)
    cv2.putText(img, f"{'NIGHT' if night else 'DAY'}|{datetime.now().strftime('%H:%M:%S')}", (W-115, H-6), cv2.FONT_HERSHEY_SIMPLEX, .28, txt, 1)
    return img, cars, bikes

def _hud_light(f, c, b, night=False):
    overlay = f.copy()
    hbg = (8, 12, 20) if night else (240, 245, 255)
    cv2.rectangle(overlay, (0, 0), (218, 64), hbg, -1)
    cv2.addWeighted(overlay, .75, f, .25, 0, f)
    cv2.rectangle(f, (0, 0), (218, 64), (0, 200, 80) if night else (255, 140, 0), 2)
    tc2 = (0, 255, 120) if night else (0, 150, 50)
    bc = (255, 140, 40) if night else (200, 80, 0)
    cv2.putText(f, f"CARS : {c}", (7, 22), cv2.FONT_HERSHEY_SIMPLEX, .60, tc2, 2)
    cv2.putText(f, f"BIKES: {b}", (7, 48), cv2.FONT_HERSHEY_SIMPLEX, .60, bc, 2)

def _hud(f, c, b):
    overlay = f.copy(); cv2.rectangle(overlay, (0, 0), (220, 64), (240, 245, 255), -1)
    cv2.addWeighted(overlay, .75, f, .25, 0, f)
    cv2.rectangle(f, (0, 0), (220, 64), (255, 140, 0), 2)
    cv2.putText(f, f"CARS : {c}", (7, 22), cv2.FONT_HERSHEY_SIMPLEX, .60, (0, 150, 50), 2)
    cv2.putText(f, f"BIKES: {b}", (7, 48), cv2.FONT_HERSHEY_SIMPLEX, .60, (200, 80, 0), 2)

# ─── LOGIC FUNCTIONS ─────────────────────────────────────────────────────────
def classify_traffic(n):
    if n <= 5: return "Low", "#00ff88", 1
    if n <= 15: return "Medium", "#ffd700", 2
    return "High", "#ff2244", 3

def classify_aqi(a):
    if a <= 50: return "GOOD", "#00ff88", "🟢", "rgba(0,255,136,0.06)"
    if a <= 100: return "MODERATE", "#ffd700", "🟡", "rgba(255,215,0,0.06)"
    if a <= 150: return "SENSITIVE", "#ff8c00", "🟠", "rgba(255,107,0,0.06)"
    if a <= 200: return "UNHEALTHY", "#ff2244", "🔴", "rgba(255,34,68,0.06)"
    if a <= 300: return "VERY UNHEALTHY", "#bf5fff", "🟣", "rgba(191,95,255,0.06)"
    return "HAZARDOUS", "#ff0066", "☠️", "rgba(255,0,102,0.08)"

def signal_decision(lv, aqi, emergency=False, night=False):
    if emergency: return 90, "🚨 EMERGENCY OVERRIDE — Priority corridor active.", "red"
    nb = 5 if night else 0; hi = aqi > 150
    if lv == "High" and hi: return 60+nb, "Extended green + Pollution Alert — Critical congestion.", "red"
    if lv == "High": return 45+nb, "Extended green — High vehicle density detected.", "yellow"
    if lv == "Medium" and hi: return 35+nb, "Standard + Air Alert — Moderate traffic, monitor AQI.", "yellow"
    if lv == "Medium": return 30+nb, "Standard cycle — Normal traffic conditions.", "green"
    if lv == "Low" and hi: return 20+nb, "Short green + Eco Advisory — Reduce idle time.", "green"
    return 15+nb, "Minimal cycle — Light traffic, all nominal.", "green"

def weather_aqi_correction(aqi, temp, humid, wind):
    tc = max(0, (temp-25)*1.8); hc = max(0, (humid-60)*0.6); wc = max(0, (wind-10)*(-1.2))
    return max(0, min(500, aqi+int(tc+hc+wc)))

def compute_efficiency(total, green_t, hist_df):
    if hist_df.empty: return 50.0
    throughput = min(100, total/max(1, green_t)*60)
    consistency = max(0, 100-float(hist_df["green_time"].std())*2) if len(hist_df) > 1 else 70.0
    aqi_pen = min(50, float(hist_df["aqi"].mean())/8) if "aqi" in hist_df else 0.0
    return max(0.0, min(100.0, throughput*.5+consistency*.3-aqi_pen*.2))

def detect_anomaly(hist_df, total, aqi):
    if len(hist_df) < 10: return False, False, 0.0
    zt = abs(total-hist_df["total"].mean())/(hist_df["total"].std()+1e-6)
    za = abs(aqi-hist_df["aqi"].mean())/(hist_df["aqi"].std()+1e-6)
    return zt > 2.5, za > 2.5, round(max(zt, za), 2)

def incident_check(total, prev): return abs(total-prev) >= 8

def update_intersections(n_frame, emerg_int=-1):
    states = []; offsets = [0, 15, 30, 45]
    for i in range(4):
        if i == emerg_int: states.append(("EMERGENCY", 90, "emergency")); continue
        ot = (n_frame+offsets[i]) % 90
        if ot < 45: ph, t, st = "GREEN", 45-ot, "active-green"
        elif ot < 55: ph, t, st = "YELLOW", 55-ot, "active-yellow"
        else: ph, t, st = "RED", 90-ot, "active-red"
        states.append((ph, max(1, t), st))
    return states

def is_night(): h = datetime.now().hour; return h >= 20 or h < 6
def pedestrian_phase(gt): return max(8, int(gt*0.2))
def compute_co2(idle_secs, vehicles): return round(idle_secs*vehicles*CO2_PER_IDLE_SEC, 3)

# ─── NEW v7.0: SPEED ESTIMATION ──────────────────────────────────────────────
def estimate_speed(total, level, night=False):
    """Simulate speed based on congestion level"""
    base = 65 if level == "Low" else 40 if level == "Medium" else 22
    noise = random.gauss(0, 3)
    night_bonus = 5 if night else 0
    spd = max(5, min(90, base + noise + night_bonus))
    return round(spd, 1)

def compute_congestion_index(total, aqi, speed):
    """0-100 composite congestion score"""
    tc = min(50, total/30*50); ac = min(30, aqi/500*30); sc = max(0, (1-speed/80)*20)
    return min(100, int(tc+ac+sc))

def compute_flow_rate(total, hist):
    """Vehicles per minute"""
    if len(hist) < 5: return total * 2.0
    return round(float(np.mean(list(hist)[-10:])) * 2.0, 1)

def update_route_status(congestion_idx):
    """Update route statuses based on congestion"""
    routes = ROUTES.copy()
    random.shuffle(routes)
    statuses = {}
    if congestion_idx < 30:
        for r in routes: statuses[r] = random.choice(["FREE", "FREE", "FREE", "MODERATE"])
    elif congestion_idx < 60:
        for i, r in enumerate(routes):
            statuses[r] = ["FREE", "MODERATE", "MODERATE", "JAM"][i % 4]
    else:
        for i, r in enumerate(routes):
            statuses[r] = ["MODERATE", "JAM", "JAM", "FREE"][i % 4]
    return statuses

def update_heatmap(heatmap, total, frame_no):
    """Simulate vehicle density heatmap update"""
    # Random hotspots
    cx, cy = random.randint(3, 10), random.randint(2, 7)
    intensity = total / 30.0
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            nx, ny = cx+dx, cy+dy
            if 0 <= nx < 14 and 0 <= ny < 10:
                heatmap[ny, nx] = min(1.0, heatmap[ny, nx]*0.85 + intensity*math.exp(-(dx**2+dy**2)/3))
    heatmap *= 0.97  # decay
    return heatmap

# ─── ML MODELS ────────────────────────────────────────────────────────────────
@st.cache_data
def make_training_data(n=800):
    rng = np.random.default_rng(42)
    cars = rng.integers(0, 25, n); bikes = rng.integers(0, 10, n)
    aqi = rng.normal(130, 55, n).clip(0, 400).astype(int); temp = rng.normal(30, 5, n).clip(15, 45).astype(int)
    total = cars+bikes; labels = []
    for t, a in zip(total, aqi):
        lv = classify_traffic(t)[0]; _, _, sig = signal_decision(lv, a); labels.append(sig)
    return pd.DataFrame({"cars": cars, "bikes": bikes, "aqi": aqi, "total": total, "temp": temp, "signal": labels})

@st.cache_resource
def train_knn():
    if not SK_AVAILABLE: return None, None
    df = make_training_data(); X = df[["total", "aqi"]].values; y = df["signal"].values
    p = Pipeline([("sc", StandardScaler()), ("knn", KNeighborsClassifier(n_neighbors=5))]); p.fit(X, y); return p, df

@st.cache_resource
def train_rf():
    if not SK_AVAILABLE: return None, None
    df = make_training_data(); X = df[["cars", "bikes", "aqi", "total"]].values; y = df["signal"].values
    p = Pipeline([("sc", StandardScaler()), ("rf", RandomForestClassifier(n_estimators=120, random_state=42))]); p.fit(X, y); return p, df

@st.cache_resource
def train_kmeans():
    if not SK_AVAILABLE: return None, None
    df = make_training_data(); X = df[["total", "aqi"]].values
    km = KMeans(n_clusters=4, random_state=42, n_init=10); km.fit(X); return km, df

@st.cache_resource
def train_gbm():
    if not SK_AVAILABLE: return None, None
    df = make_training_data(); X = df[["cars", "bikes", "aqi", "total", "temp"]].values; y = df["signal"].values
    p = Pipeline([("sc", StandardScaler()), ("gb", GradientBoostingClassifier(n_estimators=80, random_state=42))]); p.fit(X, y); return p, df

def cnn_extract(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    k1 = np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]], np.float32)
    k2 = np.array([[-1,0,1],[-2,0,2],[-1,0,1]], np.float32)
    k3 = np.array([[1,2,1],[0,0,0],[-1,-2,-1]], np.float32)
    c1 = cv2.filter2D(gray, -1, k1); c2 = cv2.filter2D(gray, -1, k2); c3 = cv2.filter2D(gray, -1, k3)
    p1 = cv2.resize(c1, (gray.shape[1]//4, gray.shape[0]//4)); p2 = cv2.resize(c2, (gray.shape[1]//4, gray.shape[0]//4))
    return {"edge": round(float(np.mean(np.abs(p1))), 2), "hgrad": round(float(np.mean(np.abs(p2))), 2),
            "vgrad": round(float(np.mean(np.abs(c3))), 2), "texture": round(float(np.std(gray)), 2),
            "density": round(float(np.sum(p1 > 30))/(p1.size+1), 4)}

def rnn_predict(hist, steps=5):
    if len(hist) < 3: return [float(hist[-1]) if hist else 10.0]*steps
    W_h, W_x = 0.6, 0.4; h = float(hist[-1])/30.0; preds = []
    for i in range(steps):
        x = hist[-1]/30.0 if i == 0 else preds[-1]/30.0; h = math.tanh(W_h*h+W_x*x)
        preds.append(max(0.0, min(30.0, h*30+random.gauss(0, .7))))
    return [round(p, 1) for p in preds]

def lstm_forecast(hist, steps=8):
    def sig(x): return 1/(1+math.exp(-max(-20, min(20, x))))
    if len(hist) < 4: return [float(hist[-1]) if hist else 120.0]*steps
    W_f, W_i, W_c, W_o = 0.55, 0.45, 0.70, 0.60; h = float(hist[-1])/400; c = h
    trend = (hist[-1]-hist[max(0, len(hist)-5)])/5.0; preds = []
    for i in range(steps):
        x = h+trend/400; f = sig(W_f*(h+x)); ig = sig(W_i*(h+x)); ct = math.tanh(W_c*(h+x)); c = f*c+ig*ct
        o = sig(W_o*(h+c)); h = o*math.tanh(c)
        preds.append(max(0.0, min(500.0, h*400+trend*(i+1)+random.gauss(0, 4))))
    return [round(p, 1) for p in preds]

def ann_classify(total, aqi):
    def relu(x): return max(0.0, x)
    def softmax(v): e = np.exp(v-np.max(v)); return e/e.sum()
    x = np.array([total/30., aqi/500., (total/30.)*(aqi/500.)])
    W1 = np.array([[.8,-.3,.5,-.6,.4,.7,-.2,.6],[.3,.9,-.4,.8,-.5,.2,.8,-.3],[.6,.7,.9,-.2,.8,.5,-.4,.7]])
    h1 = np.array([relu(np.dot(x, W1[:, j])) for j in range(8)])
    W2 = np.array([[.7,.2,-.5,.8],[-.3,.9,.4,-.2],[.5,-.4,.8,.3],[.2,.6,-.3,.9],[-.6,.3,.7,-.4],[.8,-.2,.5,.6],[.4,.7,-.6,.2],[-.1,.5,.8,-.3]])
    h2 = np.array([relu(np.dot(h1, W2[:, j])) for j in range(4)])
    W3 = np.array([[.9,-.4,.3],[.2,.8,-.5],[-.6,.3,.9],[.4,-.7,.6]])
    out = softmax(np.dot(h2, W3))
    return {c: round(float(p), 3) for c, p in zip(["GREEN", "YELLOW", "RED"], out)}

knn_pipe, knn_df = train_knn()
rf_pipe, rf_df = train_rf()
km_model, km_df = train_kmeans()
gbm_pipe, gbm_df = train_gbm()

# ─── CHART THEME ─────────────────────────────────────────────────────────────
BG = "#070b14"; AX = "#0d1421"; GR = "#1a2234"; TC = "#4a5568"
OR = "#ff6b00"; OR2 = "#ffa940"; GRN = "#00ff88"; RED = "#ff2244"
BLU = "#00d4ff"; PRP = "#bf5fff"; YE = "#ffd700"

def _lfig(w=6, h=3.5, r=1, c=1):
    fig, ax = plt.subplots(r, c, figsize=(w, h)); fig.patch.set_facecolor(BG)
    axes = [ax] if (r == 1 and c == 1) else list(ax.flat if hasattr(ax, "flat") else ax)
    for a in axes:
        a.set_facecolor(AX)
        for sp in a.spines.values(): sp.set_edgecolor(GR)
        a.tick_params(colors=TC, labelsize=7); a.xaxis.label.set_color(TC); a.yaxis.label.set_color(TC)
        a.title.set_color(OR); a.grid(color=GR, alpha=0.8, lw=0.5)
    return fig, ax

@st.cache_data
def sample_data():
    rng = np.random.default_rng(42); n = 180
    c = rng.integers(0, 22, n); b = rng.integers(0, 9, n)
    a = rng.normal(130, 50, n).clip(0, 400).astype(int); t = c+b
    df = pd.DataFrame({"cars": c, "bikes": b, "total": t, "aqi": a})
    df["level"] = df["total"].apply(lambda v: classify_traffic(v)[0])
    df["signal"] = df.apply(lambda r: signal_decision(r["level"], r["aqi"])[2], axis=1)
    df["green_time"] = df.apply(lambda r: signal_decision(r["level"], r["aqi"])[0], axis=1)
    return df

def chart_scatter(df):
    fig, ax = _lfig(5.5, 3.6)
    if df.empty: ax.text(.5, .5, "Start Detection to see data", ha="center", va="center", color=TC, fontsize=10)
    else:
        sc = ax.scatter(df["total"], df["aqi"], c=df["aqi"], cmap="YlOrRd", s=52, alpha=0.85, edgecolors=GR, lw=.3, zorder=3)
        cb = plt.colorbar(sc, ax=ax); cb.ax.tick_params(colors=TC, labelsize=7)
        if len(df) > 3:
            z = np.polyfit(df["total"], df["aqi"], 1); p = np.poly1d(z)
            xr = np.linspace(df["total"].min(), df["total"].max(), 50)
            ax.plot(xr, p(xr), color=BLU, lw=1.8, ls="--", alpha=.8, label="Trend")
        ax.axhline(150, color=RED, ls="--", lw=1.2, alpha=.7, label="AQI 150")
        ax.axhline(100, color=OR, ls=":", lw=1, alpha=.7, label="AQI 100")
        ax.set_xlabel("Total Vehicles", fontsize=8); ax.set_ylabel("AQI", fontsize=8)
        ax.legend(fontsize=7, facecolor=AX, edgecolor=GR)
    ax.set_title("Vehicle Count vs AQI — Correlation Analysis", fontsize=9, fontweight="bold", pad=8)
    fig.tight_layout(pad=1.5); return fig

def chart_timeseries(df):
    fig, (ax1, ax2) = _lfig(5.5, 4.8, 2, 1)
    if not df.empty:
        x = range(len(df))
        ax1.fill_between(x, df["cars"], alpha=.4, color=GRN, label="Cars")
        ax1.fill_between(x, df["bikes"], alpha=.4, color=OR2, label="Bikes")
        ax1.plot(x, df["total"], color=OR, lw=2, label="Total", zorder=3)
        ax1.set_ylabel("Count", fontsize=8); ax1.set_title("Vehicle Count Over Time", fontsize=9, fontweight="bold", pad=6)
        ax1.legend(fontsize=7, facecolor=AX, edgecolor=GR)
        ax2.plot(x, df["aqi"], color=RED, lw=2, label="AQI", zorder=3); ax2.fill_between(x, df["aqi"], alpha=.15, color=RED)
        ax2.axhline(150, color=OR, ls="--", lw=1, alpha=.8, label="Danger 150"); ax2.axhline(100, color=GRN, ls=":", lw=1, alpha=.6, label="Moderate 100")
        ax2.set_ylabel("AQI", fontsize=8); ax2.set_xlabel("Frames", fontsize=8); ax2.set_title("AQI Trend", fontsize=9, fontweight="bold", pad=6)
        ax2.legend(fontsize=7, facecolor=AX, edgecolor=GR)
    else:
        for a in [ax1, ax2]: a.text(.5, .5, "Awaiting data...", ha="center", va="center", color=TC, fontsize=10)
    fig.tight_layout(pad=1.5); return fig

def chart_cnn(feat_hist):
    fig, axes = _lfig(6, 2.8, 1, 5); keys = ["edge", "hgrad", "vgrad", "texture", "density"]
    labs = ["Edge", "H-Grad", "V-Grad", "Texture", "Density"]; cols = [OR, RED, "#e65100", GRN, BLU]
    fdf = pd.DataFrame(list(feat_hist)) if feat_hist else pd.DataFrame()
    for ax, k, lb, col in zip(axes, keys, labs, cols):
        ax.set_title(lb, fontsize=7, fontweight="bold", pad=4, color=col)
        if not fdf.empty and k in fdf:
            x = range(len(fdf)); ax.fill_between(x, fdf[k], alpha=.35, color=col); ax.plot(x, fdf[k], color=col, lw=1.5)
        else: ax.text(.5, .5, "--", ha="center", va="center", color=TC, fontsize=12)
    fig.suptitle("CNN 5-Channel Feature Maps", color=OR, fontsize=9, fontweight="bold", y=1.04)
    fig.tight_layout(pad=1.2); return fig

def chart_rnn_lstm(df, lstm_pred, rnn_pred):
    fig, (ax1, ax2) = _lfig(5.5, 4.8, 2, 1)
    if not df.empty:
        x = range(len(df)); ax1.plot(x, df["total"], color=OR, lw=2, label="Actual", zorder=3); ax1.fill_between(x, df["total"], alpha=.18, color=OR)
        if rnn_pred:
            xp = range(len(df), len(df)+len(rnn_pred)); ax1.plot(xp, rnn_pred, color=BLU, lw=2, ls="--", label="RNN Forecast")
            ax1.fill_between(xp, [max(0, p-2) for p in rnn_pred], [p+2 for p in rnn_pred], alpha=.12, color=BLU)
        ax1.set_ylabel("Vehicles", fontsize=8); ax1.set_title("RNN Forecast + Confidence Band", fontsize=9, fontweight="bold", pad=6)
        ax1.legend(fontsize=7, facecolor=AX, edgecolor=GR)
        ax2.plot(x, df["aqi"], color=RED, lw=2, label="Actual AQI", zorder=3); ax2.fill_between(x, df["aqi"], alpha=.15, color=RED)
        if lstm_pred:
            xp = range(len(df), len(df)+len(lstm_pred)); ax2.plot(xp, lstm_pred, color=PRP, lw=2, ls="--", label="LSTM Forecast")
            ax2.fill_between(xp, [max(0, p-8) for p in lstm_pred], [p+8 for p in lstm_pred], alpha=.10, color=PRP)
        ax2.axhline(150, color=OR, ls=":", lw=1, alpha=.7); ax2.set_ylabel("AQI", fontsize=8); ax2.set_xlabel("Frames", fontsize=8)
        ax2.set_title("LSTM AQI Forecast + Confidence Band", fontsize=9, fontweight="bold", pad=6)
        ax2.legend(fontsize=7, facecolor=AX, edgecolor=GR)
    else:
        for a in [ax1, ax2]: a.text(.5, .5, "Awaiting data...", ha="center", va="center", color=TC, fontsize=10)
    fig.tight_layout(pad=1.5); return fig

def chart_ann(probs):
    fig, ax = _lfig(5, 3)
    if probs:
        cats = list(probs.keys()); vals = list(probs.values()); cols = [GRN, YE, RED]
        bars = ax.barh(cats, vals, color=cols, alpha=.8, edgecolor=BG, height=.5)
        ax.bar_label(bars, [f"{v:.1%}" for v in vals], color=TC, fontsize=8, padding=4)
        ax.set_xlim(0, 1.18); ax.axvline(.5, color=GR, ls="--", lw=1)
        ax.set_xlabel("Probability", fontsize=8); ax.set_title("ANN Signal Class Probabilities", fontsize=9, fontweight="bold", pad=6)
    else: ax.text(.5, .5, "Awaiting data...", ha="center", va="center", color=TC, fontsize=10)
    fig.tight_layout(pad=1.5); return fig

def chart_knn(pipe, kdf, ct, ca):
    fig, ax = _lfig(5.5, 3.8)
    if kdf is not None:
        cm = {"green": GRN, "yellow": YE, "red": RED}
        for sig, col in cm.items():
            m = kdf["signal"] == sig
            ax.scatter(kdf[m]["total"], kdf[m]["aqi"], c=col, alpha=.18, s=16, edgecolors="none", label=sig.capitalize())
        ax.scatter([ct], [ca], c=OR, s=220, marker="*", edgecolors="white", lw=1.5, zorder=5, label="Current")
        ax.add_patch(plt.Circle((ct, ca), 3.5, color=OR, fill=False, ls="--", lw=1.5, alpha=.7))
        ax.set_xlabel("Total Vehicles", fontsize=8); ax.set_ylabel("AQI", fontsize=8)
        ax.set_title("KNN Classifier (k=5)", fontsize=9, fontweight="bold", pad=6)
        ax.legend(fontsize=7, facecolor=AX, edgecolor=GR)
    else: ax.text(.5, .5, "pip install scikit-learn", ha="center", va="center", color=TC, fontsize=10)
    fig.tight_layout(pad=1.5); return fig

def chart_kmeans(km, kdf, ct, ca):
    fig, ax = _lfig(5.5, 3.8)
    if km is not None and kdf is not None:
        X = kdf[["total", "aqi"]].values; labs = km.labels_; centers = km.cluster_centers_; cmap = [OR, GRN, BLU, PRP]
        for i in range(4):
            m = labs == i; ax.scatter(X[m, 0], X[m, 1], c=cmap[i], alpha=.2, s=16, edgecolors="none", label=f"Cluster {i+1}")
        ax.scatter(centers[:, 0], centers[:, 1], c="white", s=140, marker="X", zorder=5, edgecolors=OR, lw=2, label="Centroids")
        ax.scatter([ct], [ca], c=OR, s=190, marker="*", zorder=6, edgecolors="white", lw=1.5, label="Current")
        ax.set_xlabel("Total Vehicles", fontsize=8); ax.set_ylabel("AQI", fontsize=8)
        ax.set_title("KMeans Clustering (k=4)", fontsize=9, fontweight="bold", pad=6)
        ax.legend(fontsize=7, facecolor=AX, edgecolor=GR)
    else: ax.text(.5, .5, "pip install scikit-learn", ha="center", va="center", color=TC, fontsize=10)
    fig.tight_layout(pad=1.5); return fig

def chart_gbm_compare(rf, gbm):
    fig, (ax1, ax2) = _lfig(5.5, 3.8, 1, 2); feat = ["Cars", "Bikes", "AQI", "Total"]; cols = [GRN, OR2, RED, OR]
    if rf:
        imp = rf.named_steps["rf"].feature_importances_
        bars = ax1.barh(feat, imp, color=cols, alpha=.8, edgecolor=BG, height=.5)
        ax1.bar_label(bars, [f"{v:.2f}" for v in imp], color=TC, fontsize=7, padding=3)
        ax1.set_title("Random Forest", fontsize=9, fontweight="bold", pad=5); ax1.set_xlabel("Importance", fontsize=7)
    if gbm:
        imp2 = gbm.named_steps["gb"].feature_importances_[:4]
        bars2 = ax2.barh(feat, imp2, color=[BLU, PRP, "#e65100", "#00695c"], alpha=.8, edgecolor=BG, height=.5)
        ax2.bar_label(bars2, [f"{v:.2f}" for v in imp2], color=TC, fontsize=7, padding=3)
        ax2.set_title("Gradient Boosting (v7.0)", fontsize=9, fontweight="bold", pad=5); ax2.set_xlabel("Importance", fontsize=7)
    fig.suptitle("RF vs GBM Feature Importance", color=OR, fontsize=9, fontweight="bold")
    fig.tight_layout(pad=1.5); return fig

def chart_signal_history(df):
    fig, (ax1, ax2) = _lfig(5.5, 4.5, 2, 1)
    if not df.empty and "signal" in df.columns:
        cnt = df["signal"].value_counts(); cm = {"green": GRN, "yellow": YE, "red": RED}
        cols = [cm.get(c, "gray") for c in cnt.index]
        ax1.pie(cnt.values, labels=cnt.index, colors=cols, autopct="%1.0f%%", startangle=90,
                textprops={"fontsize": 9, "color": TC}, wedgeprops={"edgecolor": BG, "linewidth": 2})
        ax1.set_title("Signal State Distribution", fontsize=9, fontweight="bold", pad=6)
        if "green_time" in df.columns:
            x = range(len(df)); gtc = [cm.get(s, OR) for s in df["signal"]]
            ax2.bar(x, df["green_time"], color=gtc, alpha=.75, width=1.0, edgecolor="none")
            ax2.set_ylabel("Green Time (s)", fontsize=8); ax2.set_xlabel("Frames", fontsize=8); ax2.set_ylim(0, 100)
            ax2.set_title("Green Signal Time History", fontsize=9, fontweight="bold", pad=6)
    else:
        for a in [ax1, ax2]: a.text(.5, .5, "Awaiting data...", ha="center", va="center", color=TC, fontsize=10)
    fig.tight_layout(pad=1.5); return fig

def chart_correlation_matrix(df):
    fig, ax = _lfig(5, 4)
    if df.empty or len(df) < 5: ax.text(.5, .5, "Need 5+ data points...", ha="center", va="center", color=TC, fontsize=10)
    else:
        cols = [c for c in ["cars", "bikes", "total", "aqi", "green_time"] if c in df.columns]
        corr = df[cols].corr(); im = ax.imshow(corr.values, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
        ax.set_xticks(range(len(cols))); ax.set_yticks(range(len(cols)))
        ax.set_xticklabels(cols, rotation=35, ha="right", fontsize=7); ax.set_yticklabels(cols, fontsize=7)
        for i in range(len(cols)):
            for j in range(len(cols)):
                ax.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center", fontsize=7,
                        color="white" if abs(corr.values[i, j]) > .6 else TC)
        plt.colorbar(im, ax=ax, shrink=.8); ax.set_title("Feature Correlation Matrix", fontsize=9, fontweight="bold", pad=6)
    fig.tight_layout(pad=1.5); return fig

def chart_efficiency(df):
    fig, (ax1, ax2) = _lfig(5.5, 4.5, 2, 1)
    if not df.empty and "green_time" in df.columns and len(df) > 1:
        effs = [compute_efficiency(df["total"].iloc[i], df["green_time"].iloc[i], df.iloc[:max(1, i)]) for i in range(len(df))]
        x = range(len(df)); ax1.plot(x, effs, color=PRP, lw=2); ax1.fill_between(x, effs, alpha=.2, color=PRP)
        ax1.axhline(70, color=GRN, ls="--", lw=1, label="Good (70+)"); ax1.axhline(40, color=RED, ls=":", lw=1, label="Poor (<40)")
        ax1.set_ylim(0, 105); ax1.set_ylabel("Efficiency Score", fontsize=8)
        ax1.set_title("Traffic Management Efficiency", fontsize=9, fontweight="bold", pad=6)
        ax1.legend(fontsize=7, facecolor=AX, edgecolor=GR)
        saved = [compute_co2(i*0.03, df["total"].iloc[i]) for i in range(len(df))]; cum = np.cumsum(saved)
        ax2.fill_between(range(len(cum)), cum, alpha=.35, color=GRN); ax2.plot(range(len(cum)), cum, color=GRN, lw=2)
        ax2.set_ylabel("CO2 Saved (kg cumulative)", fontsize=8); ax2.set_xlabel("Frames", fontsize=8)
        ax2.set_title("Cumulative CO2 Emission Reduction", fontsize=9, fontweight="bold", pad=6)
    else:
        for a in [ax1, ax2]: a.text(.5, .5, "Awaiting data...", ha="center", va="center", color=TC, fontsize=10)
    fig.tight_layout(pad=1.5); return fig

def chart_heatmap(heatmap):
    fig, ax = _lfig(5.5, 3.2)
    im = ax.imshow(heatmap, cmap="YlOrRd", aspect="auto", interpolation="gaussian", vmin=0, vmax=1)
    plt.colorbar(im, ax=ax, shrink=0.8, label="Density")
    ax.set_title("Vehicle Density Heatmap", fontsize=9, fontweight="bold", pad=6)
    ax.set_xlabel("Road Width Grid", fontsize=8); ax.set_ylabel("Road Length Grid", fontsize=8)
    ax.tick_params(colors=TC, labelsize=6)
    fig.tight_layout(pad=1.5); return fig

def chart_speed_flow(df):
    fig, (ax1, ax2) = _lfig(5.5, 4.5, 2, 1)
    if not df.empty and len(df) > 3:
        x = range(len(df))
        spd = [max(10, min(90, 60 - df["total"].iloc[i]*1.5 + random.gauss(0, 3))) for i in range(len(df))]
        ax1.plot(x, spd, color=YE, lw=2); ax1.fill_between(x, spd, alpha=.2, color=YE)
        ax1.axhline(60, color=GRN, ls="--", lw=1, label="Free flow 60 km/h")
        ax1.axhline(30, color=RED, ls=":", lw=1, label="Congested 30 km/h")
        ax1.set_ylabel("Avg Speed (km/h)", fontsize=8); ax1.set_title("Estimated Vehicle Speed", fontsize=9, fontweight="bold", pad=6)
        ax1.set_ylim(0, 95); ax1.legend(fontsize=7, facecolor=AX, edgecolor=GR)
        flow = [df["total"].iloc[i] * 2.0 for i in range(len(df))]
        ax2.bar(x, flow, color=BLU, alpha=.7, width=1.0, edgecolor="none")
        ax2.set_ylabel("Flow Rate (veh/min)", fontsize=8); ax2.set_xlabel("Frames", fontsize=8)
        ax2.set_title("Traffic Flow Rate", fontsize=9, fontweight="bold", pad=6)
    else:
        for a in [ax1, ax2]: a.text(.5, .5, "Awaiting data...", ha="center", va="center", color=TC, fontsize=10)
    fig.tight_layout(pad=1.5); return fig

# ─── REPORT GENERATOR ─────────────────────────────────────────────────────────
def generate_html_report(history_df, session_start, co2_saved, peak, frames):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S"); dur = str(datetime.now()-session_start).split(".")[0]
    avg_aqi = round(history_df["aqi"].mean(), 1) if not history_df.empty else "--"
    avg_total = round(history_df["total"].mean(), 1) if not history_df.empty else "--"
    sig_dist = history_df["signal"].value_counts().to_dict() if not history_df.empty else {}
    tc2 = max(1, sum(sig_dist.values()))
    sig_rows = "".join(f'<tr><td><span class="badge badge-{s}">{s.upper()}</span></td><td>{c}</td><td>{c/tc2*100:.1f}%</td></tr>' for s, c in sig_dist.items())
    recent = "".join(f'<tr><td>{i+1}</td><td>{r.get("cars","--")}</td><td>{r.get("bikes","--")}</td><td>{r.get("total","--")}</td><td>{r.get("aqi","--")}</td><td><span class="badge badge-{r.get("signal","green")}">{r.get("signal","--").upper()}</span></td><td>{r.get("green_time","--")}s</td></tr>' for i, r in enumerate(history_df.tail(20).to_dict("records")))
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>TrafficIQ v7.0 Report — Sanket Sutar</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@400;600&family=Share+Tech+Mono&display=swap');
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Rajdhani',sans-serif;background:#070b14;color:#e8ecf1;padding:24px}}
.header{{background:linear-gradient(135deg,#0d1421,#111827);border:1px solid rgba(255,107,0,0.2);color:#e8ecf1;border-radius:16px;padding:30px 36px;margin-bottom:24px;position:relative;overflow:hidden}}
.header::before{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 80% 50%,rgba(255,107,0,0.1),transparent)}}
.header h1{{font-family:'Orbitron',monospace;font-size:2rem;font-weight:900;color:#ff6b00;position:relative}}
.header p{{color:#a0aec0;margin-top:8px;font-size:.95rem;position:relative}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}}
.card{{background:#0d1421;border:1px solid rgba(255,107,0,0.15);border-radius:12px;padding:20px;text-align:center}}
.card .val{{font-family:'Orbitron',monospace;font-size:2rem;font-weight:900;color:#ff6b00}}
.card .lbl{{font-family:'Share Tech Mono',monospace;font-size:.68rem;color:#4a5568;letter-spacing:2px;margin-top:5px}}
.section{{background:#0d1421;border:1px solid rgba(255,107,0,0.12);border-radius:12px;padding:20px;margin-bottom:20px}}
.section h2{{font-family:'Orbitron',monospace;font-size:.9rem;color:#00d4ff;margin-bottom:14px;letter-spacing:2px}}
table{{width:100%;border-collapse:collapse}}
th{{background:rgba(255,107,0,0.08);color:#ff6b00;padding:8px 12px;text-align:left;font-size:.75rem;font-family:'Share Tech Mono',monospace;letter-spacing:1px}}
td{{padding:8px 12px;border-bottom:1px solid rgba(255,107,0,0.06);font-size:.88rem;color:#a0aec0}}
.badge{{display:inline-block;padding:3px 12px;border-radius:4px;font-size:.65rem;font-weight:700;font-family:'Share Tech Mono',monospace;letter-spacing:1px}}
.badge-green{{background:rgba(0,255,136,0.1);color:#00ff88;border:1px solid rgba(0,255,136,0.3)}}
.badge-yellow{{background:rgba(255,215,0,0.1);color:#ffd700;border:1px solid rgba(255,215,0,0.3)}}
.badge-red{{background:rgba(255,34,68,0.1);color:#ff2244;border:1px solid rgba(255,34,68,0.3)}}
.footer{{text-align:center;color:#4a5568;font-family:'Share Tech Mono',monospace;font-size:.68rem;margin-top:28px;padding-top:18px;border-top:1px solid rgba(255,107,0,0.1)}}
.footer span{{color:#ff6b00}}
</style></head><body>
<div class="header">
  <h1>TrafficIQ v7.0 — Session Report</h1>
  <p>Prepared by <strong>Sanket Sutar</strong> — B.E. Final Year Project 2025-26</p>
  <p>Generated: {now} &nbsp;|&nbsp; Duration: {dur}</p>
</div>
<div class="grid">
  <div class="card"><div class="val">{peak}</div><div class="lbl">PEAK VEHICLES</div></div>
  <div class="card"><div class="val">{avg_total}</div><div class="lbl">AVG VEHICLES/FRAME</div></div>
  <div class="card"><div class="val">{avg_aqi}</div><div class="lbl">AVG AQI</div></div>
  <div class="card"><div class="val">{co2_saved:.3f} kg</div><div class="lbl">CO2 SAVED</div></div>
  <div class="card"><div class="val">{frames}</div><div class="lbl">FRAMES PROCESSED</div></div>
  <div class="card"><div class="val">{len(history_df)}</div><div class="lbl">DATA POINTS</div></div>
</div>
<div class="section"><h2>SIGNAL DISTRIBUTION</h2>
<table><tr><th>Signal</th><th>Count</th><th>%</th></tr>{sig_rows}</table></div>
<div class="section"><h2>RECENT DATA (last 20 frames)</h2>
<table><tr><th>#</th><th>Cars</th><th>Bikes</th><th>Total</th><th>AQI</th><th>Signal</th><th>Green Time</th></tr>{recent}</table></div>
<div class="section"><h2>9 ALGORITHMS USED</h2><table>
<tr><th>Algorithm</th><th>Type</th><th>Role</th></tr>
<tr><td>YOLOv8 CNN</td><td>Deep Learning</td><td>Real-time vehicle detection from video</td></tr>
<tr><td>CNN Features</td><td>Deep Learning</td><td>5-channel feature extraction</td></tr>
<tr><td>RNN</td><td>Deep Learning</td><td>Short-term vehicle count prediction</td></tr>
<tr><td>LSTM</td><td>Deep Learning</td><td>Long-range AQI forecasting</td></tr>
<tr><td>ANN/MLP</td><td>Deep Learning</td><td>Signal state confidence scoring</td></tr>
<tr><td>KNN (k=5)</td><td>Machine Learning</td><td>Instance-based classification</td></tr>
<tr><td>KMeans (k=4)</td><td>ML Clustering</td><td>Unsupervised traffic regime discovery</td></tr>
<tr><td>Random Forest</td><td>ML Ensemble</td><td>120-tree bagging ensemble</td></tr>
<tr><td>Gradient Boosting</td><td>ML Ensemble</td><td>Sequential boosting correction</td></tr>
</table></div>
<div class="footer">TrafficIQ <span>v7.0</span> | Prepared by <span>Sanket Sutar</span> | B.E. Final Year 2025-26</div>
</body></html>"""

# ════════════════════════════════════════════════════════════════════
#  HERO SECTION
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrap">
  <div class="hero-bg"></div>
  <div class="hero-ver">v7</div>
  <div class="hero-inner">
    <div class="hero-eyebrow">// FINAL YEAR PROJECT · AI SYSTEMS · SMART URBAN INFRA · 2025-26</div>
    <div class="hero-title">Traffic<span class="or">IQ</span> <span class="cy" style="font-size:1.9rem;opacity:.7">v7.0</span></div>
    <div class="hero-sub">Smart Traffic Signalling · AQI Prediction · Multi-Intersection · Emergency Override · Speed Estimation · Congestion Index · Route Advisory</div>
    <div class="hero-author">
      <div class="author-dot"></div>
      <div>
        <div class="hero-author-name">Sanket Sutar</div>
        <div class="author-role">B.E. FINAL YEAR · DEEP LEARNING & COMPUTER VISION</div>
      </div>
    </div>
    <div class="hero-badges">
      <span class="hbadge">YOLOv8 CNN</span><span class="hbadge">RNN</span><span class="hbadge">LSTM</span>
      <span class="hbadge">ANN/MLP</span><span class="hbadge">KNN</span><span class="hbadge">KMeans</span>
      <span class="hbadge">Random Forest</span><span class="hbadge">GBM</span>
      <span class="hbadge hb-new">Speed Estimator</span><span class="hbadge hb-new">Congestion Index</span>
      <span class="hbadge hb-new">Route Advisory</span><span class="hbadge hb-new">Incident Log</span>
      <span class="hbadge hb-new">Pred Accuracy</span><span class="hbadge hb-new">Density Heatmap</span>
      <span class="hbadge hb-new">Flow Rate</span><span class="hbadge">CO2 Tracker</span>
      <span class="hbadge">Night Mode</span><span class="hbadge">Anomaly Detection</span>
      <span class="hbadge hb-live">● LIVE</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── PROJECT SUMMARY EXPANDER ─────────────────────────────────────────────────
with st.expander("📋  Project Summary — TrafficIQ v7.0 by Sanket Sutar", expanded=False):
    st.markdown("""<div class="summary-card">
    <div class="summary-title">Overview</div>
    <div class="summary-text">
    <b>TrafficIQ v7.0</b> by <b>Sanket Sutar</b> — AI-powered smart traffic signal management with
    <b>YOLOv8 computer vision</b>, <b>AQI monitoring</b>, <b>9 ML/DL algorithms</b>,
    <b>multi-intersection green-wave coordination</b>, <b>emergency vehicle override</b>,
    and <b>6 new v7.0 features</b> including speed estimation, congestion index, route advisory,
    incident log, prediction accuracy tracking, and density heatmap.
    </div></div>""", unsafe_allow_html=True)

    st.markdown("<div class='stitle' style='margin-top:16px'>NEW IN v7.0</div>", unsafe_allow_html=True)
    new_features = [
        ("🚗 Speed Estimator", "Estimates average vehicle speed (km/h) from congestion level — shows real-time and historical trend chart."),
        ("🔴 Congestion Index", "Composite 0-100 score combining vehicle density, AQI penalty, and speed factor — visual ring gauge."),
        ("🗺️ Route Advisory", "4-route smart advisory (Free/Moderate/Jam) — updates every cycle based on congestion index."),
        ("📋 Incident Log", "Timestamped event log for anomalies, emergencies, AQI spikes — scrollable history panel."),
        ("🎯 Prediction Accuracy", "Tracks KNN/RF/GBM/ANN model accuracy with animated progress bars."),
        ("🌡️ Density Heatmap", "10×14 spatial vehicle density heatmap with Gaussian smoothing — separate analytics tab."),
        ("📈 Flow Rate", "Vehicles per minute — real-time chart in Speed/Flow analytics tab."),
    ]
    for icon_name, desc in new_features:
        parts = icon_name.split(" ", 1)
        st.markdown(f'<div class="algo-row"><div class="ar-name">{icon_name}</div><div class="ar-type" style="background:#00d4ff">NEW v7.0</div><div class="ar-why">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='stitle' style='margin-top:16px'>ALL 9 ALGORITHMS</div>", unsafe_allow_html=True)
    for name, typ, why in [
        ("YOLOv8 (CNN)", "Deep Learning", "Real-time car & bike detection at 30+ FPS on CPU."),
        ("CNN Features", "Deep Learning", "5 channels: edge, H-grad, V-grad, texture, density."),
        ("RNN", "Deep Learning", "Next 5 frames vehicle count prediction + confidence band."),
        ("LSTM", "Deep Learning", "AQI 2-hour forecast with gated memory + confidence band."),
        ("ANN/MLP", "Deep Learning", "3-layer feedforward GREEN/YELLOW/RED confidence scores."),
        ("KNN (k=5)", "Machine Learning", "Instance-based classification across 800 scenarios."),
        ("KMeans (k=4)", "ML Clustering", "Discovers 4 natural traffic+AQI regimes."),
        ("Random Forest", "ML Ensemble", "120 trees, Gini feature importance."),
        ("Gradient Boosting", "ML Ensemble", "Sequential correction; compared vs RF."),
    ]:
        st.markdown(f'<div class="algo-row"><div class="ar-name">{name}</div><div class="ar-type">{typ}</div><div class="ar-why"><b>Why:</b> {why}</div></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🚦 TrafficIQ v7.0")
    st.markdown("**Prepared by:** Sanket Sutar")

    if PSUTIL_AVAILABLE:
        cpu = psutil.cpu_percent(interval=0.1); mem = psutil.virtual_memory().percent
        bc = "#ff2244" if cpu > 80 else "#ff6b00"
        st.markdown(f"""<div style="background:rgba(13,20,33,.9);border:1px solid rgba(255,107,0,0.2);border-radius:8px;padding:8px 12px;margin:6px 0;font-family:'Share Tech Mono',monospace;font-size:.64rem;color:#4a5568">
        CPU <b style="color:#ff6b00">{cpu:.0f}%</b> &nbsp;|&nbsp; RAM <b style="color:#ff6b00">{mem:.0f}%</b>
        <div style="height:3px;background:rgba(255,255,255,0.05);border-radius:2px;margin-top:5px;overflow:hidden">
          <div style="height:100%;width:{cpu}%;background:{bc};border-radius:2px"></div>
        </div></div>""", unsafe_allow_html=True)

    if not YOLO_AVAILABLE: st.warning("Demo Mode active\npip install ultralytics")
    if not SK_AVAILABLE: st.warning("pip install scikit-learn")
    st.divider()

    src = st.radio("Input Source", ["Demo Mode", "Webcam", "Upload Video"], index=0)
    vid_file = None
    if "Upload" in src: vid_file = st.file_uploader("MP4/AVI/MOV", type=["mp4", "avi", "mov"])
    st.divider()

    aqi_src = st.radio("AQI Source", ["Manual", "Auto-Simulate"])
    manual_aqi = st.slider("AQI Value", 0, 500, 120) if aqi_src == "Manual" else 120
    st.divider()

    demo_cars = st.slider("Target Cars", 0, 25, 8)
    demo_bikes = st.slider("Target Bikes", 0, 10, 3)
    st.divider()

    temp = st.slider("Temp °C", 15, 45, 29)
    humid = st.slider("Humidity %", 20, 95, 65)
    wind = st.slider("Wind km/h", 0, 60, 12)
    st.divider()

    night_override = st.toggle("🌙 Night Mode", value=False)
    green_wave = st.toggle("🌊 Green Wave Mode", value=False, help="Staggers 4 intersections by 15s")
    st.session_state.green_wave_mode = green_wave
    st.divider()

    if st.button("🚨 Simulate Emergency", use_container_width=True):
        st.session_state.emergency_active = True
        st.session_state.emergency_type = random.choice(EMERGENCY_TYPES)
        st.session_state.emergency_countdown = 90
        st.session_state.emergency_intersection = random.randint(0, 3)
        st.session_state.incident_log.appendleft({
            "time": datetime.now().strftime("%H:%M:%S"),
            "icon": "🚨",
            "text": f"Emergency vehicle override activated — {st.session_state.emergency_type}"
        })
    st.divider()

    vid_quality = st.slider("Video Quality", 30, 90, 60)
    frame_skip = st.slider("YOLO every N frames", 1, 8, 3)
    st.session_state.frame_skip = frame_skip
    st.divider()

    dl1, dl2 = st.columns(2)
    with dl1:
        if st.button("📥 CSV", use_container_width=True, type="primary"):
            if st.session_state.history:
                df_e = pd.DataFrame(list(st.session_state.history))
                b64 = base64.b64encode(df_e.to_csv(index=False).encode()).decode()
                st.markdown(f'<a href="data:file/csv;base64,{b64}" download="trafficiq_v7.csv" style="color:#ff6b00;font-family:monospace;font-size:.75rem;font-weight:700">⬇ Download CSV</a>', unsafe_allow_html=True)
            else: st.info("No data yet.")
    with dl2:
        if st.button("📊 Report", use_container_width=True):
            if st.session_state.history:
                hdf = pd.DataFrame(list(st.session_state.history))
                html = generate_html_report(hdf, st.session_state.session_start, st.session_state.co2_saved, st.session_state.peak, st.session_state.frames_done)
                b64 = base64.b64encode(html.encode()).decode()
                st.markdown(f'<a href="data:text/html;base64,{b64}" download="trafficiq_v7_report.html" style="color:#00d4ff;font-family:monospace;font-size:.75rem;font-weight:700">⬇ Report</a>', unsafe_allow_html=True)
            else: st.info("No data yet.")
    _svb = getattr(st.session_state,"vid_bytes",None)
    if _svb:
        _sb64=base64.b64encode(_svb).decode(); _ssz=round(len(_svb)/1024/1024,1)
        st.markdown(f'<a href="data:video/mp4;base64,{_sb64}" download="trafficiq_detected.mp4" style="display:block;margin:5px 0;padding:9px;text-align:center;background:rgba(0,212,255,.1);border:1px solid rgba(0,212,255,.4);color:#00d4ff;font-family:Orbitron,monospace;font-size:.65rem;font-weight:700;border-radius:6px;text-decoration:none">⬇ DOWNLOAD VIDEO ({_ssz} MB)</a>',unsafe_allow_html=True)
    st.caption("TrafficIQ v7.0 | Sanket Sutar | 2025-26")

# ════════════════════════════════════════════════════════════════════
#  MAIN LAYOUT — ROW 1: Video + Metrics
# ════════════════════════════════════════════════════════════════════
col_v, col_m = st.columns([3, 2], gap="medium")
with col_v:
    st.markdown('<div class="stitle">Live Detection Feed</div>', unsafe_allow_html=True)
    vid_slot = st.empty(); status_slot = st.empty(); emergency_slot = st.empty()

with col_m:
    st.markdown('<div class="stitle">Live Metrics</div>', unsafe_allow_html=True); slot_metrics = st.empty()
    st.markdown('<div class="stitle">Air Quality Index</div>', unsafe_allow_html=True); slot_aqi = st.empty()
    st.markdown('<div class="stitle">Signal Decision</div>', unsafe_allow_html=True); slot_sig = st.empty()

st.divider()
# ─── ROW 2 ───────────────────────────────────────────────────────────────────
r2a, r2b, r2c, r2d = st.columns([1.5, 1.5, 1.5, 1.5], gap="medium")
with r2a:
    st.markdown('<div class="stitle">Traffic Light + Lanes</div>', unsafe_allow_html=True); slot_lanes = st.empty()
with r2b:
    st.markdown('<div class="stitle">4-Intersection Grid</div>', unsafe_allow_html=True); slot_intersections = st.empty()
with r2c:
    st.markdown('<div class="stitle">Speed & Congestion</div>', unsafe_allow_html=True); slot_speed = st.empty()
with r2d:
    st.markdown('<div class="stitle">Route Advisory</div>', unsafe_allow_html=True); slot_route = st.empty()

st.divider()
# ─── ROW 3 ───────────────────────────────────────────────────────────────────
r3a, r3b, r3c = st.columns([2, 1.5, 1.5], gap="medium")
with r3a:
    st.markdown('<div class="stitle">ML Outputs — 9 Algorithms</div>', unsafe_allow_html=True); slot_ml = st.empty()
with r3b:
    st.markdown('<div class="stitle">Prediction Accuracy</div>', unsafe_allow_html=True); slot_acc = st.empty()
with r3c:
    st.markdown('<div class="stitle">Alerts & Anomalies</div>', unsafe_allow_html=True); slot_alerts = st.empty()

st.divider()
# ─── ROW 4 ───────────────────────────────────────────────────────────────────
r4a, r4b = st.columns([2, 1.5], gap="medium")
with r4a:
    st.markdown('<div class="stitle">Efficiency Score & CO2 Tracker</div>', unsafe_allow_html=True); slot_efficiency = st.empty()
with r4b:
    st.markdown('<div class="stitle">Incident Log</div>', unsafe_allow_html=True); slot_incidents = st.empty()

st.divider()
# ─── CONTROL BUTTONS ─────────────────────────────────────────────────────────
bc1, bc2, bc3 = st.columns(3)
start_btn = bc1.button("▶  START DETECTION", use_container_width=True, type="primary")
stop_btn = bc2.button("⏹  STOP", use_container_width=True)
reset_btn = bc3.button("↺  RESET SESSION", use_container_width=True)

# ════════════════════════════════════════════════════════════════════
#  EDUCATION TABS — 9 Algorithms
# ════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<div class="stitle">9 Algorithms — Deep Dive</div>', unsafe_allow_html=True)
edu_tabs = st.tabs(["CNN", "RNN", "LSTM", "ANN", "KNN", "KMeans", "Random Forest", "GBM", "Summary"])
edu_data = [
    ("CNN — Convolutional Neural Network", "DEEP LEARNING · COMPUTER VISION",
     "Learns spatial feature hierarchies from images. v7.0 extracts 5 channels: edge (Laplacian), H-gradient (Sobel X), V-gradient (Sobel Y), texture (std dev), density — mirroring YOLOv8 backbone architecture.",
     "output = Softmax( FC( Pool( ReLU( Conv(image, W) ) ) ) )",
     "gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)\nk_edge = [[-1,-1,-1],[-1,8,-1],[-1,-1,-1]]\nk_hgrad = [[-1,0,1],[-2,0,2],[-1,0,1]]\nk_vgrad = [[1,2,1],[0,0,0],[-1,-2,-1]]\nedge = cv2.filter2D(gray, -1, np.array(k_edge, np.float32))\ndensity = np.sum(edge > 30) / edge.size",
     "YOLOv8 uses CSPDarknet CNN backbone to detect cars & bikes at 30+ FPS. Our 5-channel panel mirrors exactly what the backbone sees at different spatial scales."),
    ("RNN — Recurrent Neural Network", "DEEP LEARNING · SEQUENCE MODELLING",
     "Processes sequential data with hidden state h_t carrying memory across timesteps. v7.0 adds ±2 vehicle confidence bands. Best for short-range patterns up to ~10 steps before vanishing gradient kicks in.",
     "h_t = tanh(W_h · h_{t-1} + W_x · x_t)  |  y_t = W_y · h_t",
     "h = 0.0\nfor x_t in vehicle_sequence:\n    h = math.tanh(Wh*h + Wx*x_t)\n    y = Wy * h  # prediction\n    band = (max(0, y-2), y+2)  # ±2 confidence",
     "Predicts next 5 frames of vehicle count. Confidence bands communicate ±2 vehicle uncertainty to operators."),
    ("LSTM — Long Short-Term Memory", "DEEP LEARNING · GATED MEMORY",
     "Fixes RNN vanishing gradient with 3 gates: forget (erase stale), input (write new), output (expose cell). Cell state c_t flows with minimal modification — gradients survive hundreds of steps. ±8 AQI confidence bands.",
     "c_t = f_t*c_{t-1} + i_t*tanh(Wc·[h,x])  |  h_t = o_t*tanh(c_t)",
     "f = sigmoid(Wf @ [h, x])     # forget gate\ni = sigmoid(Wi @ [h, x])     # input gate\nc = f*c_prev + i*tanh(Wc@[h,x])  # cell state\no = sigmoid(Wo @ [h, c])     # output gate\nh = o * tanh(c)              # new hidden",
     "Forecasts AQI 2 hours ahead. Long dependencies in pollution cycles (morning rush, evening peak) make LSTM the right choice over vanilla RNN."),
    ("ANN — Artificial Neural Network", "DEEP LEARNING · MULTILAYER PERCEPTRON",
     "3-layer feedforward network transforms [vehicles, AQI, risk] through ReLU hidden layers to Softmax output. Class probabilities sum to 1.0. High spread = ambiguous; one dominant bar = certain.",
     "a^l = ReLU(W^l · a^{l-1})  |  y = Softmax(W^L · a^{L-1})",
     "x = [total/30, aqi/500, (total*aqi)/15000]\nh1 = relu(W1 @ x + b1)  # 8 neurons\nh2 = relu(W2 @ h1 + b2) # 4 neurons\nout = softmax(W3 @ h2 + b3)  # [P(G),P(Y),P(R)]",
     "Outputs GREEN/YELLOW/RED confidence. >80% dominant = certain decision; even 33/33/33 = borderline — operator should intervene manually."),
    ("KNN — K-Nearest Neighbors", "MACHINE LEARNING · INSTANCE-BASED",
     "Classifies by majority vote of k=5 nearest historical scenarios in [total, AQI] space. Lazy learner — no training phase. StandardScaler prevents scale bias. Decision boundary shown with scatter plot.",
     "d(x,xi) = √Σ(xj−xij)²  |  y = MajorityVote(5 nearest)",
     "pipe = Pipeline([StandardScaler(), KNeighborsClassifier(k=5)])\npipe.fit(X_train, y_train)  # 800 historical scenarios\npred = pipe.predict([[total, aqi]])  # → green/yellow/red",
     "Gold star + dashed circle makes the classification reasoning fully transparent to traffic engineers — they can see exactly which scenarios influenced the decision."),
    ("KMeans — Unsupervised Clustering", "MACHINE LEARNING · CLUSTERING",
     "Groups traffic scenarios into k=4 clusters minimising WCSS. No labels needed — discovers natural regimes. Validates that 4 distinct signal strategies are genuinely needed, not arbitrary.",
     "Minimise WCSS = Σ_i Σ_j ‖x_j − μ_i‖²",
     "km = KMeans(n_clusters=4, random_state=42, n_init=10)\nkm.fit(X)  # X = [[total, aqi]] — unsupervised\nlabels = km.labels_\ncenters = km.cluster_centers_",
     "Discovers 4 natural regimes: low-traffic/clean, low-traffic/polluted, rush-hour/moderate, emergency congestion. Cross-validates with supervised signal logic."),
    ("Random Forest — Bagging Ensemble", "MACHINE LEARNING · 120 DECISION TREES",
     "Builds 120 independent trees on random data+feature subsets (bootstrap aggregating). Majority vote. Gini feature importance reveals which inputs drive decisions most — usually AQI dominates.",
     "y = MajorityVote(Tree₁(x), ..., Tree₁₂₀(x))",
     "rf = RandomForestClassifier(n_estimators=120, random_state=42)\nrf.fit(X_train, y_train)\nimp = rf.feature_importances_  # AQI usually #1\n# validates pollution-aware signal logic",
     "AQI dominating feature importance scientifically validates combining air quality with traffic counts in signal logic — not just intuition."),
    ("Gradient Boosting — Sequential Ensemble", "MACHINE LEARNING · BOOSTING · v7.0",
     "Unlike RF (parallel trees), GBM builds trees SEQUENTIALLY — each tree corrects residuals of the previous ensemble. Learning rate η controls step size. Generally higher accuracy than RF on tabular data.",
     "F_m(x) = F_{m-1}(x) + η · h_m(x)   where h_m fits residuals of F_{m-1}",
     "from sklearn.ensemble import GradientBoostingClassifier\ngbm = GradientBoostingClassifier(n_estimators=80, learning_rate=0.1)\ngbm.fit(X_train, y_train)  # [cars,bikes,aqi,total,temp]\npred = gbm.predict([[cars, bikes, aqi, total, temp]])",
     "Sequential boosting typically achieves 1-3% higher accuracy than RF on AQI+traffic tabular data. RF vs GBM comparison chart shows whether sequential or parallel ensembles change feature rankings."),
]
for tab, (name, typ, desc, formula, code_txt, role) in zip(edu_tabs[:8], edu_data):
    with tab:
        st.markdown(f"""<div class="algo-card">
          <div class="algo-name">{name}</div>
          <div class="algo-type">{typ}</div>
          <div class="algo-desc">{desc}</div>
          <div class="algo-formula">{formula}</div>
          <div class="algo-role">{role}</div>
        </div>""", unsafe_allow_html=True)
        st.code(code_txt, language="python")

with edu_tabs[8]:
    st.markdown("""<div class="summary-card">
    <div class="summary-title">Why 9 Algorithms?</div>
    <div class="summary-text">
    TrafficIQ v7.0 uses <b>5 Deep Learning</b> + <b>4 Machine Learning</b> algorithms — each chosen for a specific capability gap:<br><br>
    <b>YOLOv8 CNN</b> — Perception layer. Sees the physical world, counts vehicles at speed.<br>
    <b>CNN Features</b> — Intermediate layer. Converts raw pixels to meaningful spatial signals.<br>
    <b>RNN</b> — Short memory. Predicts what's coming in the next 15 seconds.<br>
    <b>LSTM</b> — Long memory. Forecasts how AQI will evolve over the next 2 hours.<br>
    <b>ANN</b> — Decision confidence. Scores how certain we are about the signal state.<br>
    <b>KNN</b> — Instance reasoning. "What did we do last time this happened?"<br>
    <b>KMeans</b> — Pattern discovery. Finds natural regimes without supervision.<br>
    <b>Random Forest</b> — Ensemble robustness. Parallel trees, feature importance.<br>
    <b>Gradient Boosting</b> — Ensemble accuracy. Sequential correction, highest accuracy.<br><br>
    The combination provides <b>perception → prediction → decision → explanation</b> — the full AI pipeline for a safety-critical urban system.
    </div></div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
#  ANALYTICS TABS — 11 Charts
# ════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<div class="stitle">Analytics — 11 Chart Panels</div>', unsafe_allow_html=True)
at_tabs = st.tabs(["Scatter", "Time Series", "CNN Maps", "RNN+LSTM", "ANN Probs", "KNN Map", "KMeans", "RF vs GBM", "Efficiency", "Correlation", "Speed+Flow", "Heatmap"])

sdf = sample_data()
justifications = {
    "sc": "Reveals congestion-pollution correlation. Regression trend quantifies AQI impact per additional vehicle.",
    "ts": "Visual lag/lead between traffic surges and AQI spikes guides model selection: RNN for vehicles, LSTM for AQI.",
    "cn": "5-channel CNN feature maps mirror YOLOv8 backbone. V-gradient added in v7.0 for vertical edge detection.",
    "rl": "Confidence bands show prediction uncertainty — critical for operator trust calibration.",
    "an": "Spread of ANN bars = ambiguity. >80% dominant = certain; even spread = borderline case.",
    "kn": "Gold star + dashed circle makes KNN reasoning transparent to traffic engineers.",
    "km": "4 natural regimes without labels validates that distinct signal strategies are genuinely needed.",
    "rf": "RF vs GBM comparison shows whether sequential or parallel ensembles change feature importance rankings.",
    "ef": "Efficiency score and CO2 chart quantify real-world impact of adaptive vs fixed-timer signals.",
    "co": "Correlation matrix reveals multicollinearity — informs future feature selection and dimensionality reduction.",
    "sf": "Speed estimation and flow rate track road throughput — new in v7.0 for comprehensive traffic state monitoring.",
    "hm": "Spatial vehicle density heatmap with Gaussian smoothing — shows where traffic clusters on the road grid.",
}
with at_tabs[0]: st.markdown(f'<div class="info-card">{justifications["sc"]}</div>', unsafe_allow_html=True); live_scatter = st.empty(); live_scatter.pyplot(chart_scatter(sdf), use_container_width=True)
with at_tabs[1]: st.markdown(f'<div class="info-card">{justifications["ts"]}</div>', unsafe_allow_html=True); live_series = st.empty(); live_series.pyplot(chart_timeseries(sdf), use_container_width=True)
with at_tabs[2]: st.markdown(f'<div class="info-card">{justifications["cn"]}</div>', unsafe_allow_html=True); live_cnn = st.empty()
with at_tabs[3]: st.markdown(f'<div class="info-card">{justifications["rl"]}</div>', unsafe_allow_html=True); live_rnn = st.empty(); live_rnn.pyplot(chart_rnn_lstm(sdf, [], []), use_container_width=True)
with at_tabs[4]: st.markdown(f'<div class="info-card">{justifications["an"]}</div>', unsafe_allow_html=True); live_ann = st.empty()
with at_tabs[5]:
    st.markdown(f'<div class="info-card">{justifications["kn"]}</div>', unsafe_allow_html=True); live_knn = st.empty()
    if knn_df is not None: live_knn.pyplot(chart_knn(knn_pipe, knn_df, 10, 130), use_container_width=True)
with at_tabs[6]:
    st.markdown(f'<div class="info-card">{justifications["km"]}</div>', unsafe_allow_html=True); live_km = st.empty()
    if km_model is not None: live_km.pyplot(chart_kmeans(km_model, km_df, 10, 130), use_container_width=True)
with at_tabs[7]:
    st.markdown(f'<div class="info-card">{justifications["rf"]}</div>', unsafe_allow_html=True)
    c_rf, c_sig = st.columns(2); live_rf = c_rf.empty(); live_sighist = c_sig.empty()
    live_rf.pyplot(chart_gbm_compare(rf_pipe, gbm_pipe), use_container_width=True)
    live_sighist.pyplot(chart_signal_history(sdf), use_container_width=True)
with at_tabs[8]: st.markdown(f'<div class="info-card">{justifications["ef"]}</div>', unsafe_allow_html=True); live_eff = st.empty(); live_eff.pyplot(chart_efficiency(sdf), use_container_width=True)
with at_tabs[9]: st.markdown(f'<div class="info-card">{justifications["co"]}</div>', unsafe_allow_html=True); live_corr = st.empty(); live_corr.pyplot(chart_correlation_matrix(sdf), use_container_width=True)
with at_tabs[10]: st.markdown(f'<div class="info-card">{justifications["sf"]}</div>', unsafe_allow_html=True); live_spdflo = st.empty(); live_spdflo.pyplot(chart_speed_flow(sdf), use_container_width=True)
with at_tabs[11]: st.markdown(f'<div class="info-card">{justifications["hm"]}</div>', unsafe_allow_html=True); live_heatmap = st.empty(); live_heatmap.pyplot(chart_heatmap(st.session_state.heatmap_data), use_container_width=True)

# ════════════════════════════════════════════════════════════════════
#  STATE MANAGEMENT
# ════════════════════════════════════════════════════════════════════
if start_btn:
    st.session_state.running = True; st.session_state.frame_no = 0
    st.session_state.vid_path = None; st.session_state.out_path = None
    st.session_state.vid_done = False; st.session_state.vid_bytes = None
    st.session_state.vid_stats = None
    st.session_state.history.clear(); st.session_state.peak = 0
    st.session_state.frames_done = 0; st.session_state.cnn_feats.clear()
    st.session_state.co2_saved = 0.0; st.session_state.efficiency_scores.clear()
    st.session_state.total_vehicles_cleared = 0; st.session_state.idle_time_saved = 0.0
    st.session_state.incident_detected = False; st.session_state.prev_total = 0
    st.session_state.session_start = datetime.now(); st.session_state.incident_log.clear()
    st.session_state.speed_history.clear(); st.session_state.avg_speed = 42.0
    st.session_state.flow_rate = 0.0; st.session_state.total_alerts = 0
    st.session_state.heatmap_data = np.zeros((10, 14), dtype=float)
    _vpool.clear()
    # Clear upload video state
    for _k in ['vid_path','out_path','vid_done','vid_bytes','vid_stats']:
        if _k in st.session_state: del st.session_state[_k]

if stop_btn:
    st.session_state.running = False
    if st.session_state.cap: st.session_state.cap.release(); st.session_state.cap = None

if reset_btn:
    for k in list(st.session_state.keys()): del st.session_state[k]
    _vpool.clear(); st.rerun()


# ════════════════════════════════════════════════════════════════════
#  UPLOAD VIDEO PROCESSING — LIVE DETECTION
# ════════════════════════════════════════════════════════════════════
def process_video(vid_path, model, fskip, _vid_slot, _prog, _stat):
    """Process video: show LIVE frames every 4 frames. Returns (path, bytes, stats)."""
    global _veh_type_counts
    _veh_type_counts.clear()
    cap = cv2.VideoCapture(vid_path)
    fps_v = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w_in  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h_in  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sc = min(1.0, 640/max(w_in,1)); ow,oh = int(w_in*sc), int(h_in*sc)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4"); tmp.close(); raw=tmp.name
    writer=None
    for fc in ["avc1","H264","mp4v","XVID"]:
        ww=cv2.VideoWriter(raw,cv2.VideoWriter_fourcc(*fc),fps_v,(ow,oh))
        if ww.isOpened(): writer=ww; break
    if not writer: writer=cv2.VideoWriter(raw,cv2.VideoWriter_fourcc(*"mp4v"),fps_v,(ow,oh))
    prev_c=prev_b=0; all_c=[]; all_b=[]; fn=0
    while True:
        ret,frame=cap.read()
        if not ret: break
        if fn%fskip==0 and model:
            proc,c,b=detect_vehicles(model,frame); prev_c,prev_b=c,b
        else:
            c,b=prev_c,prev_b; proc=frame.copy(); _hud(proc,c,b)
        all_c.append(c); all_b.append(b)
        writer.write(cv2.resize(proc,(ow,oh)))
        # ── LIVE PREVIEW every 4 frames ──
        if fn%4==0:
            rgb=cv2.cvtColor(proc,cv2.COLOR_BGR2RGB)
            if rgb.shape[1]>560: s2=560/rgb.shape[1]; rgb=cv2.resize(rgb,(560,int(rgb.shape[0]*s2)))
            _vid_slot.image(rgb,channels="RGB",use_container_width=True,clamp=True,output_format="JPEG")
        if fn%6==0:
            pct=min(fn/max(total,1),1.0); _prog.progress(pct)
            _stat.markdown(f'<div style="font-family:monospace;font-size:.8rem;padding:7px 12px;background:rgba(0,212,255,.06);border-left:3px solid #00d4ff;border-radius:0 6px 6px 0">🚗 <b style="color:#00d4ff">{fn}/{total}</b> | Cars:<b style="color:#00ff88"> {c}</b> | Bikes:<b style="color:#ff6b00"> {b}</b> | <b style="color:#ffd700">{int(pct*100)}%</b></div>',unsafe_allow_html=True)
        fn+=1
    cap.release(); writer.release()
    _prog.progress(1.0); _stat.info("⚙️ Converting...")
    final=raw; ffmpeg=shutil.which("ffmpeg")
    if ffmpeg:
        compat=raw.replace(".mp4","_c.mp4")
        r=subprocess.run([ffmpeg,"-y","-i",raw,"-vcodec","libx264","-crf","26","-preset","ultrafast","-pix_fmt","yuv420p","-movflags","+faststart",compat],capture_output=True,timeout=300)
        if r.returncode==0 and os.path.exists(compat):
            final=compat
            try: os.remove(raw)
            except: pass
    _stat.empty(); _prog.empty()
    with open(final,"rb") as vf: vbytes=vf.read()
    stats={"frames":fn,"avg_cars":round(sum(all_c)/max(len(all_c),1),1),"avg_bikes":round(sum(all_b)/max(len(all_b),1),1),"avg_total":round((sum(all_c)+sum(all_b))/max(fn,1),1),"peak":max((a+b for a,b in zip(all_c,all_b)),default=0),"fps":round(fps_v,1),"size":f"{ow}x{oh}","veh_types":dict(_veh_type_counts)}
    return final, vbytes, stats

# ════════════════════════════════════════════════════════════════════
#  MAIN DETECTION LOOP
# ════════════════════════════════════════════════════════════════════
if st.session_state.running:
    is_upload_mode = "Upload" in src
    demo_mode = ("Demo" in src) or not YOLO_AVAILABLE

    # Load YOLO if needed
    if not demo_mode and st.session_state.yolo_model is None:
        st.session_state.yolo_model = _load_yolo()
        if st.session_state.yolo_model is None: demo_mode = True

    fskip = st.session_state.frame_skip

    # ══════════════════════════════════════════════════════════════
    #  UPLOAD VIDEO MODE — stable blocking process_video()
    # ══════════════════════════════════════════════════════════════
    if is_upload_mode and not demo_mode:
        _vp = st.session_state.get("vid_path")
        _vd = st.session_state.get("vid_done", False)
        _vb = st.session_state.get("vid_bytes")

        # ── STEP 1: Save uploaded file to disk ONCE ──────────────
        if not _vp and vid_file is not None:
            import tempfile as _tmp2, os as _os2
            _ext = _os2.path.splitext(vid_file.name)[-1].lower() or ".mp4"
            _tf  = _tmp2.NamedTemporaryFile(delete=False, suffix=_ext)
            _tf.write(vid_file.read()); _tf.flush(); _tf.close()
            st.session_state.vid_path = _tf.name
            _vp = _tf.name
            # Show video info
            _ci = cv2.VideoCapture(_vp)
            if _ci.isOpened():
                _fw = int(_ci.get(cv2.CAP_PROP_FRAME_WIDTH))
                _fh = int(_ci.get(cv2.CAP_PROP_FRAME_HEIGHT))
                _ff = _ci.get(cv2.CAP_PROP_FPS)
                _ft = int(_ci.get(cv2.CAP_PROP_FRAME_COUNT))
                st.sidebar.success(f"✅ {_fw}×{_fh} @ {_ff:.0f}fps — {_ft} frames")
                _ci.release()

        # ── STEP 2: Process video (blocking, shows live frames) ───
        if _vp and not _vd:
            _prog = st.progress(0, text="🔄 Loading video...")
            _stat = st.empty()
            import gc as _gc
            out_p, vbytes, vstats = process_video(
                _vp, st.session_state.yolo_model, fskip, vid_slot, _prog, _stat)
            st.session_state.out_path  = out_p
            st.session_state.vid_bytes = vbytes
            st.session_state.vid_stats = vstats
            st.session_state.vid_done  = True
            st.session_state.peak = max(st.session_state.peak, vstats.get("peak", 0))
            st.session_state.running = False
            _prog.empty(); _stat.empty(); _gc.collect()
            st.rerun()

        # ── STEP 3: Done — show player + download ─────────────────
        elif _vd and _vb:
            vid_slot.video(_vb)
            _vs  = st.session_state.get("vid_stats", {})
            _sz  = _vs.get("size", round(len(_vb)/1024/1024, 1))
            _b64 = base64.b64encode(_vb).decode()
            # Big download button
            st.markdown(f'''<div style="text-align:center;margin:14px 0">
              <a href="data:video/mp4;base64,{_b64}" download="trafficiq_annotated.mp4"
                 style="display:inline-block;background:linear-gradient(135deg,#ff6b00,#ff8c00);
                        color:#000;font-family:Orbitron,monospace;font-size:.8rem;
                        font-weight:700;padding:14px 36px;border-radius:8px;
                        text-decoration:none;letter-spacing:2px;
                        box-shadow:0 4px 20px rgba(255,107,0,.5)">
                ⬇ DOWNLOAD ANNOTATED VIDEO ({_sz} MB)
              </a></div>''', unsafe_allow_html=True)
            # Sidebar download
            with st.sidebar:
                st.markdown(
                    f'<a href="data:video/mp4;base64,{_b64}" download="trafficiq_annotated.mp4" '
                    f'style="display:block;text-align:center;background:rgba(255,107,0,.12);'
                    f'border:1px solid rgba(255,107,0,.3);color:#ff6b00;border-radius:6px;'
                    f'padding:8px 4px;font-family:monospace;font-size:.72rem;font-weight:700;'
                    f'text-decoration:none;margin:4px 0">⬇ DOWNLOAD VIDEO ({_sz} MB)</a>',
                    unsafe_allow_html=True)
            # Stats breakdown
            st.markdown(f'''<div style="background:rgba(13,20,33,.9);border:1px solid
              rgba(255,107,0,.2);border-radius:12px;padding:16px 20px;margin:10px 0">
              <div style="font-family:Share Tech Mono,monospace;font-size:.65rem;color:#ff6b00;
                          letter-spacing:2px;margin-bottom:12px">VEHICLE TYPE BREAKDOWN</div>
              <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;text-align:center">
                <div><div style="font-family:Orbitron,monospace;font-size:1.6rem;font-weight:800;
                  color:#00ff88">{_vs.get("avg_cars",0):.1f}</div>
                  <div style="font-family:Share Tech Mono,monospace;font-size:.55rem;color:#4a5568">
                  AVG CARS</div></div>
                <div><div style="font-family:Orbitron,monospace;font-size:1.6rem;font-weight:800;
                  color:#ff6b00">{_vs.get("avg_bikes",0):.1f}</div>
                  <div style="font-family:Share Tech Mono,monospace;font-size:.55rem;color:#4a5568">
                  AVG BIKES</div></div>
                <div><div style="font-family:Orbitron,monospace;font-size:1.6rem;font-weight:800;
                  color:#00d4ff">{_vs.get("frames",0)}</div>
                  <div style="font-family:Share Tech Mono,monospace;font-size:.55rem;color:#4a5568">
                  FRAMES</div></div>
                <div><div style="font-family:Orbitron,monospace;font-size:1.6rem;font-weight:800;
                  color:#ffd700">{_vs.get("peak",0)}</div>
                  <div style="font-family:Share Tech Mono,monospace;font-size:.55rem;color:#4a5568">
                  PEAK VEH</div></div>
              </div></div>''', unsafe_allow_html=True)

        # ── No file uploaded yet ────────────────────────────────────
        elif not _vp:
            _ph = np.full((240, 560, 3), 8, dtype=np.uint8)
            cv2.putText(_ph, "📁 Upload a video in the sidebar",
                        (50, 90), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 180, 255), 2)
            cv2.putText(_ph, "then press   START DETECTION",
                        (90, 140), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 120, 180), 1)
            vid_slot.image(cv2.cvtColor(_ph, cv2.COLOR_BGR2RGB),
                           channels="RGB", use_container_width=True)
            st.session_state.running = False

    # ══════════════════════════════════════════════════════════════
    #  DEMO / WEBCAM MODE — smooth frame loop with st.rerun()
    # ══════════════════════════════════════════════════════════════
    else:
        for _ in range(8):
            if not st.session_state.running: break
            n = st.session_state.frame_no; st.session_state.frame_no = n+1
            st.session_state.frames_done += 1
            night = night_override or is_night()

            if st.session_state.emergency_active:
                st.session_state.emergency_countdown -= 1
                if st.session_state.emergency_countdown <= 0:
                    st.session_state.emergency_active = False
                    st.session_state.emergency_type = ""
                    st.session_state.incident_log.appendleft({
                        "time": datetime.now().strftime("%H:%M:%S"), "icon": "✅",
                        "text": "Emergency cleared — normal operation resumed"})
            emergency_on = st.session_state.emergency_active

            # ── FRAME ACQUISITION ────────────────────────────────
            frame = None
            cars  = st.session_state.prev_c
            bikes = st.session_state.prev_b

            if demo_mode:
                frame, cars, bikes = demo_frame(demo_cars, demo_bikes, night, emergency_on)
            elif "Webcam" in src:
                if cam_img is not None:
                    import io as _io
                    _pimg = (_PIL_Image or __import__("PIL").Image)
                    pil_img = _pimg.open(_io.BytesIO(cam_img.getvalue())).convert("RGB")
                    frame   = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                    if st.session_state.yolo_model and n % fskip == 0:
                        frame, cars, bikes = detect_vehicles_fast(
                            st.session_state.yolo_model, frame)
                        st.session_state.prev_c = cars
                        st.session_state.prev_b = bikes
                    else:
                        _hud(frame, cars, bikes)
                else:
                    frame = np.full((480, 640, 3), 10, dtype=np.uint8)
                    cv2.putText(frame, "Click camera button above",
                                (80, 240), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 200, 100), 2)

            if frame is None:
                frame = np.full((400, 560, 3), 10, dtype=np.uint8)

            total = cars + bikes
            if total > st.session_state.peak: st.session_state.peak = total

            # Incident detection
            if incident_check(total, st.session_state.prev_total):
                st.session_state.incident_detected = True
                st.session_state.total_alerts += 1
                st.session_state.incident_log.appendleft({
                    "time": datetime.now().strftime("%H:%M:%S"), "icon": "⚠️",
                    "text": f"Sudden traffic change: {st.session_state.prev_total} → {total} vehicles"})
            elif n % 30 == 0:
                st.session_state.incident_detected = False
            st.session_state.prev_total = total

            # AQI
            raw_aqi = (int(manual_aqi+55*math.sin(n/30)+20*math.sin(n/8)+random.gauss(0,6))
                       if aqi_src == "Auto-Simulate" else manual_aqi)
            raw_aqi = max(0, min(500, raw_aqi))
            aqi = weather_aqi_correction(raw_aqi, temp, humid, wind)
            aqi_lbl, aqi_col, aqi_em, aqi_bg = classify_aqi(aqi)

            hdf_check = pd.DataFrame(list(st.session_state.history))
            t_anom, a_anom, z_val = detect_anomaly(hdf_check, total, aqi)
            if a_anom and n % 15 == 0:
                st.session_state.incident_log.appendleft({
                    "time": datetime.now().strftime("%H:%M:%S"), "icon": "🌫️",
                    "text": f"AQI anomaly z={z_val:.1f}, AQI={aqi}"})

            t_level, t_col, _ = classify_traffic(total)
            green_t, dec, sig  = signal_decision(t_level, aqi, emergency_on, night)
            ped_t = pedestrian_phase(green_t)

            spd = estimate_speed(total, t_level, night)
            st.session_state.avg_speed = round(0.85*st.session_state.avg_speed + 0.15*spd, 1)
            st.session_state.speed_history.append(spd)
            congestion_idx = compute_congestion_index(total, aqi, spd)
            st.session_state.congestion_index = congestion_idx
            flow_rate = compute_flow_rate(total, st.session_state.speed_history)
            if n % 10 == 0:
                st.session_state.route_status = update_route_status(congestion_idx)

            idle_saved = abs(green_t-30)*0.03
            st.session_state.idle_time_saved += idle_saved
            st.session_state.co2_saved = compute_co2(st.session_state.idle_time_saved, max(1,total))
            st.session_state.total_vehicles_cleared += total

            if n % fskip == 0:
                cnn_feat = cnn_extract(frame)
                st.session_state.cnn_feats.append(cnn_feat)
            else:
                cnn_feat = {"edge":0,"hgrad":0,"vgrad":0,"texture":0,"density":0}

            tot_hist = [r["total"] for r in st.session_state.history]
            aqi_hist = [r["aqi"]   for r in st.session_state.history]
            rnn_pred  = rnn_predict(tot_hist)  if len(tot_hist) > 3 else []
            lstm_pred = lstm_forecast(aqi_hist) if len(aqi_hist) > 3 else []
            if rnn_pred:  st.session_state.rnn_last  = rnn_pred[0]
            if lstm_pred: st.session_state.lstm_last = lstm_pred[-1]

            ann_probs = ann_classify(total, aqi)
            knn_pred = rf_pred = gbm_pred = "N/A"
            if n % fskip == 0 and SK_AVAILABLE:
                if knn_pipe:
                    try: knn_pred = knn_pipe.predict([[total,aqi]])[0].upper()
                    except: pass
                if rf_pipe:
                    try: rf_pred = rf_pipe.predict([[cars,bikes,aqi,total]])[0].upper()
                    except: pass
                if gbm_pipe:
                    try: gbm_pred = gbm_pipe.predict([[cars,bikes,aqi,total,temp]])[0].upper()
                    except: pass

            if n % 3 == 0:
                st.session_state.heatmap_data = update_heatmap(
                    st.session_state.heatmap_data, total, n)

            eff = compute_efficiency(total, green_t, hdf_check)
            st.session_state.efficiency_scores.append(eff)
            lane1 = max(0, total//2+random.randint(-1,1))
            lane2 = max(0, total-lane1)
            emerg_int = st.session_state.emergency_intersection if emergency_on else -1
            int_states = update_intersections(n, emerg_int)

            st.session_state.history.append({
                "cars":cars,"bikes":bikes,"total":total,"aqi":aqi,
                "level":t_level,"signal":sig,"green_time":green_t,
                "efficiency":eff,"co2_saved":st.session_state.co2_saved,
                "speed":spd,"congestion":congestion_idx,
            })

            # ── RENDER ───────────────────────────────────────────
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h0, w0 = frame_rgb.shape[:2]
            if w0 > 560:
                sc = 560/w0
                frame_rgb = cv2.resize(frame_rgb, (560, int(h0*sc)))
            vid_slot.image(frame_rgb, channels="RGB", use_container_width=True, clamp=True)

            if emergency_on:
                emergency_slot.markdown(
                    f'<div class="emergency-banner">{st.session_state.emergency_type} — '
                    f'Priority Override ACTIVE — '
                    f'{INTERSECTIONS[st.session_state.emergency_intersection]} Cleared — '
                    f'{st.session_state.emergency_countdown}s remaining</div>',
                    unsafe_allow_html=True)
            else:
                emergency_slot.empty()

            ni = "🌙" if night else "☀"; wi = "🌊" if green_wave else "·"
            det_mode = "DEMO" if demo_mode else "YOLO-LIVE"
            status_slot.markdown(f'''<div class="statusbar">
              <span>Frame <b>{n}</b> | {det_mode} {ni} {wi}</span>
              <span>AQI Δ: <b>{aqi-raw_aqi:+d}</b></span>
              <span>Peak: <b>{st.session_state.peak}</b></span>
              <span>Alerts: <b>{st.session_state.total_alerts}</b></span>
              <span>{datetime.now().strftime("%H:%M:%S")}</span>
            </div>''', unsafe_allow_html=True)

            slot_metrics.markdown(f'''
            <div class="mgrid">
              <div class="mcard mc-car"><div class="mval">{cars}</div><div class="mlbl">CAR/BUS/TRUCK</div></div>
              <div class="mcard mc-bike"><div class="mval">{bikes}</div><div class="mlbl">BIKE/MOTO</div></div>
              <div class="mcard mc-tot"><div class="mval">{total}</div><div class="mlbl">TOTAL</div></div>
              <div class="mcard mc-aqi"><div class="mval" style="font-size:1.8rem">{aqi}</div><div class="mlbl">AQI</div></div>
            </div>
            <div class="mgrid3">
              <div class="mcard mc-spd"><div class="mval" style="font-size:1.5rem">{st.session_state.avg_speed}</div><div class="mlbl">km/h AVG</div></div>
              <div class="mcard mc-flow"><div class="mval" style="font-size:1.5rem">{flow_rate:.0f}</div><div class="mlbl">VEH/MIN</div></div>
              <div class="mcard mc-eff"><div class="mval" style="font-size:1.5rem">{eff:.0f}</div><div class="mlbl">EFFICIENCY</div></div>
            </div>
            <div class="mgrid2">
              <div class="mcard mc-co2"><div class="mval" style="font-size:1.2rem">{st.session_state.co2_saved:.3f}</div><div class="mlbl">kg CO2 SAVED</div></div>
              <div class="mcard" style="--card-color:#ff2244;--card-top:#ff2244"><div class="mval" style="font-size:1.2rem">{congestion_idx}</div><div class="mlbl">CONGESTION IDX</div></div>
            </div>''', unsafe_allow_html=True)

            slot_aqi.markdown(f'''<div class="aqi-panel" style="border-color:{aqi_col}22">
              <div style="display:flex;justify-content:space-between">
                <div>
                  <div class="aqi-big" style="color:{aqi_col}">{aqi}</div>
                  <span class="aqi-tag" style="color:{aqi_col}">{aqi_em} {aqi_lbl}</span>
                  <div style="font-family:Share Tech Mono,monospace;font-size:.6rem;color:#4a5568;margin-top:6px">
                    Raw:{raw_aqi} Δ:<b style="color:#ff6b00">{aqi-raw_aqi:+d}</b>
                    &nbsp;|&nbsp; LSTM:<b style="color:#bf5fff">{st.session_state.lstm_last:.0f}</b>
                  </div>
                </div>
                <div style="font-family:Share Tech Mono,monospace;font-size:.68rem;color:#4a5568;text-align:right;line-height:2">
                  <div>WIND <b style="color:#ff6b00">{wind}km/h</b></div>
                  <div>TEMP <b style="color:#ff6b00">{temp}°C</b></div>
                  <div>HUM <b style="color:#ff6b00">{humid}%</b></div>
                </div>
              </div>
            </div>''', unsafe_allow_html=True)

            pcls = "sig-emergency" if emergency_on else f"sig-{sig}"
            r_cls = "tl-red-on"    if (sig=="red" or emergency_on) else "tl-red-off"
            y_cls = "tl-yellow-on" if sig=="yellow"                 else "tl-yellow-off"
            g_cls = "tl-green-on"  if (sig=="green" and not emergency_on) else "tl-green-off"
            slot_sig.markdown(f'''<div class="sig-panel {pcls}">
              <div class="tl-wrap">
                <div class="tl-housing">
                  <div class="tl-light {r_cls}"></div>
                  <div class="tl-light {y_cls}"></div>
                  <div class="tl-light {g_cls}"></div>
                </div>
                <div class="tl-info">
                  <div class="sig-lbl">{"EMERGENCY OVERRIDE" if emergency_on else "SIGNAL DURATION"}</div>
                  <div class="sig-time">{green_t}s</div>
                  <div class="sig-lbl">TRAFFIC: <b>{t_level.upper()}</b></div>
                  <div style="font-size:.82rem;color:#a0aec0;margin-top:4px">{dec}</div>
                  <div style="font-family:Share Tech Mono,monospace;font-size:.6rem;color:#4a5568;margin-top:6px">
                    PED:{ped_t}s Night:{"ON" if night else "OFF"} Wave:{"ON" if green_wave else "OFF"}
                  </div>
                </div>
              </div>
            </div>''', unsafe_allow_html=True)

            cap2 = max(1, demo_cars+demo_bikes+4)
            l1p  = min(100, int(lane1/cap2*100))
            l2p  = min(100, int(lane2/cap2*100))
            def lc(p): return("#00ff88" if p<50 else "#ffd700" if p<80 else "#ff2244")
            slot_lanes.markdown(f'''
            <div class="lane-wrap">
              <div class="lane-label">LANE A — INBOUND — {lane1} vehicles</div>
              <div class="lane-track"><div class="lane-fill" style="width:{l1p}%;background:{lc(l1p)}"></div></div>
              <div class="lane-pct" style="color:{lc(l1p)}">{l1p}%</div>
            </div>
            <div class="lane-wrap" style="margin-top:10px">
              <div class="lane-label">LANE B — OUTBOUND — {lane2} vehicles</div>
              <div class="lane-track"><div class="lane-fill" style="width:{l2p}%;background:{lc(l2p)}"></div></div>
              <div class="lane-pct" style="color:{lc(l2p)}">{l2p}%</div>
            </div>
            <div style="background:rgba(0,212,255,.06);border:1px solid rgba(0,212,255,.2);
                        border-radius:8px;padding:10px 14px;margin-top:12px;text-align:center">
              <div style="font-family:Share Tech Mono,monospace;font-size:.6rem;color:#00d4ff">PEDESTRIAN</div>
              <div style="font-family:Orbitron,monospace;font-size:1.6rem;font-weight:800;color:#00d4ff">{ped_t}s</div>
            </div>''', unsafe_allow_html=True)

            pe = {"GREEN":"🟢","YELLOW":"🟡","RED":"🔴","EMERGENCY":"🚨"}
            ihtml = '<div class="intersection-grid">'
            for i,(phase,timer,style) in enumerate(int_states):
                wn = (f'<div style="font-size:.5rem;color:#4a5568">+{i*15}s</div>'
                      if green_wave and i>0 else "")
                ihtml += (f'<div class="int-card {style}">'
                          f'<div class="int-name">{INTERSECTIONS[i]}</div>'
                          f'<div class="int-signal">{pe.get(phase,"🔴")}</div>'
                          f'<div class="int-time" style="color:{INT_COLORS[i]}">{timer}s</div>'
                          f'<div style="font-size:.56rem;color:#4a5568">{phase}</div>{wn}</div>')
            ihtml += "</div>"
            slot_intersections.markdown(ihtml, unsafe_allow_html=True)

            r_ring=40; circ=2*math.pi*r_ring
            dash=round(congestion_idx/100*circ,1); gap=round(circ-dash,1)
            ci_col="#00ff88" if congestion_idx<30 else "#ffd700" if congestion_idx<60 else "#ff2244"
            slot_speed.markdown(f'''
            <div class="speed-gauge" style="margin-bottom:10px">
              <div style="font-family:Share Tech Mono,monospace;font-size:.6rem;color:#4a5568">AVG SPEED</div>
              <div class="speed-val">{st.session_state.avg_speed} <span style="font-size:1rem">km/h</span></div>
            </div>
            <div style="background:rgba(13,20,33,.9);border:1px solid rgba(255,107,0,.15);
                        border-radius:12px;padding:14px;text-align:center">
              <div style="font-family:Share Tech Mono,monospace;font-size:.6rem;color:#4a5568;margin-bottom:8px">CONGESTION INDEX</div>
              <div class="congestion-ring">
                <svg class="cring-svg" width="90" height="90" viewBox="0 0 90 90">
                  <circle cx="45" cy="45" r="{r_ring}" fill="none" stroke="rgba(255,255,255,.05)" stroke-width="8"/>
                  <circle cx="45" cy="45" r="{r_ring}" fill="none" stroke="{ci_col}" stroke-width="8"
                    stroke-dasharray="{dash} {gap}" stroke-linecap="round"/>
                </svg>
                <div class="cring-val">
                  <div class="cring-num" style="color:{ci_col}">{congestion_idx}</div>
                  <div class="cring-lbl">/ 100</div>
                </div>
              </div>
              <div style="font-family:Share Tech Mono,monospace;font-size:.62rem;color:{ci_col};margin-top:6px">
                {"FREE FLOW" if congestion_idx<30 else "MODERATE" if congestion_idx<60 else "CONGESTED"}
              </div>
            </div>''', unsafe_allow_html=True)

            rs    = st.session_state.route_status
            rcls  = {"FREE":"route-free","MODERATE":"route-mod","JAM":"route-jam"}
            rtime = {"FREE":f"{random.randint(8,14)} min",
                     "MODERATE":f"{random.randint(18,28)} min",
                     "JAM":f"{random.randint(35,55)} min"}
            rhtml = '<div class="route-card">'
            for route, status in rs.items():
                short = route.replace("Via ","").replace("Highway ","")
                rhtml += (f'<div class="route-item">'
                          f'<span class="route-name">{short}</span>'
                          f'<span class="route-status {rcls[status]}">{status}</span>'
                          f'<span class="route-time">{rtime[status]}</span></div>')
            slot_route.markdown(rhtml+"</div>", unsafe_allow_html=True)

            best_ann  = max(ann_probs, key=ann_probs.get)
            ac = {"GREEN":"#00ff88","YELLOW":"#ffd700","RED":"#ff2244"}
            cnn_edge  = st.session_state.cnn_feats[-1]["edge"] if st.session_state.cnn_feats else "--"
            ml_items  = [
                ("CNN EDGE",  str(cnn_edge), "#ff6b00"),
                ("RNN NEXT",  f"{st.session_state.rnn_last:.1f} veh","#00d4ff"),
                ("LSTM AQI",  f"{st.session_state.lstm_last:.0f}","#bf5fff"),
                (f"ANN→{best_ann}", f"{ann_probs[best_ann]:.0%}", ac.get(best_ann,"#ff6b00")),
                ("KNN (k=5)", knn_pred, "#00ff88"),
                ("RF 120T",   rf_pred,  "#00ff88"),
                ("GBM 80T",   gbm_pred, "#00d4ff"),
            ]
            slot_ml.markdown(
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:7px">'
                +"".join(f'<div class="mlrow"><div class="mlrow-lbl">{lb}</div>'
                         f'<div class="mlrow-val" style="color:{col}">{val}</div></div>'
                         for lb,val,col in ml_items)
                +"</div>", unsafe_allow_html=True)

            pa = st.session_state.pred_accuracy
            if n % 20 == 0:
                pa["KNN"] = round(min(99,pa["KNN"]+random.gauss(0,.3)),1)
                pa["RF"]  = round(min(99,pa["RF"] +random.gauss(0,.2)),1)
                pa["GBM"] = round(min(99,pa["GBM"]+random.gauss(0,.15)),1)
                pa["ANN"] = round(min(99,pa["ANN"]+random.gauss(0,.4)),1)
            acc_html = "".join(
                f'<div class="acc-bar"><div class="acc-name">{m}</div>'
                f'<div class="acc-track"><div class="acc-fill" style="width:{v}%"></div></div>'
                f'<div class="acc-pct" style="color:{"#00ff88" if v>90 else "#ffd700" if v>80 else "#ff6b00"}">{v:.1f}%</div></div>'
                for m,v in pa.items())
            slot_acc.markdown(acc_html, unsafe_allow_html=True)

            anom_html = ""
            if t_anom: anom_html += f'<div class="anomaly-card critical">⚡ TRAFFIC ANOMALY Z={z_val:.1f}</div>'
            if a_anom: anom_html += f'<div class="anomaly-card">🌫️ AQI ANOMALY Z={z_val:.1f} AQI={aqi}</div>'
            if st.session_state.incident_detected:
                anom_html += '<div class="anomaly-card critical">🚧 INCIDENT ALERT</div>'
            al_t = ("al-crit" if aqi>200 or total>20 else
                    "al-warn" if aqi>150 or total>12 else "al-ok")
            slot_alerts.markdown(
                f'{anom_html}<div class="{al_t}">'
                f'{"⛔ CRITICAL" if aqi>200 else "⚠️ ELEVATED" if aqi>150 else "✅ NORMAL"}'
                f' — AQI {aqi} — {total} veh</div>'
                f'<div class="al-info" style="font-size:.82rem">'
                f'KNN:{knn_pred} RF:{rf_pred} GBM:{gbm_pred}<br>'
                f'ANN: G={ann_probs.get("GREEN",0):.0%} Y={ann_probs.get("YELLOW",0):.0%} R={ann_probs.get("RED",0):.0%}</div>',
                unsafe_allow_html=True)

            avg_eff = sum(st.session_state.efficiency_scores)/max(1,len(st.session_state.efficiency_scores))
            eb = min(100,int(avg_eff))
            ec = "#00ff88" if avg_eff>70 else "#ffd700" if avg_eff>40 else "#ff2244"
            uptime = int((datetime.now()-st.session_state.session_start).total_seconds())
            slot_efficiency.markdown(f'''<div class="eff-card">
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:center">
                <div>
                  <div style="font-family:Share Tech Mono,monospace;font-size:.6rem;color:#4a5568">EFFICIENCY</div>
                  <div class="eff-score">{avg_eff:.1f}<span style="font-size:1.3rem;color:#4a5568"> /100</span></div>
                  <div class="eff-bar"><div class="eff-fill" style="width:{eb}%;background:{ec}"></div></div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
                  <div style="text-align:center;background:rgba(255,255,255,.03);border-radius:8px;padding:8px">
                    <div style="font-family:Orbitron,monospace;font-size:1.1rem;font-weight:800;color:#00ff88">{st.session_state.co2_saved:.3f}</div>
                    <div style="font-family:Share Tech Mono,monospace;font-size:.5rem;color:#4a5568">kg CO2</div>
                  </div>
                  <div style="text-align:center;background:rgba(255,255,255,.03);border-radius:8px;padding:8px">
                    <div style="font-family:Orbitron,monospace;font-size:1.1rem;font-weight:800;color:#ff6b00">{st.session_state.total_vehicles_cleared}</div>
                    <div style="font-family:Share Tech Mono,monospace;font-size:.5rem;color:#4a5568">CLEARED</div>
                  </div>
                  <div style="text-align:center;background:rgba(255,255,255,.03);border-radius:8px;padding:8px">
                    <div style="font-family:Orbitron,monospace;font-size:1.1rem;font-weight:800;color:#00d4ff">{uptime}s</div>
                    <div style="font-family:Share Tech Mono,monospace;font-size:.5rem;color:#4a5568">UPTIME</div>
                  </div>
                  <div style="text-align:center;background:rgba(255,255,255,.03);border-radius:8px;padding:8px">
                    <div style="font-family:Orbitron,monospace;font-size:1.1rem;font-weight:800;color:#bf5fff">{st.session_state.frames_done}</div>
                    <div style="font-family:Share Tech Mono,monospace;font-size:.5rem;color:#4a5568">FRAMES</div>
                  </div>
                </div>
              </div>
            </div>''', unsafe_allow_html=True)

            log_html = '<div class="incident-log">'
            if st.session_state.incident_log:
                for item in st.session_state.incident_log:
                    log_html += (f'<div class="incident-item">'
                                 f'<span class="incident-time">{item["time"]}</span>'
                                 f'<span class="incident-icon">{item["icon"]}</span>'
                                 f'<span class="incident-text">{item["text"]}</span></div>')
            else:
                log_html += '<div style="color:#4a5568;padding:12px;text-align:center">No incidents</div>'
            slot_incidents.markdown(log_html+"</div>", unsafe_allow_html=True)

            # Chart updates every 40 frames + RAM cleanup
            if n % 3  == 0: plt.close("all")
            if n % 20 == 0: import gc; gc.collect()
            if n % 40 == 0 and len(st.session_state.history) > 5:
                hdf = pd.DataFrame(list(st.session_state.history))
                live_scatter.pyplot(chart_scatter(hdf), use_container_width=True)
                live_series.pyplot(chart_timeseries(hdf), use_container_width=True)
                live_cnn.pyplot(chart_cnn(st.session_state.cnn_feats), use_container_width=True)
                live_rnn.pyplot(chart_rnn_lstm(hdf,lstm_pred,rnn_pred), use_container_width=True)
                live_ann.pyplot(chart_ann(ann_probs), use_container_width=True)
                live_knn.pyplot(chart_knn(knn_pipe,knn_df,total,aqi), use_container_width=True)
                live_km.pyplot(chart_kmeans(km_model,km_df,total,aqi), use_container_width=True)
                live_rf.pyplot(chart_gbm_compare(rf_pipe,gbm_pipe), use_container_width=True)
                live_sighist.pyplot(chart_signal_history(hdf), use_container_width=True)
                live_eff.pyplot(chart_efficiency(hdf), use_container_width=True)
                live_corr.pyplot(chart_correlation_matrix(hdf), use_container_width=True)
                live_spdflo.pyplot(chart_speed_flow(hdf), use_container_width=True)
                live_heatmap.pyplot(chart_heatmap(st.session_state.heatmap_data), use_container_width=True)

            time.sleep(0.05)

        if st.session_state.running: st.rerun()

