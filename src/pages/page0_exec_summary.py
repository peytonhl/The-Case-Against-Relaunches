import sqlite3
import streamlit as st
from pathlib import Path
from src.utils.styling import (
    page_header, prose, pull_quote, section_heading, stat_cards, data_note, rec_box
)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "marvel.db"


def _load_key_stats():
    """Compute headline stats from the DB. Falls back to hardcoded values on failure."""
    defaults = {
        "nwh_gross":     "$1.9B",
        "sp_floor":      "$709M",
        "rt_gap":        "+26 pts",
        "avengers_drop": "−56%",
    }
    if not DB_PATH.exists():
        return defaults
    try:
        conn = sqlite3.connect(DB_PATH)

        # No Way Home worldwide gross
        row = conn.execute(
            "SELECT worldwide_gross_m FROM franchise_boxoffice "
            "WHERE film_title LIKE '%No Way Home%' LIMIT 1"
        ).fetchone()
        if row and row[0]:
            nwh = row[0]
            defaults["nwh_gross"] = f"${nwh/1000:.1f}B" if nwh >= 1000 else f"${nwh:.0f}M"

        # Spider-Man franchise floor
        row = conn.execute(
            "SELECT MIN(worldwide_gross_m) FROM franchise_boxoffice "
            "WHERE character = 'Spider-Man'"
        ).fetchone()
        if row and row[0]:
            defaults["sp_floor"] = f"${row[0]:.0f}M"

        # RT gap: strong vs weak source MCU films
        strong = conn.execute(
            "SELECT AVG(rt_score) FROM mcu_films WHERE source_quality = 'Strong'"
        ).fetchone()
        weak = conn.execute(
            "SELECT AVG(rt_score) FROM mcu_films WHERE source_quality = 'Weak'"
        ).fetchone()
        if strong and strong[0] and weak and weak[0]:
            gap = strong[0] - weak[0]
            defaults["rt_gap"] = f"+{gap:.0f} pts"

        # Avengers readership decline: peak vs most recent issue #2
        peak = conn.execute(
            "SELECT MAX(orders) FROM relaunch_multi "
            "WHERE title = 'Avengers' AND issue_num = 2"
        ).fetchone()
        recent = conn.execute(
            "SELECT orders FROM relaunch_multi "
            "WHERE title = 'Avengers' AND issue_num = 2 "
            "ORDER BY relaunch_year DESC LIMIT 1"
        ).fetchone()
        if peak and peak[0] and recent and recent[0] and peak[0] > 0:
            pct = (recent[0] - peak[0]) / peak[0] * 100
            defaults["avengers_drop"] = f"{pct:+.0f}%"

        conn.close()
    except Exception:
        pass
    return defaults


def render():
    page_header(
        kicker="Executive Summary",
        title="The Asset Case",
        subtitle="What the data says about Marvel's publishing model, and why it matters for the next decade of the franchise."
    )

    prose("""
    <p>
    The MCU generated over $30 billion at the global box office. Nearly every film in its
    first three phases was built on source material developed by comic writers who had five
    to twenty years on a single character. That is not a coincidence. It is a production
    model, and the comics division is the upstream half of it.
    </p>
    <p>
    This report examines what happens when that upstream investment shortens. Since 2018,
    the average Amazing Spider-Man writer tenure has dropped to 2.4 years. The Avengers line
    has lost 56% of its sustained readership across four relaunch cycles. MCU films built on
    thin source material average 26 Rotten Tomatoes points lower than films built on deep
    source material. These are not independent trends. They are the same trend measured in
    three different places.
    </p>
    """)

    # ── Key findings ────────────────────────────────────────────────────────

    section_heading("The Numbers That Matter")

    kv = _load_key_stats()
    stat_cards([
        (kv["nwh_gross"],      "No Way Home worldwide gross"),
        (kv["sp_floor"],       "Spider-Man's lowest franchise floor"),
        (kv["rt_gap"],         "RT gap: strong vs. weak source material"),
        ("2.4 yrs",            "Avg. ASM writer tenure, post-2018"),
        (kv["avengers_drop"],  "Avengers sustained readership, 2004 to 2018"),
        ("51",                 "Spider-Man solo media titles across all formats"),
    ])

    prose("""
    <p>
    <em>No Way Home</em>'s $1.9 billion was not driven by a new suit or a new villain.
    It was driven by three generations of Peter Parker, accumulated over twenty years of
    films built on sixty years of comics. The audience paid for a person they felt they knew.
    Spider-Man's franchise floor of $709M is nearly double Captain America's ($371M) and
    reflects the same dynamic: a character so thoroughly developed, across so many formats,
    that no single bad entry can crater the long-term relationship.
    </p>
    <p>
    The 26-point RT gap between MCU films with strong vs. weak comic source material is the
    clearest signal in this dataset. Phase 3 averaged 88%. Phase 5 averages 67%. The films
    that defined the MCU's cultural peak were, almost without exception, built on characters
    developed across decades of long-form comics. As the deep-source catalog has been adapted,
    the pipeline has thinned. What fills that pipeline next depends on decisions being made in
    publishing right now.
    </p>
    """)

    # ── The core argument ────────────────────────────────────────────────────

    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("The Core Argument")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="rec-box">'
            '<strong>What the relaunch strategy costs</strong>'
            '<p>A new #1 generates a short-term orders spike. It also resets reader loyalty, '
            'cuts a writer\'s runway short, and trains the market to treat every story arc as '
            'disposable. Across four Avengers relaunch cycles, issue #2 readership fell from '
            '153k to 67k. The spike is real. The decay is realer. '
            'The readers who would have become lifelong fans of a well-crafted 80-issue run '
            'are instead buying #1, dropping the book, and waiting for the next one.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="rec-box">'
            '<strong>What short tenure actually cuts</strong>'
            '<p>Every character that became a cultural force through comics, Venom, the Winter Soldier, '
            'Black Panther\'s modern mythology, was built by a writer given at least five years. '
            'The post-2018 average on Amazing Spider-Man is 2.4 years. That is enough time to '
            'tell a story. It is not enough time to build a villain, develop a supporting cast, '
            'or create the kind of accumulated emotional weight that makes a character worth '
            'adapting into a $200M production.</p>'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            '<div class="rec-box">'
            '<strong>Why Spider-Man survives everything</strong>'
            '<p>Three complete continuity reboots. Every one generated a $700M+ floor. '
            'The reason is Peter Parker: a civilian identity so thoroughly developed across '
            'sixty years of comics that audiences feel genuine loss when he fails and genuine '
            'joy when he wins. Characters with deep civilian identities command higher box '
            'office floors, migrate into more formats (51 solo Spider-Man media titles vs. '
            '16 for Iron Man), and sustain audience investment through reboots that would '
            'kill a property built only on the costume.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="rec-box">'
            '<strong>The pipeline problem</strong>'
            '<p>The MCU adapted its best source material in Phases 1 through 3. What comes next '
            'depends on what the comics division produces between now and when the cameras roll. '
            'A publishing model structured around 18-month creative cycles and first-issue spikes '
            'is not optimized for producing the kind of material that generates a 90% RT score '
            'and $1B at the box office. A model structured around five-year creative commitments '
            'and deep character development is.</p>'
            '</div>',
            unsafe_allow_html=True
        )

    # ── Recommendations ──────────────────────────────────────────────────────

    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("Three Recommendations")

    rec_box(
        "01: Minimum Five-Year Creative Commitments on Flagship Titles",
        "Every run that produced a culturally durable character or a film-ready arc ran for at "
        "least 60 issues. Structure flagship title contracts around a five-year minimum commitment "
        "for both writer and editorial team. This is not about locking in underperformers. It is "
        "about creating the conditions under which great work becomes possible, and making it "
        "structurally harder to pull the plug on a story before it has had time to land."
    )

    rec_box(
        "02: Source Material Depth as a Production Pipeline Criterion",
        "Build an explicit evaluation of comic source material depth into the film and television "
        "development process. The 26-point RT gap between strong-source and weak-source MCU films "
        "is large enough to function as a selection criterion. Characters and storylines with deep, "
        "critically developed comic histories should receive priority in adaptation queues. "
        "Characters with thin source material should be a signal to invest in the comics first, "
        "not to accelerate the adaptation."
    )

    rec_box(
        "03: Invest in Alter Ego Development Across the Catalog",
        "The characters that generate the highest long-term IP value are the ones whose civilian "
        "identities are as developed as their superhero identities. Peter Parker is the proof of "
        "concept. The publishing strategy should explicitly prioritize civilian-life storytelling: "
        "the job, the relationships, the failures, the texture that makes an audience care about "
        "the person underneath the mask. That is not a creative preference. It is the mechanism "
        "by which comics convert a single franchise into a fifty-title media footprint."
    )

    # ── Closing ──────────────────────────────────────────────────────────────

    st.markdown("<br>", unsafe_allow_html=True)
    prose("""
    <p>
    The goodwill Marvel has built across sixty years of publishing and thirty years of film
    is still intact. The question is whether the publishing model is structured to keep building
    it, or to spend it down one first-issue spike at a time. The data in this report points toward
    an answer. The sections that follow show the work.
    </p>
    """)

    pull_quote(
        "The next $30 billion in Marvel IP "
        "is being written right now. "
        "The question is how much runway those writers are being given."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#555;font-size:0.8rem;font-family:\'Courier New\',monospace;">'
        'Full analysis: navigate sections in the sidebar. '
        'Data sourcing and confidence documentation: Appendix.'
        '</p>',
        unsafe_allow_html=True,
    )
