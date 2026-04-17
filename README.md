# ⚡ CryptoPerp Dashboard

Dashboard de análisis técnico y fundamental para **futuros perpetuos en Binance**, diseñado para operar con riesgo bajo/medio.

---

## 📊 Estrategia

**Basada en Michaël van de Poppe** — trader holandés conocido por su método de *confluencia de zonas*.  
La idea central: **solo entrar cuando ≥ 4 de 8 indicadores apuntan en la misma dirección**.

| Señal | Condición |
|-------|-----------|
| 🟢 **LONG** | ≥ 4 señales alcistas |
| 🔴 **SHORT** | ≥ 4 señales bajistas |
| ⚪ **NEUTRAL** | Sin confluencia clara |

---

## 📈 Indicadores incluidos

### Técnicos
| Indicador | Qué mide |
|-----------|----------|
| EMA 200 | Tendencia macro |
| EMA 20/50 Stack | Tendencia de corto/medio plazo |
| RSI (14) | Sobrecompra / sobreventa |
| MACD (12/26/9) | Momentum y divergencias |
| Bollinger Bands (20) | Volatilidad y extremos de precio |
| ATR (14) | Volatilidad (base para Stop Loss / Take Profit) |
| Volumen vs MA20 | Confirmación de movimiento |

### Fundamentales
| Indicador | Qué mide |
|-----------|----------|
| Funding Rate | Sentimiento del mercado de futuros |
| Fear & Greed Index | Sentimiento macro del mercado crypto |
| Market Cap / Rank | Solidez del activo |
| Supply circulante | Presión inflacionaria |
| ATH / distancia % | Contexto histórico |

---

## 🪙 20 Criptomonedas disponibles

Seleccionadas por **liquidez alta + volumen de futuros perpetuos en Binance**:

`BTC · ETH · BNB · SOL · XRP · ADA · AVAX · DOGE · MATIC · LINK · DOT · UNI · LTC · ATOM · FIL · APT · ARB · OP · INJ · SUI`

---

## 🔌 APIs utilizadas (todas gratuitas, sin API key)

| API | Uso | Límite gratuito |
|-----|-----|-----------------|
| [Binance Futures (público)](https://binance-docs.github.io/apidocs/futures/en/) | OHLCV, ticker 24h, funding rate | 1200 req/min |
| [CoinGecko (free tier)](https://www.coingecko.com/en/api) | Market cap, supply, ATH | 10-30 req/min |
| [alternative.me](https://alternative.me/crypto/fear-and-greed-index/) | Fear & Greed Index | Sin límite práctico |

> ⚠️ CoinGecko free tier puede devolver errores 429 (rate limit) bajo uso intensivo.  
> El dashboard lo maneja con `@st.cache_data` y muestra "—" si falla.

---

## 🚀 Instalación local

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/crypto-dashboard.git
cd crypto-dashboard

# 2. Crear entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
streamlit run app.py
```

El dashboard se abre en `http://localhost:8501`

---

## ☁️ Deploy en Streamlit Cloud (gratis)

1. Sube este repositorio a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu cuenta de GitHub
4. Selecciona el repo, branch `main`, y archivo `app.py`
5. Click **Deploy** → en ~2 minutos tendrás tu URL pública

**No se requieren secrets ni API keys.**

---

## 📁 Estructura del proyecto

```
crypto-dashboard/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias Python
├── README.md           # Este archivo
└── .gitignore          # Archivos a ignorar
```

---

## ⚙️ Gestión de riesgo automática

El dashboard calcula niveles automáticamente basado en **ATR (Average True Range)**:

- **Stop Loss**: precio ± 1.5× ATR
- **Take Profit 1**: precio ± 2.0× ATR  
- **Take Profit 2**: precio ± 3.5× ATR
- **R/R Ratio**: 1:2

---

## ⚠️ Disclaimer

> Este dashboard es **solo para uso educativo y personal**.  
> No constituye asesoría financiera.  
> Opera siempre con capital que puedas permitirte perder.
