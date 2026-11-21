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

    .wl-onboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 0.85rem;
        margin-top: 0.95rem;
    }
    .wl-onboard-card {
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 12px;
        padding: 0.85rem 1rem;
    }
    .wl-step-pill {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 0.16rem 0.55rem;
        border-radius: 999px;
        margin-bottom: 0.35rem;
    }
    .wl-step-1 { background: rgba(56, 189, 248, 0.2); color: #7dd3fc !important; }
    .wl-step-2 { background: rgba(16, 185, 129, 0.2); color: #6ee7b7 !important; }
    .wl-step-3 { background: rgba(167, 139, 250, 0.22); color: #ddd6fe !important; }
    .wl-onboard-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #f8fafc !important;
        margin-bottom: 0.2rem;
    }
    .wl-onboard-desc {
        font-size: 0.81rem;
        color: #cbd5e1 !important;
        line-height: 1.45;
        margin: 0;
    }

    .wl-start-banner {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(14, 165, 233, 0.32);
        border-left: 5px solid #0284c7;
        border-radius: 14px;
        padding: 0.85rem 1.15rem;
        margin: 0.4rem 0 0.75rem 0;
    }
    .wl-start-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 0.15rem;
    }
    .wl-start-sub {
        font-size: 0.82rem;
        color: var(--text-color);
        opacity: 0.78;
        margin: 0;
    }

    .wl-trust-section {
        margin-top: 2.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(128, 128, 128, 0.22);
    }
    .wl-trust-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-top: 0.75rem;
    }
    .wl-trust-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.22);
