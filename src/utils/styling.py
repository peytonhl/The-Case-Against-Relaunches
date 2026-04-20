GLOBAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:ital,wght@0,400;0,700;1,400&display=swap');

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 3px solid #e23636;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-family: 'Comic Neue', cursive !important;
        font-weight: 700;
        font-size: 0.85rem;
        color: #cccccc !important;
        letter-spacing: 0.02em;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] small {
        font-family: 'Comic Neue', cursive;
        color: #555;
        font-size: 0.78rem;
        line-height: 1.5;
    }

    /* ── Main container ── */
    .main .block-container {
        padding-top: 2.5rem;
        padding-bottom: 4rem;
        max-width: 1050px;
    }

    /* ── Page title ── */
    .page-title {
        font-family: 'Bangers', cursive;
        font-size: 3.2rem;
        font-weight: 400;
        color: #ffffff;
        letter-spacing: 0.05em;
        line-height: 1.05;
        text-shadow: 3px 3px 0px #e23636;
        margin-bottom: 0.2rem;
    }

    /* ── Section kicker ── */
    .page-kicker {
        font-family: 'Bangers', cursive;
        font-size: 0.85rem;
        font-weight: 400;
        color: #f5e642;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    /* ── Divider ── */
    .rule {
        border: none;
        border-top: 3px solid #e23636;
        margin: 1.5rem 0;
    }

    /* ── Prose body ── */
    .prose {
        font-family: 'Comic Neue', cursive;
        font-size: 1.05rem;
        line-height: 1.9;
        color: #e0e0e0;
        max-width: 760px;
    }
    .prose p { margin-bottom: 1.2em; }
    .prose strong { color: #ffffff; }
    .prose em { color: #f5e642; font-style: italic; }

    /* ── Pull quote — speech bubble ── */
    .pull-quote {
        position: relative;
        background: #ffffff;
        color: #0a0a0a;
        border: 3px solid #0a0a0a;
        border-radius: 18px;
        padding: 1rem 1.4rem;
        font-family: 'Bangers', cursive;
        font-size: 1.35rem;
        letter-spacing: 0.04em;
        line-height: 1.5;
        max-width: 680px;
        box-shadow: 5px 5px 0px #e23636;
        margin: 1.5rem 0 2rem 0;
    }
    .pull-quote::after {
        content: '';
        position: absolute;
        bottom: -20px;
        left: 36px;
        width: 0;
        height: 0;
        border-left: 14px solid transparent;
        border-right: 0px solid transparent;
        border-top: 20px solid #0a0a0a;
    }
    .pull-quote::before {
        content: '';
        position: absolute;
        bottom: -15px;
        left: 39px;
        width: 0;
        height: 0;
        border-left: 11px solid transparent;
        border-right: 0px solid transparent;
        border-top: 16px solid #ffffff;
        z-index: 1;
    }

    /* ── Chart annotation — yellow caption box ── */
    .chart-annotation {
        background: #f5e642;
        color: #0a0a0a;
        border: 3px solid #0a0a0a;
        padding: 0.8rem 1.1rem;
        font-family: 'Comic Neue', cursive;
        font-weight: 700;
        font-size: 0.92rem;
        line-height: 1.7;
        max-width: 760px;
        box-shadow: 4px 4px 0px #333;
        margin-top: 0.6rem;
    }

    /* ── Data note ── */
    .data-note {
        font-size: 0.73rem;
        color: #444;
        font-family: 'Courier New', monospace;
        margin-top: 0.6rem;
        max-width: 760px;
    }

    /* ── Section heading ── */
    .section-heading {
        font-family: 'Bangers', cursive;
        font-size: 1.65rem;
        font-weight: 400;
        color: #ffffff;
        letter-spacing: 0.05em;
        text-shadow: 2px 2px 0px #e23636;
        margin-top: 2.5rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #2a2a2a;
        padding-bottom: 0.3rem;
    }

    /* ── Stat cards ── */
    .stat-row {
        display: flex;
        gap: 1.25rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }
    .stat-card {
        background: #0a0a0a;
        border: 3px solid #e23636;
        box-shadow: 4px 4px 0px #e23636;
        padding: 0.9rem 1.2rem;
        min-width: 145px;
    }
    .stat-number {
        font-family: 'Bangers', cursive;
        font-size: 2.2rem;
        color: #f5e642;
        line-height: 1;
        letter-spacing: 0.03em;
    }
    .stat-label {
        font-family: 'Comic Neue', cursive;
        font-size: 0.72rem;
        font-weight: 700;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.2rem;
    }

    /* ── Recommendation box ── */
    .rec-box {
        background: #0a0a0a;
        border: 3px solid #e23636;
        box-shadow: 5px 5px 0px #e23636;
        padding: 1rem 1.25rem;
        margin-bottom: 1.2rem;
        max-width: 760px;
    }
    .rec-box strong {
        font-family: 'Bangers', cursive;
        font-size: 1.1rem;
        letter-spacing: 0.06em;
        color: #f5e642;
    }
    .rec-box p {
        font-family: 'Comic Neue', cursive;
        color: #d0d0d0;
        font-size: 0.97rem;
        line-height: 1.7;
        margin-top: 0.4rem;
        margin-bottom: 0;
    }

    /* ── Sidebar title ── */
    .sidebar-title {
        font-family: 'Bangers', cursive;
        font-size: 1.5rem;
        color: #ffffff;
        letter-spacing: 0.06em;
        text-shadow: 2px 2px 0px #e23636;
        line-height: 1.2;
    }
    .sidebar-sub {
        font-family: 'Comic Neue', cursive;
        font-size: 0.78rem;
        color: #666;
        font-style: italic;
        margin-top: 0.1rem;
    }
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(kicker: str, title: str, subtitle: str = ""):
    import streamlit as st
    st.markdown(f'<div class="page-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f'<p style="color:#888;font-size:0.95rem;margin-top:0.4rem;'
            f'font-family:\'Comic Neue\',cursive;">{subtitle}</p>',
            unsafe_allow_html=True
        )
    st.markdown('<hr class="rule">', unsafe_allow_html=True)


def prose(html: str):
    import streamlit as st
    st.markdown(f'<div class="prose">{html}</div>', unsafe_allow_html=True)


def pull_quote(text: str):
    import streamlit as st
    st.markdown(f'<div class="pull-quote">{text}</div>', unsafe_allow_html=True)


def chart_annotation(text: str):
    import streamlit as st
    st.markdown(f'<div class="chart-annotation">{text}</div>', unsafe_allow_html=True)


def section_heading(text: str):
    import streamlit as st
    st.markdown(f'<div class="section-heading">{text}</div>', unsafe_allow_html=True)


def stat_cards(stats: list):
    import streamlit as st
    cards_html = '<div class="stat-row">'
    for number, label in stats:
        cards_html += (
            f'<div class="stat-card">'
            f'<div class="stat-number">{number}</div>'
            f'<div class="stat-label">{label}</div>'
            f'</div>'
        )
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)


def rec_box(title: str, body: str):
    import streamlit as st
    st.markdown(
        f'<div class="rec-box"><strong>{title}</strong><p>{body}</p></div>',
        unsafe_allow_html=True
    )


def data_note(text: str):
    import streamlit as st
    st.markdown(f'<div class="data-note">{text}</div>', unsafe_allow_html=True)


# Base Plotly layout — no xaxis/yaxis (define per-chart to avoid duplicate-kwarg errors)
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#0d0d0d",
    plot_bgcolor="#0d0d0d",
    font=dict(family="'Comic Neue', cursive, sans-serif", color="#d4d4d4", size=12),
    title_font=dict(family="Bangers, cursive", size=17, color="#ffffff"),
    margin=dict(t=55, b=50, l=60, r=30),
)

# Shared axis defaults — merge into update_layout calls explicitly
AXIS_STYLE = dict(gridcolor="#1e1e1e", linecolor="#333", tickfont=dict(size=11))
