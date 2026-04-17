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
    page_title="CryptoPerp Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');
:root {
    --bg:#0a0e1a; --panel:#111827; --border:#1f2d40;
    --accent:#00d4aa; --accent2:#f59e0b;
    --red:#ef4444; --green:#22c55e;
    --text:#e2e8f0; --muted:#64748b;
}
html,body,.stApp{background-color:var(--bg)!important;font-family:'Space Mono',monospace;color:var(--text);}
.stApp>header{background:transparent!important;}
[data-testid="stSidebar"]{background:var(--panel)!important;border-right:1px solid var(--border);}
.stSelectbox>div>div{background:var(--panel)!important;border:1px solid var(--border)!important;color:var(--text)!important;}
.metric-card{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:16px;text-align:center;}
.metric-label{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;}
.metric-value{font-size:22px;font-weight:700;font-family:'Syne',sans-serif;}
.metric-sub{font-size:11px;color:var(--muted);margin-top:2px;}
.signal-long{background:rgba(34,197,94,.15);border:1px solid var(--green);color:var(--green);border-radius:6px;padding:8px 20px;font-size:18px;font-weight:700;letter-spacing:2px;font-family:'Syne',sans-serif;}
.signal-short{background:rgba(239,68,68,.15);border:1px solid var(--red);color:var(--red);border-radius:6px;padding:8px 20px;font-size:18px;font-weight:700;letter-spacing:2px;font-family:'Syne',sans-serif;}
.signal-neutral{background:rgba(100,116,139,.15);border:1px solid var(--muted);color:var(--muted);border-radius:6px;padding:8px 20px;font-size:18px;font-weight:700;letter-spacing:2px;font-family:'Syne',sans-serif;}
.indicator-row{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;border-bottom:1px solid var(--border);font-size:12px;}
.indicator-row:last-child{border-bottom:none;}
.ind-bullish{color:var(--green);font-weight:700;}
.ind-bearish{color:var(--red);font-weight:700;}
.ind-neutral{color:var(--muted);}
.dash-title{font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:var(--accent);letter-spacing:-.5px;}
.dash-subtitle{font-size:11px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;}
.conf-bar-container{background:var(--border);border-radius:4px;height:8px;width:100%;margin:4px 0;}
.conf-bar-fill-bull{background:var(--green);height:100%;border-radius:4px;}
.conf-bar-fill-bear{background:var(--red);height:100%;border-radius:4px;}
.section-header{font-size:10px;color:var(--accent);text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid var(--border);padding-bottom:6px;margin-bottom:12px;}
#MainMenu,footer,.stDeployButton{display:none!important;}
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

# OKX swap (perpetual futures) symbol format
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
# API — OKX (primary, works from GCP/Streamlit Cloud)
# ─────────────────────────────────────────────

@st.cache_data(ttl=60)
def fetch_klines(okx_id: str, tf_label: str, limit: int = 200) -> pd.DataFrame:
    """
    OKX swap OHLCV.  Falls back to OKX spot, then CoinGecko daily.
    tf_label is the user-facing key ('15m','1h','4h','1d').
    """
    bar = TIMEFRAMES.get(tf_label, "1H")          # e.g. '1H'
    swap_sym = to_swap(okx_id)                    # e.g. 'BTC-USDT-SWAP'

    # 1. OKX Perpetual Swap
    try:
        r = requests.get(
            f"{OKX_BASE}/api/v5/market/candles",
            params={"instId": swap_sym, "bar": bar, "limit": limit},
            headers=HDR, timeout=10,
        )
        if r.status_code == 200:
            rows = r.json().get("data", [])
            if len(rows) >= 20:
                # OKX returns newest-first: [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]
                df = pd.DataFrame(list(reversed(rows)),
                                  columns=["ts","open","high","low","close","vol","volCcy","volQ","confirm"])
                for c in ["open","high","low","close","vol"]:
                    df[c] = df[c].astype(float)
                df["open_time"] = pd.to_datetime(df["ts"].astype(int), unit="ms")
                df.rename(columns={"vol": "volume"}, inplace=True)
                return df[["open_time","open","high","low","close","volume"]].tail(200)
    except Exception:
        pass

    # 2. OKX Spot (same candle format, slightly different liquidity)
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

    # 3. CoinGecko daily OHLC (last resort, daily only)
    cg_id = CG_IDS.get(okx_id, "")
    if cg_id:
        try:
            r = requests.get(
                f"{CG_BASE}/coins/{cg_id}/ohlc",
                params={"vs_currency": "usd", "days": "30"},
                headers=HDR, timeout=12,
            )
            if r.status_code == 200:
                rows = r.json()  # [[ts, o, h, l, c], ...]
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
    """24h ticker from OKX swap, then spot."""
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
    """Current funding rate from OKX perpetual swap."""
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
    """Open interest in contracts from OKX."""
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
# SIGNAL ENGINE  (Van de Poppe confluencia)
# ─────────────────────────────────────────────

def evaluate_signals(ind: dict, funding: float, oi_change_pct: float, fg: dict) -> dict:
    if not ind:
        return {}
    p = ind["price"]
    s = {}

    # 1. Trend vs EMA200
    if p > ind["ema200"] * 1.005:
        s["Trend (EMA200)"] = (1,  "Bullish — precio sobre EMA200")
    elif p < ind["ema200"] * 0.995:
        s["Trend (EMA200)"] = (-1, "Bearish — precio bajo EMA200")
    else:
        s["Trend (EMA200)"] = (0,  "Neutral — precio en EMA200")

    # 2. EMA stack 20/50
    if ind["ema20"] > ind["ema50"]:
        s["EMA Stack (20/50)"] = (1,  "Bullish — EMA20 > EMA50")
    elif ind["ema20"] < ind["ema50"]:
        s["EMA Stack (20/50)"] = (-1, "Bearish — EMA20 < EMA50")
    else:
        s["EMA Stack (20/50)"] = (0,  "Neutral")

    # 3. RSI
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

    # 4. MACD
    if ind["macd_hist"] > 0 and ind["macd"] > ind["macd_signal"]:
        s["MACD"] = (1,  "Bullish — histograma positivo")
    elif ind["macd_hist"] < 0 and ind["macd"] < ind["macd_signal"]:
        s["MACD"] = (-1, "Bearish — histograma negativo")
    else:
        s["MACD"] = (0,  "Neutral — cruce en progreso")

    # 5. Bollinger Bands
    bb_pct = (p - ind["bb_lower"]) / (ind["bb_upper"] - ind["bb_lower"] + 1e-10)
    if bb_pct < 0.2:
        s["Bollinger Bands"] = (1,  f"Bullish — precio en banda baja ({bb_pct:.0%})")
    elif bb_pct > 0.8:
        s["Bollinger Bands"] = (-1, f"Bearish — precio en banda alta ({bb_pct:.0%})")
    else:
        s["Bollinger Bands"] = (0,  f"Neutral ({bb_pct:.0%} del rango BB)")

    # 6. Volumen
    vr = ind["vol_current"] / (ind["vol_avg20"] + 1e-10)
    if vr > 1.3:
        dir_ = s.get("EMA Stack (20/50)", (0,))[0]
        if   dir_ ==  1: s["Volumen"] = (1,  f"Bullish — {vr:.1f}x volumen promedio")
        elif dir_ == -1: s["Volumen"] = (-1, f"Bearish — {vr:.1f}x volumen promedio")
        else:            s["Volumen"] = (0,  f"Alto volumen, sin dir. ({vr:.1f}x)")
    else:
        s["Volumen"] = (0, f"Normal ({vr:.1f}x promedio)")

    # 7. Funding Rate
    if funding < -0.05:
        s["Funding Rate"] = (1,  f"Bullish — negativo ({funding:.3f}%)")
    elif funding > 0.1:
        s["Funding Rate"] = (-1, f"Bearish — alto ({funding:.3f}%)")
    else:
        s["Funding Rate"] = (0,  f"Neutral ({funding:.3f}%)")

    # 8. Fear & Greed
    fv = fg.get("value", 50)
    if fv < 25:
        s["Fear & Greed"] = (1,  f"Bullish — miedo extremo ({fv})")
    elif fv > 75:
        s["Fear & Greed"] = (-1, f"Bearish — codicia extrema ({fv})")
    else:
        s["Fear & Greed"] = (0,  f"Neutral ({fv} — {fg.get('label','')})")

    # 9. Open Interest (solo si hay snapshot previo)
    if abs(oi_change_pct) >= 0.3:
        dir_ = s.get("EMA Stack (20/50)", (0,))[0]
        if oi_change_pct > 0 and dir_ ==  1:
            s["Open Interest"] = (1,  f"Bullish — OI +{oi_change_pct:.1f}% (nuevos longs)")
        elif oi_change_pct > 0 and dir_ == -1:
            s["Open Interest"] = (-1, f"Bearish — OI +{oi_change_pct:.1f}% (nuevos shorts)")
        elif oi_change_pct < 0 and dir_ ==  1:
            s["Open Interest"] = (1,  f"Bull squeeze — OI {oi_change_pct:.1f}% (shorts cubriendo)")
        elif oi_change_pct < 0 and dir_ == -1:
            s["Open Interest"] = (-1, f"Bearish — OI {oi_change_pct:.1f}% (longs liquidando)")
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
# CHART
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
        increasing_line_color="#22c55e", decreasing_line_color="#ef4444",
        increasing_fillcolor="rgba(34,197,94,.5)", decreasing_fillcolor="rgba(239,68,68,.5)",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=t, y=ind["_bb_upper"], name="BB",
        line=dict(color="rgba(100,116,139,.5)", width=1, dash="dot"), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=t, y=ind["_bb_lower"], name="BB",
        line=dict(color="rgba(100,116,139,.5)", width=1, dash="dot"),
        fill="tonexty", fillcolor="rgba(100,116,139,.05)", showlegend=False), row=1, col=1)

    for p, color in [("20","#f59e0b"), ("50","#60a5fa"), ("200","#c084fc")]:
        key = f"_ema{p}"
        if key in ind:
            fig.add_trace(go.Scatter(x=t, y=ind[key], name=f"EMA{p}",
                line=dict(color=color, width=1.5), opacity=0.85), row=1, col=1)

    fig.add_trace(go.Scatter(x=t, y=ind["_rsi"], name="RSI",
        line=dict(color="#00d4aa", width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line=dict(color="#ef4444", dash="dash", width=1), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="#22c55e", dash="dash", width=1), row=2, col=1)

    hist_colors = ["rgba(34,197,94,.7)" if v>=0 else "rgba(239,68,68,.7)" for v in ind["_macd_hist"]]
    fig.add_trace(go.Bar(x=t, y=ind["_macd_hist"], marker_color=hist_colors, showlegend=False), row=3, col=1)
    fig.add_trace(go.Scatter(x=t, y=ind["_macd"],        name="MACD",   line=dict(color="#00d4aa", width=1.5)), row=3, col=1)
    fig.add_trace(go.Scatter(x=t, y=ind["_macd_signal"], name="Signal", line=dict(color="#f59e0b", width=1.5)), row=3, col=1)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,.6)",
        font=dict(family="Space Mono", color="#e2e8f0", size=11),
        legend=dict(bgcolor="rgba(17,24,39,.8)", bordercolor="#1f2d40", borderwidth=1, font=dict(size=10)),
        xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=20,b=0), height=520, hovermode="x unified",
    )
    for i in range(1, 4):
        fig.update_xaxes(gridcolor="#1f2d40", zeroline=False, showspikes=True,
                         spikecolor="#64748b", row=i, col=1)
        fig.update_yaxes(gridcolor="#1f2d40", zeroline=False, row=i, col=1)
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
    icon = {"LONG":"▲ LONG","SHORT":"▼ SHORT","NEUTRAL":"◆ NEUTRAL","SIN DATOS":"– –"}.get(action, action)
    return f'<span class="{cls}">{icon}</span>'

def ind_html(v, desc):
    if v ==  1: return f'<span class="ind-bullish">▲ BULL</span> <span style="color:#94a3b8;font-size:11px">{desc}</span>'
    if v == -1: return f'<span class="ind-bearish">▼ BEAR</span> <span style="color:#94a3b8;font-size:11px">{desc}</span>'
    return          f'<span class="ind-neutral">◆ NEUT</span> <span style="color:#94a3b8;font-size:11px">{desc}</span>'


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="dash-title">⚡ CryptoPerp</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-subtitle">OKX Futures Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")

    selected_label  = st.selectbox("🪙 Seleccionar Par", list(CRYPTOS.keys()), index=0)
    selected_okx_id = CRYPTOS[selected_label]
    selected_tf     = st.selectbox("⏱ Timeframe", list(TIMEFRAMES.keys()), index=2)

    st.markdown("---")
    st.markdown('<div class="section-header">ESTRATEGIA</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px;color:#94a3b8;line-height:1.7'>
    Basada en <b style='color:#00d4aa'>Michaël van de Poppe</b><br>
    Confluencia multi-indicador:<br>
    • ≥ 4 señales bull → <span style='color:#22c55e'>LONG</span><br>
    • ≥ 4 señales bear → <span style='color:#ef4444'>SHORT</span><br>
    • Riesgo: Bajo/Medio<br>
    • Datos: OKX Perps + CoinGecko<br><br>
    <span style='color:#f59e0b'>⚠ No es asesoría financiera.</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔃 Actualizar datos"):
        st.cache_data.clear()
        for k in [k for k in st.session_state if k.startswith("prev_oi_")]:
            del st.session_state[k]
        st.rerun()
    st.markdown(f'<div style="font-size:10px;color:#475569;margin-top:8px">Actualizado: {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────

with st.spinner("⏳ Cargando datos de mercado (OKX)..."):
    df      = fetch_klines(selected_okx_id, selected_tf, limit=200)
    ticker  = fetch_ticker(selected_okx_id)
    funding = fetch_funding_rate(selected_okx_id)
    fg      = fetch_fear_greed()
    ind     = compute_indicators(df)

    # Open Interest delta
    cur_oi    = fetch_open_interest(selected_okx_id)
    _oi_key   = f"prev_oi_{selected_okx_id}"
    prev_oi   = st.session_state.get(_oi_key, 0.0)
    oi_chg    = ((cur_oi - prev_oi) / prev_oi * 100) if prev_oi > 0 else 0.0
    if cur_oi > 0:
        st.session_state[_oi_key] = cur_oi

    signals = evaluate_signals(ind, funding, oi_chg, fg)
    action, score, bull_count, bear_count = get_recommendation(signals)

# CoinGecko fundamentals
cg_data = {}
cg_id   = CG_IDS.get(selected_okx_id, "")
if cg_id:
    cg_data = fetch_cg_coin(cg_id)

# ── Status banner ──────────────────────────────────────────────────────
klines_ok = not df.empty
ticker_ok = bool(ticker.get("lastPrice"))
source    = ticker.get("_source", "—")

if not klines_ok or not ticker_ok:
    st.error(
        f"⚠️ No se pudieron obtener datos de mercado para **{selected_label}**. "
        "Haz clic en **🔃 Actualizar datos** en el sidebar. "
        f"Fuente intentada: OKX swap → OKX spot → CoinGecko"
    )
else:
    src_label = "OKX Swap (Perps)" if "SWAP" in source else "OKX Spot"
    st.success(f"✅ Datos cargados desde **{src_label}** · {len(df)} velas · {selected_tf}", icon=None)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

c1, c2, c3 = st.columns([3, 2, 2])
with c1:
    price_str  = fmt_price(ind.get("price", 0)) if ind else "—"
    chg        = float(ticker.get("priceChangePercent", 0)) if ticker else 0
    chg_color  = "#22c55e" if chg >= 0 else "#ef4444"
    chg_sign   = "+" if chg >= 0 else ""
    st.markdown(f"""
    <div style='margin-top:4px'>
      <span style='font-family:Syne;font-size:32px;font-weight:800;color:#e2e8f0'>{price_str}</span>
      <span style='color:{chg_color};font-size:16px;margin-left:12px'>{chg_sign}{chg:.2f}%</span>
      <div style='color:#64748b;font-size:12px;margin-top:4px'>{selected_label} · {selected_tf} · OKX Perpetual Swap</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown("""<div style='margin-top:6px'>
    <div style='font-size:10px;color:#64748b;margin-bottom:6px;letter-spacing:1px;text-transform:uppercase'>SEÑAL RECOMENDADA</div>""",
    unsafe_allow_html=True)
    st.markdown(signal_html(action), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    total = len(signals) if signals else 1
    bp    = int(bull_count / total * 100) if signals else 0
    brp   = int(bear_count / total * 100) if signals else 0
    st.markdown(f"""
    <div style='margin-top:6px'>
      <div style='font-size:10px;color:#64748b;margin-bottom:6px;letter-spacing:1px;text-transform:uppercase'>CONFLUENCIA</div>
      <div style='font-size:12px;margin-bottom:4px;color:#22c55e'>▲ Bull: {bull_count}/{total} ({bp}%)</div>
      <div class='conf-bar-container'><div class='conf-bar-fill-bull' style='width:{bp}%'></div></div>
      <div style='font-size:12px;margin-bottom:4px;color:#ef4444;margin-top:6px'>▼ Bear: {bear_count}/{total} ({brp}%)</div>
      <div class='conf-bar-container'><div class='conf-bar-fill-bear' style='width:{brp}%'></div></div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin:12px 0;border-top:1px solid #1f2d40'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────

m1, m2, m3, m4, m5, m6 = st.columns(6)
oi_sub = (f"{oi_chg:+.2f}% vs antes" if oi_chg != 0 else "primer snapshot")
for col, lbl, val, sub in [
    (m1, "Volumen 24h",   fmt_large(float(ticker.get("quoteVolume","0"))) if ticker else "—", "USDT"),
    (m2, "RSI (14)",      f"{ind.get('rsi',0):.1f}" if ind else "—", "neutro ≈ 50"),
    (m3, "Funding Rate",  f"{funding:+.4f}%", "cada 8h"),
    (m4, "ATR (14)",      fmt_price(ind.get("atr",0)) if ind else "—", "volatilidad"),
    (m5, "Fear & Greed",  str(fg.get("value",50)), fg.get("label","—")),
    (m6, "Open Interest", f"{cur_oi:,.0f}" if cur_oi else "—", oi_sub),
]:
    with col:
        st.markdown(f"""
        <div class='metric-card'>
          <div class='metric-label'>{lbl}</div>
          <div class='metric-value'>{val}</div>
          <div class='metric-sub'>{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CHART + SIGNALS
# ─────────────────────────────────────────────

ch_col, sig_col = st.columns([3, 1])

with ch_col:
    st.markdown('<div class="section-header">GRÁFICO DE PRECIO</div>', unsafe_allow_html=True)
    if klines_ok and ind:
        fig = build_chart(df, ind)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})  # noqa
    else:
        st.warning("Sin datos para el gráfico. Intenta actualizar.")

with sig_col:
    st.markdown('<div class="section-header">ANÁLISIS DE SEÑALES</div>', unsafe_allow_html=True)
    if signals:
        for name, (sv, desc) in signals.items():
            st.markdown(f"""
            <div class='indicator-row'>
              <div>
                <div style='font-size:11px;color:#e2e8f0;margin-bottom:2px'>{name}</div>
                {ind_html(sv, desc)}
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#64748b;font-size:13px;padding:12px">Sin datos de señales.<br>Presiona <b>🔃 Actualizar</b>.</div>',
                    unsafe_allow_html=True)

    # Gestión de riesgo
    if ind and action not in ("SIN DATOS", "NEUTRAL"):
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">GESTIÓN DE RIESGO</div>', unsafe_allow_html=True)
        price = ind["price"]; atr = ind.get("atr", 0)
        if action == "LONG":
            sl, tp1, tp2 = price - 1.5*atr, price + 2.0*atr, price + 3.5*atr
            sl_c, tp_c = "#ef4444", "#22c55e"
        else:
            sl, tp1, tp2 = price + 1.5*atr, price - 2.0*atr, price - 3.5*atr
            sl_c, tp_c = "#22c55e", "#ef4444"
        st.markdown(f"""
        <div style='font-size:11px;line-height:2.1'>
          <div style='color:{sl_c}'>🛑 Stop Loss: {fmt_price(sl)}</div>
          <div style='color:{tp_c}'>🎯 TP1: {fmt_price(tp1)}</div>
          <div style='color:{tp_c}'>🎯 TP2: {fmt_price(tp2)}</div>
          <div style='color:#f59e0b'>📊 R/R ratio: 1:2</div>
          <div style='color:#64748b;font-size:10px;margin-top:4px'>1.5×ATR stop · 2×/3.5×ATR targets</div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FUNDAMENTALS
# ─────────────────────────────────────────────

st.markdown("<div style='margin:16px 0;border-top:1px solid #1f2d40'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-header">DATOS FUNDAMENTALES</div>', unsafe_allow_html=True)

md        = cg_data.get("market_data", {}) if cg_data else {}
mkt_cap   = md.get("market_cap",{}).get("usd",0) if md else 0
rank      = cg_data.get("market_cap_rank","—") if cg_data else "—"
circ_s    = md.get("circulating_supply",0) if md else 0
max_s     = md.get("max_supply",None) if md else None
ath_p     = md.get("ath",{}).get("usd",0) if md else 0
ath_c     = md.get("ath_change_percentage",{}).get("usd",0) if md else 0
sup_str   = (f"{circ_s/1e6:.1f}M" + (f" / {max_s/1e6:.1f}M" if max_s else "")) if circ_s else "—"

f1,f2,f3,f4 = st.columns(4)
fv = fg.get("value",50)
fg_col = "#22c55e" if fv<=25 else "#ef4444" if fv>=75 else "#f59e0b"

for col, lbl, val, sub in [
    (f1,"Market Cap",   fmt_large(mkt_cap) if mkt_cap else "—",      f"Rank #{rank}"),
    (f2,"Supply Circ.", sup_str,                                       "Limitado" if max_s else "Sin límite"),
    (f3,"ATH",          fmt_price(ath_p) if ath_p else "—",
                        f'<span style="color:{"#ef4444" if ath_c<0 else "#22c55e"}">{ath_c:.1f}% desde ATH</span>'),
    (f4,"Fear & Greed", f'<span style="color:{fg_col};font-size:28px">{fv}</span>', fg.get("label","—")),
]:
    with col:
        st.markdown(f"""
        <div class='metric-card'>
          <div class='metric-label'>{lbl}</div>
          <div class='metric-value' style='font-size:16px'>{val}</div>
          <div class='metric-sub'>{sub}</div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RESUMEN TODOS LOS PARES
# ─────────────────────────────────────────────

st.markdown("<div style='margin:16px 0;border-top:1px solid #1f2d40'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-header">RESUMEN DE SEÑALES — TODOS LOS PARES</div>', unsafe_allow_html=True)

with st.expander("📋 Ver tabla de señales rápidas (20 pares, timeframe 4h)", expanded=False):
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
            rows.append({"Par":lbl, "Precio":fmt_price(ind_t.get("price",0)) if ind_t else "—",
                         "24h %":f"{chg_t:+.2f}%", "RSI":f"{ind_t.get('rsi',0):.1f}" if ind_t else "—",
                         "Funding":f"{fr_t:+.4f}%", "Bull":bc, "Bear":brc, "Señal":act_t})
        except Exception:
            rows.append({"Par":lbl,"Precio":"—","24h %":"—","RSI":"—","Funding":"—","Bull":0,"Bear":0,"Señal":"ERROR"})
        time.sleep(0.05)
    prog.empty()
    if rows:
        df_tbl = pd.DataFrame(rows)
        def _cs(v):
            if v=="LONG":  return "background-color:rgba(34,197,94,.15);color:#22c55e;font-weight:bold"
            if v=="SHORT": return "background-color:rgba(239,68,68,.15);color:#ef4444;font-weight:bold"
            return "color:#64748b"
        st.dataframe(df_tbl.style.map(_cs, subset=["Señal"]),
                     use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown("""
<div style='text-align:center;padding:20px;color:#475569;font-size:10px;border-top:1px solid #1f2d40;margin-top:24px'>
  ⚡ CryptoPerp Dashboard v2 · Datos: <b>OKX Public API</b> (Perpetual Swaps) + CoinGecko free tier + alternative.me<br>
  Estrategia: confluencia multi-indicador · Inspirado en Michaël van de Poppe · Riesgo bajo/medio<br>
  <span style='color:#ef4444'>⚠ Solo uso educativo/personal. No constituye asesoría financiera.</span>
</div>
""", unsafe_allow_html=True)
