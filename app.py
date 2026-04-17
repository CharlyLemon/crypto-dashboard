import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
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
    --bg: #0a0e1a;
    --panel: #111827;
    --border: #1f2d40;
    --accent: #00d4aa;
    --accent2: #f59e0b;
    --red: #ef4444;
    --green: #22c55e;
    --text: #e2e8f0;
    --muted: #64748b;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    font-family: 'Space Mono', monospace;
    color: var(--text);
}

.stApp > header { background: transparent !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--panel) !important;
    border-right: 1px solid var(--border);
}

/* Selectbox and widgets */
.stSelectbox > div > div {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}

/* Metric cards */
.metric-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}

.metric-label {
    font-size: 10px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 22px;
    font-weight: 700;
    font-family: 'Syne', sans-serif;
}

.metric-sub {
    font-size: 11px;
    color: var(--muted);
    margin-top: 2px;
}

/* Signal badge */
.signal-long {
    background: rgba(34,197,94,0.15);
    border: 1px solid var(--green);
    color: var(--green);
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 2px;
    font-family: 'Syne', sans-serif;
}

.signal-short {
    background: rgba(239,68,68,0.15);
    border: 1px solid var(--red);
    color: var(--red);
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 2px;
    font-family: 'Syne', sans-serif;
}

.signal-neutral {
    background: rgba(100,116,139,0.15);
    border: 1px solid var(--muted);
    color: var(--muted);
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 2px;
    font-family: 'Syne', sans-serif;
}

/* Indicator row */
.indicator-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    border-bottom: 1px solid var(--border);
    font-size: 12px;
}

.indicator-row:last-child { border-bottom: none; }

.ind-bullish { color: var(--green); font-weight: 700; }
.ind-bearish { color: var(--red); font-weight: 700; }
.ind-neutral { color: var(--muted); }

/* Title */
.dash-title {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: var(--accent);
    letter-spacing: -0.5px;
}

.dash-subtitle {
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* Confluence bar */
.conf-bar-container {
    background: var(--border);
    border-radius: 4px;
    height: 8px;
    width: 100%;
    margin: 4px 0;
}

.conf-bar-fill-bull {
    background: var(--green);
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s;
}

.conf-bar-fill-bear {
    background: var(--red);
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s;
}

/* Section headers */
.section-header {
    font-size: 10px;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 2px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
    margin-bottom: 12px;
}

/* Stale warning */
.stale-warn {
    font-size: 11px;
    color: var(--accent2);
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 4px;
    padding: 6px 10px;
}

/* Hide streamlit elements */
#MainMenu, footer, .stDeployButton { display: none !important; }

/* Plotly chart background */
.js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
CRYPTOS = {
    "BTC/USDT": "BTCUSDT",
    "ETH/USDT": "ETHUSDT",
    "BNB/USDT": "BNBUSDT",
    "SOL/USDT": "SOLUSDT",
    "XRP/USDT": "XRPUSDT",
    "ADA/USDT": "ADAUSDT",
    "AVAX/USDT": "AVAXUSDT",
    "DOGE/USDT": "DOGEUSDT",
    "MATIC/USDT": "MATICUSDT",
    "LINK/USDT": "LINKUSDT",
    "DOT/USDT": "DOTUSDT",
    "UNI/USDT": "UNIUSDT",
    "LTC/USDT": "LTCUSDT",
    "ATOM/USDT": "ATOMUSDT",
    "FIL/USDT": "FILUSDT",
    "APT/USDT": "APTUSDT",
    "ARB/USDT": "ARBUSDT",
    "OP/USDT": "OPUSDT",
    "INJ/USDT": "INJUSDT",
    "SUI/USDT": "SUIUSDT",
}

TIMEFRAMES = {
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
}

BINANCE_FUTURES  = "https://fapi.binance.com"
BINANCE_SPOT     = "https://api.binance.com"
BYBIT_BASE       = "https://api.bybit.com"
COINGECKO_BASE   = "https://api.coingecko.com/api/v3"

HEADERS = {"User-Agent": "Mozilla/5.0 CryptoPerpDashboard/1.0 (compatible)"}

# Bybit interval codes for each timeframe
BYBIT_INTERVALS = {"15m": "15", "1h": "60", "4h": "240", "1d": "D"}

# Symbols renamed on Bybit vs Binance
BYBIT_SYMBOL_MAP = {
    "MATICUSDT": "POLUSDT",  # Polygon rebranded to POL
}

CG_IDS = {
    "BTCUSDT": "bitcoin", "ETHUSDT": "ethereum", "BNBUSDT": "binancecoin",
    "SOLUSDT": "solana", "XRPUSDT": "ripple", "ADAUSDT": "cardano",
    "AVAXUSDT": "avalanche-2", "DOGEUSDT": "dogecoin", "MATICUSDT": "matic-network",
    "LINKUSDT": "chainlink", "DOTUSDT": "polkadot", "UNIUSDT": "uniswap",
    "LTCUSDT": "litecoin", "ATOMUSDT": "cosmos", "FILUSDT": "filecoin",
    "APTUSDT": "aptos", "ARBUSDT": "arbitrum", "OPUSDT": "optimism",
    "INJUSDT": "injective-protocol", "SUIUSDT": "sui",
}

# ─────────────────────────────────────────────
# API FUNCTIONS  (Binance Futures → Bybit → Binance Spot)
# ─────────────────────────────────────────────

def _parse_klines(data: list) -> pd.DataFrame:
    """Convert raw Binance kline list to DataFrame."""
    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "qv", "trades", "tbbv", "tbqv", "ignore"
    ])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    return df.tail(200)


def _parse_bybit_klines(data: list) -> pd.DataFrame:
    """Convert raw Bybit kline list to DataFrame.
    Bybit returns [startTime, open, high, low, close, volume, turnover] newest-first."""
    df = pd.DataFrame(list(reversed(data)), columns=[
        "open_time", "open", "high", "low", "close", "volume", "turnover"
    ])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"].astype(int), unit="ms")
    return df.tail(200)


def _normalize_bybit_ticker(t: dict) -> dict:
    """Map Bybit ticker fields to Binance-compatible names used by the rest of the app."""
    return {
        "lastPrice":           t.get("lastPrice", "0"),
        "priceChangePercent":  str(round(float(t.get("price24hPcnt", 0)) * 100, 4)),
        "quoteVolume":         t.get("turnover24h", "0"),
        "volume":              t.get("volume24h", "0"),
    }


@st.cache_data(ttl=60)
def fetch_klines(symbol: str, interval: str, limit: int = 200) -> pd.DataFrame:
    """Fetch OHLCV — tries Binance Futures, then Bybit, then Binance Spot."""
    # 1. Binance Futures
    try:
        r = requests.get(
            f"{BINANCE_FUTURES}/fapi/v1/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            headers=HEADERS, timeout=6,
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 10:
                return _parse_klines(data)
    except Exception:
        pass
    # 2. Bybit (works from cloud/datacenter IPs where Binance is blocked)
    try:
        bybit_sym      = BYBIT_SYMBOL_MAP.get(symbol, symbol)
        bybit_interval = BYBIT_INTERVALS.get(interval, interval)
        r = requests.get(
            f"{BYBIT_BASE}/v5/market/kline",
            params={"category": "linear", "symbol": bybit_sym,
                    "interval": bybit_interval, "limit": limit},
            headers=HEADERS, timeout=8,
        )
        if r.status_code == 200:
            result = r.json().get("result", {})
            data   = result.get("list", [])
            if len(data) > 10:
                return _parse_bybit_klines(data)
    except Exception:
        pass
    # 3. Binance Spot (last resort)
    try:
        r = requests.get(
            f"{BINANCE_SPOT}/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            headers=HEADERS, timeout=6,
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 10:
                return _parse_klines(data)
    except Exception:
        pass
    return pd.DataFrame()


@st.cache_data(ttl=30)
def fetch_ticker(symbol: str) -> dict:
    """Fetch 24h ticker — tries Binance Futures, then Bybit, then Binance Spot."""
    # 1. Binance Futures
    try:
        r = requests.get(f"{BINANCE_FUTURES}/fapi/v1/ticker/24hr",
                         params={"symbol": symbol}, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            d = r.json()
            if d.get("lastPrice"):
                return d
    except Exception:
        pass
    # 2. Bybit
    try:
        bybit_sym = BYBIT_SYMBOL_MAP.get(symbol, symbol)
        r = requests.get(
            f"{BYBIT_BASE}/v5/market/tickers",
            params={"category": "linear", "symbol": bybit_sym},
            headers=HEADERS, timeout=6,
        )
        if r.status_code == 200:
            items = r.json().get("result", {}).get("list", [])
            if items:
                return _normalize_bybit_ticker(items[0])
    except Exception:
        pass
    # 3. Binance Spot
    try:
        r = requests.get(f"{BINANCE_SPOT}/api/v3/ticker/24hr",
                         params={"symbol": symbol}, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


@st.cache_data(ttl=60)
def fetch_funding_rate(symbol: str) -> float:
    """Fetch latest funding rate — tries Binance Futures, then Bybit."""
    # 1. Binance Futures
    try:
        r = requests.get(f"{BINANCE_FUTURES}/fapi/v1/fundingRate",
                         params={"symbol": symbol, "limit": 1}, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            data = r.json()
            return float(data[0]["fundingRate"]) * 100 if data else 0.0
    except Exception:
        pass
    # 2. Bybit
    try:
        bybit_sym = BYBIT_SYMBOL_MAP.get(symbol, symbol)
        r = requests.get(
            f"{BYBIT_BASE}/v5/market/funding/history",
            params={"category": "linear", "symbol": bybit_sym, "limit": 1},
            headers=HEADERS, timeout=6,
        )
        if r.status_code == 200:
            items = r.json().get("result", {}).get("list", [])
            return float(items[0]["fundingRate"]) * 100 if items else 0.0
    except Exception:
        pass
    return 0.0


@st.cache_data(ttl=60)
def fetch_open_interest(symbol: str) -> float:
    """Fetch open interest — tries Binance Futures, then Bybit."""
    # 1. Binance Futures
    try:
        r = requests.get(f"{BINANCE_FUTURES}/fapi/v1/openInterest",
                         params={"symbol": symbol}, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            return float(r.json().get("openInterest", 0))
    except Exception:
        pass
    # 2. Bybit
    try:
        bybit_sym = BYBIT_SYMBOL_MAP.get(symbol, symbol)
        r = requests.get(
            f"{BYBIT_BASE}/v5/market/open-interest",
            params={"category": "linear", "symbol": bybit_sym,
                    "intervalTime": "5min", "limit": 1},
            headers=HEADERS, timeout=6,
        )
        if r.status_code == 200:
            items = r.json().get("result", {}).get("list", [])
            return float(items[0]["openInterest"]) if items else 0.0
    except Exception:
        pass
    return 0.0


@st.cache_data(ttl=300)
def fetch_fear_greed() -> dict:
    """Fetch Fear & Greed index from alternative.me."""
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1",
                         headers=HEADERS, timeout=8)
        if r.status_code == 200:
            d = r.json()["data"][0]
            return {"value": int(d["value"]), "label": d["value_classification"], "ok": True}
    except Exception:
        pass
    return {"value": 50, "label": "Neutral", "ok": False}


@st.cache_data(ttl=300)
def fetch_cg_coin(cg_id: str) -> dict:
    """Fetch market data from CoinGecko (free tier)."""
    try:
        url = f"{COINGECKO_BASE}/coins/{cg_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false",
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=12)
        if r.status_code == 429:
            # Rate limited — return cached stub so the rest of the UI still renders
            return {}
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


# ─────────────────────────────────────────────
# TECHNICAL INDICATORS
# ─────────────────────────────────────────────

def calc_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def calc_macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = calc_ema(series, fast)
    ema_slow = calc_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calc_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calc_bollinger(series: pd.Series, period=20, std_dev=2):
    sma = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = sma + std_dev * std
    lower = sma - std_dev * std
    return upper, sma, lower


def calc_atr(df: pd.DataFrame, period=14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.ewm(com=period - 1, adjust=False).mean()


def compute_indicators(df: pd.DataFrame) -> dict:
    """Compute all indicators and return dict of latest values."""
    if df.empty or len(df) < 50:
        return {}

    close = df["close"]
    vol = df["volume"]
    idx = -1  # latest candle

    ema20 = calc_ema(close, 20)
    ema50 = calc_ema(close, 50)
    ema200 = calc_ema(close, 200)
    rsi = calc_rsi(close, 14)
    macd_line, signal_line, histogram = calc_macd(close)
    bb_upper, bb_mid, bb_lower = calc_bollinger(close, 20, 2)
    atr = calc_atr(df, 14)
    vol_ma20 = vol.rolling(20).mean()

    price = close.iloc[idx]

    return {
        "price": price,
        "ema20": ema20.iloc[idx],
        "ema50": ema50.iloc[idx],
        "ema200": ema200.iloc[idx],
        "rsi": rsi.iloc[idx],
        "macd": macd_line.iloc[idx],
        "macd_signal": signal_line.iloc[idx],
        "macd_hist": histogram.iloc[idx],
        "bb_upper": bb_upper.iloc[idx],
        "bb_mid": bb_mid.iloc[idx],
        "bb_lower": bb_lower.iloc[idx],
        "atr": atr.iloc[idx],
        "vol_current": vol.iloc[idx],
        "vol_avg20": vol_ma20.iloc[idx],
        # raw series for chart
        "_ema20": ema20,
        "_ema50": ema50,
        "_ema200": ema200,
        "_rsi": rsi,
        "_macd": macd_line,
        "_macd_signal": signal_line,
        "_macd_hist": histogram,
        "_bb_upper": bb_upper,
        "_bb_mid": bb_mid,
        "_bb_lower": bb_lower,
    }


# ─────────────────────────────────────────────
# SIGNAL ENGINE (Van de Poppe confluence method)
# ─────────────────────────────────────────────

def evaluate_signals(ind: dict, funding: float, oi_change_pct: float, fg: dict) -> dict:
    """
    Score each indicator +1 (bullish), -1 (bearish), 0 (neutral).
    Confluence ≥ 4 bullish → LONG
    Confluence ≥ 4 bearish → SHORT
    oi_change_pct: % change in open interest since last refresh (0 = unknown/first load).
    """
    if not ind:
        return {}

    p = ind["price"]
    signals = {}

    # 1. Trend: Price vs EMA200
    if p > ind["ema200"] * 1.005:
        signals["Trend (EMA200)"] = (1, "Bullish — precio sobre EMA200")
    elif p < ind["ema200"] * 0.995:
        signals["Trend (EMA200)"] = (-1, "Bearish — precio bajo EMA200")
    else:
        signals["Trend (EMA200)"] = (0, "Neutral — precio en EMA200")

    # 2. EMA stack: EMA20 > EMA50
    if ind["ema20"] > ind["ema50"]:
        signals["EMA Stack (20/50)"] = (1, "Bullish — EMA20 > EMA50")
    elif ind["ema20"] < ind["ema50"]:
        signals["EMA Stack (20/50)"] = (-1, "Bearish — EMA20 < EMA50")
    else:
        signals["EMA Stack (20/50)"] = (0, "Neutral")

    # 3. RSI
    rsi = ind["rsi"]
    if rsi < 35:
        signals["RSI (14)"] = (1, f"Bullish — oversold ({rsi:.1f})")
    elif rsi > 65:
        signals["RSI (14)"] = (-1, f"Bearish — overbought ({rsi:.1f})")
    elif 45 < rsi < 55:
        signals["RSI (14)"] = (0, f"Neutral ({rsi:.1f})")
    elif rsi >= 55:
        signals["RSI (14)"] = (1, f"Bullish momentum ({rsi:.1f})")
    else:
        signals["RSI (14)"] = (-1, f"Bearish momentum ({rsi:.1f})")

    # 4. MACD
    if ind["macd_hist"] > 0 and ind["macd"] > ind["macd_signal"]:
        signals["MACD"] = (1, "Bullish — histograma positivo")
    elif ind["macd_hist"] < 0 and ind["macd"] < ind["macd_signal"]:
        signals["MACD"] = (-1, "Bearish — histograma negativo")
    else:
        signals["MACD"] = (0, "Neutral — cruce en progreso")

    # 5. Bollinger Bands
    bb_pct = (p - ind["bb_lower"]) / (ind["bb_upper"] - ind["bb_lower"] + 1e-10)
    if bb_pct < 0.2:
        signals["Bollinger Bands"] = (1, f"Bullish — precio en banda baja ({bb_pct:.0%})")
    elif bb_pct > 0.8:
        signals["Bollinger Bands"] = (-1, f"Bearish — precio en banda alta ({bb_pct:.0%})")
    else:
        signals["Bollinger Bands"] = (0, f"Neutral ({bb_pct:.0%} del rango BB)")

    # 6. Volume confirmation
    vol_ratio = ind["vol_current"] / (ind["vol_avg20"] + 1e-10)
    if vol_ratio > 1.3:
        # High volume confirms direction of EMA stack
        direction = signals["EMA Stack (20/50)"][0]
        if direction == 1:
            signals["Volumen"] = (1, f"Bullish — volumen +{vol_ratio:.1f}x promedio")
        elif direction == -1:
            signals["Volumen"] = (-1, f"Bearish — volumen +{vol_ratio:.1f}x promedio")
        else:
            signals["Volumen"] = (0, f"Alto volumen sin dirección clara ({vol_ratio:.1f}x)")
    else:
        signals["Volumen"] = (0, f"Volumen normal ({vol_ratio:.1f}x promedio)")

    # 7. Funding Rate (fundamental)
    if funding < -0.05:
        signals["Funding Rate"] = (1, f"Bullish — funding negativo ({funding:.3f}%) → longs pagados")
    elif funding > 0.1:
        signals["Funding Rate"] = (-1, f"Bearish — funding alto ({funding:.3f}%) → shorts favorecidos")
    else:
        signals["Funding Rate"] = (0, f"Neutral ({funding:.3f}%)")

    # 8. Fear & Greed
    fg_val = fg.get("value", 50)
    if fg_val < 25:
        signals["Fear & Greed"] = (1, f"Bullish — miedo extremo ({fg_val}) → oportunidad de compra")
    elif fg_val > 75:
        signals["Fear & Greed"] = (-1, f"Bearish — codicia extrema ({fg_val}) → precaución")
    else:
        signals["Fear & Greed"] = (0, f"Neutral ({fg_val} — {fg.get('label', '')})")

    # 9. Open Interest trend (only when we have a previous snapshot to compare)
    if abs(oi_change_pct) >= 0.3:
        trend_dir = signals.get("EMA Stack (20/50)", (0, ""))[0]
        if oi_change_pct > 0 and trend_dir == 1:
            signals["Open Interest"] = (1, f"Bullish — OI +{oi_change_pct:.1f}% con precio subiendo (nuevos longs)")
        elif oi_change_pct > 0 and trend_dir == -1:
            signals["Open Interest"] = (-1, f"Bearish — OI +{oi_change_pct:.1f}% con precio bajando (nuevos shorts)")
        elif oi_change_pct < 0 and trend_dir == 1:
            signals["Open Interest"] = (1, f"Bullish squeeze — OI {oi_change_pct:.1f}% (shorts cubriendo)")
        elif oi_change_pct < 0 and trend_dir == -1:
            signals["Open Interest"] = (-1, f"Bearish — OI {oi_change_pct:.1f}% (longs liquidando)")
        else:
            signals["Open Interest"] = (0, f"OI {oi_change_pct:+.1f}% sin confirmación de dirección")
    elif oi_change_pct != 0:
        signals["Open Interest"] = (0, f"OI estable ({oi_change_pct:+.2f}%)")
    # If oi_change_pct == 0 (first load), skip the OI signal entirely

    return signals


def get_recommendation(signals: dict) -> tuple:
    """Return (action, score, bull_count, bear_count)."""
    if not signals:
        return "SIN DATOS", 0, 0, 0
    bull = sum(1 for v, _ in signals.values() if v == 1)
    bear = sum(1 for v, _ in signals.values() if v == -1)
    total = len(signals)
    score = (bull - bear) / total

    if bull >= 4:
        action = "LONG"
    elif bear >= 4:
        action = "SHORT"
    else:
        action = "NEUTRAL"
    return action, score, bull, bear


# ─────────────────────────────────────────────
# CHART BUILDER
# ─────────────────────────────────────────────

def build_chart(df: pd.DataFrame, ind: dict, symbol: str) -> go.Figure:
    if df.empty or not ind:
        return go.Figure()

    times = df["open_time"]
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.25, 0.20],
        vertical_spacing=0.03,
        subplot_titles=("", "RSI (14)", "MACD"),
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=times, open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        name="OHLC",
        increasing_line_color="#22c55e",
        decreasing_line_color="#ef4444",
        increasing_fillcolor="rgba(34,197,94,0.5)",
        decreasing_fillcolor="rgba(239,68,68,0.5)",
    ), row=1, col=1)

    # Bollinger Bands
    fig.add_trace(go.Scatter(
        x=times, y=ind["_bb_upper"], name="BB Upper",
        line=dict(color="rgba(100,116,139,0.5)", width=1, dash="dot"), showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=times, y=ind["_bb_lower"], name="BB Lower",
        line=dict(color="rgba(100,116,139,0.5)", width=1, dash="dot"),
        fill="tonexty", fillcolor="rgba(100,116,139,0.05)", showlegend=False
    ), row=1, col=1)

    # EMAs
    colors_ema = {"20": "#f59e0b", "50": "#60a5fa", "200": "#c084fc"}
    for period, color in colors_ema.items():
        key = f"_ema{period}"
        if key in ind:
            fig.add_trace(go.Scatter(
                x=times, y=ind[key], name=f"EMA {period}",
                line=dict(color=color, width=1.5), opacity=0.85
            ), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(
        x=times, y=ind["_rsi"], name="RSI",
        line=dict(color="#00d4aa", width=1.5)
    ), row=2, col=1)
    fig.add_hline(y=70, line=dict(color="#ef4444", dash="dash", width=1), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="#22c55e", dash="dash", width=1), row=2, col=1)
    fig.add_hrect(y0=30, y1=70, fillcolor="rgba(100,116,139,0.05)", line_width=0, row=2, col=1)

    # MACD histogram
    hist = ind["_macd_hist"]
    colors_hist = ["rgba(34,197,94,0.7)" if v >= 0 else "rgba(239,68,68,0.7)" for v in hist]
    fig.add_trace(go.Bar(
        x=times, y=hist, name="Histograma",
        marker_color=colors_hist, showlegend=False
    ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=times, y=ind["_macd"], name="MACD",
        line=dict(color="#00d4aa", width=1.5)
    ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=times, y=ind["_macd_signal"], name="Signal",
        line=dict(color="#f59e0b", width=1.5)
    ), row=3, col=1)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.6)",
        font=dict(family="Space Mono", color="#e2e8f0", size=11),
        legend=dict(
            bgcolor="rgba(17,24,39,0.8)",
            bordercolor="#1f2d40",
            borderwidth=1,
            font=dict(size=10),
        ),
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=20, b=0),
        height=520,
        hovermode="x unified",
    )

    for i in range(1, 4):
        fig.update_xaxes(
            gridcolor="#1f2d40", gridwidth=1,
            zeroline=False, showspikes=True,
            spikecolor="#64748b", spikethickness=1,
            row=i, col=1
        )
        fig.update_yaxes(
            gridcolor="#1f2d40", gridwidth=1,
            zeroline=False,
            row=i, col=1
        )

    return fig


# ─────────────────────────────────────────────
# HELPERS FOR DISPLAY
# ─────────────────────────────────────────────

def fmt_price(p: float) -> str:
    if p >= 1000:
        return f"${p:,.2f}"
    elif p >= 1:
        return f"${p:.4f}"
    else:
        return f"${p:.6f}"


def fmt_large(n: float) -> str:
    if n >= 1e9:
        return f"${n/1e9:.2f}B"
    elif n >= 1e6:
        return f"${n/1e6:.2f}M"
    elif n >= 1e3:
        return f"${n/1e3:.2f}K"
    return f"${n:.2f}"


def signal_html(action: str) -> str:
    cls = {"LONG": "signal-long", "SHORT": "signal-short"}.get(action, "signal-neutral")
    icon = {"LONG": "▲ LONG", "SHORT": "▼ SHORT", "NEUTRAL": "◆ NEUTRAL", "SIN DATOS": "– –"}.get(action, action)
    return f'<span class="{cls}">{icon}</span>'


def ind_html(score: int, desc: str) -> str:
    if score == 1:
        return f'<span class="ind-bullish">▲ BULL</span> <span style="color:#94a3b8;font-size:11px">{desc}</span>'
    elif score == -1:
        return f'<span class="ind-bearish">▼ BEAR</span> <span style="color:#94a3b8;font-size:11px">{desc}</span>'
    return f'<span class="ind-neutral">◆ NEUT</span> <span style="color:#94a3b8;font-size:11px">{desc}</span>'


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="dash-title">⚡ CryptoPerp</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-subtitle">Binance Futures Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")

    selected_label = st.selectbox(
        "🪙 Seleccionar Par",
        list(CRYPTOS.keys()),
        index=0,
    )
    selected_symbol = CRYPTOS[selected_label]

    selected_tf = st.selectbox(
        "⏱ Timeframe",
        list(TIMEFRAMES.keys()),
        index=2,  # default 4h
    )

    st.markdown("---")
    st.markdown('<div class="section-header">ESTRATEGIA</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px;color:#94a3b8;line-height:1.6'>
    Basada en <b style='color:#00d4aa'>Michaël van de Poppe</b><br>
    Confluencia multi-indicador:<br>
    • ≥ 4 señales bull → <span style='color:#22c55e'>LONG</span><br>
    • ≥ 4 señales bear → <span style='color:#ef4444'>SHORT</span><br>
    • Riesgo: Bajo/Medio<br><br>
    <span style='color:#f59e0b'>⚠ No es asesoría financiera.</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    auto_refresh = st.checkbox("🔄 Auto-refresh (60s)", value=False)
    if st.button("🔃 Actualizar ahora"):
        st.cache_data.clear()
        # Reset OI baseline so the change is computed fresh after the update
        for k in list(st.session_state.keys()):
            if k.startswith("prev_oi_"):
                del st.session_state[k]
        st.rerun()

    # Countdown display
    if auto_refresh:
        last = st.session_state.get("last_refresh_ts", 0)
        elapsed = time.time() - last
        remaining = max(0, 60 - int(elapsed))
        st.markdown(
            f'<div style="font-size:11px;color:#64748b">Próximo refresh en <b style="color:#00d4aa">{remaining}s</b></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(f'<div style="font-size:10px;color:#475569">Actualizado: {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# AUTO REFRESH  (non-blocking: 2-second ticks, data cleared every 60s)
# ─────────────────────────────────────────────
if auto_refresh:
    if "last_refresh_ts" not in st.session_state:
        st.session_state.last_refresh_ts = time.time()

    elapsed = time.time() - st.session_state.last_refresh_ts
    if elapsed >= 60:
        st.session_state.last_refresh_ts = time.time()
        # Reset OI baselines so new snapshots are taken after the refresh
        for k in list(st.session_state.keys()):
            if k.startswith("prev_oi_"):
                del st.session_state[k]
        st.cache_data.clear()
        st.rerun()
    else:
        # Short sleep so the countdown ticks; UI remains interactive
        time.sleep(2)
        st.rerun()

# ─────────────────────────────────────────────
# MAIN CONTENT — Load Data
# ─────────────────────────────────────────────

with st.spinner("Cargando datos de mercado..."):
    df      = fetch_klines(selected_symbol, TIMEFRAMES[selected_tf], limit=200)
    ticker  = fetch_ticker(selected_symbol)
    funding = fetch_funding_rate(selected_symbol)
    fg      = fetch_fear_greed()
    ind     = compute_indicators(df)

    # Open Interest: compute % change vs last snapshot stored in session_state
    current_oi = fetch_open_interest(selected_symbol)
    _oi_key    = f"prev_oi_{selected_symbol}"
    _prev_oi   = st.session_state.get(_oi_key, 0.0)
    oi_change_pct = ((current_oi - _prev_oi) / _prev_oi * 100) if _prev_oi > 0 else 0.0
    if current_oi > 0:
        st.session_state[_oi_key] = current_oi

    signals = evaluate_signals(ind, funding, oi_change_pct, fg)
    action, score, bull_count, bear_count = get_recommendation(signals)

# CoinGecko fundamentals
cg_data = {}
cg_id = CG_IDS.get(selected_symbol, "")
if cg_id:
    cg_data = fetch_cg_coin(cg_id)

# ── Diagnóstico de conexión (visible si hay problemas) ──────────────────
klines_ok  = not df.empty
ticker_ok  = bool(ticker.get("lastPrice") or ticker.get("priceChangePercent"))
funding_ok = funding != 0.0 or current_oi > 0   # at least one Futures endpoint answered
fg_ok      = fg.get("ok", False)                 # set explicitly by fetch_fear_greed

if not klines_ok or not ticker_ok:
    with st.expander("⚠️ Diagnóstico de conexión API", expanded=True):
        cols_d = st.columns(4)
        def status_badge(ok, label):
            icon  = "✅" if ok else "❌"
            color = "#22c55e" if ok else "#ef4444"
            return f'<span style="color:{color};font-size:12px">{icon} {label}</span>'

        cols_d[0].markdown(status_badge(klines_ok,  "Klines (OHLCV)"),  unsafe_allow_html=True)
        cols_d[1].markdown(status_badge(ticker_ok,  "Ticker 24h"),      unsafe_allow_html=True)
        cols_d[2].markdown(status_badge(funding_ok, "Funding / OI"),    unsafe_allow_html=True)
        cols_d[3].markdown(status_badge(fg_ok,      "Fear & Greed"),    unsafe_allow_html=True)

        if not klines_ok:
            st.warning(
                "No se pudo conectar a Binance (Futures ni Spot). "
                "Haz clic en **🔃 Actualizar ahora** en el sidebar para reintentar."
            )
            # Last-resort: try fetching price from CoinGecko directly
            if cg_data:
                cg_price = cg_data.get("market_data", {}).get("current_price", {}).get("usd", 0)
                if cg_price:
                    st.info(f"💡 Precio desde CoinGecko (puede tener ~1min de retraso): **${cg_price:,.4f}**")

# ─────────────────────────────────────────────
# HEADER ROW
# ─────────────────────────────────────────────

col_title, col_signal, col_score = st.columns([3, 2, 2])

with col_title:
    price_str = fmt_price(ind.get("price", 0)) if ind else "—"
    change_24h = float(ticker.get("priceChangePercent", 0)) if ticker else 0
    change_color = "#22c55e" if change_24h >= 0 else "#ef4444"
    change_sign = "+" if change_24h >= 0 else ""

    st.markdown(f"""
    <div style='margin-top:4px'>
        <span style='font-family:Syne;font-size:32px;font-weight:800;color:#e2e8f0'>{price_str}</span>
        <span style='color:{change_color};font-size:16px;margin-left:12px'>{change_sign}{change_24h:.2f}%</span>
        <div style='color:#64748b;font-size:12px;margin-top:4px'>{selected_label} · {selected_tf} · Binance Futures</div>
    </div>
    """, unsafe_allow_html=True)

with col_signal:
    st.markdown("<div style='margin-top:6px'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:10px;color:#64748b;margin-bottom:6px;letter-spacing:1px;text-transform:uppercase'>SEÑAL RECOMENDADA</div>", unsafe_allow_html=True)
    st.markdown(signal_html(action), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_score:
    total_signals = len(signals) if signals else 1
    bull_pct = int((bull_count / total_signals) * 100) if signals else 0
    bear_pct = int((bear_count / total_signals) * 100) if signals else 0
    st.markdown(f"""
    <div style='margin-top:6px'>
        <div style='font-size:10px;color:#64748b;margin-bottom:6px;letter-spacing:1px;text-transform:uppercase'>CONFLUENCIA</div>
        <div style='font-size:12px;margin-bottom:4px;color:#22c55e'>▲ Bull: {bull_count}/{total_signals} ({bull_pct}%)</div>
        <div class='conf-bar-container'><div class='conf-bar-fill-bull' style='width:{bull_pct}%'></div></div>
        <div style='font-size:12px;margin-bottom:4px;color:#ef4444;margin-top:6px'>▼ Bear: {bear_count}/{total_signals} ({bear_pct}%)</div>
        <div class='conf-bar-container'><div class='conf-bar-fill-bear' style='width:{bear_pct}%'></div></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin: 12px 0; border-top: 1px solid #1f2d40'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# METRICS ROW
# ─────────────────────────────────────────────

m1, m2, m3, m4, m5, m6 = st.columns(6)
_oi_display = f"{current_oi:,.0f}" if current_oi > 0 else "—"
_oi_sub     = (f"{oi_change_pct:+.2f}% vs antes" if oi_change_pct != 0 else "primer snapshot")
metrics = [
    (m1, "Volumen 24h", fmt_large(float(ticker.get("quoteVolume", 0))) if ticker else "—", "USDT"),
    (m2, "RSI (14)", f"{ind.get('rsi', 0):.1f}" if ind else "—", "neutro>50"),
    (m3, "Funding Rate", f"{funding:+.4f}%", "cada 8h"),
    (m4, "ATR (14)", fmt_price(ind.get("atr", 0)) if ind else "—", "volatilidad"),
    (m5, "Fear & Greed", str(fg.get("value", 50)), fg.get("label", "—")),
    (m6, "Open Interest", _oi_display, _oi_sub),
]

for col, label, value, sub in metrics:
    with col:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>{label}</div>
            <div class='metric-value'>{value}</div>
            <div class='metric-sub'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin: 16px 0'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CHART + SIGNALS PANEL
# ─────────────────────────────────────────────

chart_col, signals_col = st.columns([3, 1])

with chart_col:
    st.markdown('<div class="section-header">GRÁFICO DE PRECIO</div>', unsafe_allow_html=True)
    if not df.empty and ind:
        fig = build_chart(df, ind, selected_symbol)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})  # noqa
    else:
        st.warning("No se pudieron cargar los datos del gráfico.")

with signals_col:
    st.markdown('<div class="section-header">ANÁLISIS DE SEÑALES</div>', unsafe_allow_html=True)

    if signals:
        for name, (score_val, desc) in signals.items():
            st.markdown(f"""
            <div class='indicator-row'>
                <div>
                    <div style='font-size:11px;color:#e2e8f0;margin-bottom:2px'>{name}</div>
                    {ind_html(score_val, desc)}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#64748b;font-size:12px">Sin datos de señales</div>', unsafe_allow_html=True)

    # Risk levels
    if ind and action != "SIN DATOS":
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">GESTIÓN DE RIESGO</div>', unsafe_allow_html=True)
        price = ind["price"]
        atr = ind.get("atr", 0)

        if action == "LONG":
            sl = price - 1.5 * atr
            tp1 = price + 2.0 * atr
            tp2 = price + 3.5 * atr
            rrr = 2.0
        elif action == "SHORT":
            sl = price + 1.5 * atr
            tp1 = price - 2.0 * atr
            tp2 = price - 3.5 * atr
            rrr = 2.0
        else:
            sl = tp1 = tp2 = 0
            rrr = 0

        if sl > 0:
            sl_color = "#ef4444" if action == "LONG" else "#22c55e"
            tp_color = "#22c55e" if action == "LONG" else "#ef4444"
            st.markdown(f"""
            <div style='font-size:11px;line-height:2'>
                <div style='color:{sl_color}'>🛑 Stop Loss: {fmt_price(sl)}</div>
                <div style='color:{tp_color}'>🎯 TP1: {fmt_price(tp1)}</div>
                <div style='color:{tp_color}'>🎯 TP2: {fmt_price(tp2)}</div>
                <div style='color:#f59e0b'>📊 R/R ratio: 1:{rrr}</div>
                <div style='color:#64748b;font-size:10px;margin-top:6px'>Basado en 1.5× ATR (SL) y 2× / 3.5× ATR (TP)</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#64748b;font-size:11px">Esperar señal direccional</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FUNDAMENTAL DATA ROW
# ─────────────────────────────────────────────

st.markdown("<div style='margin: 16px 0; border-top: 1px solid #1f2d40'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-header">DATOS FUNDAMENTALES</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)

market_data = cg_data.get("market_data", {}) if cg_data else {}
mkt_cap = market_data.get("market_cap", {}).get("usd", 0) if market_data else 0
rank = cg_data.get("market_cap_rank", "—") if cg_data else "—"
vol_24h_cg = market_data.get("total_volume", {}).get("usd", 0) if market_data else 0
circ_supply = market_data.get("circulating_supply", 0) if market_data else 0
max_supply = market_data.get("max_supply", None) if market_data else None
ath = market_data.get("ath", {}).get("usd", 0) if market_data else 0
ath_change = market_data.get("ath_change_percentage", {}).get("usd", 0) if market_data else 0

supply_str = f"{circ_supply/1e6:.1f}M" if circ_supply else "—"
if max_supply:
    supply_str += f" / {max_supply/1e6:.1f}M"

with f1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Market Cap</div>
        <div class='metric-value' style='font-size:16px'>{fmt_large(mkt_cap) if mkt_cap else '—'}</div>
        <div class='metric-sub'>Rank #{rank}</div>
    </div>""", unsafe_allow_html=True)

with f2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Supply Circulante</div>
        <div class='metric-value' style='font-size:16px'>{supply_str}</div>
        <div class='metric-sub'>{'Limitado' if max_supply else 'Sin límite'}</div>
    </div>""", unsafe_allow_html=True)

with f3:
    ath_str = fmt_price(ath) if ath else "—"
    ath_c = f"{ath_change:.1f}%" if ath_change else "—"
    ath_col = "#22c55e" if ath_change >= 0 else "#ef4444"
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>ATH</div>
        <div class='metric-value' style='font-size:16px'>{ath_str}</div>
        <div class='metric-sub' style='color:{ath_col}'>{ath_c} desde ATH</div>
    </div>""", unsafe_allow_html=True)

with f4:
    fg_val = fg.get("value", 50)
    if fg_val <= 25:
        fg_col = "#22c55e"
    elif fg_val >= 75:
        fg_col = "#ef4444"
    else:
        fg_col = "#f59e0b"
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Fear & Greed Index</div>
        <div class='metric-value' style='font-size:28px;color:{fg_col}'>{fg_val}</div>
        <div class='metric-sub'>{fg.get('label', '—')}</div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ALL CRYPTOS OVERVIEW TABLE
# ─────────────────────────────────────────────

st.markdown("<div style='margin: 16px 0; border-top: 1px solid #1f2d40'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-header">RESUMEN DE SEÑALES — TODOS LOS PARES</div>', unsafe_allow_html=True)

with st.expander("📋 Ver tabla de señales rápidas (requiere múltiples llamadas a la API)", expanded=False):
    table_data = []
    prog = st.progress(0)
    symbols_list = list(CRYPTOS.items())

    for i, (label, sym) in enumerate(symbols_list):
        prog.progress((i + 1) / len(symbols_list))
        try:
            df_t = fetch_klines(sym, "4h", limit=100)
            tk = fetch_ticker(sym)
            fr = fetch_funding_rate(sym)
            ind_t = compute_indicators(df_t)
            sigs_t = evaluate_signals(ind_t, fr, 0, fg)
            act_t, _, bc, brc = get_recommendation(sigs_t)
            change = float(tk.get("priceChangePercent", 0)) if tk else 0
            price_t = ind_t.get("price", 0) if ind_t else 0
            rsi_t = ind_t.get("rsi", 0) if ind_t else 0
            table_data.append({
                "Par": label,
                "Precio": fmt_price(price_t),
                "24h %": f"{change:+.2f}%",
                "RSI": f"{rsi_t:.1f}",
                "Funding": f"{fr:+.4f}%",
                "Bull": bc,
                "Bear": brc,
                "Señal": act_t,
            })
        except Exception:
            table_data.append({
                "Par": label, "Precio": "—", "24h %": "—", "RSI": "—",
                "Funding": "—", "Bull": 0, "Bear": 0, "Señal": "ERROR"
            })
        time.sleep(0.05)

    prog.empty()

    if table_data:
        df_table = pd.DataFrame(table_data)

        def color_signal(val):
            if val == "LONG":
                return "background-color: rgba(34,197,94,0.15); color: #22c55e; font-weight: bold"
            elif val == "SHORT":
                return "background-color: rgba(239,68,68,0.15); color: #ef4444; font-weight: bold"
            return "color: #64748b"

        styled = df_table.style.map(color_signal, subset=["Señal"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown("""
<div style='text-align:center;padding:20px;color:#475569;font-size:10px;border-top:1px solid #1f2d40;margin-top:24px'>
    ⚡ CryptoPerp Dashboard · Datos: Binance Futures API (público) + CoinGecko (free tier) + alternative.me<br>
    Estrategia basada en confluencia multi-indicador (inspirado en Michaël van de Poppe) · Riesgo bajo/medio<br>
    <span style='color:#ef4444'>⚠ Solo uso educativo / personal. No constituye asesoría financiera.</span>
</div>
""", unsafe_allow_html=True)
