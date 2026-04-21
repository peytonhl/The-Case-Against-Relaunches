import streamlit as st
from src.utils.styling import (
    page_header, prose, pull_quote, section_heading, stat_cards, data_note
)


def render():
    page_header(
        kicker="Section 01",
        title="The Case Against the Relaunch",
        subtitle="A data-driven argument for investing in the stories that built the Marvel universe, and will build the next one."
    )

    prose("""
    <p>
    Marvel Comics has spent sixty years building some of the most durable characters in popular
    fiction. Spider-Man, Captain America, Black Panther, the Guardians of the Galaxy: characters
    that began as ink on newsprint and became a $30 billion film franchise. That did not happen
    by accident. It happened because generations of writers were given the time and editorial
    support to develop those characters fully, and because Marvel's publishing model, at its best,
    functioned less as a periodical business than as an IP development engine for the entire franchise.
    </p>
    <p>
    This project examines what the data shows about that model: where it has worked, where recent
    trends diverge from the patterns that produced Marvel's most enduring stories, and what a
    publishing strategy explicitly oriented toward long-term character development might look like.
    The argument is data-driven and the goal is straightforward: more great Marvel stories, built
    to last, for more generations of readers.
    </p>
    """)

    pull_quote(
        "The goodwill is still there. "
        "The question is whether we spend it on another #1 "
        "or invest it in a story worth remembering."
    )

    prose("""
    <p>
    Simon Sinek's <em>The Infinite Game</em> offers a useful frame. Finite game players optimize for
    winning the current round: market share, quarterly revenue, the top slot on Diamond's sales chart.
    Infinite game players optimize for staying in the game by building institutions and relationships
    robust enough to outlast any single transaction. The relaunch strategy is a finite game play.
    Each new #1 captures a short-term bump that is paid for with long-term reader investment.
    The readers who would become lifelong fans of a well-crafted, long-running Spider-Man story
    are instead trained to buy the first issue and drop the book. The casual reader who might have
    been converted by a thirty-issue arc is presented with a continuity maze and walks away.
    </p>
    <p>
    This is a specific, falsifiable argument with three data-driven pillars.
    </p>
    """)

    section_heading("The Three Pillars")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="stat-card" style="height:100%;">'
            '<div style="font-family:\'Bangers\',cursive;font-size:0.75rem;color:#e23636;'
            'letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.4rem;">Pillar I: Audience Decay</div>'
            '<div class="stat-number">−56%</div>'
            '<div class="stat-label">Avengers issue #2 readership<br>2004 → 2018</div>'
            '<p style="font-family:\'Comic Neue\',cursive;font-size:0.82rem;color:#888;'
            'line-height:1.6;margin-top:0.6rem;margin-bottom:0;">'
            'New Avengers opened at 153k at issue #2 in 2004. The 2018 relaunch: 67k. '
            'Daredevil is down 43% from its late-90s baseline. '
            'Amazing Spider-Man has held ~110–125k across every relaunch, '
            'which tells you something about how much the character carries the book.'
            '</p>'
            '</div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            '<div class="stat-card" style="height:100%;">'
            '<div style="font-family:\'Bangers\',cursive;font-size:0.75rem;color:#e23636;'
            'letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.4rem;">Pillar II: Tenure Collapse</div>'
            '<div class="stat-number">2.4 yrs</div>'
            '<div class="stat-label">Avg. ASM writer tenure<br>post-2018</div>'
            '<p style="font-family:\'Comic Neue\',cursive;font-size:0.82rem;color:#888;'
            'line-height:1.6;margin-top:0.6rem;margin-bottom:0;">'
            'Since 2018, both ASM relaunch cycles ended before reaching 3 years. '
            'Michelinie, Straczynski, Slott: every run that produced a lasting character '
            'or villain ran for at least 5 years.'
            '</p>'
            '</div>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            '<div class="stat-card" style="height:100%;">'
            '<div style="font-family:\'Bangers\',cursive;font-size:0.75rem;color:#e23636;'
            'letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.4rem;">Pillar III: Pipeline Erosion</div>'
            '<div class="stat-number">−21 pts</div>'
            '<div class="stat-label">MCU avg RT score<br>Phase 3 → Phase 5</div>'
            '<p style="font-family:\'Comic Neue\',cursive;font-size:0.82rem;color:#888;'
            'line-height:1.6;margin-top:0.6rem;margin-bottom:0;">'
            'Phase 3 averaged ~88% on Rotten Tomatoes. Phase 5 averages ~67%. '
            'Films built on strong source material average 26 points higher than weak-source films.'
            '</p>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    prose("""
    <p>
    <strong>First:</strong> The relaunch cycle's costs are not evenly distributed.
    Amazing Spider-Man has held its core readership with remarkable consistency, around
    110–125k at issue #2 across five relaunches spanning 25 years. Spider-Man is resilient enough
    to absorb the reset. The Avengers line is not: 153k at issue #2 in 2004, down to 67k by 2018,
    a 56% decline in sustained readership across four relaunch cycles. Daredevil is down 43% from
    its late-90s baseline. The difference is not creative quality. Daredevil had Miller, Bendis,
    and Waid, three of the strongest sustained runs in Marvel's catalog. The difference is that
    readers are invested in <em>Peter Parker</em>, not just Spider-Man. The alter-ego depth that
    makes ASM resilient is precisely what the rest of the catalog lacks, and what long-form
    development is best positioned to build.
    </p>
    <p>
    <strong>Second:</strong> Writer tenures on Amazing Spider-Man have compressed significantly.
    Lee, Conway, Michelinie, Straczynski: the runs that defined Spider-Man as a cultural force
    were built by writers given 40 to 153 issues to develop their vision. The post-2018 average
    is 57 issues across two relaunches. The characters that became cultural phenomena, Venom,
    the Hobgoblin, the black costume arc, were built slowly. That kind of development requires runway.
    </p>
    <p>
    <strong>Third:</strong> MCU films built on deep comic source material average ~90% on Rotten
    Tomatoes. Films built on thinner source material average in the mid-60s. That 26-point gap
    holds across phases and genres. The franchise's strongest creative period correlates directly
    with its deepest source material, and the comics being written today are the source material
    for whatever comes next.
    </p>
    <p>
    The sections that follow present the data behind each of these findings, and close with a set
    of concrete recommendations for how the publishing model might evolve to keep building the
    kind of story depth that has defined Marvel at its best.
    </p>
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("Definitions")

    prose("""
    <p>
    Several terms are used throughout this document in specific, defined ways. This section establishes
    those definitions to ensure the argument is falsifiable and the data is interpretable.
    </p>
    """)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            '<div class="rec-box">'
            '<strong>The Relaunch</strong>'
            '<p>A full cancellation of a running title followed by a new series starting at #1. '
            'Distinguished from a soft renumbering (continuing story, new number) or a reboot '
            '(full continuity reset). Relaunches are identified by a new volume designation '
            'and a new #1 issue. The defining feature is the deliberate break in numbering '
            'to generate a first-issue sales spike.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="rec-box">'
            '<strong>Issue #2 Baseline</strong>'
            '<p>We use issue #2 (not #1) as the readership baseline for each relaunch. '
            'Issue #1 orders are inflated by variant cover editions, which are multiple '
            'printings of the same content ordered separately by retailers. '
            'ASM Vol. 3 #1 (2014) reported 532,586 units; issue #2 came in at 123,945, '
            'a 77% single-issue drop that was not reader attrition. It was the speculator '
            'market clearing. Issue #2 is the first variant-free, reader-demand signal.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="rec-box">'
            '<strong>Writer Tenure</strong>'
            '<p>Measured as the contiguous issue count for a single primary writer on a title. '
            'Multi-writer event crossovers, fill-in issues, and co-writing credits '
            'are excluded. Tenure ends when the writer departs the title, regardless of whether '
            'a relaunch follows immediately or later.</p>'
            '</div>',
            unsafe_allow_html=True
        )
    with col_b:
        st.markdown(
            '<div class="rec-box">'
            '<strong>Source Material Depth</strong>'
            '<p>Our classification for MCU films (<em>Strong</em>, <em>Moderate</em>, or <em>Weak</em>) '
            'reflects the depth of published comic source material available at the time of production. '
            '<em>Strong</em>: a substantial, critically regarded long-form run with documented influence '
            'on the adaptation. <em>Moderate</em>: partial source material or a shorter run. '
            '<em>Weak</em>: characters with thin, scattered, or non-existent long-form comic development. '
            'Classifications are author judgments, documented in the Appendix.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="rec-box">'
            '<strong>Publishing Eras</strong>'
            '<p>Comic book history is conventionally divided into publishing eras by changes '
            'in content, distribution, and readership. This document uses: '
            '<em>Golden Age</em> (1938–1955), <em>Silver Age</em> (1956–1969), '
            '<em>Bronze Age</em> (1970–1984), <em>Copper Age</em> (1985–1992), '
            '<em>Modern Age</em> (1993–2009), and <em>Contemporary</em> (2010–present). '
            'Era assignments are based on a character\'s first comic appearance.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="rec-box">'
            '<strong>Diamond vs. PRH Data</strong>'
            '<p>Diamond Comic Distributors published monthly order charts for 30+ years, '
            'enabling public tracking of direct-market sales. Penguin Random House (PRH) '
            'took over Marvel distribution in October 2021 and publishes no equivalent data. '
            'Figures marked <em>Confirmed</em> come from Comichron\'s Diamond records. '
            'Figures marked <em>PRH Estimate</em> are approximations based on available '
            'partial data and Comichron\'s published normalization methodology. '
            'See the Appendix for full confidence documentation.</p>'
            '</div>',
            unsafe_allow_html=True
        )

    data_note("Definitions reflect industry conventions and author methodology. See the Appendix for complete data sourcing and confidence classifications.")

    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#555;font-size:0.8rem;font-family:\'Courier New\',monospace;">'
        'Navigate using the sidebar → Begin with Section 02: Relaunch Bump Decay'
        '</p>',
        unsafe_allow_html=True
    )
