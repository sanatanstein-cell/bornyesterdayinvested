import base64
import json
import os
import re
import urllib.request
from datetime import datetime
from urllib.parse import quote_plus
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from edgar import Company, set_identity


def find_logo_file() -> str | None:
    for fname in os.listdir("."):
        if fname.lower() in ("logo.png", "logo.jpg", "logo.jpeg", "logo.webp"):
            return fname
    return None


LOGO_PATH = find_logo_file()

st.set_page_config(
    page_title="BornYesterdayInvestEd.com — SEC Research, AI Coach & Paper Trading",
    page_icon=LOGO_PATH or "📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 1. THEME-ADAPTIVE FINTECH DESIGN SYSTEM (LIGHT & DARK MODE READY)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .wl-masthead {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        padding: 0.25rem 0 0.85rem 0;
        margin-bottom: 0.35rem;
    }
    .wl-masthead-logo {
        width: 46px;
        height: 46px;
        border-radius: 11px;
        object-fit: cover;
        flex-shrink: 0;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.14);
    }
    .wl-masthead-name {
        font-size: 1.52rem;
        font-weight: 700;
        color: var(--text-color);
        line-height: 1.15;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .wl-masthead-tagline {
        font-size: 0.84rem;
        color: var(--text-color);
        opacity: 0.72;
        margin: 0.15rem 0 0 0;
    }

    .wl-hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 58%, #164e63 100%);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 16px;
        padding: 1.15rem 1.5rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.12);
    }
    .wl-hero-badge {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.22rem 0.7rem;
        border-radius: 999px;
        background: rgba(56, 189, 248, 0.18);
        color: #7dd3fc !important;
        border: 1px solid rgba(56, 189, 248, 0.35);
        margin-bottom: 0.45rem;
    }
    .wl-hero .wl-hero-sub {
        font-size: 0.93rem;
        color: #e2e8f0 !important;
        margin: 0;
        max-width: 920px;
        line-height: 1.55;
    }

    .ad-slot-wrapper {
        background-color: var(--secondary-background-color);
        border: 1px dashed rgba(128, 128, 128, 0.38);
        border-radius: 12px;
        padding: 0.65rem 1rem;
        margin: 0.65rem 0 1rem 0;
        text-align: center;
    }
    .ad-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.6;
        margin-bottom: 0.25rem;
        font-weight: 600;
    }
    .ad-copy {
        font-size: 0.85rem;
        color: var(--text-color);
        opacity: 0.88;
    }

    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 14px;
        padding: 0.9rem 1.1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
    }

    .speculator-box {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(139, 92, 246, 0.38);
        border-left: 5px solid #8b5cf6;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin: 0.4rem 0 0.9rem 0;
        color: var(--text-color);
    }
    .formula-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.84rem;
        background: rgba(128, 128, 128, 0.12);
        border: 1px solid rgba(128, 128, 128, 0.24);
        border-radius: 8px;
        padding: 0.45rem 0.75rem;
        margin: 0.45rem 0;
        display: inline-block;
    }

    .guide-box {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.1rem;
        font-size: 0.92rem;
        line-height: 1.58;
        color: var(--text-color);
    }

    .wl-footer {
        margin-top: 3rem;
        padding-top: 1.25rem;
        border-top: 1px solid rgba(128, 128, 128, 0.22);
        font-size: 0.8rem;
        opacity: 0.78;
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. SESSION STATE (NAVIGATION, CHAT HISTORY & MOCK TRADING ACCOUNT)
# ==============================================================================
if "active_page" not in st.session_state:
    st.session_state.active_page = "Research & Paper Trading Studio"
if "selected_term" not in st.session_state:
    st.session_state.selected_term = "Show All Terms (Textbook Guide)"
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

if "paper_account" not in st.session_state:
    st.session_state.paper_account = {
        "created": False,
        "name": "My Practice Portfolio",
        "starting_cash": 25000.0,
        "cash": 25000.0,
        "holdings": {},
        "trades": [],
    }


def go_to_definitions(term: str = "Show All Terms (Textbook Guide)"):
    st.session_state.active_page = "Definitions & Textbook Guide"
    st.session_state.selected_term = term


def fmt_money(val: float | None) -> str:
    if val is None:
        return "N/A"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1e9:
        return f"{sign}${abs_val / 1e9:.2f}B"
    if abs_val >= 1e6:
        return f"{sign}${abs_val / 1e6:.2f}M"
    return f"{sign}${abs_val:,.2f}"


def safe_md(text: str) -> str:
    return text.replace("$", "\\$")


def searchable_selectbox(
    label: str, options: list[str], index: int = 0, placeholder: str = ""
) -> str:
    try:
        return st.selectbox(
            label,
            options=options,
            index=index,
            placeholder=placeholder,
            accept_new_options=True,
        )
    except TypeError:
        return st.selectbox(label, options=options, index=index)


@st.cache_data(ttl=900)
def fetch_market_price(ticker: str) -> tuple[float | None, str]:
    try:
        t_up = ticker.upper()
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{t_up}"
            "?interval=1d&range=5d"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            meta = payload["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice") or meta.get("previousClose")
            if price and float(price) > 0:
                return round(float(price), 2), "Live Market Quote"
    except Exception:
        pass
    return None, "Custom / Manual Quote"


# ==============================================================================
# 3. AUTOMATIC YOUTUBE STOCK VIDEO FINDER (ZERO API KEY NEEDED + API OPTION)
# ==============================================================================
@st.cache_data(ttl=3600)
def fetch_stock_youtube_videos(
    ticker: str, company_name: str, yt_api_key: str = ""
) -> list[dict]:
    clean_co = re.sub(
        r"\b(Inc|Corp|Corporation|Ltd|PLC|Holdings|Group|Co)\b\.?",
        "",
        company_name,
        flags=re.I,
    ).strip()
    query = f"{ticker} {clean_co} stock analysis earnings".strip()
    videos = []

    if yt_api_key.strip():
        try:
            api_url = (
                "https://www.googleapis.com/youtube/v3/search"
                "?part=snippet&type=video&videoEmbeddable=true&maxResults=3"
                f"&q={quote_plus(query)}&key={quote_plus(yt_api_key.strip())}"
            )
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for item in data.get("items", []):
                    vid = item["id"]["videoId"]
                    snip = item["snippet"]
                    videos.append(
                        {
                            "video_id": vid,
                            "url": f"https://www.youtube.com/watch?v={vid}",
                            "title": snip.get("title", f"{ticker} Stock Analysis"),
                            "channel": snip.get("channelTitle", "YouTube"),
                        }
                    )
                if videos:
                    return videos
        except Exception:
            pass

    try:
        search_url = (
            f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        )
        req = urllib.request.Request(
            search_url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        raw_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        unique_ids = []
        for vid in raw_ids:
            if vid not in unique_ids:
                unique_ids.append(vid)
            if len(unique_ids) >= 6:
                break

        for vid in unique_ids:
            watch_url = f"https://www.youtube.com/watch?v={vid}"
            oembed_url = (
                "https://www.youtube.com/oembed"
                f"?url={quote_plus(watch_url)}&format=json"
            )
            try:
                oreq = urllib.request.Request(
                    oembed_url, headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(oreq, timeout=4) as oresp:
                    meta = json.loads(oresp.read().decode("utf-8"))
                    videos.append(
                        {
                            "video_id": vid,
                            "url": watch_url,
                            "title": meta.get("title", f"{ticker} Market Analysis"),
                            "channel": meta.get("author_name", "YouTube Creator"),
                        }
                    )
                if len(videos) >= 3:
                    break
            except Exception:
                continue
    except Exception:
        pass

    return videos


# ==============================================================================
# 4. AD REVENUE & SPONSOR RENDERER (HIDDEN WHEN UNCONFIGURED)
# ==============================================================================
def render_ad_slot(
    slot_name: str,
    dimensions: str,
    enabled: bool,
    preview_empty: bool,
    adsense_pub_id: str,
    adsense_slot_id: str,
    sponsor_title: str,
    sponsor_url: str,
):
    if not enabled:
        return

    pub = adsense_pub_id.strip()
    slot = adsense_slot_id.strip()

    if pub.startswith("ca-pub-") and slot:
        height_px = 100 if "728" in dimensions else 260
        ad_html = (
            '<div style="text-align:center; overflow:hidden;">'
            '<script async src="https://pagead2.googlesyndication.com/pagead/js/'
            f'adsbygoogle.js?client={pub}" crossorigin="anonymous"></script>'
            '<ins class="adsbygoogle" style="display:block" '
            f'data-ad-client="{pub}" data-ad-slot="{slot}" '
            'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            "<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>"
            "</div>"
        )
        components.html(ad_html, height=height_px)
        return

    if sponsor_title.strip() and sponsor_url.strip():
        st.markdown(
            f'<div class="ad-slot-wrapper">'
            f'<div class="ad-label">Sponsored Partner • {slot_name}</div>'
            f'<div class="ad-copy"><a href="{sponsor_url.strip()}" '
            'target="_blank" rel="noopener noreferrer" '
            'style="font-weight:600; text-decoration:none;">'
            f"{sponsor_title.strip()} →</a></div></div>",
            unsafe_allow_html=True,
        )
        return

    if preview_empty:
        st.markdown(
            f'<div class="ad-slot-wrapper">'
            f'<div class="ad-label">Ad Slot Preview • {slot_name} ({dimensions})</div>'
            f'<div class="ad-copy">Paste your <code>ca-pub-...</code> Google AdSense ID '
            "or Sponsor Link in the sidebar to serve live ads here.</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ==============================================================================
# 5. TEXTBOOK FINANCIAL GLOSSARY (DEFINITIONS, FORMULAS & BENCHMARKS)
# ==============================================================================
DEFINITIONS_DB = {
    "Price-to-Sales Ratio ('2x Sales')": {
        "category": "Valuation Multiples",
        "range": "Valuation Metric",
        "textbook": (
            "A valuation multiple that compares a company's total market value "
            "(Market Capitalization) to its trailing twelve-month top-line revenue. "
            "Saying a stock trades at '2x sales' means investors are paying $2 for "
            "every $1 of annual revenue the business generates."
        ),
        "formula": "Price-to-Sales (P/S) = Market Capitalization ÷ Annual Revenue",
        "benchmarks": (
            "Under 1.5x is typical for lower-margin retail or manufacturing; 2x–4x is "
            "common for steady industrial/tech businesses; 6x–15x+ is usually reserved "
            "for high-margin, rapidly growing software companies."
        ),
        "why_it_matters": (
            "Useful for valuing young or fast-growing companies that reinvest heavily "
            "and do not yet report positive net earnings—though high sales multiples "
            "carry steep downside if revenue growth slows."
        ),
    },
    "Sales Growth (YoY & QoQ Revenue Growth)": {
        "category": "Top-Line Momentum",
        "range": "Growth Metric",
        "textbook": (
            "The percentage rate at which a company's gross top-line revenue increases "
            "from one reporting period to the comparable prior period (Year-over-Year "
            "compares Q3 this year to Q3 last year to remove seasonal distortion)."
        ),
        "formula": "Sales Growth (%) = [(Current Rev − Prior Rev) ÷ |Prior Rev|] × 100",
        "benchmarks": (
            "0%–5% signals mature/GDP-level expansion; 10%–20% reflects healthy "
            "compound growth; 25%+ signals hyper-growth—provided gross margins and "
            "cash flow scale alongside it."
        ),
        "why_it_matters": (
            "Consistent sales growth proves customer demand is expanding, which is "
            "the primary justification for higher valuation multiples like 4x–8x sales."
        ),
    },
    "Current Ratio (Short-Term Liquidity)": {
        "category": "Balance Sheet Health",
        "range": "Liquidity Ratio",
        "textbook": (
            "A balance-sheet liquidity ratio measuring a company's ability to pay off "
            "all short-term obligations due within 12 months (Current Liabilities) "
            "using assets convertible to cash within 12 months (Current Assets)."
        ),
        "formula": "Current Ratio = Total Current Assets ÷ Total Current Liabilities",
        "benchmarks": (
            "1.5x–3.0x indicates comfortable short-term liquidity; below 1.0x warns "
            "that near-term bills exceed liquid assets; above 4.0x may suggest idle "
            "cash not being reinvested efficiently."
        ),
        "why_it_matters": (
            "Acts as an early-warning indicator of working-capital stress before a "
            "company misses supplier or debt payments."
        ),
    },
    "Cash on Hand & Net Liquidity": {
        "category": "Balance Sheet Health",
        "range": "Balance Sheet",
        "textbook": (
            "The most liquid line item on the Consolidated Balance Sheet, representing "
            "unrestricted currency, bank deposits, and highly liquid money-market "
            "instruments maturing within 90 days."
        ),
        "formula": "Net Cash = Cash & Short-Term Investments − Total Debt",
        "benchmarks": (
            "Companies with positive Net Cash (more cash than total debt) can weather "
            "recessions without distress."
        ),
        "why_it_matters": (
            "Cash pays payroll and R&D—companies can report accounting profits while "
            "still running out of real cash."
        ),
    },
    "Operating Cash Flow (OCF)": {
        "category": "Balance Sheet Health",
        "range": "Cash Flow Statement",
        "textbook": (
            "Net cash generated or consumed by a company's core ongoing operations, "
            "adjusting GAAP Net Income for non-cash charges (depreciation, stock-based "
            "compensation) and changes in working capital."
        ),
        "formula": "OCF = Net Income + Non-Cash Expenses ± Changes in Working Capital",
        "benchmarks": (
            "Consistently positive OCF confirms the core business model is "
            "self-sustaining; persistent negative OCF requires external cash reserves."
        ),
        "why_it_matters": (
            "Harder to manipulate than accounting earnings because it tracks actual "
            "bank-account cash inflows and outflows."
        ),
    },
    "Free Cash Flow (FCF)": {
        "category": "Balance Sheet Health",
        "range": "Cash Flow Statement",
        "textbook": (
            "The discretionary cash generated by operations after funding all Capital "
            "Expenditures (CapEx) required to maintain and expand property, plant, "
            "equipment, and infrastructure."
        ),
        "formula": "Free Cash Flow (FCF) = Operating Cash Flow − Capital Expenditures",
        "benchmarks": (
            "An FCF Margin (FCF ÷ Revenue) above 15% signals an elite "
            "cash-compounding business."
        ),
        "why_it_matters": (
            "FCF is the true surplus available to retire debt, buy back shares, pay "
            "dividends, or fund acquisitions without dilution."
        ),
    },
    "Cash Runway & Share Dilution Risk": {
        "category": "Balance Sheet Health",
        "range": "Liquidity Horizon",
        "textbook": (
            "The estimated number of quarters a cash-burning enterprise can sustain "
            "operations at its current quarterly operating cash outflow before "
            "depleting cash reserves."
        ),
        "formula": "Cash Runway (Quarters) = Cash on Hand ÷ Quarterly Cash Burn",
        "benchmarks": (
            "8+ quarters (2+ years) provides strategic breathing room; under 8 "
            "quarters places a company on 'Dilution Watch' for equity offerings."
        ),
        "why_it_matters": (
            "When runway drops below 4–6 quarters, management frequently issues new "
            "shares at a discount, diluting existing shareholders' ownership percentage."
        ),
    },
    "Debt-to-Equity Ratio": {
        "category": "Balance Sheet Health",
        "range": "Solvency & Leverage",
        "textbook": (
            "A solvency ratio comparing a company's total financial liabilities to "
            "its total shareholders' equity, quantifying how much operations rely on "
            "debt versus owner capital."
        ),
        "formula": "Debt-to-Equity = Total Liabilities ÷ Total Stockholders' Equity",
        "benchmarks": (
            "Under 1.0x is conservative; 1.0x–2.0x is moderate; above 2.0x signals "
            "high financial leverage (common in utilities/banks, riskier in tech)."
        ),
        "why_it_matters": (
            "High leverage amplifies returns in boom times but magnifies bankruptcy "
            "or restructuring risk when revenue contracts."
        ),
    },
    "Dynamic Wealth Glide-Path": {
        "category": "Portfolio & Simulator",
        "range": "Allocation Strategy",
        "textbook": (
            "A time-varying asset allocation schedule that begins with higher-beta "
            "growth exposure during early accumulation years and shifts toward "
            "lower-volatility assets as the target horizon approaches."
        ),
        "formula": "Rate(t) = Growth_CAGR − 0.5 × (Growth_CAGR − Maint_CAGR) × (t ÷ Horizon)",
        "benchmarks": (
            "Balances early wealth velocity with late-stage sequence-of-returns "
            "protection."
        ),
        "why_it_matters": (
            "Prevents a severe market drawdown right before your goal date from "
            "wiping out decades of compounding."
        ),
    },
    "Escape Velocity (Compounding Crossover)": {
        "category": "Portfolio & Simulator",
        "range": "Compounding Milestone",
        "textbook": (
            "The mathematical inflection point in a recurring-contribution portfolio "
            "where periodic investment gains exceed periodic principal deposits."
        ),
        "formula": "Portfolio Balance × Monthly Return Rate ≥ Monthly Contribution",
        "benchmarks": (
            "Typically reached between Years 7 and 14 depending on savings rate and "
            "annualized return."
        ),
        "why_it_matters": (
            "Marks the transition where your invested capital works harder than your "
            "paycheck."
        ),
    },
}


# ==============================================================================
# 6. EDUCATIONAL CHART BUILDERS
# ==============================================================================
def render_balance_sheet_health_chart(card: dict):
    curr_ratio = card.get("current_ratio")
    dte = card.get("debt_to_equity")
    runway = card.get("runway_quarters")

    labels = [
        "Current Ratio (Target ≥ 1.5x)",
        "Debt-to-Equity (Target ≤ 2.0x)",
        "Cash Runway Qtrs (Target ≥ 8)",
    ]
    actuals = [
        min(curr_ratio, 5.0) if curr_ratio is not None else 0.0,
        min(dte, 5.0) if dte is not None else 0.0,
        min(runway, 16.0) if runway is not None else 12.0,
    ]
    benchmarks = [1.5, 2.0, 8.0]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name=f"{card['ticker']} Actual",
            x=labels,
            y=actuals,
            marker_color=["#0284c7", "#8b5cf6", "#10b981"],
            text=[
                f"{curr_ratio}x" if curr_ratio is not None else "N/A",
                f"{dte}x" if dte is not None else "N/A",
                "Self-Funding" if runway is None else f"{runway} Qtrs",
            ],
            textposition="outside",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Institutional Reference Benchmark",
            x=labels,
            y=benchmarks,
            marker_color="rgba(148, 163, 184, 0.45)",
            text=["1.5x Min", "2.0x Max", "8.0 Qtrs Min"],
            textposition="outside",
        )
    )
    fig.update_layout(
        title=f"Balance-Sheet Health Diagnostic: {card['company']} ({card['ticker']})",
        barmode="group",
        height=330,
        margin=dict(l=15, r=15, t=45, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_2x_sales_chart(card: dict):
    ann_rev = card.get("annualized_revenue", 0.0)
    if ann_rev <= 0:
        ann_rev = 500_000_000.0

    multiples = [
        "1x Sales (Value / Retail)",
        "2x Sales (Industrial / Balanced)",
        "4x Sales (Growth Tech)",
        "8x Sales (High-Margin SaaS)",
    ]
    valuations = [ann_rev * 1, ann_rev * 2, ann_rev * 4, ann_rev * 8]

    fig = go.Figure(
        data=[
            go.Bar(
                x=multiples,
                y=valuations,
                marker_color=["#64748b", "#0284c7", "#10b981", "#8b5cf6"],
                text=[fmt_money(v) for v in valuations],
                textposition="outside",
            )
        ]
    )
    fig.update_layout(
        title=(
            f"What '2x Sales' Looks Like for {card['ticker']} "
            f"(Annualized Rev: {fmt_money(ann_rev)})"
        ),
        yaxis_title="Implied Company Valuation ($)",
        height=330,
        margin=dict(l=15, r=15, t=45, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_sales_growth_chart(card: dict):
    base_rev = card.get("annualized_revenue", 0.0)
    if base_rev <= 0:
        base_rev = 100_000_000.0

    yrs = np.arange(0, 6)
    fig = go.Figure()
    rates = [
        ("5% Mature Growth", 0.05, "#94a3b8", "dash"),
        ("15% Compounder", 0.15, "#0284c7", "solid"),
        ("30% High-Growth", 0.30, "#10b981", "solid"),
        ("50% Hyper-Growth", 0.50, "#8b5cf6", "dot"),
    ]
    for label, g, color, dash in rates:
        proj = [base_rev * ((1 + g) ** t) for t in yrs]
        fig.add_trace(
            go.Scatter(
                x=[f"Year {t}" for t in yrs],
                y=proj,
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=3, dash=dash),
            )
        )
    fig.update_layout(
        title=f"5-Year Sales Growth Curve (Starting from {fmt_money(base_rev)} Revenue)",
        yaxis_title="Projected Annual Revenue ($)",
        hovermode="x unified",
        height=330,
        margin=dict(l=15, r=15, t=45, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


# ==============================================================================
# 7. SIDEBAR: NAVIGATION, MOCK ACCOUNT, MONETIZATION, TEXTBOOK & AI SETTINGS
# ==============================================================================
st.sidebar.markdown("### Workspace Navigation")
page = st.sidebar.radio(
    "Workspace View",
    [
        "Research & Paper Trading Studio",
        "Definitions & Textbook Guide",
        "Mock Trading Account",
    ],
    key="active_page",
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.markdown("### Paper Portfolio Snapshot")
acct = st.session_state.paper_account
if acct["created"]:
    st.sidebar.caption(f"Account: **{acct['name']}**")
    st.sidebar.metric("Available Virtual Cash", fmt_money(acct["cash"]))
    st.sidebar.caption(
        f"Open Positions: **{len(acct['holdings'])}** • "
        f"Trades Logged: **{len(acct['trades'])}**"
    )
else:
    st.sidebar.info(
        "No mock trading account active yet. Open one in **Mock Trading Account** "
        "to practice with virtual cash."
    )

st.sidebar.divider()
st.sidebar.markdown("### Quick Textbook Lookup")
term_choices = ["Show All Terms (Textbook Guide)"] + list(DEFINITIONS_DB.keys())
picked_term = st.sidebar.selectbox(
    "Inspect a formula or definition:",
    options=term_choices,
    key="selected_term",
)

if picked_term != "Show All Terms (Textbook Guide)":
    info = DEFINITIONS_DB[picked_term]
    st.sidebar.info(
        safe_md(f"**{picked_term}**\n\n{info['textbook']}\n\n`{info['formula']}`")
    )
    if page != "Definitions & Textbook Guide":
        st.sidebar.button(
            "Open Full Textbook & Charts →",
            on_click=go_to_definitions,
            args=(picked_term,),
            use_container_width=True,
        )
else:
    if page != "Definitions & Textbook Guide":
        st.sidebar.button(
            "Open Textbook & Visual Charts →",
            on_click=go_to_definitions,
            args=("Show All Terms (Textbook Guide)",),
            use_container_width=True,
        )

st.sidebar.divider()
with st.sidebar.expander("Ad Revenue & Sponsor Settings", expanded=False):
    show_ads = st.checkbox("Enable Ad Revenue Slots", value=True)
    preview_empty_ads = st.checkbox("Preview Empty Ad Slots", value=False)
    adsense_pub = st.text_input(
        "Google AdSense Publisher ID", value="", placeholder="ca-pub-xxxxxxxxxxxxxxxx"
    )
    adsense_slot = st.text_input(
        "AdSense Ad Unit Slot ID", value="", placeholder="1234567890"
    )
    sponsor_title = st.text_input(
        "Or Custom Sponsor / Affiliate Text",
        value="",
        placeholder="e.g., Try Commission-Free Paper Trading",
    )
    sponsor_url = st.text_input(
        "Custom Sponsor / Affiliate URL", value="", placeholder="https://..."
    )
    st.caption(
        "**Monetization Note:** Empty ad slots stay hidden from visitors until you "
        "paste a `ca-pub-...` AdSense ID or Sponsor Link above."
    )

with st.sidebar.expander("AI Coach, YouTube & SEC API Settings", expanded=False):
    env_gemini = os.environ.get("GEMINI_API_KEY", "").strip()
    user_gemini_key = st.text_input(
        "Gemini API Key (Optional override)",
        value="",
        type="password",
        placeholder=(
            "Uses server GEMINI_API_KEY automatically if set"
            if env_gemini
            else "Paste AIza... key for live dynamic chat"
        ),
    )
    active_gemini_key = user_gemini_key.strip() or env_gemini

    yt_api_key = st.text_input(
        "YouTube Data API v3 Key (Optional)",
        value=os.environ.get("YOUTUBE_API_KEY", ""),
        type="password",
        placeholder="Leave blank for automatic keyless search",
    )
    ai_model = st.selectbox(
        "AI Model",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0,
    )
    sec_email = st.text_input("SEC Contact Email", value="sanatanstein@gmail.com")

set_identity(sec_email)

render_ad_slot(
    "Sidebar Rectangle",
    "300×250",
    show_ads,
    preview_empty_ads,
    adsense_pub,
    adsense_slot,
    sponsor_title,
    sponsor_url,
)


# ==============================================================================
# 8. SEC EDGAR LIVE DATA MINER (FINANCIALS, LATEST FILINGS & INSIDER TRADES)
# ==============================================================================
@st.cache_data(ttl=86400)
def load_sec_directory() -> list[str]:
    featured = [
        "LUNR — Intuitive Machines, Inc.",
        "NVDA — NVIDIA CORP",
        "RKLB — Rocket Lab USA, Inc.",
        "SMR — NuScale Power Corp",
        "PLTR — Palantir Technologies Inc.",
        "AAPL — Apple Inc.",
        "TSLA — Tesla, Inc.",
        "MSFT — MICROSOFT CORP",
        "AMZN — AMAZON COM INC",
        "ASTS — AST SpaceMobile, Inc.",
    ]
    try:
        from edgar.reference.tickers import get_cik_tickers

        df = get_cik_tickers()
        ticker_col = next((c for c in df.columns if "ticker" in c.lower()), None)
        name_col = next(
            (
                c
                for c in df.columns
                if c.lower() in ("title", "name", "company", "company_name")
            ),
            None,
        )
        if ticker_col and name_col:
            seen = {item.split(" — ")[0] for item in featured}
            rest = []
            for t, n in zip(df[ticker_col].astype(str), df[name_col].astype(str)):
                t_clean = t.strip().upper()
                if t_clean and t_clean not in seen and t_clean != "NAN":
                    seen.add(t_clean)
                    rest.append(f"{t_clean} — {n.strip()}")
            return (featured + rest)[:300]
    except Exception:
        pass
    return featured


def extract_cash(fin) -> tuple[float, str]:
    if fin is None:
        return 0.0, "Unavailable"
    bs = fin.balance_sheet()
    if bs is None:
        return float(fin.get_current_assets() or 0.0), "Latest"
    bs_df = bs.to_dataframe()
    if bs_df is None or bs_df.empty:
        return float(fin.get_current_assets() or 0.0), "Latest"
    date_cols = [c for c in bs_df.columns if str(c).startswith("20")]
    if not date_cols:
        return float(fin.get_current_assets() or 0.0), "Latest"
    latest_period = date_cols[0]
    cash_rows = bs_df[bs_df["label"].str.contains("Cash", case=False, na=False)]
    numeric_cash = pd.to_numeric(cash_rows[latest_period], errors="coerce").dropna()
    if not numeric_cash.empty:
        return float(numeric_cash.iloc[0]), str(latest_period)
    return float(fin.get_current_assets() or 0.0), str(latest_period)


def extract_sales_growth(fin) -> float | None:
    if fin is None:
        return None
    try:
        inc = fin.income_statement()
        if inc is None:
            return None
        inc_df = inc.to_dataframe()
        if inc_df is None or inc_df.empty:
            return None
        date_cols = [c for c in inc_df.columns if str(c).startswith("20")]
        if len(date_cols) < 2:
            return None
        rev_rows = inc_df[
            inc_df["label"].str.contains("Revenue|Sales", case=False, na=False)
        ]
        if rev_rows.empty:
            return None
        curr_val = pd.to_numeric(rev_rows[date_cols[0]], errors="coerce").dropna()
        prev_val = pd.to_numeric(rev_rows[date_cols[1]], errors="coerce").dropna()
        if not curr_val.empty and not prev_val.empty:
            c_v = float(curr_val.iloc[0])
            p_v = float(prev_val.iloc[0])
            if p_v != 0:
                return round(((c_v - p_v) / abs(p_v)) * 100.0, 1)
    except Exception:
        pass
    return None


@st.cache_data(ttl=1800)
def build_health_card(ticker: str) -> dict:
    company = Company(ticker)
    q_fin = company.get_quarterly_financials()
    a_fin = company.get_financials()
    fin = q_fin if q_fin is not None else a_fin
    is_quarterly = q_fin is not None

    revenue = fin.get_revenue() or 0.0
    annualized_rev = (revenue * 4.0) if is_quarterly else revenue
    net_income = fin.get_net_income() or 0.0
    op_cf = fin.get_operating_cash_flow() or 0.0
    free_cf = fin.get_free_cash_flow()
    total_liabilities = fin.get_total_liabilities() or 0.0
    equity = fin.get_stockholders_equity() or 0.0

    try:
        curr_assets = fin.get_current_assets() or 0.0
        curr_liab = fin.get_current_liabilities() or 0.0
        current_ratio = round(curr_assets / curr_liab, 2) if curr_liab > 0 else None
    except Exception:
        current_ratio = None

    sales_growth_pct = extract_sales_growth(fin)
    if sales_growth_pct is None and is_quarterly and a_fin is not None:
        sales_growth_pct = extract_sales_growth(a_fin)

    cash, latest_period = extract_cash(fin)
    if cash == 0.0 and is_quarterly and a_fin is not None:
        cash, latest_period = extract_cash(a_fin)

    if op_cf >= 0:
        runway_quarters = None
        health_badge = "Self-Funding (Positive Operating Cash Flow)"
    else:
        quarterly_burn = abs(op_cf) if is_quarterly else abs(op_cf) / 4.0
        runway_quarters = round(cash / quarterly_burn, 1) if quarterly_burn > 0 else 0.0
        health_badge = (
            "Healthy Runway (8+ Quarters)"
            if runway_quarters >= 8
            else "Dilution Watch (Under 8 Quarters)"
        )

    debt_to_equity = round(total_liabilities / equity, 2) if equity > 0 else None

    if op_cf >= 0 and (debt_to_equity is None or debt_to_equity <= 1.5):
        stress_tier = "Fortress Liquidity"
    elif op_cf >= 0 or (runway_quarters is not None and runway_quarters >= 8):
        stress_tier = "Steady Runway"
    else:
        stress_tier = "Speculative Cash Burn"

    recent_filings = []
    try:
        filings = company.get_filings().head(8)
        for f in filings:
            f_url = getattr(f, "homepage_url", None) or getattr(f, "url", "")
            recent_filings.append(
                {
                    "Form": str(getattr(f, "form", "")),
                    "Filed Date": str(getattr(f, "filing_date", "")),
                    "Period": str(getattr(f, "report_date", "") or "—"),
                    "SEC Link": str(f_url),
                }
            )
    except Exception:
        pass

    insider_filings_count = 0
    latest_insider_date = "None in past 90d"
    try:
        f4 = company.get_filings(form="4").head(5)
        f4_list = list(f4)
        insider_filings_count = len(f4_list)
        if f4_list:
            latest_insider_date = str(getattr(f4_list[0], "filing_date", "Recent"))
    except Exception:
        pass

    return {
        "ticker": ticker.upper(),
        "company": company.name,
        "period": latest_period,
        "filing_cadence": "Quarterly (10-Q)" if is_quarterly else "Annual (10-K)",
        "mined_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "cash_on_hand": round(cash, 2),
        "revenue": round(revenue, 2),
        "annualized_revenue": round(annualized_rev, 2),
        "two_x_sales_val": round(annualized_rev * 2.0, 2),
        "sales_growth_pct": sales_growth_pct,
        "net_income": round(net_income, 2),
        "operating_cash_flow": round(op_cf, 2),
        "free_cash_flow": round(free_cf, 2) if free_cf is not None else None,
        "current_ratio": current_ratio,
        "debt_to_equity": debt_to_equity,
        "runway_quarters": runway_quarters,
        "health_badge": health_badge,
        "stress_tier": stress_tier,
        "recent_filings": recent_filings,
        "insider_filings_count": insider_filings_count,
        "latest_insider_date": latest_insider_date,
    }


# ==============================================================================
# 9. DYNAMIC CONNECTIVE CHATBOT ENGINE (PLAIN ENGLISH OR ANY USER-CHOSEN FIELD)
# ==============================================================================
def build_plain_english_fallback(
    card: dict, user_prompt: str, connect_topic: str
) -> str:
    cash_str = fmt_money(card["cash_on_hand"])
    rev_str = fmt_money(card["annualized_revenue"])
    two_x_str = fmt_money(card["two_x_sales_val"])
    cf_str = fmt_money(card["operating_cash_flow"])
    fcf_str = fmt_money(card["free_cash_flow"])
    runway = card["runway_quarters"]
    dte = card["debt_to_equity"]
    cr = card["current_ratio"]
    growth = card["sales_growth_pct"]

    q_low = user_prompt.lower()
    topic_clean = connect_topic.strip()

    if "2x" in q_low or "sales" in q_low or "valuation" in q_low:
        growth_note = f" ({growth:+.1f}% period sales growth)" if growth is not None else ""
        base = (
            f"**Plain English Breakdown ({card['ticker']}):**\n"
            f"- What they bring in: is currently pacing at "
            f"**{rev_str}** in annualized revenue{growth_note}.\n"
            f"- **What '2x Sales' means:** If investors value the whole company at "
            f"**2x annual sales**, that puts its price tag at **{two_x_str}** — "
            "meaning buyers pay $2 for every $1 of yearly revenue before expenses.\n"
            "- **Why it matters:** Lower-margin businesses often trade around 1x–2x "
            "sales, while fast-growing software or tech companies can trade at 5x–10x+."
        )
    elif "dilut" in q_low or "runway" in q_low or "cash" in q_low or "burn" in q_low:
        if runway is None:
            base = (
                f"**Plain English Breakdown ({card['ticker']}):**\n"
                f"- Low dilution pressure: generated **{cf_str}** "
                f"in positive operating cash flow ({fcf_str} Free Cash Flow) and holds "
                f"**{cash_str}** in cash.\n"
                "- **What that means for you:** Because the core business brings in "
                "more cash than it spends, it doesn't urgently need to issue new shares."
            )
        else:
            burn_str = fmt_money(abs(card["operating_cash_flow"]))
            base = (
                f"**Plain English Breakdown ({card['ticker']}):**\n"
                f"- The cash clock: has **{cash_str}** in the bank "
                f"while burning roughly **{burn_str}** per period, leaving about "
                f"**{runway} quarters** of runway.\n"
                "- **Share dilution explained simply:** If cash runway drops under "
                "8 quarters, companies often raise cash by issuing new shares—shrinking "
                "each existing share's slice of the company."
            )
    elif (
        "debt" in q_low
        or "current ratio" in q_low
        or "balance sheet" in q_low
        or "healthy" in q_low
        or "big picture" in q_low
    ):
        runway_line = (
            f"Their core operations bring in **{cf_str}** in cash flow, so they fund themselves."
            if runway is None
            else (
                f"They are currently burning cash, giving them roughly **{runway} quarters** "
                f"of runway from their **{cash_str}** cash reserve."
            )
        )
        cr_disp = f"{cr}x" if cr is not None else "N/A"
        dte_disp = f"{dte}x" if dte is not None else "N/A"
        base = (
            f"**Plain English Snapshot — {card['company']} ({card['ticker']}):**\n"
            f"- **Cash vs. Burn:** {runway_line}\n"
            f"- **Short-Term Bills (Current Ratio: {cr_disp}):** Measures whether short-term "
            "assets cover bills due in the next 12 months (above `1.5x` is comfortable).\n"
            f"- **Debt Load (Debt-to-Equity: {dte_disp}):** Compares total liabilities against "
            "shareholder equity (under `1.5x–2.0x` is moderate)."
        )
    else:
        cr_disp = f"{cr}x" if cr is not None else "N/A"
        dte_disp = f"{dte}x" if dte is not None else "N/A"
        base = (
            f"**Plain English Answer for {card['company']} ({card['ticker']}):**\n"
            f"- **Revenue pace:** **{rev_str}** annualized ({two_x_str} at 2x Sales).\n"
            f"- **Cash & Operations:** **{cash_str}** cash on hand with **{cf_str}** "
            f"operating cash flow ({card['health_badge']}).\n"
            f"- **Balance-Sheet Ratios:** Current Ratio is **{cr_disp}** and "
            f"Debt-to-Equity is **{dte_disp}**."
        )

    if topic_clean:
        base += (
            f"\n\n*Tip for **{topic_clean}** connections:* Add your free `GEMINI_API_KEY` "
            "in Render Environment Variables (or the sidebar) to unlock live AI reasoning "
            f"that weaves **{topic_clean}** directly into any follow-up question you ask!"
        )
    return base


def generate_chat_reply(
    card: dict,
    messages: list[dict],
    user_prompt: str,
    connect_topic: str,
    api_key: str,
    model_name: str,
) -> str:
    if not api_key.strip():
        return build_plain_english_fallback(card, user_prompt, connect_topic)

    try:
        from google import genai

        client = genai.Client(api_key=api_key.strip())

        runway_val = (
            card["runway_quarters"]
            if card["runway_quarters"] is not None
            else "Self-Funding (Positive Operating Cash Flow)"
        )
        sec_context = {
            "company": card["company"],
            "ticker": card["ticker"],
            "period": card["period"],
            "filing_cadence": card["filing_cadence"],
            "cash_on_hand": fmt_money(card["cash_on_hand"]),
            "annualized_revenue": fmt_money(card["annualized_revenue"]),
            "two_x_sales_valuation": fmt_money(card["two_x_sales_val"]),
            "sales_growth_pct": card["sales_growth_pct"],
            "operating_cash_flow": fmt_money(card["operating_cash_flow"]),
            "free_cash_flow": fmt_money(card["free_cash_flow"]),
            "current_ratio": card["current_ratio"],
            "debt_to_equity": card["debt_to_equity"],
            "runway_quarters": runway_val,
            "health_badge": card["health_badge"],
            "stress_tier": card["stress_tier"],
            "recent_insider_form4_count": card["insider_filings_count"],
        }

        topic_clean = connect_topic.strip()
        if topic_clean:
            bridge_instruction = (
                f"The user optionally asked to connect investing concepts to: '{topic_clean}'. "
                f"Build organic, genuinely insightful connective pathways between how "
                f"{card['company']} operates financially and real mechanics in '{topic_clean}'. "
                "CRITICAL RULE: Do NOT force cheesy one-to-one props or corny metaphors for "
                "every single number. Only draw a parallel where the underlying logic actually "
                "clicks, and explain the rest in crisp, everyday Plain English."
            )
        else:
            bridge_instruction = (
                "The user chose Plain English mode (no outside hobby or metaphor). Explain "
                "everything in clear, zero-jargon everyday English—like a sharp, friendly "
                "peer breaking down the SEC numbers over coffee."
            )

        recent_turns = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in messages[-6:]
        )

        system_and_prompt = f"""You are the live interactive financial learning coach on BornYesterdayInvestEd.com.
Your job is to help beginners understand real SEC filing numbers clearly, honestly, and conversationally—without Wall Street jargon or hype.

VERIFIED SEC DATA FOR {card['company']} ({card['ticker']}):
{json.dumps(sec_context, indent=2)}

EXPLANATION STYLE & CONNECTIVE PATHWAY INSTRUCTION:
{bridge_instruction}

GUIDELINES:
- Ground your answer in the verified SEC numbers above (cite exact dollar figures and ratios naturally).
- Keep responses concise, scannable, and conversational (2 short paragraphs or 3-4 crisp bullets—under 180 words unless the user asks to go deep).
- Never give personalized buy/sell financial advice or predict stock prices.
- End with one natural, optional follow-up angle the user might want to explore next.

CONVERSATION SO FAR:
{recent_turns}

USER'S NEW MESSAGE:
{user_prompt}
"""
        res = client.models.generate_content(
            model=model_name, contents=system_and_prompt
        )
        return res.text.strip()
    except Exception as e:
        fallback = build_plain_english_fallback(card, user_prompt, connect_topic)
        return f"*Live AI note ({e}) — showing Plain English breakdown:*\n\n{fallback}"


# ==============================================================================
# 10. SLEEK BRAND MASTHEAD, COMPACT HERO BANNER & GLOBAL TICKER SELECTOR
# ==============================================================================
if LOGO_PATH:
    ext = LOGO_PATH.rsplit(".", 1)[-1].lower()
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    with open(LOGO_PATH, "rb") as f:
        b64_logo = base64.b64encode(f.read()).decode("utf-8")
    brand_mark_html = (
        f'<img src="data:{mime};base64,{b64_logo}" '
        'alt="BornYesterdayInvestEd" class="wl-masthead-logo" />'
    )
else:
    brand_mark_html = """
    <svg class="wl-masthead-logo" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
        <rect width="120" height="120" rx="24" fill="#0f172a"/>
        <polyline points="14,98 44,72 56,80 82,50 92,56 106,24" fill="none" stroke="#22c55e" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"/>
        <polygon points="106,18 94,26 109,33" fill="#22c55e"/>
        <circle cx="28" cy="74" r="7" fill="#ffffff"/>
        <line x1="28" y1="81" x2="28" y2="94" stroke="#ffffff" stroke-width="4" stroke-linecap="round"/>
        <line x1="28" y1="94" x2="22" y2="104" stroke="#ffffff" stroke-width="4" stroke-linecap="round"/>
        <line x1="28" y1="94" x2="35" y2="104" stroke="#ffffff" stroke-width="4" stroke-linecap="round"/>
        <circle cx="56" cy="52" r="8" fill="#ffffff"/>
        <line x1="56" y1="60" x2="56" y2="80" stroke="#ffffff" stroke-width="4.5" stroke-linecap="round"/>
        <line x1="56" y1="80" x2="47" y2="104" stroke="#ffffff" stroke-width="4.5" stroke-linecap="round"/>
        <line x1="56" y1="80" x2="66" y2="104" stroke="#ffffff" stroke-width="4.5" stroke-linecap="round"/>
        <circle cx="88" cy="30" r="10" fill="#ffffff"/>
        <line x1="88" y1="40" x2="88" y2="70" stroke="#ffffff" stroke-width="5" stroke-linecap="round"/>
        <line x1="88" y1="70" x2="75" y2="104" stroke="#ffffff" stroke-width="5" stroke-linecap="round"/>
        <line x1="88" y1="70" x2="102" y2="104" stroke="#ffffff" stroke-width="5" stroke-linecap="round"/>
    </svg>
    """

st.markdown(
    f"""
    <div class="wl-masthead">
        {brand_mark_html}
        <div>
            <div class="wl-masthead-name">BornYesterdayInvestEd.com</div>
            <div class="wl-masthead-tagline">SEC EDGAR Filing Miner • Plain-English AI Coach • Textbook Charts • Paper Trading</div>
        </div>
    </div>
    <div class="wl-hero">
        <div class="wl-hero-badge">Zero-Jargon Market Research & Practice Sandbox</div>
        <p class="wl-hero-sub">
            Start from square one and build real market literacy. Pick any public company below—mine its newest SEC EDGAR filings (10-Q, 10-K, 8-K, Form 4),
            chat live with an AI coach in <strong>Plain English</strong> (or connect concepts to any topic you already know),
            and test your ideas risk-free in your Mock Trading Account.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

render_ad_slot(
    "Top Leaderboard",
    "728×90",
    show_ads,
    preview_empty_ads,
    adsense_pub,
    adsense_slot,
    sponsor_title,
    sponsor_url,
)

sec_options = load_sec_directory()

col_in1, col_in2 = st.columns([3.2, 0.8])
with col_in1:
    selected_company = searchable_selectbox(
        "Choose a Company to Research (Search or Type Any SEC Ticker)",
        options=sec_options,
        index=0,
        placeholder="Type a company name or ticker (e.g., Rocket, NVIDIA, PLTR, SMR)...",
    )
with col_in2:
    st.write("")
    st.write("")
    if st.button(
        "Refresh SEC Data",
        help="Clear cache and pull newest SEC filings & quotes",
        use_container_width=True,
    ):
        build_health_card.clear()
        fetch_stock_youtube_videos.clear()
        fetch_market_price.clear()
        st.rerun()

ticker = selected_company.split(" — ")[0].strip().upper() if selected_company else "LUNR"

with st.spinner(f"Mining latest SEC filings & market quotes for {ticker}..."):
    try:
        card = build_health_card(ticker)
        live_quote, quote_src = fetch_market_price(ticker)
    except Exception as e:
        st.error(
            f"Could not find SEC XBRL financials for '{ticker}' ({e}). "
            "Try selecting another company above."
        )
        st.stop()


# ==============================================================================
# 11. PAGE A: IN-DEPTH DEFINITIONS & TEXTBOOK GUIDE (WITH INTERACTIVE CHARTS)
# ==============================================================================
if page == "Definitions & Textbook Guide":

    def back_to_main():
        st.session_state.active_page = "Research & Paper Trading Studio"

    top_b1, top_b2 = st.columns([3.2, 1])
    with top_b1:
        st.header("Textbook Financial Definitions & Visual Guide")
        st.markdown(
            "Plain-English & formal textbook definitions, formulas, institutional "
            f"benchmarks, and live charts grounded in **{card['company']} ({card['ticker']})**."
        )
    with top_b2:
        st.write("")
        st.button(
            "← Back to Studio",
            on_click=back_to_main,
            type="primary",
            use_container_width=True,
        )

    filter_cat = st.radio(
        "Filter Textbook Module:",
        [
            "All Modules (10)",
            "Balance Sheet Health",
            "Valuation Multiples ('2x Sales')",
            "Top-Line Momentum (Sales Growth)",
            "Portfolio & Simulator",
        ],
        horizontal=True,
    )

    st.markdown("### Visual Chart Lab (Live SEC Data + Benchmark Curves)")
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(
        [
            "Chart 1: Balance-Sheet Health Benchmarks",
            "Chart 2: '2x Sales' Valuation Multiple Ladder",
            "Chart 3: Sales Growth Compounding Curves",
        ]
    )
    with chart_tab1:
        render_balance_sheet_health_chart(card)
        st.caption(
            "Compares the selected company's Current Ratio, Debt-to-Equity leverage, "
            "and Cash Runway against standard institutional safety guardrails."
        )
    with chart_tab2:
        render_2x_sales_chart(card)
        st.caption(
            "Illustrates how company valuation scales at 1x, 2x, 4x, and 8x annualized "
            "revenue—showing why '2x sales' doubles top-line revenue to price the business."
        )
    with chart_tab3:
        render_sales_growth_chart(card)
        st.caption(
            "Demonstrates how 5%, 15%, 30%, and 50% annual sales growth rates compound "
            "a company's top line over a 5-year horizon."
        )

    st.divider()
    st.markdown("### Textbook Reference Entries")

    terms_to_show = list(DEFINITIONS_DB.keys())
    if picked_term != "Show All Terms (Textbook Guide)" and picked_term in DEFINITIONS_DB:
        terms_to_show = [picked_term] + [t for t in terms_to_show if t != picked_term]

    for term in terms_to_show:
        item = DEFINITIONS_DB[term]
        if (
            filter_cat == "Balance Sheet Health"
            and item["category"] != "Balance Sheet Health"
        ):
            continue
        if (
            filter_cat == "Valuation Multiples ('2x Sales')"
            and item["category"] != "Valuation Multiples"
        ):
            continue
        if (
            filter_cat == "Top-Line Momentum (Sales Growth)"
            and item["category"] != "Top-Line Momentum"
        ):
            continue
        if (
            filter_cat == "Portfolio & Simulator"
            and item["category"] != "Portfolio & Simulator"
        ):
            continue

        is_highlighted = term == picked_term
        with st.container(border=True):
            c_head, c_badge = st.columns([4, 1.1])
            c_head.subheader(f"{'Focused Entry: ' if is_highlighted else ''}{term}")
            c_badge.caption(f"**{item['category']}**\n\n`{item['range']}`")

            st.markdown(
                safe_md(f"**Plain-English & Textbook Definition:** {item['textbook']}")
            )
            st.markdown(
                f'<div class="formula-pill">Formula: {item["formula"]}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(safe_md(f"**Institutional Benchmarks:** {item['benchmarks']}"))
            st.markdown(safe_md(f"**Why It Matters:** {item['why_it_matters']}"))


# ==============================================================================
# 12. PAGE B: MOCK TRADING ACCOUNT (PAPER PORTFOLIO)
# ==============================================================================
elif page == "Mock Trading Account":

    def back_to_studio():
        st.session_state.active_page = "Research & Paper Trading Studio"

    h1, h2 = st.columns([3.2, 1])
    with h1:
        st.header("Mock Trading Account (Paper Portfolio)")
        st.caption(
            "Practice turning SEC balance-sheet and valuation research into portfolio "
            "decisions using virtual cash—zero real money at risk."
        )
    with h2:
        st.write("")
        st.button(
            "← Back to Research Studio",
            on_click=back_to_studio,
            type="primary",
            use_container_width=True,
        )

    if not acct["created"]:
        with st.container(border=True):
            st.subheader("Create Your Practice Portfolio")
            st.write(
                "Open a virtual brokerage account to test how companies with strong "
                "balance-sheet health, reasonable sales multiples, or accelerating "
                "revenue growth perform over time."
            )
            c_setup1, c_setup2 = st.columns(2)
            acct_name = c_setup1.text_input(
                "Portfolio Name", value="My Research Portfolio"
            )
            start_balance = c_setup2.selectbox(
                "Starting Virtual Cash",
                [10000.0, 25000.0, 50000.0, 100000.0],
                index=1,
                format_func=lambda x: f"${x:,.0f}",
            )
            if st.button("Open Mock Trading Account", type="primary"):
                st.session_state.paper_account = {
                    "created": True,
                    "name": acct_name.strip() or "My Practice Portfolio",
                    "starting_cash": float(start_balance),
                    "cash": float(start_balance),
                    "holdings": {},
                    "trades": [],
                }
                st.rerun()
    else:
        holdings_rows = []
        invested_value = 0.0
        for sym, pos in acct["holdings"].items():
            live_px, _ = fetch_market_price(sym)
            mark_px = live_px if live_px is not None else pos["avg_cost"]
            mkt_val = pos["shares"] * mark_px
            cost_basis = pos["shares"] * pos["avg_cost"]
            pnl = mkt_val - cost_basis
            pnl_pct = (
                ((mark_px - pos["avg_cost"]) / pos["avg_cost"] * 100.0)
                if pos["avg_cost"] > 0
                else 0.0
            )
            invested_value += mkt_val
            holdings_rows.append(
                {
                    "Ticker": sym,
                    "Company": pos["company"],
                    "Shares": round(pos["shares"], 4),
                    "Avg Cost": f"${pos['avg_cost']:,.2f}",
                    "Current Price": f"${mark_px:,.2f}",
                    "Market Value": mkt_val,
                    "Unrealized P&L": pnl,
                    "Return (%)": f"{pnl_pct:+.2f}%",
                }
            )

        total_equity = acct["cash"] + invested_value
        total_pnl = total_equity - acct["starting_cash"]
        total_pnl_pct = (
            (total_pnl / acct["starting_cash"] * 100.0)
            if acct["starting_cash"] > 0
            else 0.0
        )

        st.subheader(f"{acct['name']}")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric(
            "Total Account Value",
            fmt_money(total_equity),
            delta=f"{total_pnl_pct:+.2f}% overall",
        )
        k2.metric("Available Virtual Cash", fmt_money(acct["cash"]))
        k3.metric("Invested in Stocks", fmt_money(invested_value))
        k4.metric("Total Gain / Loss", fmt_money(total_pnl))

        st.divider()
        trade_col, port_col = st.columns([1.05, 1.45], gap="large")

        with trade_col:
            with st.container(border=True):
                st.markdown(f"#### Place a Paper Trade: `{ticker}`")
                st.caption(f"{card['company']} • **{card['health_badge']}**")

                default_px = live_quote if live_quote is not None else 25.00
                st.caption(f"Quote Source: **{quote_src}**")

                side = st.radio("Order Action", ["Buy", "Sell"], horizontal=True)
                exec_price = st.number_input(
                    "Execution Price ($)",
                    min_value=0.01,
                    value=float(default_px),
                    step=0.50,
                )
                dollar_amt = st.number_input(
                    "Order Amount ($ USD)",
                    min_value=10.0,
                    max_value=1000000.0,
                    value=1000.0,
                    step=100.0,
                )
                est_shares = dollar_amt / exec_price
                st.write(
                    safe_md(f"Estimated Shares: **{est_shares:.4f} shares** of **{ticker}**")
                )

                if st.button(
                    f"Submit Paper {side} Order", type="primary", use_container_width=True
                ):
                    if side == "Buy":
                        if dollar_amt > acct["cash"]:
                            st.error("Insufficient virtual cash for this order.")
                        else:
                            acct["cash"] -= dollar_amt
                            existing = acct["holdings"].get(ticker)
                            if existing:
                                new_shares = existing["shares"] + est_shares
                                new_avg = (
                                    (existing["shares"] * existing["avg_cost"])
                                    + dollar_amt
                                ) / new_shares
                                acct["holdings"][ticker] = {
                                    "company": card["company"],
                                    "shares": new_shares,
                                    "avg_cost": new_avg,
                                }
                            else:
                                acct["holdings"][ticker] = {
                                    "company": card["company"],
                                    "shares": est_shares,
                                    "avg_cost": exec_price,
                                }
                            acct["trades"].insert(
                                0,
                                {
                                    "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "Action": "BUY",
                                    "Ticker": ticker,
                                    "Shares": round(est_shares, 4),
                                    "Price": f"${exec_price:,.2f}",
                                    "Total": fmt_money(dollar_amt),
                                },
                            )
                            st.success(
                                safe_md(
                                    f"Bought {est_shares:.4f} shares of {ticker} "
                                    f"for {fmt_money(dollar_amt)}."
                                )
                            )
                            st.rerun()
                    else:
                        existing = acct["holdings"].get(ticker)
                        if not existing or existing["shares"] <= 0:
                            st.error(
                                f"You don't currently own any shares of {ticker} to sell."
                            )
                        else:
                            sell_shares = min(est_shares, existing["shares"])
                            proceeds = sell_shares * exec_price
                            acct["cash"] += proceeds
                            rem_shares = existing["shares"] - sell_shares
                            if rem_shares <= 0.0001:
                                del acct["holdings"][ticker]
                            else:
                                existing["shares"] = rem_shares
                            acct["trades"].insert(
                                0,
                                {
                                    "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "Action": "SELL",
                                    "Ticker": ticker,
                                    "Shares": round(sell_shares, 4),
                                    "Price": f"${exec_price:,.2f}",
                                    "Total": fmt_money(proceeds),
                                },
                            )
                            st.success(
                                safe_md(
                                    f"Sold {sell_shares:.4f} shares of {ticker} "
                                    f"for {fmt_money(proceeds)}."
                                )
                            )
                            st.rerun()

            with st.expander("Account Settings & Reset", expanded=False):
                if st.button("Reset Account & Start Over", use_container_width=True):
                    st.session_state.paper_account["created"] = False
                    st.rerun()

        with port_col:
            st.markdown("#### Current Holdings")
            if holdings_rows:
                df_hold = pd.DataFrame(holdings_rows)
                df_display = df_hold.copy()
                df_display["Market Value"] = df_display["Market Value"].apply(fmt_money)
                df_display["Unrealized P&L"] = df_display["Unrealized P&L"].apply(
                    fmt_money
                )
                st.dataframe(df_display, use_container_width=True, hide_index=True)

                alloc_fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=["Virtual Cash"]
                            + [r["Ticker"] for r in holdings_rows],
                            values=[acct["cash"]]
                            + [r["Market Value"] for r in holdings_rows],
                            hole=0.48,
                        )
                    ]
                )
                alloc_fig.update_layout(
                    height=260,
                    margin=dict(l=10, r=10, t=20, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(alloc_fig, use_container_width=True)
            else:
                st.info(
                    "Your portfolio is currently 100% virtual cash. Use the order "
                    "ticket on the left to place your first practice trade."
                )

            if acct["trades"]:
                st.markdown("#### Recent Trade History")
                st.dataframe(
                    pd.DataFrame(acct["trades"]),
                    use_container_width=True,
                    hide_index=True,
                )


# ==============================================================================
# 13. PAGE C: MAIN RESEARCH & PAPER TRADING STUDIO (LIVE CHATBOT + SEC MINER)
# ==============================================================================
else:
    top_m1, top_m2, top_m3, top_m4, top_m5 = st.columns(5)
    top_m1.metric(
        "Latest Market Price",
        f"${live_quote:,.2f}" if live_quote else "N/A",
        delta=quote_src,
    )
    top_m2.metric("Cash on Hand", fmt_money(card["cash_on_hand"]))
    top_m3.metric("Annualized Sales", fmt_money(card["annualized_revenue"]))
    top_m4.metric("2x Sales Valuation", fmt_money(card["two_x_sales_val"]))
    top_m5.metric("SEC Stress Tier", card["stress_tier"])

    tab_chat, tab_val, tab_sim, tab_check = st.tabs(
        [
            "1. Live AI Coach, SEC Filings & Video Briefing",
            "2. Balance Sheet, '2x Sales' & Sales Growth",
            "3. Wealth Glide-Path Simulator",
            "4. Self-Check Practice",
        ]
    )

    with tab_chat:
        left_col, right_col = st.columns([1.45, 1.0], gap="large")

        with left_col:
            st.subheader(
                f"Ask the Live AI Coach about {card['company']} ({card['ticker']})"
            )

            with st.container(border=True):
                mode_col1, mode_col2 = st.columns([1.15, 1.35])
                with mode_col1:
                    explanation_mode = st.radio(
                        "How should I explain concepts?",
                        [
                            "Plain English (Simple & Jargon-Free)",
                            "Connect to a Topic I Already Know",
                        ],
                        index=0,
                        key=f"exp_mode_{ticker}",
                    )
                with mode_col2:
                    if explanation_mode == "Connect to a Topic I Already Know":
                        connect_topic = st.text_input(
                            "What topic or field do you want to connect to?",
                            placeholder="e.g., NBA salary cap, music production, gaming...",
                            key=f"topic_box_{ticker}",
                        )
                    else:
                        connect_topic = ""
                        st.caption(
                            "**Plain English Mode active:** No metaphors—just clear, "
                            "straightforward answers grounded in the real SEC filing."
                        )

            if ticker not in st.session_state.chat_histories:
                runway_intro = (
                    f"generates **{fmt_money(card['operating_cash_flow'])} in positive "
                    "operating cash flow"
                    if card["runway_quarters"] is None
                    else f"has roughly  quarters of cash runway"
                )
                st.session_state.chat_histories[ticker] = [
                    {
                        "role": "assistant",
                        "content": (
                            f"I've pulled 's ({card['ticker']}) latest "
                            f"** SEC filing (period `{card['period']}`). "
                            f"In plain English: they hold **{fmt_money(card['cash_on_hand'])}** "
                            f"in cash, pace at **{fmt_money(card['annualized_revenue'])}** in "
                            f"yearly sales, and {runway_intro}.\n\n"
                            "Ask me anything below—like what a term means, whether their "
                            "balance sheet looks healthy, or how this business model compares "
                            "to a field you already know."
                        ),
                    }
                ]

            history = st.session_state.chat_histories[ticker]

            st.caption("Quick prompts to get started:")
            qp1, qp2, qp3, qp4 = st.columns([1.1, 1.1, 1.1, 0.7])
            queued_prompt = None
            if qp1.button("Plain-English health check", use_container_width=True):
                queued_prompt = (
                    f"Give me a plain-English checkup on {card['ticker']}'s balance "
                    "sheet and cash flow."
                )
            if qp2.button("Explain '2x Sales' here", use_container_width=True):
                queued_prompt = (
                    f"In plain English, what does a '2x Sales' valuation look like for "
                    f"{card['ticker']}?"
                )
            if qp3.button("Any dilution or debt risk?", use_container_width=True):
                queued_prompt = (
                    f"Does {card['ticker']} have any share dilution or debt risk based "
                    "on these numbers?"
                )
            if qp4.button("Clear chat", use_container_width=True):
                del st.session_state.chat_histories[ticker]
                st.rerun()

            chat_box = st.container(height=410, border=True)
            with chat_box:
                for msg in history:
                    with st.chat_message(msg["role"]):
                        st.markdown(safe_md(msg["content"]))

            topic_hint = connect_topic.strip() or "plain English"
            typed_prompt = st.chat_input(
                f"Ask anything about {card['ticker']}, SEC terms, or {topic_hint}..."
            )
            active_prompt = queued_prompt or typed_prompt

            if active_prompt:
                history.append({"role": "user", "content": active_prompt})
                with chat_box:
                    with st.chat_message("user"):
                        st.markdown(safe_md(active_prompt))
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking through the SEC numbers..."):
                            reply = generate_chat_reply(
                                card=card,
                                messages=history,
                                user_prompt=active_prompt,
                                connect_topic=connect_topic,
                                api_key=active_gemini_key,
                                model_name=ai_model,
                            )
                            st.markdown(safe_md(reply))
                history.append({"role": "assistant", "content": reply})
                st.rerun()

        with right_col:
            st.subheader("SEC Filing Snapshot & Video")

            tier_desc = {
                "Fortress Liquidity": (
                    "Positive operating cash flow paired with conservative balance-sheet "
                    "leverage gives the business strong internal funding resilience."
                ),
                "Steady Runway": (
                    "Liquid reserves cover at least 8 quarters at current burn rates "
                    "(or operations are cash-flow positive), providing multi-year "
                    "operational breathing room."
                ),
                "Speculative Cash Burn": (
                    "Cash runway sits below 8 quarters at current operating burn, "
                    "signaling an elevated likelihood of future capital raises or dilution."
                ),
            }[card["stress_tier"]]

            st.markdown(
                f"""
                <div class="speculator-box">
                    <div style="font-weight:700; font-size:0.96rem; margin-bottom:0.35rem;">
                        Balance-Sheet Stress Tier: <span style="color:#8b5cf6;">{card['stress_tier']}</span>
                    </div>
                    <p style="margin:0 0 0.4rem 0; font-size:0.89rem; line-height:1.5;">{tier_desc}</p>
                    <p style="margin:0; font-size:0.76rem; opacity:0.75;">
                        <em>Educational Note:</em> Measures corporate liquidity from SEC filings—not stock price direction.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.container(border=True):
                st.markdown(f"#### YouTube Analysis for `{card['ticker']}`")
                yt_videos = fetch_stock_youtube_videos(
                    card["ticker"], card["company"], yt_api_key
                )
                if yt_videos:
                    vid_labels = [
                        f"{v['title']} ({v['channel']})" for v in yt_videos
                    ]
                    chosen_idx = st.selectbox(
                        "Select a stock video:",
                        range(len(yt_videos)),
                        format_func=lambda i: vid_labels[i],
                        key=f"yt_pick_{ticker}",
                    )
                    selected_vid = yt_videos[chosen_idx]
                    st.video(selected_vid["url"])
                    st.caption(
                        f"Source: **{selected_vid['channel']} • "
                        f"[Open on YouTube]({selected_vid['url']})"
                    )
                else:
                    yt_search_link = (
                        "https://www.youtube.com/results?search_query="
                        f"{quote_plus(card['ticker'] + ' ' + card['company'] + ' stock analysis')}"
                    )
                    st.info(
                        f"[Watch the latest {card['ticker']} stock analysis videos on YouTube →]({yt_search_link})"
                    )

            with st.expander(
                f"Latest Mined SEC Filings for {card['ticker']} (10-Q, 10-K, 8-K, Form 4)",
                expanded=True,
            ):
                st.caption(
                    f"Recent Form 4 Insider Filings:  "
                    f"(Latest: **)"
                )
                if card["recent_filings"]:
                    df_filings = pd.DataFrame(card["recent_filings"])
                    st.dataframe(
                        df_filings,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "SEC Link": st.column_config.LinkColumn(
                                "SEC Filing", display_text="Open Filing →"
                            )
                        },
                    )
                else:
                    st.write("No recent filing index rows returned for this ticker.")

            with st.container(border=True):
                st.markdown(f"**Practice trading {card['ticker']} risk-free**")
                st.caption(
                    f"Test your research in your Mock Trading Account ({fmt_money(acct['cash'])} virtual cash available)."
                    if acct["created"]
                    else "Open a free Mock Trading Account to practice trading with virtual cash."
                )

                def open_trade_page():
                    st.session_state.active_page = "Mock Trading Account"

                st.button(
                    "Open Mock Trading Account →",
                    on_click=open_trade_page,
                    use_container_width=True,
                )

    with tab_val:
        h_v1, h_v2 = st.columns([3.2, 1.2])
        with h_v1:
            st.subheader(
                f"{card['company']} ({card['ticker']}) — Balance Sheet, '2x Sales' & Growth"
            )
        with h_v2:
            st.button(
                "Open Textbook Definitions →",
                on_click=go_to_definitions,
                args=("Price-to-Sales Ratio ('2x Sales')",),
                use_container_width=True,
            )

        if "Self-Funding" in card["health_badge"] or "Healthy" in card["health_badge"]:
            st.success(f"Filing Status: {card['health_badge']} • Period: {card['period']}")
        else:
            st.warning(f"Filing Status: {card['health_badge']} • Period: {card['period']}")

        cr_str = (
            f"{card['current_ratio']}x" if card["current_ratio"] is not None else "N/A"
        )
        dte_str = (
            f"{card['debt_to_equity']}x"
            if card["debt_to_equity"] is not None
            else "N/A"
        )

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Cash on Hand", fmt_money(card["cash_on_hand"]))
        m2.metric("Annualized Sales", fmt_money(card["annualized_revenue"]))
        m3.metric("2x Sales Valuation", fmt_money(card["two_x_sales_val"]))
        m4.metric(
            "Period Sales Growth",
            (
                f"{card['sales_growth_pct']:+.1f}%"
                if card["sales_growth_pct"] is not None
                else "N/A"
            ),
        )
        m5.metric("Current Ratio", cr_str)
        m6.metric("Debt-to-Equity", dte_str)

        st.divider()
        c_left, c_right = st.columns(2, gap="large")
        with c_left:
            render_balance_sheet_health_chart(card)
            st.markdown(
                safe_md(
                    "**Plain-English Takeaway (Balance Sheet):** A **Current Ratio** "
                    "above `1.5x` indicates short-term assets comfortably cover short-term "
                    "bills, while **Debt-to-Equity** below `2.0x` keeps debt leverage "
                    f"moderate. {card['company']} reported a Current Ratio of **{cr_str}** "
                    f"and Debt-to-Equity of **{dte_str}**."
                )
            )
        with c_right:
            render_2x_sales_chart(card)
            st.markdown(
                safe_md(
                    "**Plain-English Takeaway ('2x Sales'):** Price-to-Sales compares "
                    f"Market Cap to Annual Revenue. At **{fmt_money(card['annualized_revenue'])}** "
                    f"in annualized revenue, a **2x Sales** multiple implies a "
                    f"**{fmt_money(card['two_x_sales_val'])}** company valuation—whereas "
                    "faster-growing software firms often trade at 6x–10x sales."
                )
            )

        st.divider()
        render_sales_growth_chart(card)

    with tab_sim:
        h_col1, h_col2 = st.columns([3.2, 1.2])
        with h_col1:
            st.subheader("Dynamic Wealth Glide-Path & Escape Velocity Simulator")
        with h_col2:
            st.button(
                "Open Slider Definitions →",
                on_click=go_to_definitions,
                args=("Dynamic Wealth Glide-Path",),
                use_container_width=True,
            )

        st.markdown(
            """
            <div class="guide-box">
                <strong>How this simulator works:</strong> A <strong>Dynamic Glide-Path</strong> models starting with higher-growth investments
                early on (<em>Growth Mode CAGR</em>) and gradually shifting toward steadier returns (<em>Maintenance CAGR</em>) over time.
                The green dotted line marks <strong>Escape Velocity</strong>—the year when monthly investment gains exceed your monthly deposits.
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4, c5 = st.columns(5)
        start_cap = c1.slider("Starting Capital ($)", 500, 50000, 18000, step=500)
        monthly_add = c2.slider("Monthly Deposit ($)", 0, 2000, 100, step=50)
        growth_cagr = c3.slider("Growth Mode CAGR (%)", 8, 50, 28, step=1)
        maint_cagr = c4.slider("Maintenance CAGR (%)", 4, 18, 9, step=1)
        years = c5.slider("Horizon (Years)", 5, 35, 20, step=1)

        months = np.arange(0, years * 12 + 1)
        glide_vals = [float(start_cap)]
        bench_vals = [float(start_cap)]
        escape_year = None

        for m in range(1, len(months)):
            progress = m / (years * 12)
            current_cagr = growth_cagr - 0.5 * (growth_cagr - maint_cagr) * progress
            r_m = (current_cagr / 100.0) / 12.0
            monthly_gain = glide_vals[-1] * r_m
            if escape_year is None and monthly_add > 0 and monthly_gain >= monthly_add:
                escape_year = round(m / 12.0, 1)
            elif escape_year is None and monthly_add == 0:
                escape_year = 0.0
            glide_vals.append(glide_vals[-1] + monthly_gain + monthly_add)
            bench_vals.append(bench_vals[-1] * (1 + 0.08 / 12.0) + monthly_add)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=months / 12.0,
                y=glide_vals,
                mode="lines",
                name="Dynamic Glide-Path Strategy",
                line=dict(color="#0284c7", width=3),
                fill="tozeroy",
                fillcolor="rgba(2, 132, 199, 0.14)",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=months / 12.0,
                y=bench_vals,
                mode="lines",
                name="8% Standard Index Benchmark",
                line=dict(color="#64748b", width=2, dash="dash"),
            )
        )
        if escape_year is not None and escape_year > 0:
            fig.add_vline(
                x=escape_year,
                line_dash="dot",
                line_color="#10b981",
                annotation_text=f"Escape Velocity (Year {escape_year})",
                annotation_position="top left",
            )
        fig.update_layout(
            xaxis_title="Years",
            yaxis_title="Portfolio Value ($)",
            hovermode="x unified",
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        total_contributed = start_cap + monthly_add * 12 * years
        ending_glide = glide_vals[-1]
        ending_bench = bench_vals[-1]
        compounding_multiple = round(ending_glide / max(total_contributed, 1), 1)

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Total Cash Contributed", fmt_money(total_contributed))
        s2.metric("8% Index Benchmark", fmt_money(ending_bench))
        s3.metric(
            "Glide-Path Projected Value",
            fmt_money(ending_glide),
            delta=f"{compounding_multiple}x cash invested",
        )
        s4.metric(
            "Escape Velocity Milestone",
            (
                "Immediate (No Deposits)"
                if escape_year == 0.0
                else (f"Year {escape_year}" if escape_year else "Beyond Horizon")
            ),
        )

    with tab_check:
        st.subheader(
            f"Applied Concept Check — Live Case: {card['company']} ({card['ticker']})"
        )
        st.markdown(
            """
            <div class="guide-box">
                Practice applying plain-English definitions to real SEC numbers with instant explanations—no scores, streaks, or XP.
            </div>
            """,
            unsafe_allow_html=True,
        )

        practice_bank = [
            {
                "id": f"q_sales_{ticker}",
                "title": "1. Understanding '2x Sales' Valuation",
                "prompt": (
                    f"{card['company']} generates **{fmt_money(card['annualized_revenue'])}** "
                    "in annualized revenue. If the market values the company at **2x Sales**, "
                    "what is its implied Market Capitalization?"
                ),
                "options": [
                    f"{fmt_money(card['two_x_sales_val'])} — twice its annualized top-line revenue.",
                    f"{fmt_money(card['cash_on_hand'])} — equal to its Cash on Hand.",
                    "2% of its annual operating expenses.",
                ],
                "correct": (
                    f"{fmt_money(card['two_x_sales_val'])} — twice its annualized top-line revenue."
                ),
                "explain": (
                    "Price-to-Sales (P/S) = Market Cap ÷ Annual Revenue, so a 2x Sales "
                    "multiple equals 2 × Annualized Revenue."
                ),
            },
            {
                "id": f"q_curr_{ticker}",
                "title": "2. Current Ratio & Short-Term Balance Sheet Health",
                "prompt": "In plain English, what does a Current Ratio below 1.0x indicate?",
                "options": [
                    "Short-term liabilities due within 12 months exceed current liquid assets, signaling potential working-capital strain.",
                    "The company has zero debt and infinite cash runway.",
                    "Annual sales growth exceeded 100% last quarter.",
                ],
                "correct": (
                    "Short-term liabilities due within 12 months exceed current liquid assets, signaling potential working-capital strain."
                ),
                "explain": (
                    "Current Ratio = Current Assets ÷ Current Liabilities. Ratios above 1.5x "
                    "indicate a healthy short-term liquidity buffer."
                ),
            },
            {
                "id": f"q_growth_{ticker}",
                "title": "3. Interpreting Top-Line Sales Growth",
                "prompt": (
                    "Why do analysts compare Year-over-Year (YoY) revenue rather than "
                    "just looking at one quarter in isolation?"
                ),
                "options": [
                    "Comparing the same quarter across consecutive years removes seasonal spikes (like holiday shopping) and reveals true growth momentum.",
                    "SEC rules prohibit looking at quarterly revenue.",
                    "YoY growth guarantees positive Free Cash Flow.",
                ],
                "correct": (
                    "Comparing the same quarter across consecutive years removes seasonal spikes (like holiday shopping) and reveals true growth momentum."
                ),
                "explain": (
                    "Seasonality distorts sequential quarter-over-quarter comparisons in retail, "
                    "aerospace, and consumer sectors; YoY measures true underlying expansion."
                ),
            },
        ]

        for q in practice_bank:
            with st.container(border=True):
                st.markdown(f"#### {q['title']}")
                st.write(safe_md(q["prompt"]))
                choice = st.radio(
                    "Choose an interpretation:",
                    [safe_md(opt) for opt in q["options"]],
                    key=f"radio_{q['id']}",
                    label_visibility="collapsed",
                )
                if st.button("Check Interpretation", key=f"btn_{q['id']}"):
                    if choice == safe_md(q["correct"]):
                        st.success(safe_md(f"That's right — {q['explain']}"))
                    else:
                        st.info(safe_md(f"Review — {q['explain']}"))

# ==============================================================================
# 14. FOOTER & AD / PRIVACY DISCLOSURE
# ==============================================================================
st.markdown(
    """
    <div class="wl-footer">
        <span><strong>BornYesterdayInvestEd.com</strong> • Live SEC EDGAR XBRL Miner + Interactive AI Coach</span>
        <span>Educational tool & paper trading sandbox — not personalized investment advice. May display sponsored links or ads.</span>
    </div>
    """,
    unsafe_allow_html=True,
)
