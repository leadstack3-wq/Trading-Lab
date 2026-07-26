"""
Trading Lab
A Streamlit dashboard for stock investigation using yfinance data and TA-Lib indicators,
styled with the Green Gradient Theme, built-in Streamlit Caching, Plotly visually integrated,
and Dynamic Indicator Parameters.
"""

import json
from datetime import date, timedelta
import requests

import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# TA-Lib Import
try:
    from talib import abstract as talib_abstract
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False


# --------------------------------------------------------------------------
# PAGE CONFIG & CSS
# --------------------------------------------------------------------------
st.set_page_config(page_title="Trading Lab", layout="wide", page_icon="🧪", initial_sidebar_state="collapsed")

def inject_green_gradient_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── hide all native chrome ── */
    header[data-testid="stHeader"] { display:none !important; }
    #MainMenu, footer { display:none !important; }
    .stAppDeployButton, [data-testid="stAppDeployButton"],
    button[title="View fullscreen"], [data-testid="StyledFullScreenButton"] { display:none !important; }
    [data-testid="stSidebar"], .stSidebar { display:none !important; }
    [data-testid="collapsedControl"], button[data-testid="baseButton-headerNoPadding"],
    .stSidebarCollapsedControl, section[data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    :root {
        --p: #10B981; --p-mid: #34D399; --p-light: #D1FAE5; --p-xlight: #ECFDF5;
        --bg: #E8E6EF; --surface: #FFFFFF; --border: #E5E7EB;
        --text: #1F2937; --muted: #6B7280; --label: #9CA3AF;
        --green: #059669; --green-bg: #D1FAE5;
        --red: #DC2626; --red-bg: #FEE2E2; --yellow: #D97706;
        --sans: 'Inter', system-ui, sans-serif;
        --mono: 'JetBrains Mono', 'Courier New', monospace;
        --card-shadow: 0 8px 40px rgba(0,0,0,.13), 0 2px 8px rgba(0,0,0,.07);
    }

    /* ── dashboard background ── */
    .stApp { background: var(--bg) !important; color: var(--text) !important; font-family: var(--sans) !important; }

    /* ── elevated card container ── */
    .block-container {
        background: var(--surface) !important;
        border-radius: 24px !important;
        max-width: 1100px !important;
        margin: 2rem auto !important;
        padding: 2rem 2.5rem 2.5rem !important;
        box-shadow: var(--card-shadow) !important;
    }
    @media (max-width: 768px) {
        .block-container {
            border-radius: 14px !important;
            margin: 0.75rem !important;
            padding: 1rem 1rem 1.5rem !important;
        }
    }

    h1,h2,h3,h4,h5,h6 { font-family: var(--sans) !important; color: var(--text) !important; margin: 0 0 .1rem !important; letter-spacing: -.2px; }
    p, label, span, div { font-family: var(--sans) !important; }

    /* ── topbar ── */
    .theme-topbar {
        background: linear-gradient(135deg, #34D399 0%, #10B981 60%, #059669 100%);
        padding: 16px 24px 18px; border-radius: 16px; margin: 0 0 1.4rem 0;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 4px 18px rgba(16,185,129,.25);
        flex-wrap: wrap;
        gap: 12px;
    }
    .theme-topbar-title { font-size: 20px; font-weight: 800; color: #fff; letter-spacing: -.3px; }
    .theme-topbar-sub { font-size: 11px; color: rgba(255,255,255,.9); font-weight: 500; letter-spacing: .6px; margin-top: 2px; }
    .theme-live-dot {
        display: inline-block; width: 8px; height: 8px; background: #34D399;
        border-radius: 50%; margin-right: 6px; box-shadow: 0 0 0 2px rgba(255,255,255,.4);
        animation: pulse 1.8s infinite;
    }
    @keyframes pulse {
        0%,100% { box-shadow: 0 0 0 2px rgba(255,255,255,.4); }
        50% { box-shadow: 0 0 0 5px rgba(255,255,255,.15); }
    }
    .theme-topbar-badge {
        background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.3);
        color: #fff; font-size: 11px; font-weight: 700; padding: 4px 12px;
        border-radius: 20px; letter-spacing: .5px;
        white-space: nowrap;
    }

    /* ── section headers ── */
    .theme-section-header { background: var(--surface); border: 1px solid var(--border); border-top: 3px solid var(--p); padding: 10px 16px; border-radius: 12px 12px 0 0; margin-bottom: -1px; }
    .theme-section-header h3 { font-size: 13px !important; font-weight: 700 !important; color: var(--p) !important; text-transform: uppercase; letter-spacing: .8px; margin: 0 !important; }
    
    .theme-config-header { background: var(--p-xlight); border-left: 3px solid var(--p); padding: 8px 12px; border-radius: 8px; margin: 14px 0 10px; }
    .theme-config-header h3 { font-size: 11px !important; font-weight: 700 !important; color: var(--p) !important; text-transform: uppercase; letter-spacing: .9px; margin: 0 !important; }

    /* ── inputs ── */
    div[data-baseweb="input"] input, .stNumberInput input {
        background: #FAFAFA !important; color: var(--text) !important;
        border: 1px solid var(--border) !important; border-radius: 8px !important;
        font-size: 14px !important; font-family: var(--sans) !important;
        transition: border-color .15s ease, box-shadow .15s ease;
    }
    div[data-baseweb="input"] input:focus, .stNumberInput input:focus {
        border-color: var(--p) !important; box-shadow: 0 0 0 2px rgba(16,185,129,.12) !important; background: #fff !important;
    }
    div[data-baseweb="select"] { background-color: transparent !important; }
    div[data-baseweb="select"] > div {
        background-color: #FAFAFA !important; border: 1px solid var(--border) !important;
        border-radius: 8px !important; color: var(--text) !important;
        transition: border-color .15s ease;
    }
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label, .stDateInput label {
        color: var(--muted) !important; font-size: 11px !important; font-weight: 600 !important;
        text-transform: uppercase !important; letter-spacing: .7px !important;
    }
    div[role="radiogroup"] { margin-bottom: 10px; }
    div[role="radiogroup"] label { font-size: 14px !important; text-transform: none !important; font-weight: 500 !important;}

    /* ── buttons ── */
    .stButton > button, div.stDownloadButton > button {
        background: linear-gradient(135deg, var(--p-mid) 0%, var(--p) 100%) !important;
        color: #fff !important; border: none !important; border-radius: 10px !important;
        font-family: var(--sans) !important; font-weight: 700 !important; font-size: 13px !important;
        letter-spacing: .6px !important; text-transform: uppercase !important;
        padding: 11px 20px !important; box-shadow: 0 4px 14px rgba(16,185,129,.25) !important;
        transition: all .15s ease;
        width: 100% !important; 
    }
    .stButton > button:hover, div.stDownloadButton > button:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(16,185,129,.38) !important; color: white !important;}

    /* ── modern pill tabs ── */
    div[data-baseweb="tab-list"] {
        background: #F3F4F6 !important;
        border-bottom: none !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 2px !important;
        margin-bottom: 1.2rem !important;
        overflow-x: auto;
        flex-wrap: nowrap;
    }
    button[data-baseweb="tab"] {
        background: transparent !important;
        color: var(--muted) !important;
        font-size: 13px !important; font-weight: 600 !important;
        padding: 9px 22px !important;
        border: none !important;
        border-radius: 9px !important;
        text-transform: uppercase; letter-spacing: .4px;
        transition: all .15s ease;
        white-space: nowrap;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: var(--surface) !important;
        color: var(--p) !important;
        box-shadow: 0 1px 4px rgba(0,0,0,.10) !important;
    }

    /* ── metric cards ── */
    .metric-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.04); }
    .metric-card-accent { border-top: 3px solid var(--p); }
    .metric-card-green { border-top: 3px solid var(--green); }
    .metric-card-yellow { border-top: 3px solid var(--yellow); }
    .metric-label { color: var(--label); font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
    .metric-value { color: var(--text); font-size: 17px; font-weight: 700; font-family: var(--mono); word-wrap: break-word; }

    /* ── misc ── */
    div[data-testid="stAlert"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }
    .stDataFrame, [data-testid="stDataFrame"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; overflow: hidden; width: 100%; overflow-x: auto; }
    .stDataFrame th { background: var(--p-xlight) !important; color: var(--p) !important; font-size: 11px !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: .6px !important; }
    ::-webkit-scrollbar { width:5px; height:5px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: rgba(16,185,129,.3); border-radius:3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--p); }

    /* ── RESPONSIVE DESIGN (Tablets & Mobile) ── */
    @media (max-width: 768px) {
        .block-container {
            border-radius: 14px !important;
            margin: 0.5rem auto !important;
            padding: 1rem 1rem 1.5rem !important;
        }
        .theme-topbar {
            flex-direction: column !important;
            align-items: flex-start !important;
            padding: 14px !important;
        }
        .theme-topbar-title {
            font-size: 17px !important;
        }
        .theme-topbar-badge {
            align-self: flex-start !important;
        }
        .metric-value {
            font-size: 14px !important;
        }
        .metric-card {
            padding: 10px 12px !important;
        }
        button[data-baseweb="tab"] {
            font-size: 11px !important;
            padding: 8px 14px !important;
        }
        div[role="radiogroup"] {
            flex-direction: column !important;
            gap: 5px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# INDICATOR CATALOGUE (TA-Lib, 8 categories)
# --------------------------------------------------------------------------
INDICATOR_DICT = {
    "Overlap Studies": ["BBANDS", "DEMA", "EMA", "HT_TRENDLINE", "KAMA", "MA", "MAMA", "MAVP", "MIDPOINT", "MIDPRICE", "SAR", "SAREXT", "SMA", "T3", "TEMA", "TRIMA", "WMA"],
    "Momentum Indicators": ["ADX", "ADXR", "APO", "AROON", "AROONOSC", "BOP", "CCI", "CMO", "DX", "MACD", "MACDEXT", "MACDFIX", "MFI", "MINUS_DI", "MINUS_DM", "MOM", "PLUS_DI", "PLUS_DM", "PPO", "ROC", "ROCP", "ROCR", "ROCR100", "RSI", "STOCH", "STOCHF", "STOCHRSI", "TRIX", "ULTOSC", "WILLR"],
    "Volume Indicators": ["AD", "ADOSC", "OBV"],
    "Cycle Indicators": ["HT_DCPERIOD", "HT_DCPHASE", "HT_PHASOR", "HT_SINE", "HT_TRENDMODE"],
    "Price Transform": ["AVGPRICE", "MEDPRICE", "TYPPRICE", "WCLPRICE"],
    "Volatility Indicators": ["ATR", "NATR", "TRANGE"],
    "Pattern Recognition": ["CDL2CROWS", "CDL3BLACKCROWS", "CDL3INSIDE", "CDL3LINESTRIKE", "CDL3OUTSIDE", "CDL3STARSINSOUTH", "CDL3WHITESOLDIERS", "CDLABANDONEDBABY", "CDLADVANCEBLOCK", "CDLBELTHOLD", "CDLBREAKAWAY", "CDLCLOSINGMARUBOZU", "CDLCONCEALBABYSWALL", "CDLCOUNTERATTACK", "CDLDARKCLOUDCOVER", "CDLDOJI", "CDLDOJISTAR", "CDLDRAGONFLYDOJI", "CDLENGULFING", "CDLEVENINGDOJISTAR", "CDLEVENINGSTAR", "CDLGAPSIDESIDEWHITE", "CDLGRAVESTONEDOJI", "CDLHAMMER", "CDLHANGINGMAN", "CDLHARAMI", "CDLHARAMICROSS", "CDLHIGHWAVE", "CDLHIKKAKE", "CDLHIKKAKEMOD", "CDLHOMINGPIGEON", "CDLIDENTICAL3CROWS", "CDLINNECK", "CDLINVERTEDHAMMER", "CDLKICKING", "CDLKICKINGBYLENGTH", "CDLLADDERBOTTOM", "CDLLONGLEGGEDDOJI", "CDLLONGLINE", "CDLMARUBOZU", "CDLMATCHINGLOW", "CDLMATHOLD", "CDLMORNINGDOJISTAR", "CDLMORNINGSTAR", "CDLONNECK", "CDLPIERCING", "CDLRICKSHAWMAN", "CDLRISEFALL3METHODS", "CDLSEPARATINGLINES", "CDLSHOOTINGSTAR", "CDLSHORTLINE", "CDLSPINNINGTOP", "CDLSTALLEDPATTERN", "CDLSTICKSANDWICH", "CDLTAKURI", "CDLTASUKIGAP", "CDLTHRUSTING", "CDLTRISTAR", "CDLUNIQUE3RIVER", "CDLUPSIDEGAP2CROWS", "CDLXSIDEGAP3METHODS"],
    "Statistic Functions": ["BETA", "CORREL", "LINEARREG", "LINEARREG_ANGLE", "LINEARREG_INTERCEPT", "LINEARREG_SLOPE", "STDDEV", "TSF", "VAR"],
}

TIMEFRAME_OPTIONS = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
INTRADAY_TIMEFRAMES = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}

# --------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------
def init_state():
    defaults = {
        "symbol": "AAPL",
        "timeframe": "1d",
        "mode": "Historical Data",
        "start_date": date.today() - timedelta(days=180),
        "end_date": date.today(),
        "selected_indicators": [], 
        "fetched_df": None,
        "gsheet_url": "",
        "indicator_count": 1, 
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def compute_indicator(ind_config: dict, df: pd.DataFrame) -> pd.DataFrame:
    """Run a TA-Lib indicator against OHLCV data using dynamic parameters."""
    if not TALIB_AVAILABLE:
        return pd.DataFrame(index=df.index)

    name = ind_config["name"]
    user_params = ind_config.get("params", {})
    func = talib_abstract.Function(name)
    
    inputs = {
        "open": df["Open"].astype(float).values,
        "high": df["High"].astype(float).values,
        "low": df["Low"].astype(float).values,
        "close": df["Close"].astype(float).values,
        "volume": df["Volume"].astype(float).values,
    }
    
    try:
        outputs = func(inputs, **user_params)
    except Exception as exc:
        st.warning(f"Could not compute {name}: {exc}")
        return pd.DataFrame(index=df.index)

    param_suffix = "_".join(str(v) for v in user_params.values())
    base_name = f"{name}_{param_suffix}" if param_suffix else name

    output_names = func.output_names
    if not isinstance(outputs, (list, tuple)):
        outputs = [outputs]

    result = pd.DataFrame(index=df.index)
    for out_name, out_values in zip(output_names, outputs):
        col_name = base_name if len(output_names) == 1 else f"{base_name}_{out_name}"
        result[col_name] = out_values

    return result

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(symbol: str, timeframe: str, mode: str, start_dt, end_dt) -> pd.DataFrame:
    """Pull OHLCV data from yfinance with local caching enabled."""
    if mode == "Historical Data":
        df = yf.download(
            symbol,
            start=start_dt,
            end=end_dt,
            interval=timeframe,
            progress=False,
            auto_adjust=False,
        )
    else:
        if timeframe in INTRADAY_TIMEFRAMES:
            period = "5d" if timeframe in {"1m", "2m", "5m"} else "1mo"
        else:
            period = "3mo"
        df = yf.download(
            symbol,
            period=period,
            interval=timeframe,
            progress=False,
            auto_adjust=False,
        )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df

def push_to_google_sheets_webhook(df: pd.DataFrame, webhook_url: str):
    """Export the ledger to Google Sheets via Apps Script Webhook."""
    if not webhook_url:
        st.error("Please provide a Google Apps Script URL in the input field above.")
        return
        
    with st.spinner("Streaming complete metadata blocks to master database..."):
        try:
            export_df = df.reset_index()
            export_df.columns = export_df.columns.astype(str)
            export_df = export_df.astype(str)
            
            response = requests.post(webhook_url, json=export_df.to_dict(orient='records'))
            st.success("✅ Remote Google Sheets Matrix Synchronized!")
        except Exception as exc:
            st.error(f"Google Sheets synchronization failed: {exc}")

# --------------------------------------------------------------------------
# APP MAIN
# --------------------------------------------------------------------------
def main():
    inject_green_gradient_css()
    init_state()

    st.markdown("""
    <div class="theme-topbar">
      <div>
        <div class="theme-topbar-title">🧪 Trading Lab</div>
        <div class="theme-topbar-sub"><span class="theme-live-dot"></span>Extract structured stock data, overlay indicators, and stream to Google Sheets</div>
      </div>
      <div class="theme-topbar-badge">DATA PIPELINE</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["⚙️ Configuration", "📊 Indicators", "📖 Data Table", "📈 Interactive Chart"])

    # ------------------------------------------------------------------
    # TAB 1 — CONFIGURATION
    # ------------------------------------------------------------------
    with tab1:
        st.markdown('<div class="theme-section-header"><h3>🎯 Target Asset Parameters</h3></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            symbol = st.text_input("Stock Symbol", value=st.session_state["symbol"], placeholder="e.g. AAPL")
        with col2:
            timeframe = st.selectbox(
                "Timeframe",
                TIMEFRAME_OPTIONS,
                index=TIMEFRAME_OPTIONS.index(st.session_state["timeframe"]),
            )

        st.write("")

        mode = st.radio(
            "Data Extraction Mode",
            ["Historical Data", "Live Data"],
            index=0 if st.session_state.get("mode", "Historical Data") == "Historical Data" else 1,
            horizontal=True,
            help="Switching to Live Data will disable custom date selection and pull the most recent intraday records."
        )
        
        is_live = (mode == "Live Data")
        
        dcol1, dcol2 = st.columns(2)
        with dcol1:
            start_date = st.date_input("Start Date", value=st.session_state["start_date"], disabled=is_live)
        with dcol2:
            end_date = st.date_input("End Date", value=st.session_state["end_date"], disabled=is_live)

        st.session_state.update({
            "symbol": symbol.strip().upper() if symbol else symbol,
            "timeframe": timeframe,
            "mode": mode,
            "start_date": start_date,
            "end_date": end_date,
        })

    # ------------------------------------------------------------------
    # TAB 2 — INDICATORS
    # ------------------------------------------------------------------
    with tab2:
        st.markdown('<div class="theme-section-header"><h3>⚙️ Technical Analysis Clues</h3></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.warning(
            "**⚠️ Capacity Disclaimer:** Stacking too many identifiers (e.g., 20+) may slow down dashboard rendering, "
            "make the data table difficult to read horizontally, and cause JSON payload timeouts."
        )

        if not TALIB_AVAILABLE:
            st.error("TA-Lib is missing. Install with `pip install TA-Lib` to compute these clues.")

        selected_indicators = []
        cat_keys = ["None"] + list(INDICATOR_DICT.keys())
        
        for i in range(st.session_state["indicator_count"]):
            cat_col, ind_col = st.columns(2)
            
            with cat_col:
                cat_selection = st.selectbox(f"Pair {i+1}: Category", cat_keys, key=f"cat_{i}")
                
            with ind_col:
                if cat_selection != "None":
                    ind_options = ["None"] + INDICATOR_DICT[cat_selection]
                    ind_selection = st.selectbox(f"Pair {i+1}: Indicator", ind_options, key=f"ind_{i}")
                    
                    if ind_selection != "None":
                        func_meta = talib_abstract.Function(ind_selection)
                        default_params = func_meta.parameters
                        user_params = {}
                        
                        if default_params:
                            st.caption(f"🔧 Adjust **{ind_selection}** Settings")
                            param_cols = st.columns(len(default_params))
                            for idx, (p_name, p_default) in enumerate(default_params.items()):
                                with param_cols[idx]:
                                    if isinstance(p_default, float):
                                        user_params[p_name] = st.number_input(p_name, value=float(p_default), key=f"{ind_selection}_{i}_{p_name}")
                                    else:
                                        user_params[p_name] = st.number_input(p_name, value=int(p_default), key=f"{ind_selection}_{i}_{p_name}")
                            
                        selected_indicators.append({"name": ind_selection, "params": user_params})
                else:
                    st.selectbox(f"Pair {i+1}: Indicator", ["None"], key=f"ind_{i}", disabled=True)

        st.write("") 
        
        btn_col1, btn_col2, _ = st.columns([1, 1, 3])
        with btn_col1:
            if st.button("➕ Add Pair", use_container_width=True):
                st.session_state["indicator_count"] += 1
                st.rerun()
                
        with btn_col2:
            if st.session_state["indicator_count"] > 1:
                if st.button("➖ Remove Last", use_container_width=True):
                    cat_key_to_remove = f"cat_{st.session_state['indicator_count'] - 1}"
                    ind_key_to_remove = f"ind_{st.session_state['indicator_count'] - 1}"
                    
                    if cat_key_to_remove in st.session_state:
                        del st.session_state[cat_key_to_remove]
                    if ind_key_to_remove in st.session_state:
                        del st.session_state[ind_key_to_remove]
                        
                    st.session_state["indicator_count"] -= 1
                    st.rerun()

        st.caption(f"**Total Identifiers Selected:** {len(selected_indicators)}")
        st.session_state["selected_indicators"] = selected_indicators

    # ------------------------------------------------------------------
    # TAB 3 — DATA TABLE
    # ------------------------------------------------------------------
    with tab3:
        st.markdown('<div class="theme-section-header"><h3>📊 Execution Matrix</h3></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        run_search = st.button("🚀 Harvest Enriched Data", use_container_width=True)

        if run_search:
            current_symbol = st.session_state["symbol"]
            if not current_symbol:
                st.warning("Please supply a valid target symbol in the Configuration tab.")
            else:
                with st.spinner(f"Spawning data miner for {current_symbol}..."):
                    try:
                        raw_df = fetch_data(
                            current_symbol,
                            st.session_state["timeframe"],
                            st.session_state["mode"],
                            st.session_state["start_date"],
                            st.session_state["end_date"],
                        )
                    except Exception as exc:
                        st.error(f"Miner Runtime Exception: {exc}")
                        raw_df = pd.DataFrame()

                if raw_df.empty:
                    st.warning("No data found. Ensure market was open or adjust dates.")
                    st.session_state["fetched_df"] = None
                else:
                    final_df = raw_df.copy()
                    if TALIB_AVAILABLE and st.session_state["selected_indicators"]:
                        for ind_config in st.session_state["selected_indicators"]:
                            ind_df = compute_indicator(ind_config, raw_df)
                            final_df = pd.concat([final_df, ind_df], axis=1)
                    st.session_state["fetched_df"] = final_df

        final_df = st.session_state.get("fetched_df")

        if final_df is not None:
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f"""
                    <div class="metric-card metric-card-green">
                        <div class="metric-label">Pipeline Output</div>
                        <div class="metric-value">📍 {len(final_df)} Candle Records</div>
                    </div>
                """, unsafe_allow_html=True)
            with m2:
                indicator_count = len([col for col in final_df.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume']])
                st.markdown(f"""
                    <div class="metric-card metric-card-yellow"> 
                        <div class="metric-label">Features Generated</div>
                        <div class="metric-value">💬 {indicator_count} Custom Metrics</div>
                    </div>
                """, unsafe_allow_html=True)

            st.dataframe(final_df, use_container_width=True)
            
            st.divider()
            
            # Export Options
            colA, colB = st.columns(2)
            
            with colA:
                st.markdown('<div class="theme-config-header"><h3>📥 Local Export</h3></div>', unsafe_allow_html=True)
                csv_bytes = final_df.to_csv().encode("utf-8")
                st.download_button(
                    "Export Compiled Dataset (CSV)",
                    data=csv_bytes,
                    file_name=f"{st.session_state['symbol']}_compiled.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            with colB:
                st.markdown('<div class="theme-config-header"><h3>🔗 Cloud Sync</h3></div>', unsafe_allow_html=True)
                gsheet_url = st.text_input(
                    "Google Apps Script URL", 
                    value=st.session_state.get("gsheet_url", ""), 
                    placeholder="Enter webhook deployment URL...",
                    label_visibility="collapsed"
                )
                st.session_state["gsheet_url"] = gsheet_url
                
                if st.button("📤 Push to Google Sheets", use_container_width=True):
                    push_to_google_sheets_webhook(final_df, gsheet_url)
        else:
            st.info("The execution matrix is empty. Adjust configuration and click **Harvest Enriched Data**.")

    # ------------------------------------------------------------------
    # TAB 4 — INTERACTIVE CHART (PLOTLY)
    # ------------------------------------------------------------------
    with tab4:
        st.markdown('<div class="theme-section-header"><h3>📈 Interactive Price Chart</h3></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        final_df_chart = st.session_state.get("fetched_df")
        
        if final_df_chart is not None and not final_df_chart.empty:
            fig = go.Figure()
            
            # Plot the main financial candlestick chart
            fig.add_trace(go.Candlestick(
                x=final_df_chart.index,
                open=final_df_chart['Open'],
                high=final_df_chart['High'],
                low=final_df_chart['Low'],
                close=final_df_chart['Close'],
                name='Price Action',
                increasing_line_color='#10B981', 
                decreasing_line_color='#DC2626'  
            ))
            
            # Dynamically overlay computed indicators on top of price data
            indicator_cols = [col for col in final_df_chart.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume']]
            for col in indicator_cols:
                fig.add_trace(go.Scatter(
                    x=final_df_chart.index,
                    y=final_df_chart[col],
                    mode='lines',
                    name=col,
                    line=dict(width=1.5)
                ))
                
            fig.update_layout(
                title=f"{st.session_state['symbol']} - Technical Analysis View",
                yaxis_title="Asset Price",
                xaxis_title="Timeline",
                template="plotly_white",
                height=650,
                margin=dict(l=20, r=20, t=50, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis_rangeslider_visible=False 
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chart data is unavailable. Please navigate to the Configuration tab, adjust your settings, and execute the data pipeline to visualize the metrics.")

if __name__ == "__main__":
    main()
