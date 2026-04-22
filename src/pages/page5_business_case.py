import sqlite3
import streamlit as st
from pathlib import Path
from src.utils.styling import (
    page_header, prose, pull_quote, section_heading, stat_cards, rec_box
)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "marvel.db"


def _load_summary_stats():
    """Compute summary stats from DB. Falls back to hardcoded values."""
    out = {
        "avengers_drop": "−56%",
        "retention":     "40–45%",
        "rt_gap":        "+26 pts",
    }
    if not DB_PATH.exists():
        return out
    try:
        conn = sqlite3.connect(DB_PATH)

        # Avengers issue #2 readership decline (peak vs most recent)
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
            out["avengers_drop"] = f"{pct:+.0f}%"

        # 12-issue retention across all ASM relaunches
        twos = conn.execute(
            "SELECT relaunch_volume, orders FROM asm_relaunches WHERE issue_num = 2"
        ).fetchall()
        twelves = conn.execute(
            "SELECT relaunch_volume, orders FROM asm_relaunches WHERE issue_num = 12"
        ).fetchall()
        two_map   = {r[0]: r[1] for r in twos   if r[1]}
        twelve_map = {r[0]: r[1] for r in twelves if r[1]}
        common = set(two_map) & set(twelve_map)
        if common:
            rates = [twelve_map[v] / two_map[v] * 100 for v in common]
            avg_ret = sum(rates) / len(rates)
            out["retention"] = f"{avg_ret:.0f}%"

        # RT gap: strong vs weak source
        strong = conn.execute(
            "SELECT AVG(rt_score) FROM mcu_films WHERE source_quality = 'Strong'"
        ).fetchone()
        weak = conn.execute(
            "SELECT AVG(rt_score) FROM mcu_films WHERE source_quality = 'Weak'"
        ).fetchone()
        if strong and strong[0] and weak and weak[0]:
            out["rt_gap"] = f"+{strong[0] - weak[0]:.0f} pts"

        conn.close()
    except Exception:
        pass
    return out


def render():
    page_header(
        kicker="Section 07",
        title="The Business Case",
        subtitle="What the data suggests, and a few ideas for how to build Marvel stories that will matter for the next sixty years."
    )

    prose("""
    <p>
    This project started from a simple question: what made the Marvel stories that defined the MCU
    so good, and is that still happening?
    </p>
    <p>
    The answer the data points toward is that the best Marvel stories, on the page and on the screen,
    came from writers who were given the time to develop something real. Characters, villains, supporting
    casts, emotional arcs that took years to earn. The MCU inherited that work and turned it into a
    franchise worth billions. That inheritance is finite, and the most meaningful thing the comics line
    can do right now is keep building the next one.
    </p>
    <p>
    Marvel's comics division generates roughly $160 million annually against Disney's $88 billion
    in total revenue. It is not a major profit center, and that is actually freeing. It means the
    most important thing the comics line produces is not its direct revenue. It is the characters,
    the story infrastructure, and the creative mythology that the broader franchise draws from.
    Managing it with that in mind opens up a lot of interesting possibilities.
    </p>
    """)

    pull_quote(
        "The comics line is the most creatively flexible, lowest-cost R&D lab "
        "in the entertainment industry. "
        "The future of the franchise lives here."
    )

    section_heading("What the Data Established")

    kv = _load_summary_stats()
    stat_cards([
        (kv["avengers_drop"], "Avengers #2 readership: 2004 → 2018"),
        (kv["retention"],     "Avg. 12-issue retention across relaunches"),
        (kv["rt_gap"],        "RT score gap: strong vs. weak comic source material"),
        ("2.4 yrs",           "Avg. ASM writer tenure post-2018"),
    ])

    prose("""
    <p>
    Sections 02 through 05 document three trends worth paying attention to. Sustained readership
    at relaunch has declined across every tracked flagship title. Writer tenures have shortened
    to the point where the kind of slow-build character development that produced Venom, the Winter
    Soldier, and the modern Black Panther mythology is structurally harder to achieve. And the MCU,
    which drew so effectively from deep story wells built over decades, is beginning to show what
    happens when those wells run lower. None of this is irreversible. All of it is addressable.
    </p>
    """)

    section_heading("The Infinite Game Framing")

    prose("""
    <p>
    Finite game metrics for Marvel Publishing are: monthly sales rank, first-issue orders, variant
    cover sell-through. The relaunch strategy plays well on those metrics. It generates a reliable
    short-term bump at the cost of the longer reader relationship. Repeated over many cycles, the
    data suggests the cumulative effect is a gradually shrinking sustained audience and an IP pipeline
    that has less runway to develop genuinely new characters.
    </p>
    <p>
    Infinite game metrics look different: new breakout IP created in the last decade, depth of
    narrative infrastructure available to the film and television divisions, reader conversion from
    casual to sustained, and long-term brand equity of the Spider-Man, X-Men, and Avengers franchises.
    These metrics are harder to track in real time, which is part of why they tend to get deprioritized.
    But they are the ones that determine whether Marvel's stories will still matter in thirty years.
    </p>
    <p>
    The good news is that Marvel has done this before, repeatedly, and the playbook is visible in
    the data. The conditions that produced the best runs are well understood. They are not complicated
    to recreate. They just require prioritizing the long game.
    </p>
    """)

    pull_quote(
        "Every great Marvel character was built slowly, by a writer "
        "who was trusted to finish what they started. "
        "That trust is still the most valuable thing in the editorial toolkit."
    )

    section_heading("Recommendations")

    rec_box(
        "01: Protect Writer Tenures on Flagship Titles",
        "The creative runs that produced Marvel's most enduring characters and its most adaptable "
        "story material were built by writers given meaningful time on a title. A minimum of 36 "
        "issues gives a writer enough runway to introduce a villain, develop a supporting cast, and "
        "earn an emotional payoff. Sixty or more issues is where the really interesting things tend "
        "to happen. Roger Stern created the Hobgoblin in 29 issues. David Michelinie built Venom "
        "across 93. Dan Slott's 153-issue run on Amazing Spider-Man is the reason Spider-Man still "
        "feels like a living character. Protecting that kind of tenure, especially on flagship titles, "
        "is one of the highest-leverage investments available."
    )

    rec_box(
        "02: Solve the Accessibility Problem with New Characters, Not Continuity Resets",
        "The legitimate problem that relaunches attempt to solve is real: comics with 60 years of "
        "continuity can be genuinely hard to walk into. But the Miles Morales model shows a better "
        "path. Miles is a new character with a clean origin, a fresh supporting cast, and no "
        "continuity debt. He succeeded because he was additive, not a replacement. When Marvel "
        "wants a jumping-on point, a new character with a clear voice and a defined world is a "
        "more durable solution than resetting a 60-year continuity that readers already love. "
        "Peter Parker's history is an asset. The question is how to let new readers access it "
        "without asking existing readers to watch it be erased."
    )

    rec_box(
        "03: Weight Sustained Readership More Heavily Than Launch Numbers",
        "First-issue orders are a reasonable signal but a misleading primary metric, because they "
        "capture speculator activity as much as genuine reader interest. A title that launches at "
        "80,000 and holds 60,000 at issue twenty-four is building something durable. A title that "
        "launches at 150,000 and falls to 30,000 is not. Tracking and reporting sustained readership "
        "at issue twelve, twenty-four, and beyond would give editorial teams a clearer picture of "
        "which creative directions are genuinely working, and which ones are borrowing reader "
        "goodwill they cannot fully repay."
    )

    rec_box(
        "04: Develop Pipeline Characters on a Long Horizon",
        "The comics line has a unique advantage: it can develop characters years before a film or "
        "streaming project needs them. If the next phase of the MCU will eventually need a deeply "
        "felt Nova, a rich Ghost Rider mythology, or a well-developed Sentry, the time to build "
        "that story infrastructure is now, not six months before the film goes into production. "
        "The comics line is the cheapest place in the franchise ecosystem to develop IP that will "
        "eventually cost hundreds of millions to put on screen. Using it that way would be a "
        "genuine competitive advantage."
    )

    rec_box(
        "05: Protect Flagship Runs from Mandatory Event Crossovers",
        "Some of the best long-form runs in Marvel's history, including Brubaker's Captain America, "
        "Priest's Black Panther, and Abnett and Lanning's Guardians, were produced by writers "
        "given the space to tell their story without constant interruption. Event crossovers serve "
        "a purpose, but when they disrupt an ongoing storyline mid-arc, reset character development, "
        "or force a creative team to pause the story they are actually building, the long-term "
        "cost to the run tends to outweigh the short-term sales lift. Protecting flagship runs "
        "from crossover obligations for at least the first 24 issues would give creative teams "
        "the foundation they need to build something worth protecting."
    )

    rec_box(
        "06: Publish Monthly Sales Data",
        "When Penguin Random House took over Marvel distribution in 2021, the public data pipeline "
        "that Comichron and the broader industry had relied on for decades went dark. Diamond "
        "published monthly order charts. PRH does not. This affects more than just analysts: "
        "fans who want to support a title they love, campaign for a character they care about, "
        "or understand whether a run is in danger no longer have the information they need to act. "
        "Monthly unit sales data, published the way Diamond did for thirty years, would restore "
        "a feedback loop between publisher and audience that benefits everyone. Readers who know "
        "their favorite book is on the bubble will show up for it. That is a good thing."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("A Note on Transparency and Fan Agency")

    prose("""
    <p>
    The sixth suggestion above is worth dwelling on because it is different in kind from the others.
    The first five are about internal editorial strategy. This one is about the relationship between
    Marvel and its readers, which is one of the more remarkable relationships in entertainment.
    </p>
    <p>
    Comics readers are not a passive audience. They are among the most engaged, most loyal,
    and most financially committed fan communities anywhere. They buy variant covers to support
    a creator they believe in. They pre-order to hit thresholds that keep a title alive. They
    campaign loudly when a run they love gets cut short. They show up to conventions and spend
    money at local shops because they understand that the ecosystem that produces these stories
    depends on their participation. They do this because they care, deeply and specifically,
    about individual characters, creative teams, and the stories those creative teams are building.
    </p>
    <p>
    That level of engagement is an extraordinary resource. But it only works as a feedback loop
    if readers have the information they need. Right now, under the PRH distribution model, a fan
    has no reliable way to know whether their favorite title is selling 80,000 copies a month or
    sitting near the cancellation threshold. They cannot mobilize around a title they do not know
    is in trouble. They cannot send a signal to Marvel that a character has an audience worth
    investing in.
    </p>
    <p>
    Restoring that visibility would not just be good for fans. It would give Marvel a richer,
    more responsive picture of what its audience actually values. The relationship between a
    publisher and its readers works best as a conversation. Sales transparency is one of the
    simplest ways to keep that conversation open.
    </p>
    """)

    pull_quote(
        "A fan who knows their book is on the bubble will buy two copies. "
        "A fan who doesn't know won't know to."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("The Bottom Line")

    prose("""
    <p>
    Disney acquired Marvel in 2009 for $4.24 billion. As of 2024, the MCU alone has generated
    over $30 billion in global box office. The comics line that seeded the characters, stories,
    and mythologies behind that return generates less than $200 million per year. It is, in the
    most literal sense, the seed stock for everything else.
    </p>
    <p>
    The cost of longer writer tenures, reduced relaunch frequency, and deeper editorial protection
    is measured in foregone short-term variant cover revenue, tens of millions of dollars at most.
    The value of a deeply developed character who anchors a successful film franchise is measured
    in billions. That asymmetry is the whole argument.
    </p>
    <p>
    Marvel's comics line has been the most generative story engine in American popular culture
    for sixty years. The characters it produced built an industry, and then a franchise that
    redefined what blockbuster filmmaking could be. The next sixty years of great Marvel stories
    depend on giving writers the time and the trust to keep building. The infrastructure for
    that is already in place. The audience is already there. The characters are ready.
    </p>
    """)

    pull_quote(
        "The Silver Age writers had no idea they were building a film franchise. "
        "They just loved the characters enough to stay. "
        "That is still the only thing required."
    )

    st.markdown('<hr style="border-color:#2a2a2a;margin:2rem 0;">', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#444;font-size:0.8rem;font-family:\'Courier New\',monospace;">'
        'Prepared as a data storytelling portfolio project. '
        'All data sourced from publicly available records. '
        'Argument and analysis are the author\'s own.'
        '</p>',
        unsafe_allow_html=True
    )
