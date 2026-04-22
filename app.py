import streamlit as st

st.set_page_config(
    page_title="The Case Against the Relaunch",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.utils.styling import inject_css
from src.pages import page0_exec_summary, page1_thesis, page2_relaunch, page3_tenure, page4_characters, page4_mcu, page6_peter_parker, page5_business_case, page6_assumptions, page8_forecast

inject_css()

PAGES = {
    "Executive Summary": page0_exec_summary,
    "01 — The Thesis": page1_thesis,
    "02 — Relaunch Bump Decay": page2_relaunch,
    "03 — The Peter Parker Effect": page6_peter_parker,
    "04 — Writer Tenure": page3_tenure,
    "05 — The Character Ledger": page4_characters,
    "06 — MCU Pipeline": page4_mcu,
    "07 — The Business Case": page5_business_case,
    "08 — Readership Forecast": page8_forecast,
    "Appendix — Assumptions & Data": page6_assumptions,
}

with st.sidebar:
    st.markdown(
        '<div class="sidebar-title">The Case Against<br>the Relaunch</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-sub">A data-driven argument for<br>long-term IP investment</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr style="border-color:#e23636;border-width:2px;margin:0.75rem 0 1rem;">', unsafe_allow_html=True)

    selection = st.radio("", list(PAGES.keys()), label_visibility="collapsed")

    st.markdown('<hr style="border-color:#222;margin:1rem 0 0.5rem;">', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.7rem;color:#444;font-family:\'Courier New\',monospace;line-height:1.6;">'
        'Sources:<br>'
        '· Comichron (sales estimates)<br>'
        '· Rotten Tomatoes (MCU scores)<br>'
        '· Author-compiled (writer tenures)'
        '</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:0.7rem;color:#333;font-family:\'Courier New\',monospace;'
        'margin-top:1rem;line-height:1.4;">'
        'By Peyton Lindogan'
        '</p>',
        unsafe_allow_html=True,
    )

PAGES[selection].render()
