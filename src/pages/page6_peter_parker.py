import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from pathlib import Path
from src.utils.styling import (
    page_header, prose, pull_quote, chart_annotation, section_heading,
    stat_cards, data_note, PLOTLY_LAYOUT, AXIS_STYLE
)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "marvel.db"

FRANCHISE_COLORS = {
    "Spider-Man":      "#e23636",
    "Iron Man":        "#e8b84b",
    "Captain America": "#2aa198",
    "Thor":            "#bf6f30",
}

FRANCHISE_SYMBOLS = {
    "Spider-Man":      "circle",
    "Iron Man":        "diamond",
    "Captain America": "square",
    "Thor":            "triangle-up",
}

# Civilian story index — estimated % of narrative pages/screen time
# devoted to the hero's civilian identity (not masked, costumed, or supernatural)
# Author estimate; see Appendix for methodology note
CIVILIAN_INDEX = [
    ("Thor",            10, "Divine royalty, minimal civilian arc"),
    ("Captain America", 22, "Steve Rogers present but wartime/mission-driven"),
    ("Hulk / Banner",   26, "Banner explored but Hulk dominates page count"),
    ("Iron Man",        38, "Tony Stark persona central to tone and plot"),
    ("Daredevil",       46, "Matt Murdock's legal career woven throughout"),
    ("Spider-Man",      58, "Peter Parker: school, work, family, grief — co-lead"),
]

# Distinct solo media appearances by format (animated series, live-action TV,
# feature films, video games, other standalone media)
# Sources: Marvel wikia, IMDB, MobyGames; author-compiled
MEDIA_FORMATS = {
    "character": ["Spider-Man", "Iron Man", "Captain America", "Thor", "Hulk"],
    "Animated Series": [12, 3, 3, 2, 4],
    "Live-Action TV":  [3,  0, 1, 0, 2],
    "Feature Films":   [10, 3, 3, 4, 3],
    "Video Games":     [21, 8, 5, 4, 7],
    "Other Media":     [5,  2, 2, 2, 3],
}


def load_box_office():
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT * FROM franchise_boxoffice", conn)
            conn.close()
            return df
        except Exception:
            pass
    return pd.DataFrame()


def load_cv_appearances():
    """Return dict of character -> count_of_issue_appearances from comic_characters table."""
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            rows = conn.execute(
                "SELECT character, count_of_issue_appearances FROM comic_characters "
                "WHERE count_of_issue_appearances IS NOT NULL"
            ).fetchall()
            conn.close()
            return {r[0]: r[1] for r in rows}
        except Exception:
            pass
    return {}


def render():
    page_header(
        kicker="Section 03",
        title="The Peter Parker Effect",
        subtitle="Why the alter ego is the asset — and what that means for the catalog."
    )

    prose("""
    <p>
    Superhero IP is frequently discussed as if the costume is the product. The cowl, the shield,
    the web-shooters. But the data keeps pointing somewhere else. Spider-Man has survived three
    complete continuity reboots, each one reset to a new creative team and origin story, and still
    holds the highest franchise box office floor in Marvel's solo-character catalog. Iron Man made
    $1.2 billion on sequel momentum. Spider-Man made $1.9 billion on nostalgia for a <em>person</em>.
    </p>
    <p>
    That distinction matters. The character audiences returned to in <em>No Way Home</em> was not a
    superhero. It was a kid from Queens who lost his aunt, his identity, and his mentor inside a
    single film, and still chose to do the right thing. Tobey Maguire and Andrew Garfield did not
    return to reprise Spider-Man. They returned to reprise Peter Parker. The costume was incidental.
    </p>
    <p>
    This page examines three angles on the same hypothesis: characters with deeply developed civilian
    identities perform better across formats, sustain higher audience investment through reboots,
    and generate a broader media footprint than characters whose civilian lives remain thin.
    Peter Parker is the clearest example in the catalog. He is also the strongest argument for
    what long-form comics writing actually produces.
    </p>
    """)

    df = load_box_office()

    # ── Section 1: Franchise box office floors ──────────────────────────────

    section_heading("The Franchise That Never Bottoms Out")

    prose("""
    <p>
    Every major Marvel franchise has been tested by a weak entry. The question is where the floor sits.
    A franchise whose worst film still earns $700M is a different asset than one whose worst film
    earns $370M. The chart below plots every film for Spider-Man, Iron Man, Captain America, and Thor
    against its year of release. Continuity reboots are annotated where they occur.
    </p>
    """)

    if not df.empty:
        fig1 = go.Figure()

        for franchise, color in FRANCHISE_COLORS.items():
            subset = df[df["character"] == franchise].sort_values("year")
            if subset.empty:
                continue

            # Main line + markers
            fig1.add_trace(go.Scatter(
                x=subset["year"],
                y=subset["worldwide_gross_m"],
                mode="lines+markers",
                name=franchise,
                line=dict(color=color, width=2.5),
                marker=dict(
                    color=color,
                    size=10,
                    symbol=FRANCHISE_SYMBOLS[franchise],
                    line=dict(width=1.5, color="#111"),
                ),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Year: %{x}<br>"
                    "Worldwide: $%{y}M<br>"
                    "RT: %{customdata[1]}%"
                    "<extra></extra>"
                ),
                customdata=list(zip(subset["film_title"], subset["rt_score"])),
            ))

        # Floor reference line: Spider-Man's lowest (ASM2, $709M)
        fig1.add_hline(
            y=709,
            line_dash="dash",
            line_color="#e23636",
            line_width=1,
            annotation_text="Spider-Man floor  $709M",
            annotation_font=dict(size=9, color="#e23636"),
            annotation_position="bottom right",
        )

        # Continuity reboot annotations
        for x_pos, label in [(2012, "Webb reboot"), (2017, "MCU reboot")]:
            fig1.add_vline(
                x=x_pos - 0.3,
                line_dash="dot",
                line_color="#555",
                line_width=1,
            )
            fig1.add_annotation(
                x=x_pos - 0.3, y=1850,
                text=label,
                showarrow=False,
                font=dict(size=9, color="#666"),
                xref="x", yref="y",
                textangle=-90,
                xanchor="right",
            )

        fig1.update_layout(**dict(PLOTLY_LAYOUT))
        fig1.update_layout(
            height=460,
            xaxis=dict(**AXIS_STYLE, title="Release Year", dtick=2),
            yaxis=dict(**AXIS_STYLE, title="Worldwide Gross ($M)", range=[250, 2050]),
            legend=dict(bgcolor="#111", bordercolor="#333", borderwidth=1, font=dict(size=11)),
            title=dict(
                text="Solo-Character Franchise Box Office: Film by Film",
                font=dict(size=14, color="#ccc"), x=0.0,
            ),
            margin=dict(t=50, b=55, l=75, r=40),
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Compute floors per franchise
        floors = df.groupby("character")["worldwide_gross_m"].min()
        sp_floor = floors.get("Spider-Man", 0)
        im_floor = floors.get("Iron Man", 0)
        cap_floor = floors.get("Captain America", 0)
        thor_floor = floors.get("Thor", 0)

        cv = load_cv_appearances()
        sp_appearances = cv.get("Spider-Man", 0)
        stat_cards([
            (f"${sp_floor:.0f}M",  "Spider-Man floor"),
            (f"${im_floor:.0f}M",  "Iron Man floor"),
            (f"${cap_floor:.0f}M", "Captain America floor"),
            (f"${thor_floor:.0f}M","Thor floor"),
            (f"{sp_appearances:,}" if sp_appearances else "17,970", "Spider-Man comic appearances"),
        ])

        chart_annotation(
            "Spider-Man's worst solo film ($709M, The Amazing Spider-Man 2) earns more than "
            "Iron Man's best opening film ($585M, Iron Man) and nearly doubles Captain America's "
            "lowest entry ($371M). The dashed line marks Spider-Man's floor. No other Marvel "
            "solo franchise clears it consistently. Two complete continuity reboots did not lower "
            "that floor. They raised the ceiling. The audience was not invested in a costume; "
            "they were invested in a person."
        )
    else:
        st.warning("Box office data not found. Expected: `data/franchise_boxoffice.csv`")

    data_note(
        "Data: Box office gross figures from Box Office Mojo / The Numbers, author-compiled. "
        "Note on Captain America: Civil War ($1,153M) and Iron Man 3 ($1,215M) are included "
        "for completeness but carry ensemble-cast caveats; Civil War features 12 MCU heroes. "
        "Solo-franchise floors are calculated on the minimum single-film gross for each character."
    )

    # ── Section 2: Civilian Story Index ─────────────────────────────────────

    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("The Civilian Story Index")

    prose("""
    <p>
    The question of <em>why</em> Peter Parker produces durable audience investment is not mysterious.
    Comic writers have been answering it since 1962. The mask comes off. The grades suffer.
    The rent is late. Aunt May gets sick. Every issue of <em>Amazing Spider-Man</em> spends
    meaningful page time on the person underneath the suit, and that person has enough texture
    to carry a story without the superpowers.
    </p>
    <p>
    The chart below estimates the proportion of narrative real estate devoted to the civilian
    identity across Marvel's most prominent solo franchises. The measure is qualitative by nature,
    drawn from a reading of major runs across each character's publication history. The range is wide.
    Thor, as a divine figure with no meaningful civilian existence in most continuities, anchors the
    low end. Spider-Man and Daredevil anchor the high end. The correlation with franchise durability
    is not accidental.
    </p>
    """)

    chars  = [r[0] for r in CIVILIAN_INDEX]
    scores = [r[1] for r in CIVILIAN_INDEX]
    notes  = [r[2] for r in CIVILIAN_INDEX]

    bar_colors = []
    for c in chars:
        bar_colors.append(FRANCHISE_COLORS.get(c, "#888888"))

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=scores,
        y=chars,
        orientation="h",
        marker=dict(
            color=bar_colors,
            line=dict(color="#111", width=1.5),
        ),
        text=[f"{s}%" for s in scores],
        textposition="outside",
        textfont=dict(size=12, color="#ccc"),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Civilian narrative share: %{x}%<br>"
            "%{customdata}"
            "<extra></extra>"
        ),
        customdata=notes,
    ))

    fig2.update_layout(**dict(PLOTLY_LAYOUT))
    fig2.update_layout(
        height=340,
        xaxis=dict(
            **AXIS_STYLE,
            title="Estimated % of Narrative Devoted to Civilian Identity",
            range=[0, 75],
        ),
        yaxis=dict(**AXIS_STYLE),
        title=dict(
            text="Civilian Story Index: How Much Page Time Does the Person Get?",
            font=dict(size=14, color="#ccc"), x=0.0,
        ),
        margin=dict(t=50, b=55, l=160, r=60),
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

    chart_annotation(
        "Spider-Man devotes more narrative space to its civilian lead than any other major "
        "Marvel solo franchise. Hulk / Banner is a notable second, but Bruce Banner's civilian "
        "arc has never generated the same franchise durability. The key difference is that "
        "Peter Parker's civilian story is emotionally continuous across decades of publication: "
        "one person, aging, losing, failing, and persisting. Banner's narrative is episodic. "
        "Parker's is cumulative."
    )

    data_note(
        "Author estimate based on sampling of major runs for each character. "
        "Civilian narrative share reflects proportion of story pages or screen time "
        "spent outside the hero persona (unmasked, in civilian setting, non-combat). "
        "This metric is inherently subjective; exact figures should be treated as "
        "directionally accurate rather than precisely measured."
    )

    # ── Section 3: Media Format Breadth ─────────────────────────────────────

    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("Sixty Years of Continuous Presence")

    prose("""
    <p>
    Audience investment produces licensing opportunity. A character with broad emotional
    resonance migrates into more formats, sustains those formats longer, and returns to
    them repeatedly after periods of dormancy. The chart below counts distinct solo media
    appearances by format across five major Marvel characters, from the 1960s through 2024.
    </p>
    <p>
    Spider-Man's lead in animated series alone accounts for more entries than several
    characters' total media footprints. The video game catalog is deeper. The live-action
    library is wider. This is not purely a function of age: Hulk debuted the same year as
    Spider-Man and has a fraction of the format breadth. The differentiator is not
    first-appearance date. It is how much the audience cares about the person behind the mask.
    </p>
    """)

    mf = MEDIA_FORMATS
    characters = mf["character"]
    format_keys = ["Animated Series", "Live-Action TV", "Feature Films", "Video Games", "Other Media"]
    format_colors = ["#5b8dbf", "#6fbf7a", "#e23636", "#e8b84b", "#9b7fc4"]

    fig3 = go.Figure()
    for fmt, color in zip(format_keys, format_colors):
        fig3.add_trace(go.Bar(
            name=fmt,
            x=characters,
            y=mf[fmt],
            marker_color=color,
            marker_line=dict(color="#111", width=1),
            hovertemplate=(
                "<b>%{x}</b><br>"
                f"{fmt}: %{{y}} titles"
                "<extra></extra>"
            ),
        ))

    fig3.update_layout(**dict(PLOTLY_LAYOUT))
    fig3.update_layout(
        height=420,
        barmode="stack",
        xaxis=dict(**AXIS_STYLE),
        yaxis=dict(**AXIS_STYLE, title="Distinct Solo Media Titles"),
        legend=dict(bgcolor="#111", bordercolor="#333", borderwidth=1, font=dict(size=11)),
        title=dict(
            text="Solo Media Footprint by Format (1960s – 2024)",
            font=dict(size=14, color="#ccc"), x=0.0,
        ),
        margin=dict(t=50, b=55, l=60, r=40),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Totals for stat cards
    totals = {c: sum(mf[fmt][i] for fmt in format_keys) for i, c in enumerate(characters)}
    stat_cards([
        (str(totals["Spider-Man"]),      "Spider-Man total titles"),
        (str(totals["Iron Man"]),        "Iron Man total titles"),
        (str(totals["Captain America"]), "Cap. America total titles"),
        (str(totals["Thor"]),            "Thor total titles"),
        (str(totals["Hulk"]),            "Hulk total titles"),
    ])

    chart_annotation(
        "Spider-Man's total media footprint is more than double Iron Man's and more than "
        "triple Thor's. The animated series count alone (12 distinct shows) spans every decade "
        "from the 1960s through the 2020s. Video games add another 21+ solo titles. "
        "Hulk's comparatively thin footprint is instructive: a character introduced the same "
        "year, with similar name recognition, has not generated the same licensing depth. "
        "The difference is Peter Parker. A billionaire in a suit and an angry green giant "
        "are compelling. A teenager from Queens who can't pay his bills is <em>relatable</em>."
    )

    data_note(
        "Data: Author-compiled from Marvel wikia, IMDB, and MobyGames (April 2025). "
        "Counts reflect distinct solo-titled or co-starring-lead media where the character "
        "is a primary protagonist. Team appearances (Avengers films, crossover games) are "
        "excluded. Spider-Man feature film count of 10 includes: Raimi trilogy (2002–07), "
        "Webb duology (2012–14), MCU trilogy (2017–21), and Spider-Verse animated features "
        "(Into the Spider-Verse 2018, Across the Spider-Verse 2023). "
        "Video game counts include major console/PC releases; mobile-only titles excluded."
    )

    # ── Closing section ──────────────────────────────────────────────────────

    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("What This Means for the Catalog")

    prose("""
    <p>
    The case for long-form comic writing is not purely aesthetic. A writer given five years with
    Peter Parker will spend that time deepening the civilian side of the character: new supporting
    cast, new failures, new reasons the audience should care about the person who happens to have
    superpowers. A writer given eighteen months before the title is relaunched will spend that time
    on plot. The villain, the arc, the costume redesign. What gets cut is the part that generates
    durable investment.
    </p>
    <p>
    The box office floor, the civilian story index, and the media breadth chart are all measuring
    the same thing from different angles. Characters with deep civilian identities built through
    years of continuous narrative development are worth more. They command higher floors. They
    migrate into more formats. They sustain audience investment through reboots that would kill
    a property built only on the costume.
    </p>
    <p>
    Spider-Man has been relaunched more times than almost any Marvel character. He keeps landing.
    The reason is not the web-shooters. It is that sixty years of writers, most of whom were given
    enough time to actually develop a story, built a person that audiences feel they know.
    That is the asset. That is what the relaunch schedule erodes.
    </p>
    """)

    pull_quote(
        "The costume is the product they sell. "
        "The person underneath is the reason anyone buys it."
    )
