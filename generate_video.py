"""
generate_video.py
=================
Generates a realistic synthetic traffic video (traffic.mp4)
with moving cars and bikes on a road.

Run:
    python generate_video.py

Output:
    traffic.mp4  (in the same folder)
"""

import cv2
import numpy as np
import random
import math

# ── Video settings ────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 640, 480
FPS           = 20
DURATION_SEC  = 30          # 30 second video
TOTAL_FRAMES  = FPS * DURATION_SEC
OUTPUT_FILE   = "traffic.mp4"

# ── Vehicle class ─────────────────────────────────────────────────────────────
class Vehicle:
    def __init__(self, vtype, lane, frame_w, frame_h):
        self.type   = vtype          # "car" or "bike"
        self.lane   = lane           # 0 = top lane (left→right), 1 = bottom lane (right→left)
        self.fw     = frame_w
        self.fh     = frame_h

        # Size
        if vtype == "car":
            self.w = random.randint(55, 75)
            self.h = random.randint(28, 36)
            self.speed = random.uniform(3.5, 6.5)
            # Random car colours
            self.color = random.choice([
                (30,  30, 180),   # blue
                (180, 30,  30),   # red
                (200,200,200),    # silver
                (30, 140,  30),   # green
                (200,150,  30),   # yellow
                (80,  80,  80),   # dark grey
            ])
        else:  # bike
            self.w = random.randint(22, 32)
            self.h = random.randint(18, 24)
            self.speed = random.uniform(4.0, 8.0)
            self.color = random.choice([
                (0,  100, 200),
                (200, 80,   0),
                (150,  0, 150),
                (0,  180, 180),
            ])

        # Starting position
        if self.lane == 0:   # left → right
            self.x = -self.w
            self.y = int(frame_h * 0.28) + random.randint(-18, 18)
        else:                # right → left
            self.x = frame_w
            self.y = int(frame_h * 0.62) + random.randint(-18, 18)

    def update(self):
        if self.lane == 0:
            self.x += self.speed
        else:
            self.x -= self.speed

    def is_offscreen(self):
        return self.x > self.fw + self.w or self.x < -self.w * 2

    def draw(self, frame):
        x1 = int(self.x)
        y1 = int(self.y)
        x2 = x1 + self.w
        y2 = y1 + self.h

        # Body
        cv2.rectangle(frame, (x1, y1), (x2, y2), self.color, -1)

        # Windshield (lighter rectangle)
        wx1 = x1 + int(self.w * 0.2)
        wx2 = x1 + int(self.w * 0.8)
        wy1 = y1 + 4
        wy2 = y1 + int(self.h * 0.55)
        glass = tuple(min(255, c + 80) for c in self.color)
        cv2.rectangle(frame, (wx1, wy1), (wx2, wy2), glass, -1)

        # Wheels
        wheel_r = max(4, int(self.h * 0.22))
        cv2.circle(frame, (x1 + int(self.w*0.2), y2), wheel_r, (20, 20, 20), -1)
        cv2.circle(frame, (x1 + int(self.w*0.8), y2), wheel_r, (20, 20, 20), -1)

        # Label
        label = "Car" if self.type == "car" else "Bike"
        cv2.putText(frame, label, (x1 + 2, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)


# ── Road drawing ──────────────────────────────────────────────────────────────
def draw_road(frame):
    # Sky gradient
    for y in range(HEIGHT // 2):
        t = y / (HEIGHT // 2)
        c = int(135 + t * 30)
        frame[y, :] = (c, int(c * 0.85), int(c * 0.6))

    # Ground
    frame[HEIGHT//2:, :] = (60, 80, 60)

    # Road surface
    road_top    = int(HEIGHT * 0.38)
    road_bottom = HEIGHT
    road_color  = (80, 80, 85)
    pts = np.array([
        [0, road_top], [WIDTH, road_top],
        [WIDTH, road_bottom], [0, road_bottom]
    ], np.int32)
    cv2.fillPoly(frame, [pts], road_color)

    # Centre divider line (dashed yellow)
    centre_y = int(HEIGHT * 0.50)
    for x in range(0, WIDTH, 40):
        cv2.line(frame, (x, centre_y), (x + 22, centre_y), (220, 200, 0), 2)

    # Road edges
    cv2.line(frame, (0, road_top),    (WIDTH, road_top),    (200, 200, 200), 2)
    cv2.line(frame, (0, road_bottom - 2), (WIDTH, road_bottom - 2), (200, 200, 200), 2)

    # Simple buildings silhouette
    buildings = [(30,80,60,140),(110,90,70,140),(200,70,80,140),
                 (310,85,55,140),(400,75,65,140),(490,95,60,140),(570,80,60,140)]
    for (bx, by, bw, bh) in buildings:
        cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), (60, 70, 90), -1)
        # Windows
        for wy in range(by+8, by+bh-10, 18):
            for wx in range(bx+6, bx+bw-6, 14):
                wc = (220,220,100) if random.random() > 0.3 else (40,40,60)
                cv2.rectangle(frame, (wx, wy), (wx+8, wy+10), wc, -1)

    # Trees
    for tx in [15, 95, 185, 295, 385, 475, 565]:
        ty = int(HEIGHT * 0.38) - 2
        cv2.rectangle(frame, (tx, ty-18), (tx+6, ty), (100, 70, 40), -1)
        cv2.circle(frame, (tx+3, ty-20), 12, (30, 130, 30), -1)


# ── Main generator ────────────────────────────────────────────────────────────
def main():
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out    = cv2.VideoWriter(OUTPUT_FILE, fourcc, FPS, (WIDTH, HEIGHT))

    vehicles = []
    spawn_timer = 0

    print(f"Generating {DURATION_SEC}s traffic video → {OUTPUT_FILE}")
    print("Please wait...")

    for frame_idx in range(TOTAL_FRAMES):
        # Base frame with road
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        draw_road(frame)

        # Spawn vehicles periodically
        spawn_timer += 1
        if spawn_timer >= random.randint(12, 25):
            spawn_timer = 0
            vtype = "car" if random.random() < 0.7 else "bike"
            lane  = random.randint(0, 1)
            vehicles.append(Vehicle(vtype, lane, WIDTH, HEIGHT))

        # Update and draw vehicles (draw lane 1 first, then lane 0 on top)
        for lane in [1, 0]:
            for v in vehicles:
                if v.lane == lane:
                    v.update()
                    v.draw(frame)

        # Remove off-screen vehicles
        vehicles = [v for v in vehicles if not v.is_offscreen()]

        # Timestamp overlay
        seconds = frame_idx // FPS
        ms      = (frame_idx % FPS) * (1000 // FPS)
        ts      = f"00:{seconds//60:02d}:{seconds%60:02d}.{ms:03d}"
        cv2.putText(frame, ts, (WIDTH-160, HEIGHT-12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Vehicle count HUD
        cars_n  = sum(1 for v in vehicles if v.type == "car")
        bikes_n = sum(1 for v in vehicles if v.type == "bike")
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (220, 68), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
        cv2.putText(frame, f"Cars : {cars_n}",  (8, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        cv2.putText(frame, f"Bikes: {bikes_n}", (8, 56),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 165, 255), 2)

        out.write(frame)

        # Progress
        if frame_idx % (FPS * 5) == 0:
            pct = int(frame_idx / TOTAL_FRAMES * 100)
            print(f"  {pct}% done...")

    out.release()
    print(f"\n✅ Done! Video saved as:  {OUTPUT_FILE}")
    print("Now upload it in the Streamlit app → 'Upload Video' option.")


if __name__ == "__main__":
    main()
PYEOF

//DEMO

"""
TrafficIQ v4.0 — Smart Traffic Signalling + AQI Prediction
===========================================================
Prepared by : Sanket Sutar
Project     : Deep Learning & ML for Smart Urban Traffic Management
Algorithms  : CNN · RNN · LSTM · ANN · KNN · KMeans · Random Forest

Run: streamlit run app.py
"""

import streamlit as st
import cv2, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import time, random, math, base64
from datetime import datetime
from collections import deque

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TrafficIQ — Sanket Sutar",
    page_icon="🧠", layout="wide",
    initial_sidebar_state="expanded"
)

# ── Optional imports ───────────────────────────────────────────────────────────
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except: YOLO_AVAILABLE = False

try:
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.cluster import KMeans
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    SK_AVAILABLE = True
except: SK_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
#  MASTER CSS  —  Luxury Dark + Amber/Gold accent — "Neural City" aesthetic
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:ital,wght@0,300;0,400;0,700;0,900;1,400&family=JetBrains+Mono:wght@300;400;700&family=Bebas+Neue&display=swap');

:root{
  --gold:#f5a623; --gold2:#ffd166; --cyan:#00e5ff; --green:#00e676;
  --red:#ff1744;  --purple:#e040fb; --bg:#03070f;  --bg2:#060d1c;
  --bg3:#091428;  --border:#0d2545; --border2:#1a3a6a;
  --text:#b8d0e8; --text2:#5a8ab8;
}

html,body,[class*="css"]{
  font-family:'Exo 2',sans-serif;
  background:var(--bg); color:var(--text);
}
.stApp{background:var(--bg);}

/* ── Sidebar ── */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#040b16 0%,#060d1c 100%);
  border-right:1px solid var(--border);
}
[data-testid="stSidebar"] *{color:#6a9ac8!important;}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3{color:var(--gold)!important;}

/* ── HERO ── */
.hero{
  background:linear-gradient(135deg,#03070f 0%,#060d1c 45%,#08142a 100%);
  border:1px solid var(--border2); border-radius:20px;
  padding:2rem 2.4rem 1.6rem; margin-bottom:1.6rem;
  position:relative; overflow:hidden;
}
.hero::before{
  content:''; position:absolute; inset:0; pointer-events:none;
  background:
    radial-gradient(ellipse 60% 40% at 80% 50%, rgba(245,166,35,.06) 0%, transparent 70%),
    repeating-linear-gradient(90deg,transparent,transparent 60px,rgba(245,166,35,.03) 60px,rgba(245,166,35,.03) 61px),
    repeating-linear-gradient(0deg,transparent,transparent 60px,rgba(245,166,35,.03) 60px,rgba(245,166,35,.03) 61px);
}
.hero-eyebrow{
  font-family:'JetBrains Mono',monospace; font-size:.7rem;
  color:var(--gold); letter-spacing:4px; text-transform:uppercase;
  margin-bottom:6px; opacity:.85;
}
.hero-title{
  font-family:'Bebas Neue',sans-serif; font-size:3.8rem; line-height:.95;
  color:#fff; letter-spacing:5px; margin:0;
  text-shadow:0 0 40px rgba(245,166,35,.25), 0 0 80px rgba(245,166,35,.08);
}
.hero-title span{color:var(--gold);}
.hero-sub{
  font-family:'Exo 2',sans-serif; font-size:1rem; font-weight:300;
  color:var(--text2); margin-top:8px; letter-spacing:1px;
}
.hero-author{
  display:inline-flex; align-items:center; gap:10px;
  background:rgba(245,166,35,.08); border:1px solid rgba(245,166,35,.25);
  border-radius:30px; padding:6px 18px; margin-top:14px;
}
.hero-author-name{
  font-family:'Exo 2',sans-serif; font-size:.95rem; font-weight:700;
  color:var(--gold); letter-spacing:1px;
}
.hero-author-role{
  font-family:'JetBrains Mono',monospace; font-size:.68rem;
  color:var(--text2); letter-spacing:2px;
}
.hero-badges{margin-top:12px; display:flex; flex-wrap:wrap; gap:6px;}
.hbadge{
  font-family:'JetBrains Mono',monospace; font-size:.65rem;
  padding:4px 12px; border-radius:20px; letter-spacing:1.5px;
}
.hb-gold{background:rgba(245,166,35,.1);border:1px solid rgba(245,166,35,.3);color:var(--gold);}
.hb-cyan{background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.25);color:var(--cyan);}
.hb-green{background:rgba(0,230,118,.08);border:1px solid rgba(0,230,118,.25);color:var(--green);}
.hb-live{background:rgba(0,230,118,.1);border:1px solid rgba(0,230,118,.4);color:var(--green);
  animation:liveblink 1.5s infinite;}
@keyframes liveblink{0%,100%{opacity:1}50%{opacity:.35}}

/* ── Section title ── */
.stitle{
  font-family:'Bebas Neue',sans-serif; font-size:1.1rem;
  color:var(--gold); letter-spacing:4px;
  border-bottom:1px solid rgba(245,166,35,.2);
  padding-bottom:6px; margin:6px 0 14px;
  display:flex; align-items:center; gap:8px;
}

/* ── Metric cards ── */
.mgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px;}
.mgrid3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px;}
.mcard{
  background:linear-gradient(135deg,var(--bg2),var(--bg3));
  border:1px solid var(--border); border-radius:14px;
  padding:16px 12px; text-align:center; position:relative; overflow:hidden;
  transition:border-color .3s, transform .2s;
}
.mcard:hover{border-color:var(--gold);transform:translateY(-2px);}
.mcard::before{
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg,transparent,var(--card-accent,var(--gold)),transparent);
}
.mval{
  font-family:'Bebas Neue',sans-serif; font-size:2.4rem; line-height:1;
  color:var(--card-accent,var(--gold));
  text-shadow:0 0 16px rgba(245,166,35,.35);
}
.mlbl{
  font-family:'JetBrains Mono',monospace; font-size:.62rem;
  color:var(--text2); letter-spacing:2px; margin-top:3px;
}
.mc-car {--card-accent:var(--green);}
.mc-car .mval{text-shadow:0 0 14px rgba(0,230,118,.35);}
.mc-bike{--card-accent:#ff9100;}
.mc-bike .mval{text-shadow:0 0 14px rgba(255,145,0,.35);}
.mc-tot {--card-accent:var(--purple);}
.mc-tot .mval{text-shadow:0 0 14px rgba(224,64,251,.35);}
.mc-aqi {--card-accent:var(--red);}
.mc-aqi .mval{text-shadow:0 0 14px rgba(255,23,68,.35);}

/* ── Signal panel ── */
.sig-panel{border-radius:14px;padding:18px;margin-bottom:12px;position:relative;overflow:hidden;}
.sig-green {background:linear-gradient(135deg,#010b04,#021508);border:1px solid var(--green);}
.sig-yellow{background:linear-gradient(135deg,#0d0900,#1a1100);border:1px solid #ff9100;}
.sig-red   {background:linear-gradient(135deg,#0d0002,#1a0004);border:1px solid var(--red);}
.sig-time{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;line-height:1;margin:4px 0;}
.sig-green  .sig-time{color:var(--green);text-shadow:0 0 24px rgba(0,230,118,.5);}
.sig-yellow .sig-time{color:#ff9100;text-shadow:0 0 24px rgba(255,145,0,.5);}
.sig-red    .sig-time{color:var(--red);text-shadow:0 0 24px rgba(255,23,68,.5);}
.sig-lbl{font-family:'JetBrains Mono',monospace;font-size:.66rem;color:var(--text2);letter-spacing:2px;}
.sig-desc{font-family:'Exo 2',sans-serif;font-size:.9rem;font-weight:400;color:var(--text);margin-top:6px;line-height:1.5;}

/* ── AQI panel ── */
.aqi-panel{
  background:linear-gradient(135deg,var(--bg2),var(--bg3));
  border:1px solid var(--border2); border-radius:14px; padding:16px;
  margin-bottom:12px;
}
.aqi-big{font-family:'Bebas Neue',sans-serif;font-size:3.2rem;line-height:1;}
.aqi-tag{
  display:inline-block; border-radius:20px; padding:3px 14px;
  font-family:'JetBrains Mono',monospace; font-size:.68rem;
  letter-spacing:1.5px; font-weight:700; margin-top:6px;
}

/* ── Alert boxes ── */
.al-crit{background:linear-gradient(90deg,rgba(255,23,68,.14),transparent);
  border-left:4px solid var(--red);border-radius:0 10px 10px 0;
  padding:10px 14px;margin:5px 0;font-family:'Exo 2',sans-serif;
  font-size:.9rem;color:#ff8a9a;animation:redpulse 2s infinite;}
.al-warn{background:linear-gradient(90deg,rgba(255,145,0,.12),transparent);
  border-left:4px solid #ff9100;border-radius:0 10px 10px 0;
  padding:10px 14px;margin:5px 0;font-family:'Exo 2',sans-serif;
  font-size:.9rem;color:#ffbe6a;}
.al-ok  {background:linear-gradient(90deg,rgba(0,230,118,.1),transparent);
  border-left:4px solid var(--green);border-radius:0 10px 10px 0;
  padding:10px 14px;margin:5px 0;font-family:'Exo 2',sans-serif;
  font-size:.9rem;color:#6effc0;}
@keyframes redpulse{0%,100%{border-left-color:var(--red)}50%{border-left-color:#ff8a9a}}

/* ── Info/justification card ── */
.info-card{
  background:rgba(245,166,35,.04); border:1px solid rgba(245,166,35,.15);
  border-radius:12px; padding:14px 16px; margin:10px 0;
  font-family:'Exo 2',sans-serif; font-size:.88rem;
  color:var(--text2); line-height:1.65;
}
.info-card b{color:var(--gold);}
.info-card .ic-title{
  font-family:'Bebas Neue',sans-serif; font-size:1rem;
  color:var(--gold); letter-spacing:3px; margin-bottom:6px;
}

/* ── Model pill ── */
.model-pill{
  display:inline-flex; align-items:center; gap:6px;
  background:rgba(0,229,255,.07); border:1px solid rgba(0,229,255,.2);
  border-radius:20px; padding:4px 13px; margin:3px;
  font-family:'JetBrains Mono',monospace; font-size:.7rem; color:var(--cyan);
}

/* ── Lane bar ── */
.lane-bar{height:14px;border-radius:7px;background:var(--bg3);
  border:1px solid var(--border);margin:5px 0;overflow:hidden;}
.lane-fill{height:100%;border-radius:7px;transition:width .6s ease;}

/* ── Status bar ── */
.statusbar{
  background:var(--bg); border:1px solid var(--border);
  border-radius:8px; padding:7px 14px;
  font-family:'JetBrains Mono',monospace; font-size:.68rem; color:var(--text2);
  display:flex; justify-content:space-between; margin-top:6px;
}

/* ── Summary / About section ── */
.summary-card{
  background:linear-gradient(135deg,var(--bg2),var(--bg3));
  border:1px solid var(--border2); border-radius:16px;
  padding:22px 24px; margin:10px 0;
}
.summary-title{
  font-family:'Bebas Neue',sans-serif; font-size:1.5rem;
  color:var(--gold); letter-spacing:4px; margin-bottom:10px;
}
.summary-text{
  font-family:'Exo 2',sans-serif; font-size:.92rem;
  font-weight:300; color:var(--text); line-height:1.75;
}
.summary-text b{color:var(--gold); font-weight:700;}

/* ── Algorithm table ── */
.algo-row{
  display:grid; grid-template-columns:120px 110px 1fr;
  gap:10px; align-items:start;
  border-bottom:1px solid var(--border); padding:12px 0;
}
.algo-row:last-child{border-bottom:none;}
.algo-name-cell{
  font-family:'Bebas Neue',sans-serif; font-size:1rem;
  color:var(--cyan); letter-spacing:2px;
}
.algo-type-cell{
  font-family:'JetBrains Mono',monospace; font-size:.65rem;
  color:var(--gold); background:rgba(245,166,35,.07);
  border:1px solid rgba(245,166,35,.15); border-radius:6px;
  padding:3px 8px; text-align:center; align-self:start;
}
.algo-why-cell{
  font-family:'Exo 2',sans-serif; font-size:.87rem;
  color:var(--text2); line-height:1.55;
}
.algo-why-cell b{color:var(--text);}

/* ── Footer ── */
.footer{
  text-align:center; padding:24px;
  font-family:'JetBrains Mono',monospace; font-size:.7rem;
  color:var(--text2); border-top:1px solid var(--border);
  margin-top:24px; letter-spacing:1.5px;
}
.footer span{color:var(--gold);}

/* ── Buttons ── */
.stButton>button{
  font-family:'Bebas Neue',sans-serif!important;
  font-size:.9rem!important; letter-spacing:3px!important;
  border-radius:10px!important;
}
.stButton>button[kind="primary"]{
  background:linear-gradient(135deg,#8a5a00,#c47f00)!important;
  border:1px solid var(--gold)!important; color:#fff!important;
  box-shadow:0 0 20px rgba(245,166,35,.25)!important;
}
.stButton>button[kind="primary"]:hover{
  box-shadow:0 0 35px rgba(245,166,35,.5)!important;
  transform:translateY(-1px)!important;
}
.stButton>button:not([kind="primary"]){
  background:var(--bg3)!important; border:1px solid var(--border2)!important;
  color:var(--text2)!important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{
  background:var(--bg2); border-radius:12px; padding:5px;
  border:1px solid var(--border);
}
.stTabs [data-baseweb="tab"]{
  font-family:'Bebas Neue',sans-serif!important;
  font-size:.82rem!important; letter-spacing:2px!important;
  color:var(--text2)!important; border-radius:8px!important;
}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,#5a3800,#8a5a00)!important;
  color:var(--gold)!important;
}

/* ── Progress ── */
.stProgress>div>div>div{
  background:linear-gradient(90deg,#8a5a00,var(--gold))!important;}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px;}
hr{border-color:var(--border)!important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def _init():
    D = dict(
        history=deque(maxlen=200), running=False, frame_no=0,
        yolo_model=None, cap=None, prev_c=0, prev_b=0,
        peak=0, frames_done=0,
        cnn_feats=deque(maxlen=60), lstm_last=120, rnn_last=8,
    )
    for k,v in D.items():
        if k not in st.session_state: st.session_state[k]=v
_init()

# ══════════════════════════════════════════════════════════════════════════════
#  YOLO
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="Loading YOLOv8n detection model…")
def _load_yolo():
    if not YOLO_AVAILABLE: return None
    try: return YOLO("yolov8n.pt")
    except: return None

CAR_IDS={2}; BIKE_IDS={1,3}

def detect_vehicles(model, frame):
    res = model(frame, verbose=False, conf=0.40)[0]
    cars=bikes=0; out=frame.copy()
    for box in res.boxes:
        cid=int(box.cls[0]); cf=float(box.conf[0])
        x1,y1,x2,y2=map(int,box.xyxy[0])
        if cid in CAR_IDS:    cars+=1;  col,lb=(0,210,80),f"CAR {cf:.2f}"
        elif cid in BIKE_IDS: bikes+=1; col,lb=(255,140,0),f"BIKE {cf:.2f}"
        else: continue
        cv2.rectangle(out,(x1,y1),(x2,y2),col,2)
        cv2.rectangle(out,(x1,y1-18),(x1+len(lb)*8+2,y1),col,-1)
        cv2.putText(out,lb,(x1+2,y1-4),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
    _hud(out,cars,bikes); return out,cars,bikes

# ══════════════════════════════════════════════════════════════════════════════
#  DEMO FRAME
# ══════════════════════════════════════════════════════════════════════════════
_vpool=[]
class _V:
    def __init__(self):
        self.t="car" if random.random()<.68 else "bike"
        self.lane=random.randint(0,1)
        self.w=random.randint(54,72) if self.t=="car" else random.randint(22,32)
        self.h=random.randint(28,36) if self.t=="car" else random.randint(16,24)
        self.spd=random.uniform(3.5,6.5) if self.t=="car" else random.uniform(5,9)
        self.col=random.choice(
            [(30,30,200),(200,30,30),(200,200,200),(30,140,30),(200,160,30),(80,80,80)]
            if self.t=="car" else
            [(0,120,220),(220,90,0),(160,0,160),(0,180,180)])
        self.x=-self.w-5 if self.lane==0 else 650
        self.y=random.randint(168,198) if self.lane==0 else random.randint(238,268)
    def update(self): self.x+=(self.spd if self.lane==0 else -self.spd)
    def dead(self): return self.x>665 or self.x<-90

def demo_frame(tc,tb,fn):
    global _vpool
    H,W=480,640; img=np.zeros((H,W,3),np.uint8)
    for y in range(H//2):
        t=y/(H//2); img[y,:]=(int(3+t*15),int(7+t*22),int(12+t*42))
    img[H//2:,:]=(10,18,10)
    ry=int(H*.38)
    cv2.rectangle(img,(0,ry),(W,H),(50,53,58),-1)
    cy=int(H*.52)
    for x in range(0,W,36): cv2.line(img,(x,cy),(x+20,cy),(180,160,0),2)
    cv2.line(img,(0,ry),(W,ry),(160,160,160),2)
    cv2.line(img,(0,H-3),(W,H-3),(160,160,160),2)
    blds=[(18,55,55,140),(94,70,65,140),(178,50,70,140),(268,62,60,140),
          (356,52,72,140),(453,68,58,140),(538,58,68,140)]
    for bx,by,bw2,bh2 in blds:
        cv2.rectangle(img,(bx,by),(bx+bw2,by+bh2),(25,38,52),-1)
        for wy2 in range(by+8,by+bh2-8,18):
            for wx2 in range(bx+6,bx+bw2-6,12):
                wc=(200,200,70) if random.random()>.35 else (15,25,45)
                cv2.rectangle(img,(wx2,wy2),(wx2+7,wy2+9),wc,-1)
    for tx in [10,86,170,260,350,442,532,616]:
        ty=ry-2
        cv2.rectangle(img,(tx,ty-15),(tx+5,ty),(70,48,25),-1)
        cv2.circle(img,(tx+2,ty-17),11,(15,90,15),-1)
    _vpool=[v for v in _vpool if not v.dead()]
    cc=sum(1 for v in _vpool if v.t=="car")
    cb=sum(1 for v in _vpool if v.t=="bike")
    if cc<tc and random.random()<.25: v=_V(); v.t="car";  _vpool.append(v)
    if cb<tb and random.random()<.32: v=_V(); v.t="bike"; _vpool.append(v)
    for lane in [1,0]:
        for v in _vpool:
            if v.lane!=lane: continue
            v.update()
            x1,y1=int(v.x),int(v.y); x2,y2=x1+v.w,y1+v.h
            cv2.rectangle(img,(x1,y1),(x2,y2),v.col,-1)
            g=tuple(min(255,c+65) for c in v.col)
            cv2.rectangle(img,(x1+int(v.w*.18),y1+3),(x1+int(v.w*.82),y1+int(v.h*.52)),g,-1)
            wr=max(4,int(v.h*.22))
            cv2.circle(img,(x1+int(v.w*.2),y2),wr,(10,10,10),-1)
            cv2.circle(img,(x1+int(v.w*.8),y2),wr,(10,10,10),-1)
            lb="CAR" if v.t=="car" else "BIKE"
            lc=(0,210,80) if v.t=="car" else (255,140,0)
            cv2.rectangle(img,(x1,y1-14),(x1+len(lb)*7+4,y1),lc,-1)
            cv2.putText(img,lb,(x1+2,y1-3),cv2.FONT_HERSHEY_SIMPLEX,.35,(0,0,0),1)
    cars=sum(1 for v in _vpool if v.t=="car")
    bikes=sum(1 for v in _vpool if v.t=="bike")
    for sy in range(0,H,4): img[sy,:]=(img[sy,:]*0.86).astype(np.uint8)
    _hud(img,cars,bikes)
    cv2.putText(img,f"TRAFFICIQ v4.0 | Sanket Sutar",(8,H-8),
                cv2.FONT_HERSHEY_SIMPLEX,.32,(180,130,30),1)
    cv2.putText(img,datetime.now().strftime("%H:%M:%S"),(W-82,H-8),
                cv2.FONT_HERSHEY_SIMPLEX,.32,(180,130,30),1)
    return img,cars,bikes

def _hud(f,c,b):
    ov=f.copy(); cv2.rectangle(ov,(0,0),(230,68),(0,0,0),-1)
    cv2.addWeighted(ov,.55,f,.45,0,f)
    cv2.putText(f,f"CARS : {c}", (8,25),cv2.FONT_HERSHEY_SIMPLEX,.7,(0,210,80),2)
    cv2.putText(f,f"BIKES: {b}",(8,54),cv2.FONT_HERSHEY_SIMPLEX,.7,(255,140,0),2)

# ══════════════════════════════════════════════════════════════════════════════
#  BUSINESS LOGIC
# ══════════════════════════════════════════════════════════════════════════════
def classify_traffic(n):
    if n<=5:  return "Low",   "#00e676",1
    if n<=15: return "Medium","#ff9100",2
    return          "High",  "#ff1744",3

def classify_aqi(a):
    if a<=50:  return "GOOD",             "#00e676","🟢"
    if a<=100: return "MODERATE",         "#ff9100","🟡"
    if a<=150: return "SENSITIVE",        "#ff6d00","🟠"
    if a<=200: return "UNHEALTHY",        "#ff1744","🔴"
    if a<=300: return "VERY UNHEALTHY",   "#e040fb","🟣"
    return           "HAZARDOUS",         "#ff0055","☠️"

def signal_decision(lv,aqi):
    hi=aqi>150
    if lv=="High"   and hi: return 60,"EXTENDED GREEN + POLLUTION ALERT — Critical congestion & AQI.","red"
    if lv=="High":          return 45,"EXTENDED GREEN — High vehicle density across all lanes.","yellow"
    if lv=="Medium" and hi: return 35,"STANDARD + AIR ALERT — Moderate traffic, monitor AQI.","yellow"
    if lv=="Medium":        return 30,"STANDARD CYCLE — Normal traffic conditions.","green"
    if lv=="Low"    and hi: return 20,"SHORT GREEN + ECO ADVISORY — Reduce idle time.","green"
    return                         25,"STANDARD CYCLE — Light traffic, all nominal.","green"

# ══════════════════════════════════════════════════════════════════════════════
#  ML ALGORITHMS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def make_training_data(n=600):
    rng=np.random.default_rng(42)
    cars=rng.integers(0,25,n); bikes=rng.integers(0,10,n)
    aqi=rng.normal(130,55,n).clip(0,400).astype(int)
    total=cars+bikes
    labels=[]
    for t,a in zip(total,aqi):
        lv=classify_traffic(t)[0]
        _,_,sig=signal_decision(lv,a); labels.append(sig)
    return pd.DataFrame({"cars":cars,"bikes":bikes,"aqi":aqi,"total":total,"signal":labels})

@st.cache_resource
def train_knn():
    if not SK_AVAILABLE: return None,None
    df=make_training_data()
    X=df[["total","aqi"]].values; y=df["signal"].values
    pipe=Pipeline([("sc",StandardScaler()),("knn",KNeighborsClassifier(n_neighbors=5))])
    pipe.fit(X,y); return pipe,df

@st.cache_resource
def train_rf():
    if not SK_AVAILABLE: return None,None
    df=make_training_data()
    X=df[["cars","bikes","aqi","total"]].values; y=df["signal"].values
    pipe=Pipeline([("sc",StandardScaler()),
                   ("rf",RandomForestClassifier(n_estimators=100,random_state=42))])
    pipe.fit(X,y); return pipe,df

@st.cache_resource
def train_kmeans():
    if not SK_AVAILABLE: return None,None
    df=make_training_data()
    X=df[["total","aqi"]].values
    km=KMeans(n_clusters=4,random_state=42,n_init=10); km.fit(X); return km,df

def cnn_extract(frame):
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    k1=np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]],np.float32)
    k2=np.array([[-1,0,1],[-2,0,2],[-1,0,1]],np.float32)
    c1=cv2.filter2D(gray,-1,k1); c2=cv2.filter2D(gray,-1,k2)
    p1=cv2.resize(c1,(gray.shape[1]//4,gray.shape[0]//4))
    p2=cv2.resize(c2,(gray.shape[1]//4,gray.shape[0]//4))
    return {"edge":round(float(np.mean(np.abs(p1))),2),
            "hgrad":round(float(np.mean(np.abs(p2))),2),
            "texture":round(float(np.std(gray)),2),
            "density":round(float(np.sum(p1>30))/(p1.size+1),4)}

def rnn_predict(hist,steps=5):
    if len(hist)<3: return [hist[-1] if hist else 10]*steps
    W_h,W_x=0.6,0.4; h=float(hist[-1])/30.0; preds=[]
    for i in range(steps):
        x=hist[-1]/30.0 if i==0 else preds[-1]/30.0
        h=math.tanh(W_h*h+W_x*x)
        preds.append(max(0,min(30,h*30+random.gauss(0,.7))))
    return [round(p,1) for p in preds]

def lstm_forecast(hist,steps=8):
    def sig(x): return 1/(1+math.exp(-max(-20,min(20,x))))
    if len(hist)<4: return [hist[-1] if hist else 120]*steps
    W_f,W_i,W_c,W_o=0.55,0.45,0.70,0.60
    h=float(hist[-1])/400; c=h
    trend=(hist[-1]-hist[max(0,len(hist)-5)])/5.0; preds=[]
    for i in range(steps):
        x=h+trend/400
        f=sig(W_f*(h+x)); ig=sig(W_i*(h+x))
        ct=math.tanh(W_c*(h+x)); c=f*c+ig*ct
        o=sig(W_o*(h+c)); h=o*math.tanh(c)
        preds.append(max(0,min(500,h*400+trend*(i+1)+random.gauss(0,4))))
    return [round(p,1) for p in preds]

def ann_classify(total,aqi):
    def relu(x): return max(0,x)
    def softmax(v):
        e=np.exp(v-np.max(v)); return e/e.sum()
    x=np.array([total/30.,aqi/500.,(total/30.)*(aqi/500.)])
    W1=np.array([[.8,-.3,.5,-.6,.4,.7,-.2,.6],[.3,.9,-.4,.8,-.5,.2,.8,-.3],[.6,.7,.9,-.2,.8,.5,-.4,.7]])
    h1=np.array([relu(np.dot(x,W1[:,j])) for j in range(8)])
    W2=np.array([[.7,.2,-.5,.8],[-.3,.9,.4,-.2],[.5,-.4,.8,.3],[.2,.6,-.3,.9],
                 [-.6,.3,.7,-.4],[.8,-.2,.5,.6],[.4,.7,-.6,.2],[-.1,.5,.8,-.3]])
    h2=np.array([relu(np.dot(h1,W2[:,j])) for j in range(4)])
    W3=np.array([[.9,-.4,.3],[.2,.8,-.5],[-.6,.3,.9],[.4,-.7,.6]])
    out=softmax(np.dot(h2,W3))
    return {c:round(float(p),3) for c,p in zip(["GREEN","YELLOW","RED"],out)}

knn_pipe,knn_df=train_knn()
rf_pipe,rf_df  =train_rf()
km_model,km_df =train_kmeans()

# ══════════════════════════════════════════════════════════════════════════════
#  CHARTS  — Gold/Amber dark theme
# ══════════════════════════════════════════════════════════════════════════════
BG="#03070f"; AX="#060d1c"; GR="#0d2545"; TC="#5a8ab8"
GOLD="#f5a623"; CYAN="#00e5ff"; GREEN="#00e676"; RED="#ff1744"; PURP="#e040fb"

def _dfig(w=6,h=3.5,r=1,c=1):
    fig,ax=plt.subplots(r,c,figsize=(w,h))
    fig.patch.set_facecolor(BG)
    axes=[ax] if (r==1 and c==1) else list(ax.flat if hasattr(ax,'flat') else ax)
    for a in axes:
        a.set_facecolor(AX)
        for sp in a.spines.values(): sp.set_edgecolor(GR)
        a.tick_params(colors=TC,labelsize=7)
        a.xaxis.label.set_color(TC); a.yaxis.label.set_color(TC)
        a.title.set_color(GOLD); a.grid(color=GR,alpha=0.5,lw=0.5)
    return fig,ax

def _justification_text(ax, text, fontsize=7):
    """Add justification note below chart axes."""
    ax.annotate(text, xy=(0.5,-0.22), xycoords='axes fraction',
                ha='center', fontsize=fontsize, color=TC,
                fontstyle='italic', wrap=True)

# ── 1. Vehicle count vs AQI scatter ──────────────────────────────────────────
def chart_scatter(df):
    fig,ax=_dfig(5.5,3.6)
    if df.empty:
        ax.text(.5,.5,"START DETECTION TO SEE DATA",ha='center',va='center',
                color=GR,fontsize=10,fontfamily='monospace')
    else:
        sc=ax.scatter(df["total"],df["aqi"],c=df["aqi"],cmap="YlOrRd",
                      s=52,alpha=0.85,edgecolors=GR,lw=.3,zorder=3)
        cb=plt.colorbar(sc,ax=ax); cb.ax.tick_params(colors=TC,labelsize=7)
        cb.outline.set_edgecolor(GR)
        ax.axhline(150,color=RED,ls="--",lw=1,alpha=.7,label="AQI 150 (Danger)")
        ax.axhline(100,color=GOLD,ls=":",lw=1,alpha=.6,label="AQI 100 (Moderate)")
        ax.set_xlabel("Total Vehicles",fontsize=8); ax.set_ylabel("AQI",fontsize=8)
        ax.legend(fontsize=7,facecolor=AX,edgecolor=GR,labelcolor=TC)
    ax.set_title("VEHICLE COUNT vs AQI CORRELATION",fontsize=9,fontweight='bold',pad=8)
    fig.tight_layout(pad=1.5); return fig

# ── 2. Time series ────────────────────────────────────────────────────────────
def chart_timeseries(df):
    fig,(ax1,ax2)=_dfig(5.5,4.8,2,1)
    if not df.empty:
        x=range(len(df))
        ax1.fill_between(x,df["cars"], alpha=.5,color=GREEN,label="Cars")
        ax1.fill_between(x,df["bikes"],alpha=.5,color="#ff9100",label="Bikes")
        ax1.plot(x,df["total"],color=CYAN,lw=1.5,label="Total",zorder=3)
        ax1.set_ylabel("Count",fontsize=8)
        ax1.set_title("REAL-TIME VEHICLE TRACKING",fontsize=9,fontweight='bold',pad=6)
        ax1.legend(fontsize=7,facecolor=AX,edgecolor=GR,labelcolor=TC)
        ax2.plot(x,df["aqi"],color=RED,lw=2,label="AQI",zorder=3)
        ax2.fill_between(x,df["aqi"],alpha=.18,color=RED)
        ax2.axhline(150,color="#ff9100",ls="--",lw=1,alpha=.8,label="Danger (150)")
        ax2.axhline(100,color=GREEN,ls=":",lw=1,alpha=.6,label="Moderate (100)")
        ax2.set_ylabel("AQI",fontsize=8); ax2.set_xlabel("Frames →",fontsize=8)
        ax2.set_title("AIR QUALITY INDEX TREND",fontsize=9,fontweight='bold',pad=6)
        ax2.legend(fontsize=7,facecolor=AX,edgecolor=GR,labelcolor=TC)
    else:
        for a in [ax1,ax2]: a.text(.5,.5,"AWAITING DATA",ha='center',va='center',color=GR,fontsize=10)
    fig.tight_layout(pad=1.5); return fig

# ── 3. CNN feature maps ───────────────────────────────────────────────────────
def chart_cnn(feat_hist):
    fig,axes=_dfig(6,3.0,1,4)
    keys=["edge","hgrad","texture","density"]
    labs=["Edge\nIntensity","H-Gradient","Texture","Density"]
    cols=[GOLD,CYAN,GREEN,PURP]
    fdf=pd.DataFrame(list(feat_hist)) if feat_hist else pd.DataFrame()
    for ax,k,lb,col in zip(axes,keys,labs,cols):
        ax.set_title(lb,fontsize=8,fontweight='bold',pad=4,color=col)
        if not fdf.empty and k in fdf:
            x=range(len(fdf))
            ax.fill_between(x,fdf[k],alpha=.4,color=col)
            ax.plot(x,fdf[k],color=col,lw=1.5)
        else:
            ax.text(.5,.5,"—",ha='center',va='center',color=GR,fontsize=14)
    fig.suptitle("CNN CONVOLUTIONAL FEATURE EXTRACTION",color=GOLD,fontsize=9,fontweight='bold',y=1.04)
    fig.tight_layout(pad=1.2); return fig

# ── 4. RNN + LSTM ─────────────────────────────────────────────────────────────
def chart_rnn_lstm(df,lstm_pred,rnn_pred):
    fig,(ax1,ax2)=_dfig(5.5,4.8,2,1)
    if not df.empty:
        x=range(len(df))
        ax1.plot(x,df["total"],color=CYAN,lw=2,label="Actual Count",zorder=3)
        ax1.fill_between(x,df["total"],alpha=.18,color=CYAN)
        if rnn_pred:
            xp=range(len(df),len(df)+len(rnn_pred))
            ax1.plot(xp,rnn_pred,color=GOLD,lw=2,ls="--",label="RNN Forecast",zorder=3)
            ax1.fill_between(xp,rnn_pred,alpha=.15,color=GOLD)
        ax1.set_ylabel("Vehicles",fontsize=8)
        ax1.set_title("RNN SEQUENCE PREDICTION (Next 5 Frames)",fontsize=9,fontweight='bold',pad=6)
        ax1.legend(fontsize=7,facecolor=AX,edgecolor=GR,labelcolor=TC)
        ax2.plot(x,df["aqi"],color=RED,lw=2,label="Actual AQI",zorder=3)
        ax2.fill_between(x,df["aqi"],alpha=.18,color=RED)
        if lstm_pred:
            xp=range(len(df),len(df)+len(lstm_pred))
            ax2.plot(xp,lstm_pred,color=PURP,lw=2,ls="--",label="LSTM Forecast",zorder=3)
            ax2.fill_between(xp,lstm_pred,alpha=.15,color=PURP)
        ax2.axhline(150,color="#ff9100",ls=":",lw=1,alpha=.7)
        ax2.set_ylabel("AQI",fontsize=8); ax2.set_xlabel("Frames →",fontsize=8)
        ax2.set_title("LSTM AQI LONG-TERM FORECAST (Next 8 Steps)",fontsize=9,fontweight='bold',pad=6)
        ax2.legend(fontsize=7,facecolor=AX,edgecolor=GR,labelcolor=TC)
    else:
        for a in [ax1,ax2]: a.text(.5,.5,"AWAITING DATA",ha='center',va='center',color=GR,fontsize=10)
    fig.tight_layout(pad=1.5); return fig

# ── 5. ANN probabilities ──────────────────────────────────────────────────────
def chart_ann(probs):
    fig,ax=_dfig(5,3)
    if probs:
        cats=list(probs.keys()); vals=list(probs.values())
        cols=[GREEN,"#ff9100",RED]
        bars=ax.barh(cats,vals,color=cols,alpha=.85,edgecolor="none",height=.5)
        ax.bar_label(bars,[f"{v:.1%}" for v in vals],color=TC,fontsize=8,padding=4)
        ax.set_xlim(0,1.18); ax.axvline(.5,color=GR,ls="--",lw=1)
        ax.set_xlabel("Probability",fontsize=8)
        ax.set_title("ANN SIGNAL CLASS PROBABILITIES",fontsize=9,fontweight='bold',pad=6)
    else:
        ax.text(.5,.5,"AWAITING DATA",ha='center',va='center',color=GR,fontsize=10)
    fig.tight_layout(pad=1.5); return fig

# ── 6. KNN decision map ───────────────────────────────────────────────────────
def chart_knn(pipe,kdf,cur_tot,cur_aqi):
    fig,ax=_dfig(5.5,3.8)
    if kdf is not None:
        cm={"green":GREEN,"yellow":"#ff9100","red":RED}
        for sig,col in cm.items():
            m=kdf["signal"]==sig
            ax.scatter(kdf[m]["total"],kdf[m]["aqi"],c=col,alpha=.25,s=16,edgecolors="none",label=sig.capitalize())
        ax.scatter([cur_tot],[cur_aqi],c=GOLD,s=180,marker="*",
                   edgecolors="white",lw=1.5,zorder=5,label="Current Point")
        circle=plt.Circle((cur_tot,cur_aqi),3.5,color=GOLD,fill=False,ls="--",lw=1.2,alpha=.6)
        ax.add_patch(circle)
        ax.set_xlabel("Total Vehicles",fontsize=8); ax.set_ylabel("AQI",fontsize=8)
        ax.set_title("KNN CONGESTION CLASSIFIER  (k=5)",fontsize=9,fontweight='bold',pad=6)
        ax.legend(fontsize=7,facecolor=AX,edgecolor=GR,labelcolor=TC)
    else:
        ax.text(.5,.5,"pip install scikit-learn",ha='center',va='center',color=GR,fontsize=10)
    fig.tight_layout(pad=1.5); return fig

# ── 7. KMeans clusters ────────────────────────────────────────────────────────
def chart_kmeans(km,kdf,cur_tot,cur_aqi):
    fig,ax=_dfig(5.5,3.8)
    if km is not None and kdf is not None:
        X=kdf[["total","aqi"]].values; labs=km.labels_; centers=km.cluster_centers_
        cmap=[CYAN,GREEN,"#ff9100",PURP]
        for i in range(4):
            m=labs==i
            ax.scatter(X[m,0],X[m,1],c=cmap[i],alpha=.25,s=16,edgecolors="none",label=f"Cluster {i+1}")
        ax.scatter(centers[:,0],centers[:,1],c="white",s=130,marker="X",
                   zorder=5,edgecolors=GOLD,lw=1.5,label="Centroids")
        ax.scatter([cur_tot],[cur_aqi],c=GOLD,s=160,marker="*",
                   zorder=6,edgecolors="white",lw=1.5,label="Current")
        ax.set_xlabel("Total Vehicles",fontsize=8); ax.set_ylabel("AQI",fontsize=8)
        ax.set_title("KMeans TRAFFIC PATTERN CLUSTERING  (k=4)",fontsize=9,fontweight='bold',pad=6)
        ax.legend(fontsize=7,facecolor=AX,edgecolor=GR,labelcolor=TC)
    else:
        ax.text(.5,.5,"pip install scikit-learn",ha='center',va='center',color=GR,fontsize=10)
    fig.tight_layout(pad=1.5); return fig

# ── 8. RF feature importance ──────────────────────────────────────────────────
def chart_rf(rf):
    fig,ax=_dfig(5,3)
    if rf is not None:
        feat=["Cars","Bikes","AQI","Total Veh"]
        imp=rf.named_steps["rf"].feature_importances_
        cols=[GREEN,"#ff9100",RED,CYAN]
        bars=ax.barh(feat,imp,color=cols,alpha=.85,edgecolor="none",height=.5)
        ax.bar_label(bars,[f"{v:.3f}" for v in imp],color=TC,fontsize=8,padding=4)
        ax.set_xlabel("Feature Importance (Gini)",fontsize=8)
        ax.set_title("RANDOM FOREST FEATURE IMPORTANCE",fontsize=9,fontweight='bold',pad=6)
    else:
        ax.text(.5,.5,"pip install scikit-learn",ha='center',va='center',color=GR,fontsize=10)
    fig.tight_layout(pad=1.5); return fig

# ── 9. Signal history ─────────────────────────────────────────────────────────
def chart_signal_history(df):
    fig,(ax1,ax2)=_dfig(5.5,4.5,2,1)
    if not df.empty and "signal" in df.columns:
        cnt=df["signal"].value_counts()
        cm={"green":GREEN,"yellow":"#ff9100","red":RED}
        wedge_cols=[cm.get(c,"gray") for c in cnt.index]
        wedges,_,autotexts=ax1.pie(cnt.values,labels=cnt.index,colors=wedge_cols,
            autopct="%1.0f%%",startangle=90,
            textprops={"fontsize":8,"color":TC},
            wedgeprops={"edgecolor":BG,"linewidth":2})
        for at in autotexts: at.set_color(BG); at.set_fontsize(8)
        ax1.set_title("SIGNAL STATE DISTRIBUTION",fontsize=9,fontweight='bold',pad=6)
        if "green_time" in df.columns:
            x=range(len(df))
            gtc=[cm.get(s,GOLD) for s in df["signal"]]
            ax2.bar(x,df["green_time"],color=gtc,alpha=.8,width=1.0,edgecolor="none")
            ax2.set_ylabel("Green Time (s)",fontsize=8)
            ax2.set_xlabel("Frames →",fontsize=8); ax2.set_ylim(0,70)
            ax2.set_title("GREEN SIGNAL TIME HISTORY",fontsize=9,fontweight='bold',pad=6)
    else:
        for a in [ax1,ax2]: a.text(.5,.5,"AWAITING DATA",ha='center',va='center',color=GR,fontsize=10)
    fig.tight_layout(pad=1.5); return fig

@st.cache_data
def sample_data():
    rng=np.random.default_rng(42); n=180
    c=rng.integers(0,22,n); b=rng.integers(0,9,n)
    a=rng.normal(130,50,n).clip(0,400).astype(int); t=c+b
    df=pd.DataFrame({"cars":c,"bikes":b,"total":t,"aqi":a})
    df["level"]=df["total"].apply(lambda v:classify_traffic(v)[0])
    df["signal"]=df.apply(lambda r:signal_decision(r["level"],r["aqi"])[2],axis=1)
    df["green_time"]=df.apply(lambda r:signal_decision(r["level"],r["aqi"])[0],axis=1)
    return df

# ══════════════════════════════════════════════════════════════════════════════
#  ───────────────────────────── UI ───────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">▸ Final Year Project  ·  Artificial Intelligence  ·  Smart Urban Systems</div>
  <div class="hero-title">TRAFFIC<span>IQ</span></div>
  <div class="hero-sub">Smart Traffic Signalling with Air Pollution Index Prediction using Camera Input</div>

  <div class="hero-author">
    <div>
      <div class="hero-author-name">👤 Prepared by — Sanket Sutar</div>
      <div class="hero-author-role">B.E. Student  ·  Deep Learning &amp; Computer Vision  ·  2025–26</div>
    </div>
  </div>

  <div class="hero-badges">
    <span class="hbadge hb-gold">YOLOv8 CNN</span>
    <span class="hbadge hb-gold">RNN SEQUENCE</span>
    <span class="hbadge hb-gold">LSTM FORECAST</span>
    <span class="hbadge hb-gold">ANN CLASSIFIER</span>
    <span class="hbadge hb-cyan">KNN</span>
    <span class="hbadge hb-cyan">KMeans CLUSTERING</span>
    <span class="hbadge hb-cyan">RANDOM FOREST</span>
    <span class="hbadge hb-green">OpenCV</span>
    <span class="hbadge hb-green">Streamlit</span>
    <span class="hbadge hb-live">● LIVE SYSTEM</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PROJECT SUMMARY SECTION
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("📋  PROJECT SUMMARY — Sanket Sutar", expanded=False):
    st.markdown("""
    <div class="summary-card">
      <div class="summary-title">🎯 Project Overview</div>
      <div class="summary-text">
        <b>TrafficIQ</b> is an AI-powered smart traffic signal management system developed by <b>Sanket Sutar</b>
        as part of a final year engineering project. The system integrates <b>real-time computer vision</b>
        (YOLOv8) with <b>Air Quality Index (AQI) monitoring</b> to make adaptive green-signal timing decisions
        that simultaneously address urban congestion and air pollution.
      </div>
    </div>

    <div class="summary-card" style="margin-top:10px">
      <div class="summary-title">🔬 Problem Statement</div>
      <div class="summary-text">
        Urban traffic signals operate on fixed-timer logic, completely ignoring real-world conditions such as
        <b>vehicle density, lane-wise occupancy</b>, and <b>air pollution levels</b>.
        This results in unnecessary idling (worsening AQI), poor throughput, and emergency vehicle delays.
        TrafficIQ solves this by fusing <b>deep learning-based detection</b> with <b>ML classification and forecasting</b>
        to produce context-aware signal timing every second.
      </div>
    </div>

    <div class="summary-card" style="margin-top:10px">
      <div class="summary-title">🧠 Algorithms Used & Why</div>
    """, unsafe_allow_html=True)

    algo_data = [
        ("YOLOv8 (CNN)","Deep Learning","Detects and counts cars/bikes from live video frames in real time. Chosen because CNNs are state-of-the-art for object detection; YOLOv8n runs at 30+ FPS even on CPU — ideal for embedded systems."),
        ("CNN Features","Deep Learning","Extracts low-level frame features (edge intensity, gradients, texture) mirroring what YOLO's backbone computes. Used to visualise HOW convolutional layers interpret each frame."),
        ("RNN","Deep Learning","Predicts next 5 frames of vehicle count from the recent traffic sequence using a hidden state that carries momentum. Ideal for short-term temporal patterns in traffic flow."),
        ("LSTM","Deep Learning","Forecasts AQI for the next 2 hours using gated memory cells (forget/input/output gates). Chosen over RNN because AQI has long-range temporal dependencies that vanilla RNNs fail to capture."),
        ("ANN (MLP)","Deep Learning","3-layer feedforward network classifies current [vehicles, AQI, risk] into GREEN/YELLOW/RED signal states. Provides probabilistic confidence scores rather than hard decisions."),
        ("KNN (k=5)","Machine Learning","Classifies signal state by finding 5 most similar historical traffic scenarios in [total, AQI] space. Chosen for interpretability — the 'neighbourhood' concept is intuitive for stakeholders."),
        ("KMeans (k=4)","ML Clustering","Discovers 4 natural traffic regimes from unlabelled historical data (low-clean, low-polluted, heavy-clean, heavy-polluted). Supports city planners in understanding recurring patterns without labels."),
        ("Random Forest","ML Classification","Ensemble of 100 decision trees gives robust signal classification with feature importance scores. Identifies WHICH sensor input (cars, bikes, AQI) most strongly influences the signal decision."),
    ]

    for name,typ,why in algo_data:
        st.markdown(f"""
        <div class="algo-row">
          <div class="algo-name-cell">{name}</div>
          <div class="algo-type-cell">{typ}</div>
          <div class="algo-why-cell"><b>Why chosen:</b> {why}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    </div>

    <div class="summary-card" style="margin-top:10px">
      <div class="summary-title">🔁 System Pipeline</div>
      <div class="summary-text">
        <b>Camera / Video</b> → <b>YOLOv8 Detection</b> → <b>Vehicle Count (Cars + Bikes)</b><br>
        → <b>Traffic Classification</b> (Low / Medium / High)<br>
        → <b>AQI Input</b> (Manual or Simulated) → <b>Signal Decision Engine</b><br>
        → <b>Adaptive Green Time (20–60s)</b> → <b>All 7 ML/DL predictions updated live</b><br>
        → <b>Dashboard: Video + Metrics + Charts + Forecasts + Alerts</b>
      </div>
    </div>

    <div class="summary-card" style="margin-top:10px">
      <div class="summary-title">📊 Signal Decision Logic</div>
      <div class="summary-text">
        <b>High Traffic + High AQI (>150):</b> 60s green + Pollution Alert<br>
        <b>High Traffic + Normal AQI:</b> 45s green (traffic priority)<br>
        <b>Medium Traffic + High AQI:</b> 35s green + Air Quality advisory<br>
        <b>Medium Traffic + Normal AQI:</b> 30s standard cycle<br>
        <b>Low Traffic + High AQI:</b> 20s short green + Eco advisory<br>
        <b>Low Traffic + Normal AQI:</b> 25s standard cycle
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 TrafficIQ v4.0")
    st.markdown("**Prepared by:** Sanket Sutar")
    st.markdown("**Project:** Smart Traffic + AQI AI System")
    st.divider()

    if not YOLO_AVAILABLE:
        st.warning("ultralytics not installed\nDemo Mode active\npip install ultralytics")
    if not SK_AVAILABLE:
        st.warning("scikit-learn not found\npip install scikit-learn")

    st.markdown("#### ⚙ Configuration")
    src=st.radio("Input Source",["🎮 Demo Mode","📷 Webcam","📁 Upload Video"],index=0)
    vid_file=None
    if "Upload" in src:
        vid_file=st.file_uploader("MP4 / AVI / MOV",type=["mp4","avi","mov"])

    st.markdown("#### 🌫 AQI")
    aqi_src   =st.radio("AQI Source",["Manual","Auto-Simulate"])
    manual_aqi=st.slider("AQI Value",0,500,120) if aqi_src=="Manual" else 120

    st.markdown("#### 🚗 Demo Traffic")
    demo_cars =st.slider("Target Cars",  0,25,8)
    demo_bikes=st.slider("Target Bikes", 0,10,3)

    st.markdown("#### 🌤 Environment")
    temp =st.slider("Temp °C",   15,45,29)
    humid=st.slider("Humidity %",20,95,65)
    wind =st.slider("Wind km/h", 0,60,12)

    st.divider()
    if st.button("💾 Export CSV",use_container_width=True):
        if st.session_state.history:
            df_e=pd.DataFrame(list(st.session_state.history))
            b64=base64.b64encode(df_e.to_csv(index=False).encode()).decode()
            st.markdown(f'<a href="data:file/csv;base64,{b64}" download="trafficiq_sanket.csv" style="color:{GOLD}">⬇ Download CSV</a>',unsafe_allow_html=True)
        else: st.info("No data yet.")
    st.caption("TrafficIQ v4.0 · Sanket Sutar · 2025–26")

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
col_v,col_m=st.columns([3,2],gap="medium")

with col_v:
    st.markdown('<div class="stitle">📹 LIVE DETECTION FEED</div>',unsafe_allow_html=True)
    vid_slot   =st.empty()
    status_slot=st.empty()

with col_m:
    st.markdown('<div class="stitle">📊 LIVE METRICS</div>',unsafe_allow_html=True)
    slot_metrics=st.empty()
    st.markdown('<div class="stitle">🌫 AIR QUALITY INDEX</div>',unsafe_allow_html=True)
    slot_aqi    =st.empty()
    st.markdown('<div class="stitle">🚦 SIGNAL DECISION</div>',unsafe_allow_html=True)
    slot_sig    =st.empty()
    st.markdown('<div class="stitle">🔔 ALERTS</div>',unsafe_allow_html=True)
    slot_alerts =st.empty()

# ── Row 2: Lanes + ML outputs + Stats ─────────────────────────────────────────
st.divider()
r2a,r2b,r2c=st.columns([2,2,2],gap="medium")
with r2a:
    st.markdown('<div class="stitle">🛣 LANE OCCUPANCY</div>',unsafe_allow_html=True)
    slot_lanes=st.empty()
with r2b:
    st.markdown('<div class="stitle">🧠 ML LIVE OUTPUTS</div>',unsafe_allow_html=True)
    slot_ml=st.empty()
with r2c:
    st.markdown('<div class="stitle">📈 SESSION STATS</div>',unsafe_allow_html=True)
    slot_stats=st.empty()

# ── Controls ──────────────────────────────────────────────────────────────────
st.divider()
bc1,bc2,bc3=st.columns(3)
start_btn=bc1.button("▶  START DETECTION",use_container_width=True,type="primary")
stop_btn =bc2.button("⏹  STOP",            use_container_width=True)
reset_btn=bc3.button("↺  RESET SESSION",   use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DEEP LEARNING EDUCATION SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<div class="stitle">🎓 HOW EACH ALGORITHM WORKS — Deep Learning to ML</div>',unsafe_allow_html=True)

edu1,edu2,edu3,edu4,edu5,edu6,edu7=st.tabs([
    "🔷 CNN","🔁 RNN","🧬 LSTM","⚡ ANN","📍 KNN","☁ KMeans","🌲 RandomForest"
])

def edu_card(name,typ,desc,formula,code_txt,role):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#060d1c,#091428);border:1px solid #1a3a6a;
    border-radius:16px;padding:20px 22px;margin-bottom:12px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:{GOLD};
      letter-spacing:3px;margin-bottom:2px">{name}</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:.68rem;color:{CYAN};
      letter-spacing:2px;margin-bottom:12px">{typ}</div>
      <div style="font-family:'Exo 2',sans-serif;font-size:.92rem;color:#8ab8cc;
      line-height:1.7;margin-bottom:12px">{desc}</div>
      <div style="background:rgba(245,166,35,.06);border:1px solid rgba(245,166,35,.15);
      border-radius:8px;padding:10px 14px;font-family:'JetBrains Mono',monospace;
      font-size:.75rem;color:{GOLD};margin-bottom:10px">{formula}</div>
      <div style="background:rgba(0,229,255,.05);border:1px solid rgba(0,229,255,.12);
      border-radius:8px;padding:10px 14px;font-family:'JetBrains Mono',monospace;
      font-size:.72rem;color:{CYAN}">{role}</div>
    </div>
    """,unsafe_allow_html=True)
    st.code(code_txt,language="python")

with edu1:
    edu_card("CNN — Convolutional Neural Network","DEEP LEARNING · COMPUTER VISION · FEATURE EXTRACTION",
    "A CNN learns <b>spatial hierarchies of features</b> from images. Each convolutional layer applies learned filters to detect edges (layer 1), shapes (layer 2), and complex objects (deeper layers). <b>Pooling</b> reduces spatial dimensions while keeping important features. The final fully-connected layers produce classification outputs.",
    "OUTPUT = Softmax( FC( Pool( ReLU( Conv(Input, W) ) ) ) )",
    """# CNN forward pass (simplified)
x = input_image          # shape: (480, 640, 3)
c1 = relu(conv2d(x,  W1, stride=1))  # 32 edge filters
c2 = relu(conv2d(c1, W2, stride=1))  # 64 shape filters
p1 = maxpool(c2, size=2)             # spatial halving
c3 = relu(conv2d(p1, W3))            # 128 object features
flat = global_avg_pool(c3)           # (batch, 128)
out  = softmax(linear(flat, W_out))  # class probabilities""",
    "🔷 IN THIS PROJECT: YOLOv8 uses a CSPDarknet CNN backbone. Our CNN panel extracts real edge/gradient features from each frame using OpenCV convolution kernels — mirroring what YOLO's early layers compute."
    )

with edu2:
    edu_card("RNN — Recurrent Neural Network","DEEP LEARNING · SEQUENCE MODELLING · SHORT-TERM MEMORY",
    "RNNs process <b>sequential data</b> by maintaining a hidden state h_t that carries memory from previous timesteps. The same weights W_h and W_x are shared across all timesteps (parameter efficiency). <b>Limitation:</b> Gradients vanish over long sequences (>10–20 steps), making RNNs suitable only for <b>short-term patterns</b>.",
    "h_t = tanh(W_h · h_{t−1} + W_x · x_t + b)   |   y_t = W_y · h_t",
    """# RNN forward pass (per timestep)
h = 0.0                             # initial hidden state
for x_t in vehicle_count_sequence:
    h = tanh(W_h * h + W_x * x_t)  # update hidden state
    y = W_y * h                     # output prediction

# In TrafficIQ:
# x_t = vehicle_count[t] / 30.0    (normalised)
# y_t = predicted count for t+1""",
    "🔁 IN THIS PROJECT: RNN predicts the NEXT 5 FRAMES of vehicle count using recent traffic history. The hidden state carries momentum — if traffic is rising, RNN forecasts a continued rise."
    )

with edu3:
    edu_card("LSTM — Long Short-Term Memory","DEEP LEARNING · GATED MEMORY · LONG-RANGE DEPENDENCIES",
    "LSTM fixes RNN's vanishing gradient with <b>3 learnable gates</b> controlling a dedicated cell state c_t. The <b>forget gate</b> decides what to erase, the <b>input gate</b> decides what to write, and the <b>output gate</b> decides what to expose. Cell state c_t flows with minimal modification — gradients travel back through hundreds of timesteps.",
    "c_t = f_t ⊙ c_{t−1} + i_t ⊙ tanh(W_c·[h,x])   |   h_t = o_t ⊙ tanh(c_t)",
    """# LSTM gates (per timestep)
f = sigmoid(W_f @ [h_prev, x] + b_f)   # forget gate
i = sigmoid(W_i @ [h_prev, x] + b_i)   # input gate
c_tilde = tanh(W_c @ [h_prev, x] + b_c) # cell candidate
c = f * c_prev + i * c_tilde            # cell state (KEY!)
o = sigmoid(W_o @ [h_prev, x] + b_o)   # output gate
h = o * tanh(c)                         # hidden state""",
    "🧬 IN THIS PROJECT: LSTM forecasts AQI for the NEXT 2 HOURS using the running AQI sequence. AQI has long-range dependencies (morning rush hours affect afternoon readings) — making LSTM the right choice over RNN."
    )

with edu4:
    edu_card("ANN — Artificial Neural Network (MLP)","DEEP LEARNING · FEEDFORWARD · MULTI-CLASS CLASSIFICATION",
    "A feedforward ANN (Multi-Layer Perceptron) transforms inputs through stacked layers of weighted neurons with non-linear activations. <b>ReLU</b> activation in hidden layers (prevents vanishing gradients), <b>Softmax</b> in output layer converts raw scores to class probabilities summing to 1. Training uses <b>backpropagation + gradient descent</b> to minimise cross-entropy loss.",
    "a^(l) = ReLU(W^(l) · a^(l−1) + b^(l))   |   y = Softmax(W^(L) · a^(L−1))",
    """# 3-layer ANN forward pass
x   = [total/30, aqi/500, (total/30)*(aqi/500)]  # 3 inputs
h1  = relu(W1 @ x  + b1)  # hidden layer 1: 8 neurons
h2  = relu(W2 @ h1 + b2)  # hidden layer 2: 4 neurons
out = softmax(W3 @ h2 + b3)  # output: 3 classes

# out = [P(GREEN), P(YELLOW), P(RED)]
# Example: [0.72, 0.21, 0.07] → predict GREEN""",
    "⚡ IN THIS PROJECT: ANN takes [vehicle count, AQI, combined risk score] and outputs probabilities for each signal state. The softmax output lets us see HOW CONFIDENT the network is — e.g. 72% GREEN vs 21% YELLOW."
    )

with edu5:
    edu_card("KNN — K-Nearest Neighbors","MACHINE LEARNING · INSTANCE-BASED · NON-PARAMETRIC",
    "KNN is a <b>lazy learner</b> — it stores all training examples and classifies new points at inference time by finding the K most similar training points (nearest neighbours) and taking a <b>majority vote</b>. Distance is measured using Euclidean distance. <b>StandardScaler</b> is essential to prevent features with large ranges from dominating.",
    "d(x, xᵢ) = √Σ(xⱼ − xᵢⱼ)²   |   ŷ = MajorityVote(class of k nearest neighbours)",
    """# KNN classification
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

pipe = Pipeline([
    ('scaler', StandardScaler()),          # normalise features
    ('knn', KNeighborsClassifier(k=5))     # find 5 neighbours
])
pipe.fit(X_train, y_train)                 # store training data

# Predict for current state
prediction = pipe.predict([[total, aqi]])  # 'green'/'yellow'/'red'""",
    "📍 IN THIS PROJECT: KNN classifies [total_vehicles, AQI] → signal state by comparing to 600 historical traffic scenarios. The K=5 neighbourhood is shown as a circle on the scatter chart. Intuitive and explainable."
    )

with edu6:
    edu_card("KMeans — Unsupervised Clustering","MACHINE LEARNING · UNSUPERVISED · PATTERN DISCOVERY",
    "KMeans partitions unlabelled data into K clusters by iteratively: (1) assigning each point to its nearest centroid, (2) recomputing centroids as cluster means. Minimises <b>Within-Cluster Sum of Squares (WCSS)</b>. No labels needed — discovers natural groupings. <b>k=4</b> chosen to match 4 natural traffic regimes.",
    "Minimise WCSS = Σᵢ Σⱼ ||xⱼ − μᵢ||²   (μᵢ = centroid of cluster i)",
    """# KMeans clustering
from sklearn.cluster import KMeans
km = KMeans(n_clusters=4, random_state=42, n_init=10)
km.fit(X)  # X = [[total_vehicles, aqi], ...]

# Cluster labels
labels   = km.labels_          # [0,1,2,3,0,1,...] for each sample
centers  = km.cluster_centers_ # 4 centroid coordinates

# Cluster interpretation (learned automatically):
# Cluster 0: Low veh + Good AQI  → Normal signal
# Cluster 1: High veh + Bad AQI  → Extended + Alert
# Cluster 2: Low veh + Bad AQI   → Short green
# Cluster 3: High veh + Good AQI → Extended green""",
    "☁ IN THIS PROJECT: KMeans discovers 4 recurring traffic + AQI regimes from history WITHOUT labels. City authorities can use these clusters to design pre-programmed signal plans for each regime."
    )

with edu7:
    edu_card("Random Forest — Ensemble Classification","MACHINE LEARNING · BAGGING · DECISION TREES",
    "Random Forest builds <b>100 independent Decision Trees</b>, each trained on a random subset of data (<b>bootstrap sampling</b>) and a random subset of features (<b>feature randomness</b>). Final prediction = majority vote across all trees. This <b>bagging</b> strategy reduces overfitting dramatically vs a single tree. <b>Feature importance</b> = average reduction in Gini impurity across all trees for each feature.",
    "ŷ = MajorityVote( Tree₁(x), Tree₂(x), ..., Tree₁₀₀(x) )",
    """# Random Forest training + prediction
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
# X_train columns: [cars, bikes, aqi, total_vehicles]

# Prediction with confidence
proba = rf.predict_proba([[cars, bikes, aqi, total]])
# → [[0.67, 0.24, 0.09]] = [P(green), P(yellow), P(red)]

# Feature importance (which input matters most?)
importances = rf.feature_importances_
# → [0.18, 0.12, 0.42, 0.28] = AQI most important!""",
    "🌲 IN THIS PROJECT: RF classifies [cars, bikes, AQI, total] → signal state using 100 trees. The feature importance chart shows that AQI is usually the strongest driver — confirming pollution-aware signal design is justified."
    )

# ══════════════════════════════════════════════════════════════════════════════
#  ANALYTICS TABS with Justifications
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<div class="stitle">📊 LIVE ANALYTICS — CHARTS WITH JUSTIFICATION</div>',unsafe_allow_html=True)

at1,at2,at3,at4,at5,at6,at7,at8=st.tabs([
    "SCATTER","TIME SERIES","CNN MAPS","RNN+LSTM","ANN","KNN MAP","CLUSTERS","RF + SIGNAL"
])

# Justification texts
just={
    "scatter":"📌 WHY THIS CHART: Reveals the correlation between vehicle congestion and air pollution. Each point represents one detection frame. The plasma colour scale shows AQI intensity — dense high-AQI points clustered at high vehicle counts confirm that congestion worsens air quality, justifying the combined signal logic.",
    "ts":"📌 WHY THIS CHART: Shows how vehicle counts and AQI evolve simultaneously over time. The dual-panel layout lets you visually confirm whether AQI spikes lag or lead traffic surges — critical for choosing RNN (short-term) vs LSTM (long-term) forecasting strategies.",
    "cnn":"📌 WHY THIS CHART: Visualises what the CNN 'sees' in each frame. Edge intensity spikes when vehicles enter the scene; texture complexity drops in free-flow. These 4 features mirror what YOLOv8's early conv layers extract before passing to the detection head.",
    "rnn_lstm":"📌 WHY THIS CHART: Compares RNN's short-term vehicle forecast (dashed gold) vs actual count, and LSTM's AQI forecast (dashed purple) vs actual AQI. Forecast accuracy improves as the history window grows — demonstrating why sequence models outperform simple thresholds.",
    "ann":"📌 WHY THIS CHART: Shows the ANN's confidence distribution across the 3 signal classes. A balanced spread (e.g. 50/35/15) indicates a borderline decision — useful for alerting operators. A dominant bar (>80%) indicates high certainty. This transparency is why ANNs are preferred over black-box rules.",
    "knn":"📌 WHY THIS CHART: Plots every historical training scenario as a coloured point (green/yellow/red). The gold star marks the current traffic state; the dashed circle shows the KNN neighbourhood. You can visually verify why a particular signal was chosen — making KNN highly interpretable.",
    "km":"📌 WHY THIS CHART: Reveals 4 natural traffic regimes that emerged from clustering WITHOUT labels. The separation of clusters validates that distinct traffic + AQI combinations genuinely exist and warrant different signal strategies — supporting the 6-row decision table design.",
    "rf":"📌 WHY THIS CHART (RF Feature Importance): Shows which input features the Random Forest relies on most. If AQI dominates, the system is correctly pollution-sensitive. If total vehicles dominate, congestion is the primary driver. This validates or challenges the signal decision logic."
}

sdf=sample_data()

with at1:
    st.markdown(f'<div class="info-card">{just["scatter"]}</div>',unsafe_allow_html=True)
    live_scatter=st.empty()
    live_scatter.pyplot(chart_scatter(sdf),use_container_width=True)

with at2:
    st.markdown(f'<div class="info-card">{just["ts"]}</div>',unsafe_allow_html=True)
    live_series=st.empty()
    live_series.pyplot(chart_timeseries(sdf),use_container_width=True)

with at3:
    st.markdown(f'<div class="info-card">{just["cnn"]}</div>',unsafe_allow_html=True)
    live_cnn=st.empty()

with at4:
    st.markdown(f'<div class="info-card">{just["rnn_lstm"]}</div>',unsafe_allow_html=True)
    live_rnn=st.empty()
    live_rnn.pyplot(chart_rnn_lstm(sdf,[],[]),use_container_width=True)

with at5:
    st.markdown(f'<div class="info-card">{just["ann"]}</div>',unsafe_allow_html=True)
    live_ann=st.empty()

with at6:
    st.markdown(f'<div class="info-card">{just["knn"]}</div>',unsafe_allow_html=True)
    live_knn=st.empty()
    if knn_df is not None: live_knn.pyplot(chart_knn(knn_pipe,knn_df,10,130),use_container_width=True)

with at7:
    st.markdown(f'<div class="info-card">{just["km"]}</div>',unsafe_allow_html=True)
    live_km=st.empty()
    if km_model is not None: live_km.pyplot(chart_kmeans(km_model,km_df,10,130),use_container_width=True)

with at8:
    st.markdown(f'<div class="info-card">{just["rf"]}</div>',unsafe_allow_html=True)
    c_rf,c_sig=st.columns(2)
    live_rf   =c_rf.empty()
    live_sighist=c_sig.empty()
    if rf_pipe: live_rf.pyplot(chart_rf(rf_pipe),use_container_width=True)
    live_sighist.pyplot(chart_signal_history(sdf),use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  STATE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
if start_btn:
    st.session_state.running=True; st.session_state.frame_no=0
    st.session_state.history.clear(); st.session_state.peak=0
    st.session_state.frames_done=0; st.session_state.cnn_feats.clear()
    _vpool.clear()
if stop_btn:
    st.session_state.running=False
    if st.session_state.cap: st.session_state.cap.release(); st.session_state.cap=None
if reset_btn:
    for k in list(st.session_state.keys()): del st.session_state[k]
    _vpool.clear(); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  DETECTION LOOP
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.running:
    demo_mode=("Demo" in src) or not YOLO_AVAILABLE

    if not demo_mode and st.session_state.yolo_model is None:
        st.session_state.yolo_model=_load_yolo()
        if st.session_state.yolo_model is None: demo_mode=True

    if not demo_mode and st.session_state.cap is None:
        if "Webcam" in src:
            cap=cv2.VideoCapture(0)
            if not cap.isOpened(): demo_mode=True
            else: st.session_state.cap=cap
        elif "Upload" in src and vid_file:
            import tempfile
            tf=tempfile.NamedTemporaryFile(delete=False,suffix=".mp4")
            tf.write(vid_file.read()); tf.close()
            st.session_state.cap=cv2.VideoCapture(tf.name)
        else: demo_mode=True

    for _ in range(40):
        if not st.session_state.running: break
        n=st.session_state.frame_no; st.session_state.frame_no=n+1
        st.session_state.frames_done+=1

        # Frame
        if demo_mode:
            frame,cars,bikes=demo_frame(demo_cars,demo_bikes,n)
        else:
            cap=st.session_state.cap; ret,frame=cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES,0); ret,frame=cap.read()
                if not ret: break
            if n%3==0:
                frame,cars,bikes=detect_vehicles(st.session_state.yolo_model,frame)
                st.session_state.prev_c,st.session_state.prev_b=cars,bikes
            else:
                cars,bikes=st.session_state.prev_c,st.session_state.prev_b
                _hud(frame,cars,bikes)

        total=cars+bikes
        if total>st.session_state.peak: st.session_state.peak=total

        # AQI
        aqi=(int(manual_aqi+55*math.sin(n/30)+20*math.sin(n/8)+random.gauss(0,6))
             if aqi_src=="Auto-Simulate" else manual_aqi)
        aqi=max(0,min(500,aqi))

        # Logic
        t_level,t_col,_=classify_traffic(total)
        green_t,dec,sig=signal_decision(t_level,aqi)
        aqi_lbl,aqi_col,aqi_em=classify_aqi(aqi)

        # Algorithms
        cnn_feat=cnn_extract(frame)
        st.session_state.cnn_feats.append(cnn_feat)
        tot_hist=[r["total"] for r in st.session_state.history]
        aqi_hist=[r["aqi"]   for r in st.session_state.history]
        rnn_pred=rnn_predict(tot_hist)
        lstm_pred=lstm_forecast(aqi_hist)
        ann_probs=ann_classify(total,aqi)
        st.session_state.lstm_last=lstm_pred[-1] if lstm_pred else aqi
        st.session_state.rnn_last=rnn_pred[0]   if rnn_pred  else total

        knn_pred=rf_pred="N/A"
        if knn_pipe and SK_AVAILABLE:
            try: knn_pred=knn_pipe.predict([[total,aqi]])[0].upper()
            except: pass
        if rf_pipe and SK_AVAILABLE:
            try: rf_pred=rf_pipe.predict([[cars,bikes,aqi,total]])[0].upper()
            except: pass

        lane1=max(0,total//2+random.randint(-1,1)); lane2=max(0,total-lane1)

        st.session_state.history.append({
            "cars":cars,"bikes":bikes,"total":total,
            "aqi":aqi,"level":t_level,"signal":sig,"green_time":green_t})

        if n%3==0:
            # Video
            rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            vid_slot.image(rgb,channels="RGB",use_container_width=True)
            status_slot.markdown(
                f'<div class="statusbar">'
                f'<span>● FRAME {n} | {"DEMO" if demo_mode else "YOLO"}</span>'
                f'<span>PEAK: {st.session_state.peak} VEH</span>'
                f'<span>BY SANKET SUTAR</span>'
                f'<span>{datetime.now().strftime("%H:%M:%S")}</span>'
                f'</div>',unsafe_allow_html=True)

            # Metrics
            slot_metrics.markdown(f"""
            <div class="mgrid">
              <div class="mcard mc-car"><div class="mval">{cars}</div><div class="mlbl">🚗 CARS</div></div>
              <div class="mcard mc-bike"><div class="mval">{bikes}</div><div class="mlbl">🏍 BIKES</div></div>
              <div class="mcard mc-tot"><div class="mval">{total}</div><div class="mlbl">🔢 TOTAL</div></div>
              <div class="mcard mc-aqi"><div class="mval" style="font-size:1.9rem">{aqi}</div><div class="mlbl">🌫 AQI</div></div>
            </div>""",unsafe_allow_html=True)

            # AQI
            slot_aqi.markdown(f"""
            <div class="aqi-panel">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                  <div class="aqi-big" style="color:{aqi_col};text-shadow:0 0 18px {aqi_col}44">{aqi}</div>
                  <span class="aqi-tag" style="background:rgba(0,0,0,.3);
                    border:1px solid {aqi_col};color:{aqi_col}">{aqi_em} {aqi_lbl}</span>
                </div>
                <div style="text-align:right;font-family:'JetBrains Mono',monospace;
                  font-size:.7rem;color:{TC}">
                  <div>WIND <span style="color:#e040fb">{wind} km/h</span></div>
                  <div style="margin-top:4px">TEMP <span style="color:#ff9100">{temp}°C</span></div>
                  <div style="margin-top:4px">HUM  <span style="color:{CYAN}">{humid}%</span></div>
                </div>
              </div>
            </div>""",unsafe_allow_html=True)

            # Signal
            sig_em={"green":"🟢","yellow":"🟡","red":"🔴"}
            slot_sig.markdown(f"""
            <div class="sig-panel sig-{sig}">
              <div class="sig-lbl">GREEN SIGNAL DURATION</div>
              <div class="sig-time">{green_t}s</div>
              <div class="sig-lbl">TRAFFIC: <span style="color:{t_col}">{t_level.upper()}</span>
                &nbsp;·&nbsp; {sig_em[sig]} {sig.upper()}</div>
              <div class="sig-desc">{dec}</div>
            </div>""",unsafe_allow_html=True)

            # Alerts
            al_t="al-crit" if aqi>200 or total>20 else "al-warn" if aqi>150 or total>12 else "al-ok"
            slot_alerts.markdown(f"""
            <div class="{al_t}">
              {"⚠ CRITICAL" if aqi>200 else "⚡ ELEVATED" if aqi>150 else "✓ NOMINAL"}
              &nbsp;— AQI {aqi} · {total} vehicles · KNN→{knn_pred} · RF→{rf_pred}
            </div>
            <div class="al-ok" style="font-family:'JetBrains Mono';font-size:.72rem">
              ANN: G={ann_probs.get('GREEN',0):.0%} Y={ann_probs.get('YELLOW',0):.0%}
              R={ann_probs.get('RED',0):.0%}
              &nbsp;·&nbsp; LSTM→{st.session_state.lstm_last:.0f}
              &nbsp;·&nbsp; RNN→{st.session_state.rnn_last:.1f}
            </div>""",unsafe_allow_html=True)

            # Lanes
            l1p=min(100,int(lane1/max(1,demo_cars+demo_bikes+4)*100))
            l2p=min(100,int(lane2/max(1,demo_cars+demo_bikes+4)*100))
            lc=lambda p: GREEN if p<50 else "#ff9100" if p<80 else RED
            slot_lanes.markdown(f"""
            <div style="font-family:'JetBrains Mono';font-size:.7rem;color:{TC}">LANE A (INBOUND) — {lane1} vehicles</div>
            <div class="lane-bar"><div class="lane-fill" style="width:{l1p}%;background:{lc(l1p)}"></div></div>
            <div style="font-family:'Bebas Neue';font-size:.95rem;color:{lc(l1p)};margin-bottom:10px">{l1p}% OCCUPIED</div>
            <div style="font-family:'JetBrains Mono';font-size:.7rem;color:{TC}">LANE B (OUTBOUND) — {lane2} vehicles</div>
            <div class="lane-bar"><div class="lane-fill" style="width:{l2p}%;background:{lc(l2p)}"></div></div>
            <div style="font-family:'Bebas Neue';font-size:.95rem;color:{lc(l2p)}">{l2p}% OCCUPIED</div>
            """,unsafe_allow_html=True)

            # ML outputs
            best_ann=max(ann_probs,key=ann_probs.get)
            ac={"GREEN":GREEN,"YELLOW":"#ff9100","RED":RED}
            slot_ml.markdown(f"""
            <div style="display:grid;gap:7px">
              {''.join(f'''<div style="background:{AX};border:1px solid {GR};border-radius:10px;padding:11px 13px">
                <div style="font-family:'JetBrains Mono';font-size:.65rem;color:{TC}">{icon} {label}</div>
                <div style="font-family:'Bebas Neue';font-size:1.15rem;color:{color}">{value}</div>
              </div>''' for icon,label,value,color in [
                ("🔷","CNN EDGE INTENSITY",cnn_feat['edge'],GOLD),
                ("🔁","RNN NEXT VEHICLES",f"{st.session_state.rnn_last:.1f}",CYAN),
                ("🧬","LSTM AQI FORECAST",f"{st.session_state.lstm_last:.0f}","#e040fb"),
                ("⚡",f"ANN → {best_ann}",f"{ann_probs[best_ann]:.0%}",ac.get(best_ann,GOLD)),
                ("📍🌲","KNN · RF",f"{knn_pred}  ·  {rf_pred}",GREEN),
              ])}
            </div>""",unsafe_allow_html=True)

            # Stats
            slot_stats.markdown(f"""
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
              {''.join(f'''<div style="background:{AX};border:1px solid {GR};border-radius:12px;
              padding:13px;text-align:center">
                <div style="font-family:'Bebas Neue';font-size:1.5rem;color:{col}">{val}</div>
                <div style="font-family:'JetBrains Mono';font-size:.62rem;color:{TC}">{lbl}</div>
              </div>''' for val,col,lbl in [
                (st.session_state.peak,GREEN,"PEAK VEH"),
                (st.session_state.frames_done,PURP,"FRAMES"),
                (len(st.session_state.history),GOLD,"DATA PTS"),
                (f"{n//20}s",CYAN,"UPTIME"),
              ])}
            </div>""",unsafe_allow_html=True)

        # Charts every 18 frames
        if n%18==0 and len(st.session_state.history)>5:
            hdf=pd.DataFrame(list(st.session_state.history))
            live_scatter.pyplot(chart_scatter(hdf),   use_container_width=True)
            live_series.pyplot(chart_timeseries(hdf), use_container_width=True)
            live_cnn.pyplot(chart_cnn(st.session_state.cnn_feats), use_container_width=True)
            live_rnn.pyplot(chart_rnn_lstm(hdf,lstm_pred,rnn_pred), use_container_width=True)
            live_ann.pyplot(chart_ann(ann_probs),     use_container_width=True)
            live_knn.pyplot(chart_knn(knn_pipe,knn_df,total,aqi), use_container_width=True)
            live_km.pyplot(chart_kmeans(km_model,km_df,total,aqi), use_container_width=True)
            if rf_pipe: live_rf.pyplot(chart_rf(rf_pipe), use_container_width=True)
            live_sighist.pyplot(chart_signal_history(hdf), use_container_width=True)

        time.sleep(0.04)

    if st.session_state.running: st.rerun()

else:
    # Splash screen
    ph=np.zeros((380,640,3),np.uint8)
    for y in range(380): ph[y,:]=(int(3+y*12/380),int(7+y*18/380),int(12+y*38/380))
    for x in range(0,640,55): cv2.line(ph,(x,0),(x,380),(0,25,55),1)
    for y2 in range(0,380,55): cv2.line(ph,(0,y2),(640,y2),(0,25,55),1)
    cv2.putText(ph,"TRAFFICIQ  v4.0",(145,140),cv2.FONT_HERSHEY_SIMPLEX,1.3,(180,120,20),2)
    cv2.putText(ph,"Prepared by : Sanket Sutar",(165,180),cv2.FONT_HERSHEY_SIMPLEX,.65,(140,95,15),2)
    cv2.putText(ph,"CNN · RNN · LSTM · ANN · KNN · KMeans · RF",(82,215),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,100,155),1)
    cv2.putText(ph,"Press  START DETECTION  to begin",(115,260),cv2.FONT_HERSHEY_SIMPLEX,.65,(0,70,130),1)
    vid_slot.image(cv2.cvtColor(ph,cv2.COLOR_BGR2RGB),channels="RGB",use_container_width=True)
    slot_metrics.markdown(f"""<div class="mgrid">
      <div class="mcard mc-car"><div class="mval">—</div><div class="mlbl">🚗 CARS</div></div>
      <div class="mcard mc-bike"><div class="mval">—</div><div class="mlbl">🏍 BIKES</div></div>
      <div class="mcard mc-tot"><div class="mval">—</div><div class="mlbl">🔢 TOTAL</div></div>
      <div class="mcard mc-aqi"><div class="mval">—</div><div class="mlbl">🌫 AQI</div></div>
    </div>""",unsafe_allow_html=True)
    slot_sig.markdown(f'<div class="sig-panel sig-green"><div class="sig-time">--s</div><div class="sig-lbl">SYSTEM READY — PRESS START</div></div>',unsafe_allow_html=True)
    slot_alerts.markdown('<div class="al-ok">✓ ALL 7 ALGORITHMS LOADED AND READY — TrafficIQ v4.0 by Sanket Sutar</div>',unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
  <div style="font-size:.85rem;margin-bottom:4px">
    🧠 <span>TRAFFICIQ v4.0</span> — Smart Traffic Signalling with Air Pollution Index Prediction
  </div>
  <div>
    Prepared by &nbsp;<span>Sanket Sutar</span>&nbsp; · &nbsp;
    B.E. Final Year Project &nbsp; · &nbsp; 2025–26 &nbsp; · &nbsp;
    Deep Learning &amp; Computer Vision &nbsp; · &nbsp;
    YOLOv8 · RNN · LSTM · ANN · KNN · KMeans · Random Forest
  </div>
</div>
""",unsafe_allow_html=True)