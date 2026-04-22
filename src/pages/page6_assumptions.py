import streamlit as st
import pandas as pd
import os
from src.utils.styling import (
    page_header, prose, pull_quote, section_heading, data_note, PLOTLY_LAYOUT
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "asm_relaunches.csv")


def confidence_badge(level: str) -> str:
    colors = {
        "Confirmed":                  ("#1a3a1a", "#6fbf7a"),
        "Confirmed - Variant Inflated": ("#3a2a00", "#e8b84b"),
        "Confirmed - Event Boosted":   ("#3a2a00", "#e8b84b"),
        "PRH Estimate":               ("#2a1a1a", "#e23636"),
        "Estimate":                   ("#1a1a2a", "#7799cc"),
    }
    bg, fg = colors.get(level, ("#222", "#888"))
    return (
        f'<span style="background:{bg};color:{fg};border:1px solid {fg};'
        f'font-size:0.72rem;font-family:\'Courier New\',monospace;'
        f'padding:2px 7px;border-radius:2px;white-space:nowrap;">{level}</span>'
    )


def render():
    page_header(
        kicker="Appendix",
        title="Assumptions & Data Clarification",
        subtitle="A complete accounting of data sources, confirmed figures, estimates, and known limitations."
    )

    prose("""
    <p>
    The argument in this project is only as strong as its data. This page documents exactly what
    is confirmed, what is estimated, how estimates were derived, and where the data has structural
    limitations that affect interpretation. Readers who want to contest the analysis should start here.
    </p>
    """)

    # -------------------------------------------------------------------------
    section_heading("1. Amazing Spider-Man Sales Data")

    prose("""
    <p>
    Sales figures for Amazing Spider-Man come from <strong>Comichron</strong>
    (comichron.com), maintained by comics historian John Jackson Miller. Comichron compiles
    monthly order estimates from Diamond Comic Distributors' publicly released sales charts.
    These figures represent estimated retailer orders (not sell-through to readers) and are
    the industry standard for tracking periodical comic sales in the North American direct market.
    </p>
    """)

    section_heading("1a. The Variant Cover Problem")

    prose("""
    <p>
    First issues routinely carry anywhere from a handful to 75+ variant cover editions. Each
    variant is ordered and counted separately in Diamond's charts. When a retailer orders
    10 copies of the "main cover" and 5 copies of each of 20 variants, Diamond's chart records
    110 units, but only 15 of those represent unique readers. The other 95 are speculation
    inventory ordered in hopes the variants will appreciate in value.
    </p>
    <p>
    <strong>Amazing Spider-Man Vol. 3 #1 (April 2014)</strong> is the clearest example in this
    dataset. Its reported figure of <strong>532,586 units</strong> made it "the best-selling new
    comic book in more than a decade" according to Comichron. Issue #2, which shipped the following
    month with a single standard cover, came in at <strong>123,945 units</strong>, a 77% drop
    in one issue. That drop does not represent 400,000 readers who tried the book and quit.
    It represents 400,000 units of speculative variant inventory that evaporated the moment
    the novelty wore off.
    </p>
    <p>
    <strong>How this affects our charts:</strong> Where #1 figures appear, they are flagged as
    variant-inflated and excluded from trajectory comparisons. <strong>Issue #2 is used as the
    primary readership baseline.</strong> It is the first issue with a standard cover edition
    and represents actual sustained reader demand rather than speculator activity.
    </p>
    """)

    pull_quote(
        "A 77% single-issue drop is not reader attrition. "
        "It is the speculator market clearing. "
        "Issue #2 is the first number that means something."
    )

    # -------------------------------------------------------------------------
    section_heading("1b. The Diamond-to-Penguin Random House Distribution Shift")

    prose("""
    <p>
    For most of Marvel's modern publishing history, a single company handled distribution
    of comics to comic shops across North America: <strong>Diamond Comic Distributors</strong>,
    based in Timonium, Maryland. Diamond held a near-monopoly on the direct market from the
    early 1990s onward. Every month, Diamond released itemized order data by title, which
    Comichron compiled into the charts this project relies on. That data pipeline was imperfect
    (it counted orders, not reads) but it was consistent, comprehensive, and publicly accessible.
    </p>
    <p>
    In <strong>October 2021</strong>, Marvel ended its distribution relationship with Diamond
    and moved to <strong>Penguin Random House (PRH)</strong> as its primary distributor. DC had
    already made a similar move to Lunar Distribution in 2020. Diamond, stripped of its two
    largest clients, lost its position as the industry's central clearinghouse. The consequences
    for data transparency were immediate and severe.
    </p>
    <p>
    <strong>PRH does not publish order data.</strong> Unlike Diamond, which released monthly
    sales charts as a standard part of its business operations, Penguin Random House treats
    its order figures as proprietary. There is no official public source for Marvel unit sales
    after October 2021 that is comparable to the pre-2021 Diamond data.
    </p>
    <p>
    Comichron confirmed the scale of the problem explicitly: after October 2021,
    <em>"Diamond only accounts for about 35% of Marvel's output."</em>
    This means any raw Diamond figure for a post-October-2021 Marvel comic represents
    approximately one-third of total orders. An unqualified comparison between a 2020
    Diamond figure and a 2022 Diamond figure would understate 2022 orders by roughly 65%.
    </p>
    """)

    st.markdown("""
    <div style="background:#0f0f0f;border:1px solid #2a2a2a;padding:1.25rem 1.5rem;max-width:760px;margin:1rem 0;">
    <div style="font-size:0.7rem;color:#e8b84b;font-family:'Courier New',monospace;
    letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.75rem;">
    Distribution Timeline
    </div>
    <div style="font-size:0.88rem;color:#c0c0c0;font-family:Georgia,serif;line-height:2;">
    <span style="color:#6fbf7a;">Pre-Oct 2021:</span> Diamond distributes all Marvel titles →
    Diamond publishes monthly order data → Comichron records it → comparable year-over-year data<br>
    <span style="color:#e8b84b;">Oct 2021:</span> Marvel moves to PRH as primary distributor<br>
    <span style="color:#e23636;">Post-Oct 2021:</span> Diamond = ~35% of Marvel orders →
    PRH publishes nothing → Comichron estimates totals from partial data →
    error bars widen from ~±5% to ~±20%
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    section_heading("1c. Normalizing Post-2021 Data: What We Can Do")

    prose("""
    <p>
    There is no clean solution to the PRH data gap, but there are three approaches that improve
    comparability:
    </p>
    <p>
    <strong>Approach 1: Use Comichron's estimates.</strong> Comichron has been attempting to
    reconstruct total market figures by combining Diamond data with estimates derived from PRH's
    reorder charts, retailer-reported data, and historical ratios. For Amazing Spider-Man Vol. 6
    #1 (April 2022), Comichron reported a Diamond-only figure of 92,448 and estimated a combined
    total of approximately 256,800, implying a Diamond share of roughly 36%. This is the approach
    used in this project where Comichron estimates are available.
    </p>
    <p>
    <strong>Approach 2: Apply the 35% normalization factor.</strong> Where Comichron does not
    provide a combined estimate, a raw Diamond figure can be divided by 0.35 to produce a rough
    total-market estimate. This is a blunt instrument. The actual Diamond share varies by
    title, retailer, and month, but it provides a directionally correct comparison to pre-2021
    figures. All Vol. 6 figures beyond #1 in this dataset use this approach and are labeled
    <em>PRH Estimate</em>.
    </p>
    <p>
    <strong>Approach 3: Restrict comparisons to pre-2021 data.</strong> The cleanest analytical
    choice is to limit trajectory comparisons to the period where data is directly comparable
    (1999–2021). The Vol. 5 run (2018–2021) provides a complete, high-confidence dataset for
    the final pre-PRH relaunch cycle. This approach is appropriate when precision matters
    more than recency.
    </p>
    <p>
    <strong>What would make this better:</strong> If PRH ever publishes order data (which would
    require regulatory pressure, a business model change, or industry advocacy) it could
    be retrofitted into the charts immediately. ICv2 (icv2.com) also publishes its own monthly
    estimates which could serve as a cross-reference; their methodology differs from Comichron's
    but the figures are broadly comparable.
    </p>
    """)

    # -------------------------------------------------------------------------
    section_heading("2. Full Data Confidence Table")

    prose("""
    <p>
    The table below shows every data point in the Amazing Spider-Man relaunch dataset,
    its source, and its confidence classification.
    </p>
    """)

    path = os.path.normpath(DATA_PATH)
    if os.path.exists(path):
        df = pd.read_csv(path)
        display_df = df[["relaunch_volume", "relaunch_year", "writer", "issue_num",
                          "orders", "data_confidence"]].copy()
        display_df.columns = ["Volume", "Year", "Writer", "Issue #", "Orders", "Confidence"]
        display_df["Orders"] = display_df["Orders"].apply(lambda x: f"{x:,}")

        confidence_order = {
            "Confirmed": 0,
            "Confirmed - Variant Inflated": 1,
            "Confirmed - Event Boosted": 2,
            "PRH Estimate": 3,
            "Estimate": 4,
        }

        st.markdown("""
        <style>
        [data-testid="stDataFrame"] table { font-size: 0.82rem; }
        </style>
        """, unsafe_allow_html=True)

        def style_confidence(val):
            colors = {
                "Confirmed":                   "color: #6fbf7a",
                "Confirmed - Variant Inflated": "color: #e8b84b",
                "Confirmed - Event Boosted":    "color: #e8b84b",
                "PRH Estimate":                "color: #e23636",
                "Estimate":                    "color: #7799cc",
            }
            return colors.get(val, "")

        try:
            styled = display_df.style.map(style_confidence, subset=["Confidence"])
        except AttributeError:
            styled = display_df.style.applymap(style_confidence, subset=["Confidence"])
        st.dataframe(styled, use_container_width=True, height=400)

        confirmed = (df["data_confidence"].str.startswith("Confirmed")).sum()
        estimates = len(df) - confirmed
        st.markdown(
            f'<div class="data-note">'
            f'{confirmed} confirmed Comichron figures · '
            f'{estimates} estimated or PRH-normalized figures · '
            f'{len(df)} total data points'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.warning("Data file not found: data/asm_relaunches.csv")

    # -------------------------------------------------------------------------
    section_heading("2b. Multi-Title Comparison Data")

    prose("""
    <p>
    The multi-title chart in Section 02 includes issue #2 order estimates for Captain America
    and Thor in addition to the Amazing Spider-Man, Avengers, and Daredevil data documented
    above. These figures carry a different confidence level and that distinction matters.
    </p>
    <p>
    <strong>Amazing Spider-Man, Avengers, and Daredevil</strong> figures come from Comichron's
    published Diamond monthly charts and are labeled Confirmed or PRH Estimate accordingly.
    </p>
    <p>
    <strong>Captain America and Thor</strong> figures are author estimates derived from
    Comichron's monthly chart archives and labeled <em>Estimate</em> throughout. They have not
    been individually verified against the specific monthly chart page for each issue. The
    directional pattern (a consistent decline from the mid-2000s through 2018) is well-supported
    by industry reporting and is unlikely to change materially with direct verification, but
    readers who want confirmed figures should check the relevant Comichron monthly pages:
    comichron.com/monthlycomicssales/YEAR/YEAR-MM.html for the shipping month of each issue #2.
    </p>
    <p>
    Specific figures used: Captain America Vol. 3 (1998, Waid) ~85k; Vol. 5 (2004, Brubaker)
    ~90k; Vol. 7 (2013, Remender) ~72k; Captain America (2018, Coates) ~57k.
    Thor Vol. 3 (2007, Straczynski) ~78k; Thor: God of Thunder (2012, Aaron) ~63k;
    Thor (2018, Aaron) ~50k.
    </p>
    """)

    # -------------------------------------------------------------------------
    section_heading("3. MCU Film Data")

    prose("""
    <p>
    Rotten Tomatoes critical scores are sourced from RT's public website as of April 2025.
    These are critics' scores (Tomatometer), not audience scores. For films with fewer than
    40 reviews, RT scores have higher variance; all MCU theatrical releases have well above
    that threshold.
    </p>
    <p>
    <strong>Source quality classifications</strong> (Strong / Moderate / Weak) are the author's
    judgments based on three criteria: (1) the length and depth of the primary comic run that
    served as source material; (2) the critical and commercial reputation of that run at the time
    of release; and (3) how directly the film's narrative, tone, and character work draws from
    the comics. These classifications are arguable at the margins. Reasonable people could
    reclassify <em>Thor: Ragnarok</em> from Strong to Moderate given how liberally it adapts
    <em>Planet Hulk</em>, but the aggregate pattern is robust to any plausible set of
    reclassifications.
    </p>
    <p>
    Films released from Phase 6 onward (2024–present) have fewer data points and should be
    treated with more caution than the Phase 1–5 trendline.
    </p>
    """)

    # -------------------------------------------------------------------------
    section_heading("4. Writer Tenure Data")

    prose("""
    <p>
    Amazing Spider-Man writer tenures are author-compiled from published issue credits, collected
    edition indicia, and the Grand Comics Database (comics.org). Issue counts represent
    <em>primary writer</em> tenure on the main Amazing Spider-Man title. Fill-in issues,
    backup stories, and co-writing credits are excluded unless the writer held the primary
    plotting role.
    </p>
    <p>
    Several periods are consolidated or simplified:
    </p>
    <ul style="color:#d4d4d4;font-family:Georgia,serif;font-size:1.05rem;line-height:1.85;max-width:760px;">
    <li><strong>The Brand New Day rotation (2008–2010)</strong> featured Dan Slott, Marc Guggenheim,
    Bob Gale, and Zeb Wells rotating on roughly 3-issue arcs. Each writer's individual tenure was
    ~25 issues. This is shown as a single entry to represent the structural decision (rotation
    over singular creative vision) rather than individual credits.</li>
    <li><strong>The 1990s Clone Saga period</strong> involved simultaneous writers across multiple
    Spider-Man titles with shared plots. Howard Mackie's tenure on the main ASM title is counted;
    writers who contributed primarily to other Spider-Man titles (Tom DeFalco on <em>Spectacular</em>,
    J.M. DeMatteis on <em>Web of</em>) are shown only for their primary ASM tenure.</li>
    <li>Minor corrections welcome. If you have more precise issue credits, update
    <code>WRITER_DATA</code> in <code>src/pages/page3_tenure.py</code>.</li>
    </ul>
    """)

    # -------------------------------------------------------------------------
    section_heading("5. Updating This Data")

    prose("""
    <p>
    <strong>To fill in the remaining Comichron estimates:</strong> visit
    comichron.com/monthlycomicssales/YEAR/YEAR-MM.html for the month each issue shipped.
    Amazing Spider-Man appears in the top 300 for virtually every issue in the 2014–2021 window.
    The URL pattern is consistent back to 1996. Update the <code>orders</code> column and change
    <code>data_confidence</code> from <code>Estimate</code> to <code>Confirmed</code>.
    </p>
    <p>
    <strong>To improve post-2021 data:</strong> Comichron publishes its own combined estimates
    on its monthly pages when the data permits. For months where Comichron provides a combined
    Diamond + PRH estimate, use that figure and set <code>data_confidence</code> to
    <code>PRH Estimate</code>. For months where only Diamond data is available, divide by 0.35
    and label <code>PRH Estimate (normalized)</code>.
    </p>
    <p>
    <strong>Alternative sources:</strong> ICv2 (icv2.com/articles/comics/charts/) publishes its
    own monthly estimates derived from Diamond and other data. Their figures are typically within
    5–10% of Comichron's and can serve as a cross-check. No official PRH sales data is publicly
    available as of the publication of this project (April 2025).
    </p>
    """)

    data_note(
        "All source URLs, confidence levels, and derivation methods are documented "
        "in data/asm_relaunches.csv (notes column). "
        "Charts in Section 02 reflect the confidence classification of each data point."
    )
