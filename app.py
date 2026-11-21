import json
import os
import re
import time
import urllib.request
from datetime import datetime
from urllib.parse import quote_plus
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from edgar import Company, set_identity

LOGO_PATH = "logo.png" if os.path.exists("logo.png") else None

st.set_page_config(
    page_title="BornYesterdayInvestEd.com — SEC Research, Video Briefings & Paper Trading",
    page_icon=LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 1. THEME-ADAPTIVE FRIENDLY FINTECH DESIGN SYSTEM (LIGHT & DARK MODE READY)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Welcome Banner */
    .wl-hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 58%, #164e63 100%);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 18px;
        padding: 1.5rem 1.85rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.14);
    }
    .wl-hero-badge {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        background: rgba(56, 189, 248, 0.18);
        color: #7dd3fc;
        border: 1px solid rgba(56, 189, 248, 0.35);
        margin-bottom: 0.5rem;
    }
    .wl-hero-title {
        font-size: 1.78rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 0.4rem 0;
        line-height: 1.25;
    }
    .wl-hero-sub {
        font-size: 0.95rem;
        color: #e2e8f0;
        margin: 0;
        max-width: 880px;
        line-height: 1.58;
    }

    /* Ad Slot Container Styling */
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

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 14px;
        padding: 0.9rem 1.1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
    }

    /* Friendly AI Research Team Cards */
    .team-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.24);
        border-radius: 14px;
        padding: 0.95rem 1.1rem;
        margin-bottom: 0.72rem;
    }
    .team-card.active {
        border-color: #10b981;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.12);
    }
    .team-card.speculator {
        border-left: 4px solid #8b5cf6;
    }
    .team-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.32rem;
    }
    .team-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-color);
    }
    .team-role {
        font-size: 0.78rem;
        opacity: 0.75;
        font-weight: 500;
    }
    .status-chip {
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        background: rgba(128, 128, 128, 0.14);
        color: var(--text-color);
    }
    .status-chip.ready {
        background: rgba(16, 185, 129, 0.16);
        color: #059669;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .team-body {
        font-size: 0.87rem;
        color: var(--text-color);
        opacity: 0.9;
        line-height: 1.48;
        margin: 0.28rem 0 0 0;
    }

    /* Friendly Analogy Story Bubble */
    .story-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(2, 132, 199, 0.35);
        border-left: 5px solid #0284c7;
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        margin: 0.6rem 0 1rem 0;
        font-size: 1.01rem;
        line-height: 1.66;
        color: var(--text-color);
        box-shadow: 0 4px 16px rgba(2, 132, 199, 0.08);
    }
    .story-eyebrow {
        font-size: 0.78rem;
        font-weight: 700;
        color: #0284c7;
        margin-bottom: 0.42rem;
        letter-spacing: 0.02em;
    }

    /* Grand Speculator Card */
    .speculator-box {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(139, 92, 246, 0.38);
        border-left: 5px solid #8b5cf6;
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin: 0.6rem 0 1rem 0;
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

    /* Soft Editorial Guide Box */
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

    /* Footer */
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
# 2. SESSION STATE (NAVIGATION, BRIEFINGS & MOCK TRADING ACCOUNT)
# ==============================================================================
if "active_page" not in st.session_state:
    st.session_state.active_page = "Research & Paper Trading Studio"
if "selected_term" not in st.session_state:
    st.session_state.selected_term = "Show All Terms (Textbook Guide)"
if "briefing_ran" not in st.session_state:
    st.session_state.briefing_ran = {}
if "team_question" not in st.session_state:
    st.session_state.team_question = "Give me the big picture: is this company financially healthy?"

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
    """Escapes dollar signs so Streamlit never misreads currency as LaTeX math."""
    return text.replace("$", "\\$")


def searchable_selectbox(label: str, options: list[str], index: int = 0, placeholder: str = "") -> str:
    """Live type-ahead dropdown that filters while typing AND accepts brand-new entries."""
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
    """Fetches the latest market quote without extra dependencies."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker.upper()}?interval=1d&range=5d"
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
def fetch_stock_youtube_videos(ticker: str, company_name: str, yt_api_key: str = "") -> list[dict]:
    """
    Finds up to 3 verified, embeddable YouTube videos for any stock ticker.
    Uses YouTube Data API v3 if a key is provided; otherwise uses YouTube search
    + official youtube.com/oembed verification (zero API key required).
    """
    clean_co = re.sub(r"\b(Inc|Corp|Corporation|Ltd|PLC|Holdings|Group|Co)\b\.?", "", company_name, flags=re.I).strip()
    query = f"{ticker} {clean_co} stock analysis earnings".strip()
    videos = []

    if yt_api_key.strip():
        try:
            api_url = (
                "https://www.googleapis.com/youtube/v3/search"
                f"?part=snippet&type=video&videoEmbeddable=true&maxResults=3"
                f"&q={quote_plus(query)}&key={quote_plus(yt_api_key.strip())}"
            )
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for item in data.get("items", []):
                    vid = item["id"]["videoId"]
                    snip = item["snippet"]
                    videos.append({
                        "video_id": vid,
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "title": snip.get("title", f"{ticker} Stock Analysis"),
                        "channel": snip.get("channelTitle", "YouTube"),
                    })
                if videos:
                    return videos
        except Exception:
            pass

    try:
        search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        req = urllib.request.Request(
            search_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
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
            oembed_url = f"https://www.youtube.com/oembed?url={quote_plus(watch_url)}&format=json"
            try:
                oreq = urllib.request.Request(oembed_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(oreq, timeout=4) as oresp:
                    meta = json.loads(oresp.read().decode("utf-8"))
                    videos.append({
                        "video_id": vid,
                        "url": watch_url,
                        "title": meta.get("title", f"{ticker} Market Analysis"),
                        "channel": meta.get("author_name", "YouTube Creator"),
                    })
                if len(videos) >= 3:
                    break
            except Exception:
                continue
    except Exception:
        pass

    return videos


# ==============================================================================
# 4. AD REVENUE & SPONSOR RENDERER
# ==============================================================================
def render_ad_slot(
    slot_name: str,
    dimensions: str,
    enabled: bool,
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
        ad_html = f"""
        <div style="text-align:center; overflow:hidden;">
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={pub}" crossorigin="anonymous"></script>
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="{pub}"
                 data-ad-slot="{slot}"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
        </div>
        """
        components.html(ad_html, height=height_px)
        return

    if sponsor_title.strip() and sponsor_url.strip():
        st.markdown(
            f"""
            <div class="ad-slot-wrapper">
                <div class="ad-label">Sponsored Partner • {slot_name}</div>
                <div class="ad-copy">
                    <a href="{sponsor_url.strip()}" target="_blank" rel="noopener noreferrer" style="font-weight:600; text-decoration:none;">
                        {sponsor_title.strip()} →
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="ad-slot-wrapper">
                <div class="ad-label">Ad Revenue Slot • {slot_name} ({dimensions})</div>
                <div class="ad-copy">
                    BornYesterdayInvestEd.com monetization slot — paste your <code>ca-pub-...</code> Google AdSense ID or Sponsor Link in the sidebar to serve live ads.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# 5. IN-DEPTH TEXTBOOK FINANCIAL GLOSSARY (DEFINITIONS, FORMULAS & BENCHMARKS)
# ==============================================================================
DEFINITIONS_DB = {
    "Price-to-Sales Ratio ('2x Sales')": {
        "category": "Valuation Multiples",
        "range": "Valuation Metric",
        "textbook": "A valuation multiple that compares a company's total market value (Market Capitalization) to its trailing twelve-month top-line revenue. Saying a stock trades at '2x sales' means investors are paying $2 for every $1 of annual revenue the business generates.",
        "formula": "Price-to-Sales (P/S) = Market Capitalization ÷ Annual Revenue",
        "benchmarks": "Under 1.5x is typical for lower-margin retail or manufacturing; 2x–4x is common for steady industrial/tech businesses; 6x–15x+ is usually reserved for high-margin, rapidly growing software companies.",
        "why_it_matters": "Useful for valuing young or fast-growing companies that reinvest heavily and do not yet report positive net earnings—though high sales multiples carry steep downside if revenue growth slows.",
        "analogy_fn": lambda h: f"In **{h}**, buying a franchise at '2x sales' means paying upfront for two full seasons of ticket and merch revenue before counting player salaries or stadium costs.",
    },
    "Sales Growth (YoY & QoQ Revenue Growth)": {
        "category": "Top-Line Momentum",
        "range": "Growth Metric",
        "textbook": "The percentage rate at which a company's gross top-line revenue increases from one reporting period to the comparable prior period (Year-over-Year compares Q3 this year to Q3 last year to remove seasonal distortion).",
        "formula": "Sales Growth (%) = [(Current Revenue − Prior Revenue) ÷ |Prior Revenue|] × 100",
        "benchmarks": "0%–5% signals mature/GDP-level expansion; 10%–20% reflects healthy compound growth; 25%+ signals hyper-growth—provided gross margins and cash flow scale alongside it.",
        "why_it_matters": "Consistent sales growth proves customer demand is expanding, which is the primary justification for higher valuation multiples like 4x–8x sales.",
        "analogy_fn": lambda h: f"In **{h}**, sales growth is how fast your fan attendance and season-ticket base are expanding from one season to the next.",
    },
    "Current Ratio (Short-Term Liquidity)": {
        "category": "Balance Sheet Health",
        "range": "Liquidity Ratio",
        "textbook": "A balance-sheet liquidity ratio measuring a company's ability to pay off all short-term obligations due within 12 months (Current Liabilities) using assets that can be converted to cash within 12 months (Current Assets).",
        "formula": "Current Ratio = Total Current Assets ÷ Total Current Liabilities",
        "benchmarks": "1.5x–3.0x indicates comfortable short-term liquidity; below 1.0x warns that near-term bills exceed liquid assets; above 4.0x may suggest idle cash not being reinvested efficiently.",
        "why_it_matters": "Acts as an early-warning indicator of working-capital stress before a company misses supplier or debt payments.",
        "analogy_fn": lambda h: f"In **{h}**, a Current Ratio above 1.5x means having more than enough liquid supplies in your pack to cover every upcoming checkpoint bill.",
    },
    "Cash on Hand & Net Liquidity": {
        "category": "Balance Sheet Health",
        "range": "Balance Sheet",
        "textbook": "The most liquid line item on the Consolidated Balance Sheet, representing unrestricted currency, bank deposits, and highly liquid money-market instruments maturing within 90 days.",
        "formula": "Net Cash = Cash & Short-Term Investments − Total Debt",
        "benchmarks": "Companies with positive Net Cash (more cash than total debt) can weather recessions without distress.",
        "why_it_matters": "Cash pays payroll and R&D—companies can report accounting profits while still running out of real cash.",
        "analogy_fn": lambda h: f"In **{h}**, this is the liquid reserve sitting in your tank right now.",
    },
    "Operating Cash Flow (OCF)": {
        "category": "Balance Sheet Health",
        "range": "Cash Flow Statement",
        "textbook": "Net cash generated or consumed by a company's core ongoing business operations, adjusting GAAP Net Income for non-cash charges (such as depreciation and stock-based compensation) and changes in working capital.",
        "formula": "OCF = Net Income + Non-Cash Expenses ± Changes in Working Capital",
        "benchmarks": "Consistently positive OCF confirms the core business model is self-sustaining; persistent negative OCF requires external cash reserves.",
        "why_it_matters": "Harder to manipulate than accounting earnings because it tracks actual bank-account cash inflows and outflows.",
        "analogy_fn": lambda h: f"In **{h}**, OCF measures whether each round adds real points to your reserves or drains stamina.",
    },
    "Free Cash Flow (FCF)": {
        "category": "Balance Sheet Health",
        "range": "Cash Flow Statement",
        "textbook": "The discretionary cash generated by operations after funding all Capital Expenditures (CapEx) required to maintain and expand property, plant, equipment, and infrastructure.",
        "formula": "Free Cash Flow (FCF) = Operating Cash Flow − Capital Expenditures (CapEx)",
        "benchmarks": "An FCF Margin (FCF ÷ Revenue) above 15% signals an elite cash-compounding business.",
        "why_it_matters": "FCF is the true surplus available to retire debt, buy back shares, pay dividends, or fund acquisitions without dilution.",
        "analogy_fn": lambda h: f"In **{h}**, FCF is the pure surplus left after paying operating costs AND upgrading all your gear.",
    },
    "Cash Runway & Share Dilution Risk": {
        "category": "Balance Sheet Health",
        "range": "Liquidity Horizon",
        "textbook": "The estimated number of quarters a cash-burning enterprise can sustain operations at its current quarterly operating cash outflow before depleting cash reserves.",
        "formula": "Cash Runway (Quarters) = Cash on Hand ÷ Quarterly Operating Cash Burn",
        "benchmarks": "8+ quarters (2+ years) provides strategic breathing room; under 8 quarters places a company on 'Dilution Watch' for secondary equity offerings.",
        "why_it_matters": "When runway drops below 4–6 quarters, management frequently issues new shares at a discount, diluting existing shareholders' ownership percentage.",
        "analogy_fn": lambda h: f"In **{h}**, this is the countdown clock before you have to trade away future draft picks or split your prize.",
    },
    "Debt-to-Equity Ratio": {
        "category": "Balance Sheet Health",
        "range": "Solvency & Leverage",
        "textbook": "A solvency ratio comparing a company's total financial liabilities to its total shareholders' equity, quantifying the degree to which operations are funded through debt versus owner capital.",
        "formula": "Debt-to-Equity = Total Liabilities ÷ Total Stockholders' Equity",
        "benchmarks": "Under 1.0x is conservative; 1.0x–2.0x is moderate; above 2.0x signals high financial leverage (common in utilities/banks, riskier in cyclical tech).",
        "why_it_matters": "High leverage amplifies returns in boom times but magnifies bankruptcy or restructuring risk when revenue contracts.",
        "analogy_fn": lambda h: f"In **{h}**, this is the weight of borrowed armor you are carrying while trying to sprint.",
    },
    "Dynamic Wealth Glide-Path": {
        "category": "Portfolio & Simulator",
        "range": "Allocation Strategy",
        "textbook": "A time-varying asset allocation schedule that begins with higher-beta growth exposure during early accumulation years and systematically shifts toward lower-volatility assets as the target horizon approaches.",
        "formula": "Annualized Rate(t) = Growth_CAGR − 0.5 × (Growth_CAGR − Maint_CAGR) × (t ÷ Horizon)",
        "benchmarks": "Balances early wealth velocity with late-stage sequence-of-returns protection.",
        "why_it_matters": "Prevents a severe market drawdown right before your goal date from wiping out decades of compounding.",
        "analogy_fn": lambda h: f"In **{h}**, it is like pushing an aggressive pace in the first half to build a commanding lead, then shifting to smart defense to protect the win.",
    },
    "Escape Velocity (Compounding Crossover)": {
        "category": "Portfolio & Simulator",
        "range": "Compounding Milestone",
        "textbook": "The mathematical inflection point in a recurring-contribution portfolio where periodic investment gains exceed periodic out-of-pocket principal deposits.",
        "formula": "Portfolio Balance × Monthly Return Rate ≥ Monthly Contribution",
        "benchmarks": "Typically reached between Years 7 and 14 depending on savings rate and annualized return.",
        "why_it_matters": "Marks the transition where your invested capital works harder than your paycheck.",
        "analogy_fn": lambda h: f"In **{h}**, this is breaking free of gravity—your momentum sustains itself without needing constant outside fuel.",
    },
}


# ==============================================================================
# 6. EDUCATIONAL CHART BUILDERS
# ==============================================================================
def render_balance_sheet_health_chart(card: dict):
    curr_ratio = card.get("current_ratio")
    dte = card.get("debt_to_equity")
    runway = card.get("runway_quarters")

    labels = ["Current Ratio (Target ≥ 1.5x)", "Debt-to-Equity (Target ≤ 2.0x)", "Cash Runway Qtrs (Target ≥ 8)"]
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

    multiples = ["1x Sales (Value / Retail)", "2x Sales (Industrial / Balanced)", "4x Sales (Growth Tech)", "8x Sales (High-Margin SaaS)"]
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
        title=f"What '2x Sales' Looks Like for {card['ticker']} (Annualized Revenue: {fmt_money(ann_rev)})",
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
        title=f"5-Year Sales Growth Compounding Curve (Starting from {fmt_money(base_rev)} Revenue)",
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
if LOGO_PATH:
    st.sidebar.image(LOGO_PATH, width=92)
st.sidebar.markdown("### BornYesterdayInvestEd.com")
page = st.sidebar.radio(
    "Workspace View",
    [
        "Research & Paper Trading Studio",
        "Definitions & Textbook Guide",
        "Mock Trading Account",
    ],
    key="active_page",
)

st.sidebar.divider()
st.sidebar.markdown("### Paper Portfolio Snapshot")
acct = st.session_state.paper_account
if acct["created"]:
    st.sidebar.caption(f"Account: **{acct['name']}**")
    st.sidebar.metric("Available Virtual Cash", fmt_money(acct["cash"]))
    st.sidebar.caption(f"Open Positions: **{len(acct['holdings'])}** • Trades Logged: **{len(acct['trades'])}**")
else:
    st.sidebar.info("No mock trading account active yet. Open one in **Mock Trading Account** to practice with virtual cash.")

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
    st.sidebar.info(safe_md(f"**{picked_term}**\n\n{info['textbook']}\n\n`{info['formula']}`"))
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
    adsense_pub = st.text_input("Google AdSense Publisher ID", value="", placeholder="ca-pub-xxxxxxxxxxxxxxxx")
    adsense_slot = st.text_input("AdSense Ad Unit Slot ID", value="", placeholder="1234567890")
    sponsor_title = st.text_input("Or Custom Sponsor / Affiliate Text", value="", placeholder="e.g., Try Commission-Free Paper Trading")
    sponsor_url = st.text_input("Custom Sponsor / Affiliate URL", value="", placeholder="https://...")
    st.caption(
        "**Monetization Note:** Once `bornyesterdayinvested.com` is approved in Google AdSense, paste your `ca-pub-...` ID and Slot ID above to serve live ads."
    )

with st.sidebar.expander("AI, YouTube & SEC API Settings", expanded=False):
    gemini_key = st.text_input(
        "Gemini API Key (Optional)",
        value="",
        placeholder="Paste AIza... key for custom AI",
    )
    yt_api_key = st.text_input(
        "YouTube Data API v3 Key (Optional)",
        value="",
        placeholder="Leave blank for automatic keyless search",
    )
    ai_model = st.selectbox(
        "AI Model",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0,
        disabled=not bool(gemini_key.strip()),
    )
    ai_tone = st.selectbox(
        "Coaching Style",
        [
            "Warm & Encouraging Plain-English Coach",
            "ELI5 (Super Simple, Zero Jargon)",
            "Sports Broadcast Storyteller",
            "Strategy & RPG Guide",
            "Thoughtful Risk Analyst",
        ],
    )
    custom_ai_rules = st.text_area(
        "Custom Prompt Notes (Optional)",
        value="",
        placeholder="e.g., Keep explanations under 3 short sentences.",
        height=65,
    )
    sec_email = st.text_input("SEC Contact Email", value="sanatanstein@gmail.com")

set_identity(sec_email)

# Sidebar 300x250 Ad Slot
render_ad_slot("Sidebar Rectangle", "300×250", show_ads, adsense_pub, adsense_slot, sponsor_title, sponsor_url)


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
        name_col = next((c for c in df.columns if c.lower() in ("title", "name", "company", "company_name")), None)
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
        rev_rows = inc_df[inc_df["label"].str.contains("Revenue|Sales", case=False, na=False)]
        if rev_rows.empty:
            return None
        curr_val = pd.to_numeric(rev_rows[date_cols[0]], errors="coerce").dropna()
        prev_val = pd.to_numeric(rev_rows[date_cols[1]], errors="coerce").dropna()
        if not curr_val.empty and not prev_val.empty and float(prev_val.iloc[0]) != 0:
            c_v = float(curr_val.iloc[0])
            p_v = float(prev_val.iloc[0])
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
            recent_filings.append({
                "Form": str(getattr(f, "form", "")),
                "Filed Date": str(getattr(f, "filing_date", "")),
                "Period": str(getattr(f, "report_date", "") or "—"),
                "SEC Link": str(f_url),
            })
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
# 9. FRIENDLY ANALOGY & AI TEAM ENGINE
# ==============================================================================
def get_analogy(
    card: dict,
    interest: str,
    api_key: str,
    model_name: str,
    tone: str,
    extra_instructions: str,
    focus_question: str = "",
) -> tuple[str, list[str]]:
    cash_str = fmt_money(card["cash_on_hand"])
    cf_str = fmt_money(card["operating_cash_flow"])
    fcf_str = fmt_money(card["free_cash_flow"])
    runway = card["runway_quarters"]
    dte = card["debt_to_equity"]
    is_profitable_cf = runway is None

    if api_key.strip():
        try:
            from google import genai
            client = genai.Client(api_key=api_key.strip())
            custom_block = f"\nExtra user preferences: {extra_instructions.strip()}" if extra_instructions.strip() else ""
            q_block = f"\nSpecific question the learner asked: {focus_question}" if focus_question else ""
            prompt = (
                f"You are a friendly, encouraging financial coach helping
