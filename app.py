import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CryptoPerp Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — PHOSPHOR TERMINAL
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root{
    --bg:#060A0F; --surface:#0C1219; --surface2:#101820;
    --border:#192233; --border2:#1F2D40;
    --accent:#F5A623; --accent-dim:rgba(245,166,35,0.10); --accent-glow:rgba(245,166,35,0.22);
    --green:#2DFF6E; --green-dim:rgba(45,255,110,0.08); --green-glow:rgba(45,255,110,0.20);
    --red:#FF3358; --red-dim:rgba(255,51,88,0.08); --red-glow:rgba(255,51,88,0.20);
    --text:#CDD6E4; --text2:#6B7E96; --muted:#3D5268;
}
html,body{background:#060A0F !important;}
.stApp{
    background-color:#060A0F !important;
    background-image:radial-gradient(rgba(31,45,64,0.42) 1px, transparent 1px) !important;
    background-size:28px 28px !important;
    font-family:'Plus Jakarta Sans',sans-serif;
    color:var(--text);
}
.stApp>header{background:transparent !important;}
[data-testid="stSidebar"]{
    background:var(--surface) !important;
    border-right:1px solid var(--border2) !important;
}
hr{border-color:var(--border2) !important;opacity:1 !important;margin:16px 0 !important;}
[data-testid="stWidgetLabel"] p,
.stSelectbox label{
    color:var(--text2) !important;font-family:'IBM Plex Mono',monospace !important;
    font-size:10px !important;letter-spacing:1.5px !important;text-transform:uppercase !important;
}
.stSelectbox>div>div{
    background:var(--surface2) !important;border:1px solid var(--border2) !important;
    color:var(--text) !important;border-radius:2px !important;
    font-family:'IBM Plex Mono',monospace !important;font-size:12px !important;
}
.stButton>button{
    background:var(--accent-dim) !important;border:1px solid var(--accent) !important;
    color:var(--accent) !important;border-radius:2px !important;
    font-family:'Plus Jakarta Sans',sans-serif !important;font-weight:700 !important;
    letter-spacing:2px !important;font-size:10px !important;text-transform:uppercase !important;
    padding:8px 16px !important;width:100% !important;transition:all 0.2s ease !important;
}
.stButton>button:hover{
    background:var(--accent-glow) !important;box-shadow:0 0 14px var(--accent-glow) !important;
}
.metric-card{
    background:var(--surface);border:1px solid var(--border2);
    border-left:3px solid var(--accent);border-radius:0;padding:14px 16px;
}
.metric-label{
    font-size:9px;color:var(--text2);text-transform:uppercase;
    letter-spacing:2.5px;margin-bottom:8px;font-family:'IBM Plex Mono',monospace;
}
.metric-value{
    font-size:20px;font-weight:700;font-family:'IBM Plex Mono',monospace;
    color:var(--text);line-height:1;
}
.metric-sub{font-size:10px;color:var(--muted);margin-top:7px;font-family:'IBM Plex Mono',monospace;}
.signal-long{
    display:flex;align-items:center;justify-content:center;
    background:var(--green-dim);border:1px solid var(--green);color:var(--green);
    border-radius:2px;padding:12px 20px;font-size:28px;letter-spacing:5px;
    font-family:'Bebas Neue',cursive;
    box-shadow:0 0 20px var(--green-glow),inset 0 0 12px rgba(45,255,110,0.05);
    animation:pulseGreen 2.5s ease-in-out infinite;width:100%;text-align:center;
}
.signal-short{
    display:flex;align-items:center;justify-content:center;
    background:var(--red-dim);border:1px solid var(--red);color:var(--red);
    border-radius:2px;padding:12px 20px;font-size:28px;letter-spacing:5px;
    font-family:'Bebas Neue',cursive;
    box-shadow:0 0 20px var(--red-glow),inset 0 0 12px rgba(255,51,88,0.05);
    animation:pulseRed 2.5s ease-in-out infinite;width:100%;text-align:center;
}
.signal-neutral{
    display:flex;align-items:center;justify-content:center;
    background:rgba(58,78,98,0.12);border:1px solid var(--muted);color:var(--text2);
    border-radius:2px;padding:12px 20px;font-size:28px;letter-spacing:5px;
    font-family:'Bebas Neue',cursive;width:100%;text-align:center;
}
@keyframes pulseGreen{
    0%,100%{box-shadow:0 0 20px var(--green-glow),inset 0 0 12px rgba(45,255,110,0.05);}
    50%{box-shadow:0 0 36px rgba(45,255,110,0.40),inset 0 0 20px rgba(45,255,110,0.12);}
}
@keyframes pulseRed{
    0%,100%{box-shadow:0 0 20px var(--red-glow),inset 0 0 12px rgba(255,51,88,0.05);}
    50%{box-shadow:0 0 36px rgba(255,51,88,0.40),inset 0 0 20px rgba(255,51,88,0.12);}
}
.indicator-row{
    display:flex;justify-content:space-between;align-items:flex-start;
    padding:8px 10px;border-bottom:1px solid var(--border);
    font-family:'IBM Plex Mono',monospace;
}
.indicator-row:last-child{border-bottom:none;}
.ind-name{font-size:10px;color:var(--text2);margin-bottom:3px;letter-spacing:0.5px;}
.ind-bullish{color:var(--green);font-weight:600;font-size:10px;letter-spacing:1px;}
.ind-bearish{color:var(--red);font-weight:600;font-size:10px;letter-spacing:1px;}
.ind-neutral{color:var(--muted);font-size:10px;letter-spacing:1px;}
.section-header{
    font-size:9px;color:var(--accent);text-transform:uppercase;letter-spacing:3px;
    border-bottom:1px solid var(--border2);padding-bottom:8px;margin-bottom:14px;
    font-family:'IBM Plex Mono',monospace;
}
.dash-title{
    font-family:'Bebas Neue',cursive;font-size:38px;color:var(--accent);
    letter-spacing:3px;line-height:1;text-shadow:0 0 24px var(--accent-glow);
}
.dash-subtitle{
    font-size:9px;color:var(--text2);letter-spacing:3px;text-transform:uppercase;
    font-family:'IBM Plex Mono',monospace;margin-top:4px;
}
.conf-bar-container{background:var(--border2);border-radius:0;height:5px;width:100%;margin:4px 0;}
.conf-bar-fill-bull{background:var(--green);height:100%;border-radius:0;box-shadow:0 0 6px var(--green-glow);}
.conf-bar-fill-bear{background:var(--red);height:100%;border-radius:0;box-shadow:0 0 6px var(--red-glow);}
[data-testid="stExpander"]{
    border:1px solid var(--border2) !important;border-radius:0 !important;
    background:var(--surface) !important;
}
#MainMenu,footer,.stDeployButton{display:none !important;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
CRYPTOS = {
    "BTC/USDT":  "BTC-USDT",   "ETH/USDT":  "ETH-USDT",
    "BNB/USDT":  "BNB-USDT",   "SOL/USDT":  "SOL-USDT",
    "XRP/USDT":  "XRP-USDT",   "ADA/USDT":  "ADA-USDT",
    "AVAX/USDT": "AVAX-USDT",  "DOGE/USDT": "DOGE-USDT",
    "MATIC/USDT":"MATIC-USDT", "LINK/USDT": "LINK-USDT",
    "DOT/USDT":  "DOT-USDT",   "UNI/USDT":  "UNI-USDT",
    "LTC/USDT":  "LTC-USDT",   "ATOM/USDT": "ATOM-USDT",
    "FIL/USDT":  "FIL-USDT",   "APT/USDT":  "APT-USDT",
    "ARB/USDT":  "ARB-USDT",   "OP/USDT":   "OP-USDT",
    "INJ/USDT":  "INJ-USDT",   "SUI/USDT":  "SUI-USDT",
}

def to_swap(okx_id: str) -> str:
    return okx_id.replace("-USDT", "-USDT-SWAP")

TIMEFRAMES = {"15m": "15m", "1h": "1H", "4h": "4H", "1d": "1D"}
TF_LABELS   = {"15m": "15m", "1H": "1h", "4H": "4h", "1D": "1d"}

OKX_BASE  = "https://www.okx.com"
CG_BASE   = "https://api.coingecko.com/api/v3"
FNG_URL   = "https://api.alternative.me/fng/?limit=1"

CG_IDS = {
    "BTC-USDT":"bitcoin",     "ETH-USDT":"ethereum",       "BNB-USDT":"binancecoin",
    "SOL-USDT":"solana",      "XRP-USDT":"ripple",         "ADA-USDT":"cardano",
    "AVAX-USDT":"avalanche-2","DOGE-USDT":"dogecoin",      "MATIC-USDT":"matic-network",
    "LINK-USDT":"chainlink",  "DOT-USDT":"polkadot",       "UNI-USDT":"uniswap",
    "LTC-USDT":"litecoin",    "ATOM-USDT":"cosmos",        "FIL-USDT":"filecoin",
    "APT-USDT":"aptos",       "ARB-USDT":"arbitrum",       "OP-USDT":"optimism",
    "INJ-USDT":"injective-protocol", "SUI-USDT":"sui",
}

HDR = {"User-Agent": "Mozilla/5.0 (compatible; CryptoPerpDashboard/2.0)"}

# ─────────────────────────────────────────────
# API — OKX (primary)
# ─────────────────────────────────────────────

@st.cache_data(ttl=60)
def fetch_klines(okx_id: str, tf_label: str, limit: int = 200) -> pd.DataFrame:
    bar = TIMEFRAMES.get(tf_label, "1H")
    swap_sym = to_swap(okx_id)

    try:
        r = requests.get(
            f"{OKX_BASE}/api/v5/market/candles",
            params={"instId": swap_sym, "bar": bar, "limit": limit},
            headers=HDR, timeout=10,
        )
        if r.status_code == 200:
            rows = r.json().get("data", [])
            if len(rows) >= 20:
                df = pd.DataFrame(list(reversed(rows)),
                                  columns=["ts","open","high","low","close","vol","volCcy","volQ","confirm"])
                for c in ["open","high","low","close","vol"]:
                    df[c] = df[c].astype(float)
                df["open_time"] = pd.to_datetime(df["ts"].astype(int), unit="ms")
                df.rename(columns={"vol": "volume"}, inplace=True)
                return df[["open_time","open","high","low","close","volume"]].tail(200)
    except Exception:
        pass

    try:
        r = requests.get(
            f"{OKX_BASE}/api/v5/market/candles",
            params={"instId": okx_id, "bar": bar, "limit": limit},
            headers=HDR, timeout=10,
        )
        if r.status_code == 200:
            rows = r.json().get("data", [])
            if len(rows) >= 20:
                df = pd.DataFrame(list(reversed(rows)),
                                  columns=["ts","open","high","low","close","vol","volCcy","volQ","confirm"])
                for c in ["open","high","low","close","vol"]:
                    df[c] = df[c].astype(float)
                df["open_time"] = pd.to_datetime(df["ts"].astype(int), unit="ms")
                df.rename(columns={"vol": "volume"}, inplace=True)
                return df[["open_time","open","high","low","close","volume"]].tail(200)
    except Exception:
        pass

    cg_id = CG_IDS.get(okx_id, "")
    if cg_id:
        try:
            r = requests.get(
                f"{CG_BASE}/coins/{cg_id}/ohlc",
                params={"vs_currency": "usd", "days": "30"},
                headers=HDR, timeout=12,
            )
            if r.status_code == 200:
                rows = r.json()
                if rows:
                    df = pd.DataFrame(rows, columns=["ts","open","high","low","close"])
                    for c in ["open","high","low","close"]:
                        df[c] = df[c].astype(float)
                    df["open_time"] = pd.to_datetime(df["ts"], unit="ms")
                    df["volume"] = 0.0
                    return df[["open_time","open","high","low","close","volume"]].tail(200)
        except Exception:
            pass

    return pd.DataFrame()


@st.cache_data(ttl=30)
def fetch_ticker(okx_id: str) -> dict:
    swap_sym = to_swap(okx_id)
    for inst_id in [swap_sym, okx_id]:
        try:
            r = requests.get(
                f"{OKX_BASE}/api/v5/market/ticker",
                params={"instId": inst_id},
                headers=HDR, timeout=8,
            )
            if r.status_code == 200:
                data = r.json().get("data", [])
                if data:
                    d = data[0]
                    last = float(d.get("last", 0))
                    open24 = float(d.get("open24h", last) or last)
                    change_pct = ((last - open24) / open24 * 100) if open24 else 0.0
                    return {
                        "lastPrice": str(last),
                        "priceChangePercent": f"{change_pct:.4f}",
                        "quoteVolume": d.get("volCcy24h", "0"),
                        "volume": d.get("vol24h", "0"),
                        "_source": inst_id,
                    }
        except Exception:
            pass
    return {}


@st.cache_data(ttl=60)
def fetch_funding_rate(okx_id: str) -> float:
    swap_sym = to_swap(okx_id)
    try:
        r = requests.get(
            f"{OKX_BASE}/api/v5/public/funding-rate",
            params={"instId": swap_sym},
            headers=HDR, timeout=8,
        )
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                return float(data[0].get("fundingRate", 0)) * 100
    except Exception:
        pass
    return 0.0


@st.cache_data(ttl=60)
def fetch_open_interest(okx_id: str) -> float:
    swap_sym = to_swap(okx_id)
    try:
        r = requests.get(
            f"{OKX_BASE}/api/v5/public/open-interest",
            params={"instType": "SWAP", "instId": swap_sym},
            headers=HDR, timeout=8,
        )
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                return float(data[0].get("oi", 0))
    except Exception:
        pass
    return 0.0


@st.cache_data(ttl=300)
def fetch_fear_greed() -> dict:
    try:
        r = requests.get(FNG_URL, headers=HDR, timeout=8)
        if r.status_code == 200:
            d = r.json()["data"][0]
            return {"value": int(d["value"]), "label": d["value_classification"], "ok": True}
    except Exception:
        pass
    return {"value": 50, "label": "Neutral", "ok": False}


@st.cache_data(ttl=180)
def fetch_cg_coin(cg_id: str) -> dict:
    try:
        r = requests.get(
            f"{CG_BASE}/coins/{cg_id}",
            params={"localization":"false","tickers":"false","community_data":"false",
                    "developer_data":"false","sparkline":"false"},
            headers=HDR, timeout=12,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


# ─────────────────────────────────────────────
# TECHNICAL INDICATORS
# ─────────────────────────────────────────────

def calc_ema(s, p):
    return s.ewm(span=p, adjust=False).mean()

def calc_rsi(s, p=14):
    d = s.diff()
    g = d.clip(lower=0)
    l = -d.clip(upper=0)
    ag = g.ewm(com=p-1, adjust=False).mean()
    al = l.ewm(com=p-1, adjust=False).mean()
    rs = ag / al.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))

def calc_macd(s, fast=12, slow=26, sig=9):
    ef = calc_ema(s, fast); es = calc_ema(s, slow)
    ml = ef - es; sl = calc_ema(ml, sig)
    return ml, sl, ml - sl

def calc_bollinger(s, p=20, k=2):
    m = s.rolling(p).mean(); st = s.rolling(p).std()
    return m + k*st, m, m - k*st

def calc_atr(df, p=14):
    hl = df["high"] - df["low"]
    hc = (df["high"] - df["close"].shift()).abs()
    lc = (df["low"]  - df["close"].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.ewm(com=p-1, adjust=False).mean()

def compute_indicators(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 50:
        return {}
    close = df["close"]; vol = df["volume"]
    ema20  = calc_ema(close, 20)
    ema50  = calc_ema(close, 50)
    ema200 = calc_ema(close, 200)
    rsi    = calc_rsi(close)
    ml, sl, hist = calc_macd(close)
    bbu, bbm, bbl = calc_bollinger(close)
    atr   = calc_atr(df)
    vma20 = vol.rolling(20).mean()
    return {
        "price":  close.iloc[-1], "ema20": ema20.iloc[-1],
        "ema50":  ema50.iloc[-1], "ema200": ema200.iloc[-1],
        "rsi":    rsi.iloc[-1],   "macd":   ml.iloc[-1],
        "macd_signal": sl.iloc[-1], "macd_hist": hist.iloc[-1],
        "bb_upper": bbu.iloc[-1], "bb_mid": bbm.iloc[-1], "bb_lower": bbl.iloc[-1],
        "atr":    atr.iloc[-1],
        "vol_current": vol.iloc[-1], "vol_avg20": vma20.iloc[-1],
        "_ema20": ema20, "_ema50": ema50, "_ema200": ema200,
        "_rsi": rsi, "_macd": ml, "_macd_signal": sl, "_macd_hist": hist,
        "_bb_upper": bbu, "_bb_mid": bbm, "_bb_lower": bbl,
    }


# ─────────────────────────────────────────────
# SIGNAL ENGINE
# ─────────────────────────────────────────────

def evaluate_signals(ind: dict, funding: float, oi_change_pct: float, fg: dict) -> dict:
    if not ind:
        return {}
    p = ind["price"]
    s = {}

    if p > ind["ema200"] * 1.005:
        s["Trend (EMA200)"] = (1,  "Bullish — precio sobre EMA200")
    elif p < ind["ema200"] * 0.995:
        s["Trend (EMA200)"] = (-1, "Bearish — precio bajo EMA200")
    else:
        s["Trend (EMA200)"] = (0,  "Neutral — precio en EMA200")

    if ind["ema20"] > ind["ema50"]:
        s["EMA Stack (20/50)"] = (1,  "Bullish — EMA20 > EMA50")
    elif ind["ema20"] < ind["ema50"]:
        s["EMA Stack (20/50)"] = (-1, "Bearish — EMA20 < EMA50")
    else:
        s["EMA Stack (20/50)"] = (0,  "Neutral")

    rsi = ind["rsi"]
    if rsi < 35:
        s["RSI (14)"] = (1,  f"Bullish — oversold ({rsi:.1f})")
    elif rsi > 65:
        s["RSI (14)"] = (-1, f"Bearish — overbought ({rsi:.1f})")
    elif rsi >= 55:
        s["RSI (14)"] = (1,  f"Bullish momentum ({rsi:.1f})")
    elif rsi <= 45:
        s["RSI (14)"] = (-1, f"Bearish momentum ({rsi:.1f})")
    else:
        s["RSI (14)"] = (0,  f"Neutral ({rsi:.1f})")

    if ind["macd_hist"] > 0 and ind["macd"] > ind["macd_signal"]:
        s["MACD"] = (1,  "Bullish — histograma positivo")
    elif ind["macd_hist"] < 0 and ind["macd"] < ind["macd_signal"]:
        s["MACD"] = (-1, "Bearish — histograma negativo")
    else:
        s["MACD"] = (0,  "Neutral — cruce en progreso")

    bb_pct = (p - ind["bb_lower"]) / (ind["bb_upper"] - ind["bb_lower"] + 1e-10)
    if bb_pct < 0.2:
        s["Bollinger Bands"] = (1,  f"Bullish — banda baja ({bb_pct:.0%})")
    elif bb_pct > 0.8:
        s["Bollinger Bands"] = (-1, f"Bearish — banda alta ({bb_pct:.0%})")
    else:
        s["Bollinger Bands"] = (0,  f"Neutral ({bb_pct:.0%} del rango)")

    vr = ind["vol_current"] / (ind["vol_avg20"] + 1e-10)
    if vr > 1.3:
        dir_ = s.get("EMA Stack (20/50)", (0,))[0]
        if   dir_ ==  1: s["Volumen"] = (1,  f"Bullish — {vr:.1f}x vol. promedio")
        elif dir_ == -1: s["Volumen"] = (-1, f"Bearish — {vr:.1f}x vol. promedio")
        else:            s["Volumen"] = (0,  f"Alto vol., sin dir. ({vr:.1f}x)")
    else:
        s["Volumen"] = (0, f"Normal ({vr:.1f}x promedio)")

    if funding < -0.05:
        s["Funding Rate"] = (1,  f"Bullish — negativo ({funding:.3f}%)")
    elif funding > 0.1:
        s["Funding Rate"] = (-1, f"Bearish — alto ({funding:.3f}%)")
    else:
        s["Funding Rate"] = (0,  f"Neutral ({funding:.3f}%)")

    fv = fg.get("value", 50)
    if fv < 25:
        s["Fear & Greed"] = (1,  f"Bullish — miedo extremo ({fv})")
    elif fv > 75:
        s["Fear & Greed"] = (-1, f"Bearish — codicia extrema ({fv})")
    else:
        s["Fear & Greed"] = (0,  f"Neutral ({fv} — {fg.get('label','')})")

    if abs(oi_change_pct) >= 0.3:
        dir_ = s.get("EMA Stack (20/50)", (0,))[0]
        if oi_change_pct > 0 and dir_ ==  1:
            s["Open Interest"] = (1,  f"Bullish — OI +{oi_change_pct:.1f}%")
        elif oi_change_pct > 0 and dir_ == -1:
            s["Open Interest"] = (-1, f"Bearish — OI +{oi_change_pct:.1f}%")
        elif oi_change_pct < 0 and dir_ ==  1:
            s["Open Interest"] = (1,  f"Bull squeeze — OI {oi_change_pct:.1f}%")
        elif oi_change_pct < 0 and dir_ == -1:
            s["Open Interest"] = (-1, f"Bearish — OI {oi_change_pct:.1f}%")
        else:
            s["Open Interest"] = (0,  f"OI {oi_change_pct:+.1f}% sin confirm.")
    elif oi_change_pct != 0:
        s["Open Interest"] = (0, f"OI estable ({oi_change_pct:+.2f}%)")

    return s


def get_recommendation(signals: dict):
    if not signals:
        return "SIN DATOS", 0, 0, 0
    bull  = sum(1 for v,_ in signals.values() if v ==  1)
    bear  = sum(1 for v,_ in signals.values() if v == -1)
    total = len(signals)
    score = (bull - bear) / total
    action = "LONG" if bull >= 4 else "SHORT" if bear >= 4 else "NEUTRAL"
    return action, score, bull, bear


# ─────────────────────────────────────────────
# CHART — Phosphor Terminal palette
# ─────────────────────────────────────────────

def build_chart(df, ind):
    if df.empty or not ind:
        return go.Figure()
    t = df["open_time"]
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.55, 0.25, 0.20], vertical_spacing=0.03,
                        subplot_titles=("", "RSI (14)", "MACD"))

    fig.add_trace(go.Candlestick(x=t, open=df["open"], high=df["high"],
        low=df["low"], close=df["close"], name="OHLC",
        increasing_line_color="#2DFF6E", decreasing_line_color="#FF3358",
        increasing_fillcolor="rgba(45,255,110,0.45)", decreasing_fillcolor="rgba(255,51,88,0.45)",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=t, y=ind["_bb_upper"], name="BB",
        line=dict(color="rgba(61,82,104,0.55)", width=1, dash="dot"), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=t, y=ind["_bb_lower"], name="BB",
        line=dict(color="rgba(61,82,104,0.55)", width=1, dash="dot"),
        fill="tonexty", fillcolor="rgba(61,82,104,0.06)", showlegend=False), row=1, col=1)

    for p, color in [("20","#F5A623"), ("50","#60A5FA"), ("200","#C084FC")]:
        key = f"_ema{p}"
        if key in ind:
            fig.add_trace(go.Scatter(x=t, y=ind[key], name=f"EMA{p}",
                line=dict(color=color, width=1.5), opacity=0.9), row=1, col=1)

    fig.add_trace(go.Scatter(x=t, y=ind["_rsi"], name="RSI",
        line=dict(color="#F5A623", width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line=dict(color="#FF3358", dash="dash", width=1), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="#2DFF6E", dash="dash", width=1), row=2, col=1)

    hist_colors = ["rgba(45,255,110,0.7)" if v >= 0 else "rgba(255,51,88,0.7)" for v in ind["_macd_hist"]]
    fig.add_trace(go.Bar(x=t, y=ind["_macd_hist"], marker_color=hist_colors, showlegend=False), row=3, col=1)
    fig.add_trace(go.Scatter(x=t, y=ind["_macd"],        name="MACD",   line=dict(color="#2DFF6E", width=1.5)), row=3, col=1)
    fig.add_trace(go.Scatter(x=t, y=ind["_macd_signal"], name="Signal", line=dict(color="#F5A623", width=1.5)), row=3, col=1)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(12,18,25,0.88)",
        font=dict(family="IBM Plex Mono", color="#6B7E96", size=10),
        legend=dict(bgcolor="rgba(12,18,25,0.92)", bordercolor="#1F2D40", borderwidth=1, font=dict(size=10)),
        xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=20,b=0), height=520, hovermode="x unified",
    )
    for i in range(1, 4):
        fig.update_xaxes(gridcolor="#192233", zeroline=False, showspikes=True,
                         spikecolor="#3D5268", row=i, col=1)
        fig.update_yaxes(gridcolor="#192233", zeroline=False, row=i, col=1)
    return fig


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def fmt_price(p):
    if p >= 1000:  return f"${p:,.2f}"
    if p >= 1:     return f"${p:.4f}"
    return f"${p:.6f}"

def fmt_large(n):
    if n >= 1e9: return f"${n/1e9:.2f}B"
    if n >= 1e6: return f"${n/1e6:.2f}M"
    if n >= 1e3: return f"${n/1e3:.2f}K"
    return f"${n:.2f}"

def signal_html(action):
    cls  = {"LONG":"signal-long","SHORT":"signal-short"}.get(action,"signal-neutral")
    icon = {"LONG":"▲  LONG","SHORT":"▼  SHORT","NEUTRAL":"◆  NEUTRAL","SIN DATOS":"—  —"}.get(action, action)
    return f'<div class="{cls}">{icon}</div>'

def ind_html(v, desc):
    if v ==  1:
        badge = '<span class="ind-bullish">▲ BULL</span>'
    elif v == -1:
        badge = '<span class="ind-bearish">▼ BEAR</span>'
    else:
        badge = '<span class="ind-neutral">◆ NEUT</span>'
    return (f'<div style="margin-top:2px">{badge}'
            f' <span style="color:#3D5268;font-size:10px;font-family:\'IBM Plex Mono\',monospace">{desc}</span></div>')


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="dash-title">CRYPTOPERP</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-subtitle">OKX Futures Terminal</div>', unsafe_allow_html=True)
    st.markdown("---")

    selected_label  = st.selectbox("Seleccionar Par", list(CRYPTOS.keys()), index=0)
    selected_okx_id = CRYPTOS[selected_label]
    selected_tf     = st.selectbox("Timeframe", list(TIMEFRAMES.keys()), index=2)

    st.markdown("---")
    st.markdown('<div class="section-header">Estrategia</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px;color:#6B7E96;line-height:1.8;font-family:"IBM Plex Mono",monospace'>
    Basada en <b style='color:#F5A623'>M. van de Poppe</b><br>
    Confluencia multi-indicador:<br>
    <span style='color:#2DFF6E'>≥ 4 bull → LONG</span><br>
    <span style='color:#FF3358'>≥ 4 bear → SHORT</span><br>
    Datos: OKX Perps + CoinGecko<br><br>
    <span style='color:#F5A623'>⚠ No es asesoría financiera.</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Actualizar datos"):
        st.cache_data.clear()
        for k in [k for k in st.session_state if k.startswith("prev_oi_")]:
            del st.session_state[k]
        st.rerun()
    st.markdown(
        f'<div style="font-size:9px;color:#3D5268;margin-top:8px;font-family:\'IBM Plex Mono\',monospace;letter-spacing:1px">'
        f'SYNC {datetime.now().strftime("%H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────

with st.spinner("Cargando datos · OKX..."):
    df      = fetch_klines(selected_okx_id, selected_tf, limit=200)
    ticker  = fetch_ticker(selected_okx_id)
    funding = fetch_funding_rate(selected_okx_id)
    fg      = fetch_fear_greed()
    ind     = compute_indicators(df)

    cur_oi    = fetch_open_interest(selected_okx_id)
    _oi_key   = f"prev_oi_{selected_okx_id}"
    prev_oi   = st.session_state.get(_oi_key, 0.0)
    oi_chg    = ((cur_oi - prev_oi) / prev_oi * 100) if prev_oi > 0 else 0.0
    if cur_oi > 0:
        st.session_state[_oi_key] = cur_oi

    signals = evaluate_signals(ind, funding, oi_chg, fg)
    action, score, bull_count, bear_count = get_recommendation(signals)

cg_data = {}
cg_id   = CG_IDS.get(selected_okx_id, "")
if cg_id:
    cg_data = fetch_cg_coin(cg_id)

klines_ok = not df.empty
ticker_ok = bool(ticker.get("lastPrice"))
source    = ticker.get("_source", "—")

if not klines_ok or not ticker_ok:
    st.error(
        f"⚠ Sin datos para {selected_label}. "
        "Haz clic en Actualizar datos · OKX swap → spot → CoinGecko"
    )
else:
    src_label = "OKX Swap (Perps)" if "SWAP" in source else "OKX Spot"
    st.success(f"✓  {src_label}  ·  {len(df)} velas  ·  {selected_tf}", icon=None)


# ─────────────────────────────────────────────
# HEADER — price / signal / confluence
# ─────────────────────────────────────────────

c1, c2, c3 = st.columns([3, 2, 2])
with c1:
    price_str = fmt_price(ind.get("price", 0)) if ind else "—"
    chg       = float(ticker.get("priceChangePercent", 0)) if ticker else 0
    chg_color = "#2DFF6E" if chg >= 0 else "#FF3358"
    chg_sign  = "+" if chg >= 0 else ""
    st.markdown(f"""
    <div style='margin-top:4px'>
      <div style='font-family:"Bebas Neue",cursive;font-size:52px;color:#CDD6E4;
                  letter-spacing:2px;line-height:1'>{price_str}</div>
      <div style='display:flex;align-items:center;gap:14px;margin-top:6px'>
        <span style='color:{chg_color};font-size:15px;font-family:"IBM Plex Mono",monospace;
                     font-weight:600'>{chg_sign}{chg:.2f}%</span>
        <span style='color:#3D5268;font-size:10px;font-family:"IBM Plex Mono",monospace;
                     letter-spacing:1px'>{selected_label} · {selected_tf} · OKX PERPS</span>
      </div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(
        '<div style="font-size:9px;color:#3D5268;margin-bottom:8px;letter-spacing:2.5px;'
        'text-transform:uppercase;font-family:\'IBM Plex Mono\',monospace;margin-top:6px">'
        'SEÑAL RECOMENDADA</div>',
        unsafe_allow_html=True
    )
    st.markdown(signal_html(action), unsafe_allow_html=True)

with c3:
    total = len(signals) if signals else 1
    bp    = int(bull_count / total * 100) if signals else 0
    brp   = int(bear_count / total * 100) if signals else 0
    st.markdown(f"""
    <div style='margin-top:6px'>
      <div style='font-size:9px;color:#3D5268;margin-bottom:8px;letter-spacing:2.5px;
                  text-transform:uppercase;font-family:"IBM Plex Mono",monospace'>CONFLUENCIA</div>
      <div style='font-size:11px;margin-bottom:3px;color:#2DFF6E;
                  font-family:"IBM Plex Mono",monospace'>▲ BULL: {bull_count}/{total} ({bp}%)</div>
      <div class='conf-bar-container'><div class='conf-bar-fill-bull' style='width:{bp}%'></div></div>
      <div style='font-size:11px;margin-bottom:3px;color:#FF3358;margin-top:8px;
                  font-family:"IBM Plex Mono",monospace'>▼ BEAR: {bear_count}/{total} ({brp}%)</div>
      <div class='conf-bar-container'><div class='conf-bar-fill-bear' style='width:{brp}%'></div></div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin:14px 0;border-top:1px solid #192233'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────

m1, m2, m3, m4, m5, m6 = st.columns(6)
oi_sub = (f"{oi_chg:+.2f}% vs antes" if oi_chg != 0 else "primer snapshot")

rsi_val    = ind.get("rsi", 50) if ind else 50
rsi_color  = "#2DFF6E" if rsi_val < 35 else "#FF3358" if rsi_val > 65 else "#F5A623"
fund_color = "#2DFF6E" if funding < -0.05 else "#FF3358" if funding > 0.1 else "#F5A623"
fv_raw     = fg.get("value", 50)
fg_color   = "#2DFF6E" if fv_raw <= 25 else "#FF3358" if fv_raw >= 75 else "#F5A623"

for col, lbl, val, sub, bc in [
    (m1, "Volumen 24h",   fmt_large(float(ticker.get("quoteVolume","0"))) if ticker else "—", "USDT",          "#F5A623"),
    (m2, "RSI (14)",      f"{rsi_val:.1f}" if ind else "—",                                   "neutro ≈ 50",   rsi_color),
    (m3, "Funding Rate",  f"{funding:+.4f}%",                                                  "cada 8h",       fund_color),
    (m4, "ATR (14)",      fmt_price(ind.get("atr",0)) if ind else "—",                        "volatilidad",   "#F5A623"),
    (m5, "Fear & Greed",  str(fv_raw),                                                         fg.get("label","—"), fg_color),
    (m6, "Open Interest", f"{cur_oi:,.0f}" if cur_oi else "—",                                oi_sub,          "#F5A623"),
]:
    with col:
        st.markdown(f"""
        <div class='metric-card' style='border-left-color:{bc}'>
          <div class='metric-label'>{lbl}</div>
          <div class='metric-value'>{val}</div>
          <div class='metric-sub'>{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin:18px 0'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CHART + SIGNALS
# ─────────────────────────────────────────────

ch_col, sig_col = st.columns([3, 1])

with ch_col:
    st.markdown('<div class="section-header">Gráfico de precio</div>', unsafe_allow_html=True)
    if klines_ok and ind:
        fig = build_chart(df, ind)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.warning("Sin datos para el gráfico. Presiona Actualizar.")

with sig_col:
    st.markdown('<div class="section-header">Análisis de señales</div>', unsafe_allow_html=True)
    if signals:
        for name, (sv, desc) in signals.items():
            st.markdown(f"""
            <div class='indicator-row'>
              <div style='flex:1'>
                <div class='ind-name'>{name}</div>
                {ind_html(sv, desc)}
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="color:#3D5268;font-size:11px;padding:12px;'
            'font-family:\'IBM Plex Mono\',monospace">Sin señales.<br>Presiona Actualizar.</div>',
            unsafe_allow_html=True
        )

    if ind and action not in ("SIN DATOS", "NEUTRAL"):
        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Gestión de riesgo</div>', unsafe_allow_html=True)
        price = ind["price"]; atr = ind.get("atr", 0)
        if action == "LONG":
            sl, tp1, tp2 = price - 1.5*atr, price + 2.0*atr, price + 3.5*atr
            sl_c, tp_c = "#FF3358", "#2DFF6E"
        else:
            sl, tp1, tp2 = price + 1.5*atr, price - 2.0*atr, price - 3.5*atr
            sl_c, tp_c = "#2DFF6E", "#FF3358"
        st.markdown(f"""
        <div style='font-size:11px;line-height:2.2;font-family:"IBM Plex Mono",monospace'>
          <div style='color:{sl_c}'>■ SL &nbsp;&nbsp;{fmt_price(sl)}</div>
          <div style='color:{tp_c}'>▲ TP1 &nbsp;{fmt_price(tp1)}</div>
          <div style='color:{tp_c}'>▲ TP2 &nbsp;{fmt_price(tp2)}</div>
          <div style='color:#F5A623'>◈ R/R &nbsp;&nbsp;1 : 2</div>
          <div style='color:#3D5268;font-size:9px;margin-top:6px;letter-spacing:1px'>
            1.5×ATR STOP · 2× / 3.5× TARGETS
          </div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FUNDAMENTALS
# ─────────────────────────────────────────────

st.markdown("<div style='margin:18px 0;border-top:1px solid #192233'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-header">Datos fundamentales</div>', unsafe_allow_html=True)

md      = cg_data.get("market_data", {}) if cg_data else {}
mkt_cap = md.get("market_cap",{}).get("usd",0) if md else 0
rank    = cg_data.get("market_cap_rank","—") if cg_data else "—"
circ_s  = md.get("circulating_supply",0) if md else 0
max_s   = md.get("max_supply",None) if md else None
ath_p   = md.get("ath",{}).get("usd",0) if md else 0
ath_c   = md.get("ath_change_percentage",{}).get("usd",0) if md else 0
sup_str = (f"{circ_s/1e6:.1f}M" + (f" / {max_s/1e6:.1f}M" if max_s else "")) if circ_s else "—"

f1, f2, f3, f4 = st.columns(4)
ath_sub_color = "#FF3358" if ath_c < 0 else "#2DFF6E"

for col, lbl, val, sub, bc in [
    (f1, "Market Cap",   fmt_large(mkt_cap) if mkt_cap else "—",   f"Rank #{rank}",                           "#F5A623"),
    (f2, "Supply Circ.", sup_str,                                    "Limitado" if max_s else "Sin límite",     "#F5A623"),
    (f3, "ATH",          fmt_price(ath_p) if ath_p else "—",
         f'<span style="color:{ath_sub_color}">{ath_c:.1f}% desde ATH</span>',                                 "#F5A623"),
    (f4, "Fear & Greed",
         f'<span style="color:{fg_color};font-family:\'Bebas Neue\',cursive;font-size:34px">{fv_raw}</span>',
         fg.get("label","—"),                                                                                    fg_color),
]:
    with col:
        st.markdown(f"""
        <div class='metric-card' style='border-left-color:{bc}'>
          <div class='metric-label'>{lbl}</div>
          <div class='metric-value' style='font-size:16px'>{val}</div>
          <div class='metric-sub'>{sub}</div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RESUMEN TODOS LOS PARES
# ─────────────────────────────────────────────

st.markdown("<div style='margin:18px 0;border-top:1px solid #192233'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-header">Resumen de señales — todos los pares</div>', unsafe_allow_html=True)

with st.expander("Ver tabla de señales rápidas — 20 pares · 4h", expanded=False):
    rows, prog = [], st.progress(0)
    for i, (lbl, okx_id) in enumerate(CRYPTOS.items()):
        prog.progress((i+1)/len(CRYPTOS))
        try:
            df_t   = fetch_klines(okx_id, "4h", limit=100)
            tk_t   = fetch_ticker(okx_id)
            fr_t   = fetch_funding_rate(okx_id)
            ind_t  = compute_indicators(df_t)
            sigs_t = evaluate_signals(ind_t, fr_t, 0, fg)
            act_t, _, bc, brc = get_recommendation(sigs_t)
            chg_t  = float(tk_t.get("priceChangePercent",0)) if tk_t else 0
            rows.append({
                "Par": lbl,
                "Precio": fmt_price(ind_t.get("price",0)) if ind_t else "—",
                "24h %": f"{chg_t:+.2f}%",
                "RSI": f"{ind_t.get('rsi',0):.1f}" if ind_t else "—",
                "Funding": f"{fr_t:+.4f}%",
                "Bull": bc, "Bear": brc,
                "Señal": act_t,
            })
        except Exception:
            rows.append({"Par":lbl,"Precio":"—","24h %":"—","RSI":"—","Funding":"—","Bull":0,"Bear":0,"Señal":"ERROR"})
        time.sleep(0.05)
    prog.empty()
    if rows:
        df_tbl = pd.DataFrame(rows)
        def _cs(v):
            if v == "LONG":  return "background-color:rgba(45,255,110,0.12);color:#2DFF6E;font-weight:bold"
            if v == "SHORT": return "background-color:rgba(255,51,88,0.12);color:#FF3358;font-weight:bold"
            return "color:#3D5268"
        st.dataframe(df_tbl.style.map(_cs, subset=["Señal"]),
                     use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown("""
<div style='text-align:center;padding:24px;color:#3D5268;font-size:9px;
            border-top:1px solid #192233;margin-top:24px;
            font-family:"IBM Plex Mono",monospace;letter-spacing:1px;line-height:2'>
  CRYPTOPERP TERMINAL v2 · OKX PUBLIC API (PERPETUAL SWAPS) + COINGECKO + ALTERNATIVE.ME<br>
  ESTRATEGIA: CONFLUENCIA MULTI-INDICADOR · INSPIRADO EN MICHAËL VAN DE POPPE · RIESGO BAJO/MEDIO<br>
  <span style='color:#FF3358'>⚠ SOLO USO EDUCATIVO/PERSONAL — NO CONSTITUYE ASESORÍA FINANCIERA</span>
</div>
""", unsafe_allow_html=True)
