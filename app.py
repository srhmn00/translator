import streamlit as st
import streamlit.components.v1 as components
import anthropic
import openai
import json
import re
import os
import datetime
import urllib.request
import urllib.error

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Awkward Translator",
    page_icon="💌",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts: handwriting display + rounded body ── */
@import url('https://fonts.googleapis.com/css2?family=Gaegu:wght@400;700&family=Quicksand:wght@400;500;600;700&display=swap');

:root {
    --bg-primary:    #FAF4E8;   /* warm cream paper */
    --bg-secondary:  #F4EADA;   /* sidebar */
    --bg-card:       #FFFDF8;   /* note paper */
    --bg-elevated:   #FFFFFF;
    --border:        #ECDCC4;
    --border-hover:  #E0C9A8;
    --accent:        #FF7A6B;   /* soft coral */
    --accent-2:      #FFB4A8;
    --accent-glow:   rgba(255,122,107,0.22);
    --accent-subtle: #FFEDE8;
    --text-primary:  #5B4D40;   /* warm ink */
    --text-secondary:#9A8979;
    --text-tertiary: #C2B19B;
    --success:       #5FAE84;
    --success-subtle:#E9F5EE;
    --warning:       #E69A3C;
    --highlight:     #FFF1B8;   /* highlighter yellow */
    --dot:           rgba(91,77,64,0.07);
    --radius-sm:     10px;
    --radius-md:     16px;
    --radius-lg:     22px;
    --radius-xl:     28px;
}

/* ── Base: cream paper with notebook dots ── */
.stApp {
    background-color: var(--bg-primary) !important;
    background-image: radial-gradient(var(--dot) 1.4px, transparent 1.4px);
    background-size: 22px 22px;
    font-family: 'Quicksand', -apple-system, sans-serif !important;
    color: var(--text-primary);
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarHeader"] { display: none !important; }
.block-container { padding: 1.5rem 1.5rem 4rem !important; max-width: 720px !important; }

* { color: var(--text-primary); }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 2px dashed var(--border-hover) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: var(--bg-elevated) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Quicksand', monospace !important;
    font-size: 13px !important;
}

/* ── Hero ── */
.hero-section { text-align: center; padding: 2rem 0 1.5rem; position: relative; }
.hero-badge {
    display: inline-block; background: var(--accent-subtle);
    border: 1.5px solid var(--accent-2); color: var(--accent);
    font-family: 'Quicksand'; font-size: 12px; font-weight: 700; letter-spacing: 0.02em;
    padding: 5px 16px; border-radius: 100px; margin-bottom: 1rem;
    transform: rotate(-2deg); box-shadow: 2px 2px 0 var(--accent-2);
}
.hero-title {
    font-family: 'Gaegu', cursive; font-size: clamp(2.6rem, 7vw, 3.8rem); font-weight: 700;
    color: var(--text-primary); line-height: 1.05; margin: 0 0 0.5rem;
}
.hero-title span {
    color: var(--accent);
    text-decoration: underline wavy var(--accent-2);
    text-underline-offset: 8px;
}
.hero-subtitle {
    font-size: 1.08rem; color: var(--text-secondary); font-weight: 500; line-height: 1.65;
    margin: 0.6rem 0 0; text-align: center !important;
}
.hero-subtitle strong { color: var(--accent); font-weight: 700; }

/* ── Step cards: note paper ── */
.step-card {
    background: var(--bg-card); border: 2px solid var(--border); border-radius: var(--radius-lg);
    padding: 1.5rem 1.6rem; margin: 1.1rem 0; position: relative;
    box-shadow: 4px 4px 0 rgba(91,77,64,0.06); transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.step-card:hover { transform: translate(-1px,-1px); box-shadow: 6px 6px 0 rgba(91,77,64,0.08); }
.step-label { display: flex; align-items: center; gap: 10px; margin-bottom: 1.1rem; }
.step-number {
    width: 28px; height: 28px; background: var(--accent); color: #fff; border-radius: 50%;
    font-family: 'Gaegu'; font-size: 16px; font-weight: 700;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    box-shadow: 2px 2px 0 var(--accent-2);
}
.step-title {
    font-family: 'Gaegu', cursive; font-size: 20px; font-weight: 700; color: var(--text-primary);
    letter-spacing: 0; text-transform: none;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--bg-elevated) !important; color: var(--text-primary) !important;
    border: 2px solid var(--border) !important; border-radius: 100px !important;
    font-family: 'Quicksand', sans-serif !important; font-size: 13px !important; font-weight: 600 !important;
    padding: 0.5rem 1rem !important; transition: all 0.15s ease !important; width: 100% !important;
    box-shadow: 2px 2px 0 rgba(91,77,64,0.06) !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important; color: var(--accent) !important; background: var(--accent-subtle) !important;
    transform: translate(-1px,-1px) !important; box-shadow: 3px 3px 0 var(--accent-2) !important;
}
.stButton > button:active { transform: translate(0,0) !important; box-shadow: 1px 1px 0 var(--accent-2) !important; }

.intent-selected > .stButton > button {
    background: var(--accent) !important; border-color: var(--accent) !important; color: #fff !important;
    box-shadow: 2px 2px 0 var(--accent-2) !important;
}

.generate-btn > .stButton > button {
    background: var(--accent) !important; border-color: var(--accent) !important; color: #fff !important;
    font-family: 'Gaegu', cursive !important; font-size: 22px !important; font-weight: 700 !important;
    padding: 0.5rem 2rem !important; box-shadow: 3px 3px 0 var(--accent-2) !important;
}
.generate-btn > .stButton > button:hover {
    transform: translate(-2px,-2px) !important; box-shadow: 5px 5px 0 var(--accent-2) !important; color: #fff !important;
    background: var(--accent) !important;
}
.generate-btn > .stButton > button:disabled {
    background: var(--border) !important; border-color: var(--border) !important; color: var(--text-tertiary) !important;
    box-shadow: none !important;
}

/* ── Text area ── */
.stTextArea textarea {
    background: var(--bg-elevated) !important; border: 2px solid var(--border) !important;
    border-radius: var(--radius-md) !important; color: var(--text-primary) !important;
    caret-color: var(--accent) !important;
    font-family: 'Quicksand', sans-serif !important; font-size: 15px !important; line-height: 1.6 !important;
    padding: 1rem !important; resize: none !important; transition: border-color 0.15s ease !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--accent-glow) !important; outline: none !important;
}
.stTextArea textarea::placeholder { color: var(--text-tertiary) !important; }

/* ── Radio chips ── */
.stRadio > div { flex-direction: row !important; gap: 8px !important; flex-wrap: wrap; }
.stRadio > div > label {
    background: var(--bg-elevated) !important; border: 2px solid var(--border) !important;
    border-radius: 100px !important; padding: 6px 16px !important; color: var(--text-secondary) !important;
    font-size: 13px !important; font-weight: 600 !important; cursor: pointer !important; transition: all 0.15s !important;
}
.stRadio > div > label:hover { border-color: var(--accent-2) !important; color: var(--text-primary) !important; }
[data-testid="stWidgetLabel"] {
    color: var(--text-secondary) !important; font-family: 'Gaegu', cursive !important;
    font-size: 16px !important; font-weight: 700 !important; letter-spacing: 0 !important;
    text-transform: none !important; margin-bottom: 6px !important;
}

/* ── Output: cute note ── */
.output-card {
    background: var(--bg-card); border: 2px solid var(--accent-2); border-radius: var(--radius-lg);
    padding: 1.6rem 1.7rem; margin: 1.2rem 0; position: relative;
    box-shadow: 5px 5px 0 var(--accent-glow);
}
.output-card::before {
    content: '✿'; position: absolute; top: -14px; left: 22px; background: var(--bg-primary);
    color: var(--accent); font-size: 20px; padding: 0 6px;
}
.output-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
.output-tag {
    font-family: 'Gaegu', cursive; font-size: 17px; font-weight: 700; color: var(--accent);
    background: var(--accent-subtle); border: 1.5px solid var(--accent-2); padding: 1px 12px; border-radius: 100px;
}
.output-text {
    font-size: 15.5px; line-height: 1.8; color: var(--text-primary); font-weight: 500;
    white-space: pre-wrap; word-break: break-word;
}

/* ── Strategy tip: highlighter sticky ── */
.strategy-box {
    background: var(--highlight); border: 1.5px dashed #E8C95A; border-radius: var(--radius-md);
    padding: 0.9rem 1.1rem; margin-top: 1.2rem; display: flex; gap: 10px; align-items: flex-start;
    transform: rotate(-0.6deg);
}
.strategy-icon { font-size: 18px; flex-shrink: 0; }
.strategy-label {
    font-family: 'Gaegu', cursive; font-size: 14px; font-weight: 700; letter-spacing: 0;
    text-transform: none; color: #9A7B16; margin-bottom: 2px;
}
.strategy-text { font-size: 13px; color: #7A6420; line-height: 1.5; font-weight: 500; }

/* ── Monetization ── */
.monetization-box {
    background: var(--bg-card); border: 2px dashed var(--border-hover); border-radius: var(--radius-lg);
    padding: 1.4rem 1.8rem; margin: 1.8rem 0 1rem; text-align: center;
}
.mono-text { font-size: 14px; color: var(--text-secondary); margin-bottom: 0.9rem; line-height: 1.5; font-weight: 500; }
.mono-text strong { color: var(--text-primary); }
.coffee-btn > .stButton > button, .coffee-btn a {
    background: #FFD64A !important; border: 2px solid #E8B91F !important; color: #6B4E00 !important;
    font-family: 'Gaegu', cursive !important; font-weight: 700 !important; font-size: 18px !important;
    border-radius: 100px !important; padding: 0.4rem 2rem !important; box-shadow: 2px 2px 0 #E8B91F !important;
}
.coffee-btn > .stButton > button:hover, .coffee-btn a:hover {
    transform: translate(-1px,-1px) !important; box-shadow: 3px 3px 0 #E8B91F !important; color: #6B4E00 !important;
}

.custom-divider { border: none; border-top: 2px dashed var(--border-hover); margin: 1.8rem 0; }
.footer { text-align: center; padding: 1.5rem 0; color: var(--text-tertiary); font-size: 12px; font-weight: 500; }

/* ── Misc widgets ── */
.stSelectbox div[data-baseweb="select"] > div {
    background: var(--bg-elevated) !important; border: 2px solid var(--border) !important;
    border-radius: var(--radius-md) !important; color: var(--text-primary) !important;
}
.stSpinner > div { border-top-color: var(--accent) !important; }
.stAlert {
    background: var(--accent-subtle) !important; border: 1.5px solid var(--accent-2) !important;
    border-radius: var(--radius-md) !important; color: var(--text-primary) !important;
}
.stCode, .stCodeBlock, pre {
    background: var(--bg-elevated) !important; border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}
.stCode *, pre * { color: var(--text-primary) !important; }
.char-count { font-size: 12px; color: var(--text-tertiary); text-align: right; margin-top: -6px; margin-bottom: 8px; font-weight: 600; }

.api-status { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; }
.api-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--success); }
.api-dot.offline { background: var(--text-tertiary); }

/* ── Slider ── */
.stSlider [data-baseweb="slider"] [role="slider"] { background: var(--accent) !important; }
.stSlider [data-baseweb="slider"] > div > div { background: var(--accent) !important; }

/* ── Tabs (variants): little chips ── */
[data-baseweb="tab-list"] { gap: 6px !important; background: transparent !important; border-bottom: 2px dashed var(--border) !important; }
[data-baseweb="tab"] {
    background: var(--bg-elevated) !important; border: 2px solid var(--border) !important; border-bottom: none !important;
    border-radius: 14px 14px 0 0 !important; padding: 5px 14px !important;
}
[data-baseweb="tab"] p { font-family: 'Quicksand' !important; font-size: 13px !important; font-weight: 600 !important; color: var(--text-secondary) !important; }
[aria-selected="true"][data-baseweb="tab"] { background: var(--accent-subtle) !important; border-color: var(--accent-2) !important; }
[aria-selected="true"][data-baseweb="tab"] p { color: var(--accent) !important; }

/* ── Primary (selected / generate) buttons — actually filled coral ── */
.stButton button[kind="primary"] {
    background: var(--accent) !important; border: 2px solid var(--accent) !important; color: #fff !important;
    font-family: 'Gaegu', cursive !important; font-size: 18px !important; font-weight: 700 !important;
    box-shadow: 3px 3px 0 var(--accent-2) !important;
}
.stButton button[kind="primary"]:hover {
    transform: translate(-1px,-1px) !important; box-shadow: 4px 4px 0 var(--accent-2) !important;
    color: #fff !important; background: var(--accent) !important;
}

/* ── Slim section labels (replaces tall step cards) ── */
.sec-label {
    font-family: 'Gaegu', cursive; font-size: 20px; font-weight: 700; color: var(--text-primary);
    margin: 1.2rem 0 0.5rem; display: flex; align-items: center; gap: 8px;
}
.sec-label .num {
    display: inline-flex; width: 26px; height: 26px; align-items: center; justify-content: center;
    background: var(--accent); color: #fff; border-radius: 50%; font-size: 15px; flex-shrink: 0;
    box-shadow: 2px 2px 0 var(--accent-2);
}
.sec-label .opt { font-family: 'Quicksand'; font-size: 12px; font-weight: 500; color: var(--text-tertiary); }

/* lighter labels for optional tone/length */
.mini-label { font-family: 'Gaegu', cursive; font-size: 16px; font-weight: 700; color: var(--text-secondary); margin: 1rem 0 0.3rem; }

/* ── Text inputs ── */
.stTextInput input {
    background: var(--bg-elevated) !important; border: 2px solid var(--border) !important;
    border-radius: 14px !important; color: var(--text-primary) !important;
    caret-color: var(--accent) !important;
    font-family: 'Quicksand' !important; font-size: 14px !important; padding: 0.55rem 0.9rem !important;
}
.stTextInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--accent-glow) !important; }
.stTextInput input::placeholder { color: var(--text-tertiary) !important; }

/* ── Mobile ── */
@media (max-width: 640px) {
    .block-container { padding: 1rem 0.75rem 3rem !important; }
    .hero-title { font-size: 2.6rem !important; }
    .step-card { padding: 1.2rem 1rem !important; }
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 8px !important; }
    [data-testid="stHorizontalBlock"] > [data-testid="column"],
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        flex: 1 1 calc(50% - 8px) !important; min-width: calc(50% - 8px) !important; width: calc(50% - 8px) !important;
    }
    .stButton > button { font-size: 12px !important; padding: 0.5rem 0.5rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ─── CONSTANTS ────────────────────────────────────────────────────────────────
INTENTS = {
    "Requesting":  {"emoji": "🙏", "desc": "Ask for something with grace",   "vibes": ["Warm", "Appreciative"],                "color": "#5E9EFF"},
    "Claiming":    {"emoji": "⚡", "desc": "Assert your rights firmly",       "vibes": ["Firm", "Logical"],                     "color": "#FF9F0A"},
    "Declining":   {"emoji": "🚫", "desc": "Say no without burning bridges",  "vibes": ["Neutral", "Direct"],                   "color": "#BF5AF2"},
    "Negotiating": {"emoji": "🤝", "desc": "Find mutual ground",              "vibes": ["Confident", "Collaborative"],          "color": "#30D158"},
    "Apologizing": {"emoji": "💙", "desc": "Heal the situation genuinely",    "vibes": ["Sincere", "Professional", "Humble"],   "color": "#64D2FF"},
    "Breaking up": {"emoji": "💔", "desc": "End it — a partner or a friend",   "label": "Break up / cut off", "vibes": ["Sincere", "Direct", "Warm"], "color": "#FF6482"},
    "Confronting": {"emoji": "🗣️", "desc": "Address conflict or hard feedback","vibes": ["Direct", "Firm", "Logical"],           "color": "#FFD60A"},
    "Comforting":  {"emoji": "🕊️", "desc": "Console someone going through it", "vibes": ["Warm", "Sincere", "Professional"],     "color": "#5AC8FA"},
    "Excusing":    {"emoji": "🫣", "desc": "Explain or excuse yourself",        "vibes": ["Logical", "Sincere", "Confident"],     "color": "#A98BE0"},
}

LENGTHS = {
    "Short":  {"tokens": 110, "desc": "a quick text — 1 to 2 sentences, straight to the point"},
    "Medium": {"tokens": 240, "desc": "a normal message — about 4 to 6 sentences, one short paragraph"},
    "Long":   {"tokens": 420, "desc": "a fuller, heartfelt message — 2 to 3 real paragraphs with specific detail, not padding"},
}

# Optional manner/tone — applied across all 4 variants. (intensity, manner description)
TONES = {
    "✿ auto":      (55, "natural and balanced"),
    "🍃 gentle":   (30, "gentle, soft, and careful with the other person's feelings"),
    "🔥 firm":     (85, "firm, decisive, and assertive — clear and no wavering"),
    "🌫️ hesitant": (40, "a little hesitant and tentative — leaves room, not too direct"),
    "😎 cool":     (50, "casual, breezy, and unbothered — low emotional investment, light and a little detached, like it's no big deal"),
}

VIBE_DEFINITIONS = {
    "Warm":          "friendly, caring, and relationship-preserving — like talking to someone you genuinely like",
    "Appreciative":  "expressing gratitude upfront, making the recipient feel valued before making the ask",
    "Firm":          "clear, resolute, non-negotiable — asserting rights without aggression",
    "Logical":       "fact-based, unemotional, structured — reasoning your way to the conclusion",
    "Neutral":       "polite but unambiguous — no excessive softening, no harsh edges",
    "Direct":        "minimal words, maximum clarity — straight to the point with zero ambiguity",
    "Confident":     "self-assured, outcome-focused, projecting authority without arrogance",
    "Collaborative": "we-focused, solution-oriented, inviting the other party to co-create",
    "Sincere":       "deeply genuine, emotionally honest, vulnerable without being dramatic",
    "Professional":  "measured, formal, maintaining dignity for both parties",
    "Humble":        "acknowledging fault fully, placing the other person's feelings first",
}

# Per-intent strategic approaches → each becomes one distinct variant (English output)
APPROACHES = {
    "Requesting": [
        {"key": "Polite",       "desc": "humble and courteous — asks gently with deference"},
        {"key": "Appreciative", "desc": "gratitude first — makes them feel valued before the ask"},
        {"key": "Confident",    "desc": "direct and matter-of-fact — asks plainly, no over-apologizing"},
        {"key": "Reciprocal",   "desc": "leans on give-and-take — references mutual help or future return"},
    ],
    "Claiming": [
        {"key": "Polite but firm", "desc": "courteous wording, but unambiguous about the problem"},
        {"key": "Factual",         "desc": "evidence- and agreement-based, calm and unemotional"},
        {"key": "Pressing",        "desc": "insistent — names the issue and sets a clear deadline"},
        {"key": "Final notice",    "desc": "polite but signals escalation if unresolved"},
    ],
    "Declining": [
        {"key": "Soft no",          "desc": "gentle and warm — protects the relationship"},
        {"key": "Honest & direct",  "desc": "clear, brief, zero ambiguity"},
        {"key": "Not right now",    "desc": "declines but leaves the door open for later"},
        {"key": "With alternative", "desc": "says no but offers another option or referral"},
    ],
    "Negotiating": [
        {"key": "Collaborative", "desc": "win-win framing — shared benefit before terms"},
        {"key": "Anchored",      "desc": "states your terms first, confidently"},
        {"key": "Flexible",      "desc": "signals real room to move and compromise"},
        {"key": "Bottom line",   "desc": "polite but makes your walk-away point clear"},
    ],
    "Apologizing": [
        {"key": "Full ownership",  "desc": "takes complete responsibility, no deflection"},
        {"key": "Short & sincere", "desc": "brief and heartfelt — no over-explaining"},
        {"key": "With context",    "desc": "explains what happened without making excuses"},
        {"key": "Repair-focused",  "desc": "centers on concretely making it right"},
    ],
    "Breaking up": [
        {"key": "Gentle & vague",  "desc": "kind and soft; does NOT spell out the reasons — just that it isn't right for you anymore"},
        {"key": "Warm & grateful", "desc": "leads with genuine appreciation; very light on the why"},
        {"key": "Kind but clear",  "desc": "clearly ending it; reasons hinted at but softened, not listed"},
        {"key": "Honest & direct", "desc": "names the real reason plainly, while staying respectful"},
    ],
    "Confronting": [
        {"key": "Calm & specific", "desc": "names the behavior, not the person; sticks to facts"},
        {"key": "I-statements",    "desc": "frames it around your feelings and the impact on you"},
        {"key": "Direct callout",  "desc": "clear and firm about what's not okay"},
        {"key": "Curious & open",  "desc": "raises it but invites their side before concluding"},
    ],
    "Comforting": [
        {"key": "Just present",     "desc": "acknowledges the pain without trying to fix it"},
        {"key": "Warm reassurance", "desc": "offers steadiness, hope, and that you're there"},
        {"key": "Practical help",   "desc": "offers one concrete, specific way to help"},
        {"key": "Shared feeling",   "desc": "relates with gentle empathy, keeping focus on them"},
    ],
    "Excusing": [
        {"key": "Simple & honest",  "desc": "a brief, believable reason, lightly owned"},
        {"key": "Smooth cover",     "desc": "a face-saving reason that softens the blame on you"},
        {"key": "Minimize & pivot", "desc": "downplays it and quickly moves the focus forward"},
        {"key": "Reassure",         "desc": "acknowledges it and promises it won't happen again"},
    ],
}

PROVIDERS = {
    "groq":      {"label": "Groq (Llama)",        "kind": "openai", "base": "https://api.groq.com/openai/v1",
                  "free_model": "llama-3.3-70b-versatile",
                  "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]},
    "gemini":    {"label": "Google (Gemini)",     "kind": "openai", "base": "https://generativelanguage.googleapis.com/v1beta/openai/",
                  "free_model": "gemini-2.5-flash-lite",
                  "models": ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"]},
    "openai":    {"label": "OpenAI (GPT)",        "kind": "openai", "base": None,
                  "models": ["gpt-4o-mini", "gpt-4o"]},
    "anthropic": {"label": "Anthropic (Claude)",  "kind": "anthropic", "base": None,
                  "models": ["claude-sonnet-4-6", "claude-opus-4-8", "claude-haiku-4-5-20251001"]},
}

# Per-browser-session daily cap on the shared free engine. Default 30 (generous for
# low traffic, still limits abuse of the shared key). Override via Secrets/env: FREE_DAILY_CAP.
try:
    FREE_DAILY_CAP = int(st.secrets["FREE_DAILY_CAP"])
except Exception:
    FREE_DAILY_CAP = int(os.environ.get("FREE_DAILY_CAP", "30"))

OUTPUT_LANGUAGES = {
    "English": "English",
    "Same as I wrote": "__SAME__",
    "한국어": "Korean",
    "日本語": "Japanese",
    "中文": "Chinese (Simplified)",
    "Español": "Spanish",
    "Français": "French",
    "Deutsch": "German",
    "Português": "Portuguese",
    "Tiếng Việt": "Vietnamese",
}


def output_language_rule(choice):
    target = OUTPUT_LANGUAGES.get(choice, "English")
    if target == "__SAME__":
        return ("OUTPUT LANGUAGE — detect the language the user wrote their situation in, and write "
                "EVERY message in that SAME language (natural, native-level). Do not switch to English.")
    return f"OUTPUT LANGUAGE — write EVERY message in natural, native-level {target}."


SYSTEM_PROMPT_TEMPLATE = """You are an elite communication strategist and executive ghostwriter.
Transform the user's difficult real-life situation into polished, native-sounding messages.

CONTEXT
- Intent: {intent}
- Base vibe/tone: {vibe} ({vibe_definition})
- Recipient relationship (use this to calibrate formality, warmth, and directness — this is context, not something to quote): {relationship}
- Target length: {length} — {length_desc}
- Overall strength: {intensity}/100 (0 = very gentle, 100 = very strong / insistent)
- Desired manner: {manner}
- The user's raw brain-dump (this is the input — it may be written in any language). It mixes the facts, how they feel, the real reason, and how they want it to end — possibly including things they'd rather NOT say outright: {situation}

TASK
Write ONE message for EACH of the following approaches. Same intent and same length for all, but each must use a GENUINELY different strategy and register — they should read noticeably differently, not like paraphrases of one another:
{approach_block}

{output_language_rule}

Every message must be fluent and natural in that output language, reflect the desired manner ({manner}) and the overall strength of {intensity}/100. Calibrate tone to the recipient relationship. HIT THE TARGET LENGTH ({length}: {length_desc}) — but length means MORE CONCRETE SUBSTANCE, never more padding. The four can VARY in length and shape so they feel like real alternatives at a glance (e.g. one short and punchy, one fuller and warmer) — just don't let any feel cut off or unfinished mid-thought. Across the four variants, genuinely RANGE in directness: at least one names things plainly, and at least one stays gentle and high-level — getting the message across while softening or omitting the harsh specifics rather than itemizing them (graceful and face-saving). The reader picks how much to reveal just by switching tabs, so make that range real and obvious. ALWAYS return all four variants — one per approach, never fewer.

OUTPUT — return ONLY valid JSON (no markdown fences, no preamble, no trailing text):
{{
  "variants": [
    {{"label": "<approach name exactly as given>", "message": "<the message>", "strategy_tip": "<one sentence starting with 'It uses' that names a real psychological/communication principle, e.g. Face-saving, Reciprocity norm, Loss aversion, Empathy-first, Assumptive close, Documented assertiveness>"}}
    // one object per approach, in the same order as listed above
  ]
}}

STYLE — imitate the VOICE of these (examples span different situations on purpose, so copy the style, not the content; they're shown in English only to demonstrate the voice — apply the SAME plain, specific voice in the required output language). Models obey examples better than rules:
✗ WEAK — preamble + vague abstraction (never write like this):
   "I've been doing a lot of thinking, and I need to be honest with you about something that's been weighing on me."
✓ STRONG — opens on something real and concrete, plain words, no warm-up:
   (a favor) "I'm in a real bind with rent this month and I hate even asking — any chance you could give me till the 10th?"
   (an apology) "I completely blanked on your birthday and I feel terrible — no excuse, I just dropped the ball."
   (saying no) "I want to help, but I'm stretched way too thin right now and I'd end up doing a bad job of it."
   (ending things) "Lately I leave our time together more drained than happy, and I don't think I can keep doing that."
The difference: no throat-clearing intro, plain everyday words (not "emotional resonance"), and a specific concrete thing — so it could only have been written for THIS exact situation.

Lean toward plain, concrete words over therapy-speak — say what actually happens ("I feel far from you") instead of vague phrases ("emotional distance"). These are just examples, not a checklist — the point is simply plain + specific. Write the way a person actually texts: short sentences, simple everyday words, nothing corporate or self-help-flavored. Plain and a little imperfect beats polished and hollow.

The four variants should each enter through a DIFFERENT door, e.g.: one opens on the hard truth, one on genuine appreciation, one on the plain decision itself, one on what each of you needs next. They must NOT all open by announcing that they're about to say something hard.

RULES
1. The brain-dump is messy — read between the lines. Infer the unspoken feelings and the real goal, and handle anything harsh or unflattering with tact (don't bluntly repeat it). This tool exists to help people say hard things *nicely*, so lean toward graceful, face-saving phrasing.
2. GROUND IT IN THEIR SPECIFICS. Each message MUST reference at least one concrete thing the user actually described (in their framing, softened). A message that could be copy-pasted to any random person has FAILED. No vague filler like "we want different things" or "we're not compatible" unless tied to a specific.
3. NO PREAMBLE, NO THERAPY-SPEAK. Don't open with throat-clearing like "I've been doing a lot of thinking", "I need to be honest with you", "After a lot of thought and careful consideration", "This isn't an easy decision", "This is really hard to say, but", "I've come to the difficult decision/realization/conclusion". Open with something real. And say things in plain, concrete words — avoid hollow abstractions like "emotional resonance", "deeper emotional needs", "consistent connection and support". Every sentence must earn its place.
4. THE 4 VARIANTS ARE 4 GENUINELY DIFFERENT DECISIONS a real person could choose between — not one message reworded. They must differ in (a) what they lead with, (b) their emotional stance, and (c) their structure, so the writer instantly feels these are real alternatives. No two may open the same way or share stock closings.
5. Familiar phrases are fine in small doses; the failure is a message built ENTIRELY of generic filler. Even a short, clean message should still feel like it's about THIS person.
6. Sound like a real, specific human texting — contractions, plain everyday words, a natural voice. Not a greeting card, not an advice column, not an HR email, not an AI. Never mention you are an AI; write as if you are the user.
7. Never invent specifics the user didn't give, and never output bracketed placeholders like [name] or [date].
8. This is a message, NOT a formal letter. No "Dear ..." salutations, no formal sign-offs, do not address the recipient by name. Start naturally ("Hi," / "Hey," is fine for casual relationships; very short texts can skip a greeting).
9. Write everything in the required output language stated above. Return valid JSON only.
"""


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def _conf(key, default=None):
    """Read config from Streamlit secrets OR environment variables (for Railway/Docker/etc.)."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)


def get_free_secret():
    """Return (api_key, provider_name) for the shared free engine, or (None, None)."""
    try:
        prov = str(_conf("FREE_PROVIDER", "") or "").lower()
        groq, gem = _conf("GROQ_API_KEY"), _conf("GEMINI_API_KEY")
        if prov == "groq" and groq:
            return groq, "groq"
        if prov == "gemini" and gem:
            return gem, "gemini"
        if groq:
            return groq, "groq"
        if gem:
            return gem, "gemini"
    except Exception:
        pass
    return None, None


def _coerce_variants(s: str):
    """Last-resort recovery: pull label/message/strategy_tip out of messy or invalid JSON.
    Splits on each "label" key, so missing commas / bad escaping / truncation don't break it."""
    def field(chunk, key):
        m = re.search(r'"' + key + r'"\s*:\s*"((?:[^"\\]|\\.)*)"', chunk, re.DOTALL)
        if not m:
            return ""
        body = m.group(1)
        body = (body.replace('\\\\', '\x00').replace('\\"', '"')
                    .replace('\\n', '\n').replace('\\t', '\t').replace('\x00', '\\'))
        return body.strip()
    starts = [m.start() for m in re.finditer(r'"label"\s*:', s)]
    if not starts:
        return []
    starts.append(len(s))
    out = []
    for i in range(len(starts) - 1):
        chunk = s[starts[i]:starts[i + 1]]
        msg = field(chunk, "message")
        if not msg:
            continue
        out.append({"label": field(chunk, "label") or f"Option {i + 1}",
                    "message": msg, "strategy_tip": field(chunk, "strategy_tip")})
    return out


def extract_json(raw: str) -> dict:
    """Parse model output into a dict, tolerating fences, prefixes, truncation, and malformed JSON."""
    s = (raw or "").strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s).strip()
    start, end = s.find("{"), s.rfind("}")
    inner = s[start:end + 1] if (start != -1 and end != -1 and end > start) else s
    try:
        return json.loads(inner)
    except Exception:
        pass
    try:  # optional helper if the user happens to have it installed
        import json_repair
        return json_repair.loads(inner)
    except Exception:
        pass
    vs = _coerce_variants(s)
    if vs:
        return {"variants": vs}
    raise ValueError("Could not parse the model's response.")


def _clean_key(k: str) -> str:
    """Strip whitespace and any stray non-ASCII chars that break HTTP headers."""
    return "".join(c for c in (k or "").strip() if 32 <= ord(c) < 127)


def call_openai_compatible(base_url, api_key, model, system_prompt, user_message, max_tokens) -> dict:
    api_key = _clean_key(api_key)
    client = openai.OpenAI(api_key=api_key, base_url=base_url) if base_url else openai.OpenAI(api_key=api_key)
    kwargs = dict(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_message}],
    )
    try:
        resp = client.chat.completions.create(response_format={"type": "json_object"}, **kwargs)
    except Exception:
        # Some free models reject response_format — retry without it
        resp = client.chat.completions.create(**kwargs)
    return extract_json(resp.choices[0].message.content)


def call_anthropic(api_key, model, system_prompt, user_message, max_tokens) -> dict:
    client = anthropic.Anthropic(api_key=_clean_key(api_key))
    resp = client.messages.create(
        model=model, max_tokens=max_tokens, system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    # Newer models may emit a 'thinking' block first — collect only the text blocks
    raw = "".join(getattr(b, "text", "") for b in resp.content if getattr(b, "type", None) == "text")
    if not raw and resp.content:
        raw = getattr(resp.content[0], "text", "") or ""
    return extract_json(raw)


def normalize_result(result: dict):
    """Return (detected_language, [variant, ...]) regardless of single/multi shape."""
    if isinstance(result.get("variants"), list) and result["variants"]:
        variants = []
        for v in result["variants"][:4]:
            variants.append({
                "label": v.get("label", "Balanced"),
                "message": v.get("message", "").strip(),
                "strategy_tip": v.get("strategy_tip", "").strip(),
            })
    else:
        variants = [{
            "label": "Balanced",
            "message": result.get("message", "").strip(),
            "strategy_tip": result.get("strategy_tip", "").strip(),
        }]
    return result.get("detected_language", ""), variants


def get_demo_variants(intent, situation):
    """Sample output when no engine is connected — one entry per approach."""
    s = situation
    demo = {
        "Requesting": {
            "Polite":       (f"Hi, I hope you're well. I'm so sorry to trouble you, but would you possibly be able to help me with {s}? I'd really appreciate it.",
                             "It uses deference and a soft preface to lower the social cost of saying yes."),
            "Appreciative": (f"Thank you for everything you've done so far — it genuinely means a lot. With that in mind, could I ask for your help with {s}?",
                             "It uses the Reciprocity norm by leading with gratitude before the ask."),
            "Confident":    (f"I wanted to reach out about {s}. Could you help me get this sorted? Happy to share whatever details you need.",
                             "It uses an Assumptive close — framing help as the natural next step."),
            "Reciprocal":   (f"You helped me out before and it made a real difference. I'm in a similar spot now with {s} — could I lean on you again? I'll gladly return the favor.",
                             "It uses Reciprocity by surfacing past and future mutual support."),
        },
        "Claiming": {
            "Polite but firm": (f"I'd like to resolve {s}. I've valued working with you, and I'm confident we can sort this out — could you let me know how you'll address it?",
                                "It uses Face-saving to press the issue while preserving goodwill."),
            "Factual":         (f"Per our agreement, {s} should have been handled differently. I've outlined the facts below and would appreciate a resolution based on them.",
                                "It uses Documented assertiveness to make the claim hard to dismiss."),
            "Pressing":        (f"This is the issue regarding {s}, and it needs to be resolved. Please confirm your plan to fix it within 48 hours.",
                                "It uses Loss aversion via a firm deadline to compel action."),
            "Final notice":    (f"I've raised {s} before without resolution. I'd prefer to settle this directly, but I'll need to escalate if I don't hear back by Friday.",
                                "It uses a credible-consequence frame to motivate a timely reply."),
        },
        "Declining": {
            "Soft no":          (f"Thank you so much for thinking of me. After some thought, I'm not able to take on {s} right now — I really appreciate you asking.",
                                 "It uses the Soft-No structure (acknowledge → decline → close) to protect the relationship."),
            "Honest & direct":  (f"I appreciate the offer, but I'll have to pass on {s}. Wanted to let you know clearly rather than leave you waiting.",
                                 "It uses clarity-as-respect to decline without ambiguity."),
            "Not right now":    (f"I can't commit to {s} at the moment, but the timing may be better later — feel free to check back with me down the line.",
                                 "It uses a future-pacing frame to soften the no while keeping the door open."),
            "With alternative": (f"I'm not able to take on {s} myself, but I'd be glad to point you to someone who can, or help in a smaller way if that's useful.",
                                 "It uses an alternative-offer to keep the exchange constructive."),
        },
        "Negotiating": {
            "Collaborative": (f"I think there's a solution on {s} that works well for both of us. Could we find a middle ground that meets your core needs and mine?",
                              "It uses Collaborative framing — shared benefit before terms."),
            "Anchored":      (f"Here's what I'd propose for {s}: [your terms]. I think it's fair, and I'm open to discussing the details from there.",
                              "It uses Anchoring by stating your position first to shape the range."),
            "Flexible":      (f"On {s}, I have some flexibility and I'd like to understand what matters most to you so we can shape something that fits.",
                              "It uses an interest-based approach to expand the room for agreement."),
            "Bottom line":   (f"I'd genuinely like to make {s} work, but I do have a limit I can't go past. If we can stay within that, I'm in.",
                              "It uses a clear walk-away point to signal seriousness without hostility."),
        },
        "Apologizing": {
            "Full ownership":  (f"I'm sorry for {s}. That was on me — no excuses. I understand the impact it had, and I take full responsibility.",
                                "It uses Full-ownership, separating intent from impact, to rebuild trust."),
            "Short & sincere": (f"I owe you a real apology for {s}. I'm sorry.",
                                "It uses brevity to signal sincerity without performance."),
            "With context":    (f"I'm sorry for {s}. To be clear, this isn't an excuse — here's what happened so you have the full picture, and I'll make sure it doesn't repeat.",
                                "It uses context-without-excuse to show accountability and transparency."),
            "Repair-focused":  (f"I'm sorry for {s}. More importantly, here's how I'll make it right: [concrete step]. Tell me if there's anything else you need.",
                                "It uses a repair-first frame to move from apology to resolution."),
        },
        "Breaking up": {
            "Gentle & vague":  ("Hey — I've realized this just isn't right for me anymore, and I don't think we should keep going. It's nothing dramatic, I just know it. I'm sorry, and I really do wish you well.",
                                "It uses a face-saving frame that ends things without listing any grievances."),
            "Warm & grateful": ("I'm genuinely glad I got to know you and I don't regret a second of it. But I've realized I can't give this what it needs, so I think we should stop here. Thank you, truly.",
                                "It uses appreciation-first framing so the ending feels respectful, not cold."),
            "Kind but clear":  ("I care about you, so I'll be straight: this hasn't been working for me for a while, and I think we should end it. I'd rather be honest than let it drag on.",
                                "It uses kind-but-unambiguous wording so there's no false hope."),
            "Honest & direct": ("I've felt pretty alone and unsupported in this for a while, and it's worn me down. I don't think we want the same things, and I've decided I need to end it.",
                                "It uses plain honesty about the real reason to make the decision clear."),
        },
        "Confronting": {
            "Calm & specific": (f"I want to talk about {s}. When that happened it landed badly for me, and I'd like us to sort it out.",
                                "It uses behavior-not-person framing to reduce defensiveness."),
            "I-statements":    (f"I felt hurt by {s}. I'm not trying to attack you — I just need you to know how it affected me.",
                                "It uses I-statements to express impact without triggering blame."),
            "Direct callout":  (f"We need to be straight about {s}. It's not okay with me, and I need it to change.",
                                "It uses direct clarity to set an unmistakable expectation."),
            "Curious & open":  (f"Can we talk about {s}? I might be missing context, so I'd like to hear your side — but it's been on my mind.",
                                "It uses curiosity-first to open dialogue instead of a standoff."),
        },
        "Comforting": {
            "Just present":     (f"I heard about {s}, and I'm so sorry. I don't have the perfect words — I just want you to know I'm here.",
                                 "It uses presence-over-advice, which comforts more than trying to fix things."),
            "Warm reassurance": (f"I'm thinking of you through {s}. You don't have to carry this alone, and you don't have to be okay right now.",
                                 "It uses validation to relieve the pressure to 'be fine'."),
            "Practical help":   (f"I'm so sorry about {s}. Can I drop off dinner this week or take something off your plate? Just tell me what helps.",
                                 "It uses a concrete, low-burden offer that's easy to accept."),
            "Shared feeling":   (f"What you're going through with {s} sounds really hard. I won't pretend to know exactly how you feel, but I'm right here with you.",
                                 "It uses careful empathy that connects while keeping the focus on them."),
        },
        "Excusing": {
            "Simple & honest":  (f"Sorry about {s} — something came up and I couldn't get to it in time. Totally my bad.",
                                 "It uses a brief, owned reason that's hard to argue with."),
            "Smooth cover":     (f"Really sorry about {s} — things got chaotic on my end and it slipped through. Sorting it now.",
                                 "It uses a face-saving frame that softens fault without over-explaining."),
            "Minimize & pivot": (f"Ah, {s} — minor hiccup, nothing serious. Already on it, so we're good to keep moving.",
                                 "It uses minimization to shrink the issue and redirect forward."),
            "Reassure":         (f"Sorry about {s}. I get why that's frustrating — it won't happen again, you have my word.",
                                 "It uses a clear commitment to rebuild trust and close the loop."),
        },
    }
    items = demo.get(intent, demo["Requesting"])
    return "", [{"label": k, "message": m, "strategy_tip": t} for k, (m, t) in items.items()]


# ─── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in {
    "selected_intent": None,
    "variants": None,            # list of {label, message, strategy_tip}
    "detected_language": "",
    "result_meta": "",
    "history": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# daily free-usage counter (per session, resets at date change)
_today = datetime.date.today().isoformat()
if st.session_state.get("free_usage_date") != _today:
    st.session_state.free_usage_date = _today
    st.session_state.free_usage_count = 0

FREE_KEY, FREE_PROVIDER = get_free_secret()


# (Engine settings moved into a small collapsed expander on the main page — see below)



# ─── MAIN ──────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='hero-section'>"
    "<div class='hero-badge'>✿ for the message you keep rewriting</div>"
    "<h1 class='hero-title'>The <span>Awkward</span> Translator</h1>"
    "<p class='hero-subtitle'>Awkward, hard, or just stuck on how to say it?<br>"
    "<strong>Tell me the gist — I'll give you 4 ways to say it. You just pick.</strong> ♡</p>"
    "</div>",
    unsafe_allow_html=True,
)

# ── Engine: use the shared free engine silently; only show a key field when needed ──
call_spec = None
source_label = "DEMO"
free_remaining = max(0, FREE_DAILY_CAP - st.session_state.free_usage_count) if FREE_KEY else 0

if FREE_KEY and free_remaining > 0:
    prov = PROVIDERS[FREE_PROVIDER]
    call_spec = {"kind": prov["kind"], "base": prov["base"], "key": FREE_KEY,
                 "model": prov["free_model"], "source": "free"}
    source_label = prov["free_model"].split("-")[0].upper()

# Most users never see this. It appears only when there's no shared free engine
# (operator set no key) OR the user has used up today's free generations.
show_key_ui = (not FREE_KEY) or (free_remaining <= 0)
if show_key_ui:
    exp_title = ("⚙️ Out of free uses for today · add your own key to keep going"
                 if FREE_KEY else "⚙️ Settings · add your own API key")
    with st.expander(exp_title, expanded=bool(FREE_KEY)):
        c1, c2 = st.columns(2)
        with c1:
            prov_label = st.selectbox("Provider",
                                      [PROVIDERS[p]["label"] for p in ["anthropic", "openai", "gemini", "groq"]])
        prov_key = next(p for p in PROVIDERS if PROVIDERS[p]["label"] == prov_label)
        prov = PROVIDERS[prov_key]
        with c2:
            model_choice = st.selectbox("Model", prov["models"], index=0)
        placeholder = {"anthropic": "sk-ant-api03-...", "openai": "sk-proj-...",
                       "gemini": "AIza...", "groq": "gsk_..."}[prov_key]
        api_key = st.text_input(f"{prov['label']} API key", type="password", placeholder=placeholder)
        st.caption("Free keys: Gemini → aistudio.google.com/apikey · Groq → console.groq.com/keys. Your key is never saved.")
        if api_key:
            call_spec = {"kind": prov["kind"], "base": prov["base"], "key": api_key,
                         "model": model_choice, "source": "byok"}
            source_label = model_choice.split("-")[0].upper()


# ── 1. Situation type ──
st.markdown("<div class='sec-label'><span class='num'>1</span>what kind of situation?</div>", unsafe_allow_html=True)
intent_items = list(INTENTS.items())
PER_ROW = 3
selected_intent = st.session_state.selected_intent
for r in range(0, len(intent_items), PER_ROW):
    row = intent_items[r:r + PER_ROW]
    cols = st.columns(PER_ROW)
    for c, (intent_name, meta) in enumerate(row):
        with cols[c]:
            is_sel = (selected_intent == intent_name)
            if st.button(f"{meta['emoji']} {meta.get('label', intent_name)}", key=f"intent_{intent_name}",
                         type=("primary" if is_sel else "secondary"), use_container_width=True):
                st.session_state.selected_intent = intent_name
                st.session_state.variants = None
                st.rerun()
selected_intent = st.session_state.selected_intent

# ── 2. Recipient relationship (context only) ──
st.markdown("<div class='sec-label'><span class='num'>2</span>who's it for? <span class='opt'>· just for context</span></div>",
            unsafe_allow_html=True)
rcp_rel = st.text_input("relationship", label_visibility="collapsed", key="rel_input",
                        placeholder="relationship — e.g. my boss, my partner, the landlord, a close friend")

# ── 3. The whole situation — just vent ──
st.markdown("<div class='sec-label'><span class='num'>3</span>what's going on? <span class='opt'>· just vent — the facts, how you feel, how you'd like it to end. messy is fine</span></div>",
            unsafe_allow_html=True)
st.markdown(
    "<div style='font-size:13px;color:var(--accent);font-weight:700;margin:-2px 0 8px;'>"
    "✍️ write in ANY language — 한국어 · 日本語 · Español · Français · 中文… then pick which language you want the result in below (English by default).</div>",
    unsafe_allow_html=True,
)
situation = st.text_area("situation", label_visibility="collapsed", key="situation_input",
                         placeholder=("dump it all here, in any language — e.g.\n"
                                      "my friend borrowed money months ago and still hasn't paid me back. "
                                      "i want to ask for it without making things weird between us."),
                         height=120, max_chars=600)

# ── tone + length (compact, optional) ──
st.markdown("<div class='mini-label'>how should it feel? <span class='opt'>· optional</span></div>",
            unsafe_allow_html=True)
tone = st.radio("Tone", list(TONES.keys()), horizontal=True, key="tone_radio", label_visibility="collapsed")

st.markdown("<div class='mini-label'>how long?</div>", unsafe_allow_html=True)
length = st.radio("Length", list(LENGTHS.keys()), horizontal=True, key="length_radio", label_visibility="collapsed")

st.markdown("<div class='mini-label'>reply in which language?</div>", unsafe_allow_html=True)
out_lang_choice = st.selectbox("Output language", list(OUTPUT_LANGUAGES.keys()),
                               index=0, key="outlang_select", label_visibility="collapsed")

# base vibe per intent; intensity & manner come from the chosen tone
vibe = INTENTS[selected_intent]["vibes"][0] if selected_intent else "Warm"
intensity, manner = TONES[tone]

# ── Generate ──
can_generate = bool(selected_intent and situation and situation.strip())
st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
gc1, gc2, gc3 = st.columns([1, 2, 1])
with gc2:
    generate_clicked = st.button("✿ write it for me", disabled=not can_generate,
                                 use_container_width=True, type="primary", key="generate_btn")

# engine / readiness indicator
if call_spec is None:
    note = ("you're out of free uses for today — add your own key above to keep going ♡"
            if FREE_KEY else "demo mode · sample output — add a key above for a real answer ♡")
    st.markdown(f"<div style='text-align:center;font-size:12px;color:var(--warning);margin-top:6px;'>{note}</div>",
                unsafe_allow_html=True)
elif call_spec["source"] == "free":
    st.markdown(f"<div style='text-align:center;font-size:12px;color:var(--success);margin-top:6px;'>"
                f"✦ free — {free_remaining} {'use' if free_remaining == 1 else 'uses'} left today</div>",
                unsafe_allow_html=True)
else:
    st.markdown("<div style='text-align:center;font-size:12px;color:var(--success);margin-top:6px;'>"
                "✓ ready</div>", unsafe_allow_html=True)

if not can_generate:
    hint = "pick a situation above ↑" if not selected_intent else "tell me what's going on ↑"
    st.markdown(f"<div style='text-align:center;font-size:12px;color:var(--text-tertiary);margin-top:4px;'>{hint}</div>",
                unsafe_allow_html=True)

# ── GENERATION LOGIC ──
if generate_clicked and can_generate:
    if True:
        approaches = APPROACHES.get(selected_intent, APPROACHES["Requesting"])
        approach_block = "\n".join(f'- "{a["key"]}": {a["desc"]}' for a in approaches)
        rel_val = rcp_rel.strip() if rcp_rel and rcp_rel.strip() else "(not specified)"
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            intent=selected_intent, vibe=vibe, vibe_definition=VIBE_DEFINITIONS.get(vibe, vibe.lower()),
            length=length, length_desc=LENGTHS[length]["desc"], intensity=intensity, manner=manner,
            situation=situation.strip(), approach_block=approach_block,
            relationship=rel_val, output_language_rule=output_language_rule(out_lang_choice),
        )
        user_message = (f"Intent: {selected_intent}. Recipient relationship: {rel_val}. "
                        f"Length: {length}. Manner: {manner}. "
                        f"Here's the whole situation (a raw brain-dump): {situation.strip()}")
        # Generous cap: Gemini 2.5 spends output tokens on "thinking", so leave plenty
        # of room for thinking + 4 full variants, or the JSON gets truncated.
        max_tokens = LENGTHS[length]["tokens"] * 8 + 3000

        with st.spinner("Crafting your messages..."):
            try:
                if call_spec is None:
                    import time
                    time.sleep(1.0)
                    detected, variants = get_demo_variants(selected_intent, situation.strip())
                elif call_spec["kind"] == "anthropic":
                    result = call_anthropic(call_spec["key"], call_spec["model"], system_prompt, user_message, max_tokens)
                    detected, variants = normalize_result(result)
                else:
                    result = call_openai_compatible(call_spec["base"], call_spec["key"], call_spec["model"],
                                                    system_prompt, user_message, max_tokens)
                    detected, variants = normalize_result(result)

                if call_spec and call_spec["source"] == "free":
                    st.session_state.free_usage_count += 1

                st.session_state.variants = variants
                st.session_state.detected_language = detected
                st.session_state.result_meta = f"{selected_intent} · {length.split()[0]}"

            except Exception as e:
                msg = str(e)
                low = msg.lower()
                if "ascii" in low or "codec" in low or "encode" in low or "401" in msg or "authentication" in low or "invalid_api_key" in low:
                    st.warning("That API key looks off — it may have a hidden character or be incorrect. "
                               "Re-copy it cleanly (no spaces) and paste it again.")
                elif "429" in msg or "rate" in low or "quota" in low or "resource" in low:
                    st.warning("The engine is busy right now (rate limit). Try again in a minute, "
                               "or add your own API key to keep going.")
                else:
                    st.error(f"⚠️ Generation failed: {msg}")
                    st.info("Showing demo output instead.")
                detected, variants = get_demo_variants(selected_intent, situation.strip())
                st.session_state.variants = variants
                st.session_state.detected_language = detected
                st.session_state.result_meta = f"{selected_intent} · {length.split()[0]}"


def copy_button(text, idx):
    """One-click copy button shown right on the message (clipboard API + execCommand fallback)."""
    payload = json.dumps(text)
    html = """
<style>
  .cpbtn{font-family:'Quicksand',-apple-system,sans-serif;background:#FF7A6B;color:#fff;border:none;
    border-radius:100px;padding:7px 18px;font-size:13px;font-weight:700;cursor:pointer;box-shadow:2px 2px 0 #FFB4A8;}
  .cpbtn:active{transform:translate(1px,1px);box-shadow:1px 1px 0 #FFB4A8;}
</style>
<button class="cpbtn" id="cp__IDX__" onclick="cp__IDX__f(this)">📋 Copy this</button>
<script>
function cp__IDX__f(btn){
  var t=__PAYLOAD__;
  var done=function(){btn.textContent='✓ Copied!';setTimeout(function(){btn.textContent='📋 Copy this';},1500);};
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(t).then(done).catch(function(){cp__IDX__fb(t,done);});
  }else{cp__IDX__fb(t,done);}
}
function cp__IDX__fb(t,done){
  var ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';ta.style.opacity='0';
  document.body.appendChild(ta);ta.focus();ta.select();
  try{document.execCommand('copy');}catch(e){}
  document.body.removeChild(ta);done();
}
</script>
"""
    html = html.replace("__PAYLOAD__", payload).replace("__IDX__", str(idx))
    components.html(html, height=46)


# ── OUTPUT ──
if st.session_state.variants:
    variants = st.session_state.variants
    meta_line = st.session_state.result_meta

    labels = [v["label"] for v in variants]
    st.markdown("<div style='font-size:13px;color:var(--text-secondary);margin:0.5rem 0 0.2rem;'>"
                "✨ here are 4 takes — switch tabs for a more direct or gentler version, then copy the one you like.</div>",
                unsafe_allow_html=True)
    tabs = st.tabs(labels)
    for ti, (tab, v) in enumerate(zip(tabs, variants)):
        with tab:
            st.markdown(f"""
            <div class='output-card'>
                <div class='output-header'>
                    <span class='output-tag'>✦ {v['label']}</span>
                    <span style='font-size:11px;color:var(--text-tertiary);'>{meta_line}</span>
                </div>
                <div class='output-text'>{v['message']}</div>
                <div class='strategy-box'>
                    <span class='strategy-icon'>💡</span>
                    <div>
                        <div class='strategy-label'>Why This Works</div>
                        <div class='strategy-text'>{v['strategy_tip']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            copy_button(v["message"], ti)

    rc1, rc2 = st.columns([1, 4])
    with rc1:
        if st.button("↺ Clear", key="regen"):
            st.session_state.variants = None
            st.rerun()

    # disclaimer for rights/claim-type output
    if st.session_state.selected_intent == "Claiming":
        st.markdown("""
        <div style='font-size:11px;color:var(--text-tertiary);margin-top:10px;border-left:2px solid var(--warning);padding-left:10px;'>
            ⚠️ This is communication assistance, not legal advice. For binding disputes, consult a qualified professional.
        </div>
        """, unsafe_allow_html=True)

    coffee_url = _conf("COFFEE_URL")
    if coffee_url:
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown("""
        <div class='monetization-box'>
            <div style='font-size:24px;margin-bottom:8px;'>☕</div>
            <div class='mono-text'><strong>Saved you from awkwardness?</strong><br>
            Keep this tool free for everyone — support it with a coffee.</div>
        </div>
        """, unsafe_allow_html=True)
        _, coffee_col, _ = st.columns([1, 2, 1])
        with coffee_col:
            st.markdown("<div class='coffee-btn'>", unsafe_allow_html=True)
            st.link_button("☕ Buy Me a Coffee", url=coffee_url, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)


# ── FEEDBACK (in-app → Formspree → your email) ──
feedback_endpoint = _conf("FEEDBACK_ENDPOINT", "https://formspree.io/f/xpqnnbyg")
if feedback_endpoint:
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    with st.expander("💬 Leave feedback — ideas, bugs, what felt off (anything!)"):
        st.markdown(
            "<div style='font-size:13px;color:var(--text-secondary);line-height:1.6;margin-bottom:8px;'>"
            "Thanks so much for using The Awkward Translator! 🙏 I hope it saved you from a few "
            "<i>\"ugh, how do I even word this\"</i> moments. It's an early version built by one person, "
            "so your honest feedback genuinely shapes what comes next — anything's welcome. ♡</div>",
            unsafe_allow_html=True,
        )
        fb = st.text_area("feedback", key="fb_text", label_visibility="collapsed",
                          placeholder="✍️ Write your feedback here — what worked, what felt off, an idea, a bug…",
                          height=90, max_chars=1000)
        if st.button("send ♡", key="fb_send", type="primary"):
            if fb and fb.strip():
                try:
                    payload = json.dumps({"message": fb.strip()}).encode("utf-8")
                    req = urllib.request.Request(
                        feedback_endpoint, data=payload,
                        headers={"Content-Type": "application/json",
                                 "Accept": "application/json",
                                 "User-Agent": "AwkwardTranslator/1.0"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        resp.read()
                    st.success("Thank you — got it! ♡")
                except urllib.error.HTTPError as e:
                    try:
                        detail = e.read().decode("utf-8", "ignore")[:400]
                    except Exception:
                        detail = ""
                    st.warning(f"Couldn't send (HTTP {e.code}). {detail}")
                except Exception as e:
                    st.warning(f"Couldn't send right now: {type(e).__name__} — {e}")
            else:
                st.info("Type something first ♡")


# ── FOOTER ──
feedback_url = _conf("FEEDBACK_URL")
feedback_html = (
    f"<div style='margin-bottom:8px;'><a href='{feedback_url}' target='_blank' "
    f"style='color:var(--accent);text-decoration:none;font-weight:600;'>"
    f"💬 got an idea, or something feel off? tell me ↗</a></div>"
    if feedback_url else ""
)
st.markdown(
    "<div class='footer'>"
    + feedback_html
    + "<div style='margin-bottom:6px;'>The Awkward Translator · Built with strategic psychology</div>"
    + "<div style='color:var(--text-tertiary);'>Messages are processed in-session and never stored by this app.</div>"
    + "</div>",
    unsafe_allow_html=True,
)