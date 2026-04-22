import sqlite3
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from src.utils.styling import (
    page_header, prose, pull_quote, chart_annotation, section_heading, data_note,
    PLOTLY_LAYOUT, AXIS_STYLE
)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "marvel.db"

ERA_COLORS = {
    "Golden Age":   "#f5c842",
    "Silver Age":   "#e8b84b",
    "Bronze Age":   "#b07d3e",
    "Copper Age":   "#c97c4e",
    "Modern Age":   "#5b8dbf",
    "Contemporary": "#e23636",
}

ERA_ORDER = ["Golden Age", "Silver Age", "Bronze Age", "Copper Age", "Modern Age", "Contemporary"]

CHARACTER_EMOJI = {
    "Captain America":          "🛡",
    "Iron Man":                 "⚙",
    "Thor":                     "⚡",
    "Hulk":                     "💚",
    "Spider-Man":               "🕷",
    "Doctor Strange":           "✨",
    "Black Panther":            "🐾",
    "Star-Lord":                "🚀",
    "Thanos":                   "🧤",
    "Rocket Raccoon":           "🦝",
    "Groot":                    "🌿",
    "Winter Soldier":           "🦾",
    "Ms. Marvel (Kamala Khan)": "⭐",
    "Ironheart":                "🔩",
    "Loki":                     "🐍",
    "Vision":                   "🤖",
    "Shang-Chi":                "🥋",
    "Hawkeye":                  "🏹",
    "America Chavez":           "⭐",
    "Valkyrie":                 "⚔",
    "Moon Knight":              "🌙",
    "Scarlet Witch":            "🔮",
    "Captain Marvel":          "✦",
    "Daredevil":               "⚖",
}

CHARACTER_DATA = [
    # Golden Age
    {"character": "Captain America",        "first_year": 1941, "mcu_year": 2011, "era": "Golden Age",   "role": "Lead",       "creator": "Joe Simon & Jack Kirby",      "source_run": "Brubaker's 65-issue run (2005–09)"},
    # Silver Age
    {"character": "Iron Man",               "first_year": 1963, "mcu_year": 2008, "era": "Silver Age",   "role": "Lead",       "creator": "Stan Lee & Jack Kirby",        "source_run": "Michelinie/Layton run (1979–82)"},
    {"character": "Thor",                   "first_year": 1962, "mcu_year": 2011, "era": "Silver Age",   "role": "Lead",       "creator": "Stan Lee & Jack Kirby",        "source_run": "Walt Simonson's 37-issue run (1983–87)"},
    {"character": "Hulk",                   "first_year": 1962, "mcu_year": 2008, "era": "Silver Age",   "role": "Lead",       "creator": "Stan Lee & Jack Kirby",        "source_run": "Peter David's 12-year run (1987–98)"},
    {"character": "Spider-Man",             "first_year": 1962, "mcu_year": 2016, "era": "Silver Age",   "role": "Lead",       "creator": "Stan Lee & Steve Ditko",       "source_run": "Lee/Ditko + Conway + Michelinie runs"},
    {"character": "Doctor Strange",         "first_year": 1963, "mcu_year": 2016, "era": "Silver Age",   "role": "Lead",       "creator": "Stan Lee & Steve Ditko",       "source_run": "Ditko's Strange Tales run (1963–66)"},
    {"character": "Black Panther",          "first_year": 1966, "mcu_year": 2016, "era": "Silver Age",   "role": "Lead",       "creator": "Stan Lee & Jack Kirby",        "source_run": "Christopher Priest's 62-issue run (1998–2003)"},
    {"character": "Scarlet Witch",          "first_year": 1964, "mcu_year": 2015, "era": "Silver Age",   "role": "Lead",       "creator": "Stan Lee & Jack Kirby",        "source_run": "House of M + Vision arcs"},
    {"character": "Captain Marvel",         "first_year": 1968, "mcu_year": 2019, "era": "Silver Age",   "role": "Lead",       "creator": "Roy Thomas & Gene Colan",      "source_run": "Kelly Sue DeConnick's run (2012–14)"},
    {"character": "Loki",                   "first_year": 1962, "mcu_year": 2011, "era": "Silver Age",   "role": "Supporting", "creator": "Stan Lee & Jack Kirby",        "source_run": "Journey into Mystery (Gillen, 2011–12)"},
    {"character": "Nick Fury",              "first_year": 1963, "mcu_year": 2008, "era": "Silver Age",   "role": "Supporting", "creator": "Stan Lee & Jack Kirby",        "source_run": "Sgt. Fury + Steranko's run"},
    {"character": "Hawkeye",                "first_year": 1964, "mcu_year": 2011, "era": "Silver Age",   "role": "Supporting", "creator": "Stan Lee & Don Heck",          "source_run": "Matt Fraction's run (2012–15)"},
    {"character": "Black Widow",            "first_year": 1964, "mcu_year": 2010, "era": "Silver Age",   "role": "Supporting", "creator": "Stan Lee & Don Rico",          "source_run": "Various key arcs"},
    {"character": "Falcon",                 "first_year": 1969, "mcu_year": 2014, "era": "Silver Age",   "role": "Supporting", "creator": "Stan Lee & Gene Colan",        "source_run": "Co-billed in Captain America"},
    {"character": "Kang the Conqueror",     "first_year": 1963, "mcu_year": 2021, "era": "Silver Age",   "role": "Supporting", "creator": "Stan Lee & Jack Kirby",        "source_run": "Avengers vol. 1 + Kang Dynasty"},
    {"character": "Vision",                 "first_year": 1968, "mcu_year": 2015, "era": "Silver Age",   "role": "Supporting", "creator": "Roy Thomas",                   "source_run": "Avengers + Tom King's Vision (2015–16)"},
    {"character": "Hela",                   "first_year": 1964, "mcu_year": 2017, "era": "Silver Age",   "role": "Supporting", "creator": "Stan Lee & Jack Kirby",        "source_run": "Thor mythology arcs"},
    {"character": "Wasp",                   "first_year": 1963, "mcu_year": 2018, "era": "Silver Age",   "role": "Supporting", "creator": "Stan Lee & Jack Kirby",        "source_run": "Founding Avenger"},
    {"character": "Groot",                  "first_year": 1960, "mcu_year": 2014, "era": "Silver Age",   "role": "Supporting", "creator": "Stan Lee & Jack Kirby",        "source_run": "Annihilation: Conquest"},
    # Bronze Age
    {"character": "Star-Lord",              "first_year": 1976, "mcu_year": 2014, "era": "Bronze Age",   "role": "Lead",       "creator": "Steve Englehart",              "source_run": "DnA Guardians of the Galaxy (2008–10)"},
    {"character": "Shang-Chi",              "first_year": 1973, "mcu_year": 2021, "era": "Bronze Age",   "role": "Lead",       "creator": "Steve Englehart",              "source_run": "Master of Kung Fu original series (1974–83)"},
    {"character": "Moon Knight",            "first_year": 1975, "mcu_year": 2022, "era": "Bronze Age",   "role": "Lead",       "creator": "Doug Moench",                  "source_run": "Moench original + Warren Ellis run (2014)"},
    {"character": "Thanos",                 "first_year": 1973, "mcu_year": 2018, "era": "Bronze Age",   "role": "Supporting", "creator": "Jim Starlin",                  "source_run": "Starlin's Infinity Gauntlet trilogy"},
    {"character": "Gamora",                 "first_year": 1975, "mcu_year": 2014, "era": "Bronze Age",   "role": "Supporting", "creator": "Jim Starlin",                  "source_run": "Starlin's cosmic run + Guardians"},
    {"character": "Drax",                   "first_year": 1973, "mcu_year": 2014, "era": "Bronze Age",   "role": "Supporting", "creator": "Jim Starlin",                  "source_run": "Annihilation + Guardians"},
    {"character": "Rocket Raccoon",         "first_year": 1976, "mcu_year": 2014, "era": "Bronze Age",   "role": "Supporting", "creator": "Bill Mantlo",                  "source_run": "DnA Guardians of the Galaxy (2008–10)"},
    {"character": "Mantis",                 "first_year": 1973, "mcu_year": 2017, "era": "Bronze Age",   "role": "Supporting", "creator": "Steve Englehart",              "source_run": "Avengers Celestial Madonna arc"},
    {"character": "Valkyrie",               "first_year": 1970, "mcu_year": 2017, "era": "Bronze Age",   "role": "Supporting", "creator": "Roy Thomas",                   "source_run": "Defenders + Thor mythology"},
    {"character": "War Machine",            "first_year": 1979, "mcu_year": 2010, "era": "Bronze Age",   "role": "Supporting", "creator": "David Michelinie",             "source_run": "Iron Man supporting cast"},
    # Copper Age
    {"character": "Nebula",                 "first_year": 1985, "mcu_year": 2014, "era": "Copper Age",   "role": "Supporting", "creator": "Roger Stern",                  "source_run": "Avengers + Infinity Gauntlet"},
    {"character": "Ant-Man (Scott Lang)",   "first_year": 1979, "mcu_year": 2015, "era": "Bronze Age",   "role": "Lead",       "creator": "David Michelinie",             "source_run": "Marvel Premiere (1979) + Avengers"},
    {"character": "Daredevil",             "first_year": 1964, "mcu_year": 2015, "era": "Silver Age",   "role": "Lead",       "creator": "Stan Lee & Bill Everett",      "source_run": "Frank Miller's run (1979–83); Bendis/Maleev (2001–06)"},
    # Modern Age
    {"character": "Winter Soldier",         "first_year": 2005, "mcu_year": 2014, "era": "Modern Age",   "role": "Supporting", "creator": "Ed Brubaker",                  "source_run": "Brubaker's Captain America (2005–12)"},
    {"character": "Okoye",                  "first_year": 1998, "mcu_year": 2018, "era": "Modern Age",   "role": "Supporting", "creator": "Christopher Priest",           "source_run": "Priest's Black Panther (1998–2003)"},
    {"character": "Shuri",                  "first_year": 2005, "mcu_year": 2018, "era": "Modern Age",   "role": "Supporting", "creator": "Reginald Hudlin",              "source_run": "Black Panther vol. 4"},
    # Contemporary
    {"character": "Ms. Marvel (Kamala Khan)", "first_year": 2013, "mcu_year": 2022, "era": "Contemporary", "role": "Lead",     "creator": "G. Willow Wilson",             "source_run": "Ms. Marvel vol. 1 (2014–15)"},
    {"character": "America Chavez",         "first_year": 2011, "mcu_year": 2022, "era": "Contemporary", "role": "Supporting", "creator": "Joe Casey & Nick Dragotta",    "source_run": "Vengeance (2011), one miniseries"},
    {"character": "Ironheart",              "first_year": 2016, "mcu_year": 2022, "era": "Contemporary", "role": "Lead",       "creator": "Brian Michael Bendis",         "source_run": "Invincible Iron Man vol. 3 (2016)"},
]


def render():
    page_header(
        kicker="Section 05",
        title="The Character Ledger",
        subtitle="Every major MCU character, ranked by how long their story had to develop before the cameras rolled."
    )

    prose("""
    <p>
    The MCU did not invent its characters. It inherited them from sixty years of comics written
    by people who were given the time and editorial support to develop them fully. Iron Man was
    45 years old when Robert Downey Jr. put on the suit. Captain America was 70. Doctor Strange
    was 53. The characters that built a $30 billion franchise were not created for the MCU.
    They were handed to the MCU after decades of accumulated story, villain mythology, supporting
    casts, and emotional logic had been built up in print.
    </p>
    <p>
    The chart below is a ledger of that inheritance. Each bar represents a major MCU character,
    ranked by how many years passed between their first comic appearance and their MCU debut.
    The color shows which publishing era produced them.
    </p>
    <p>
    Read it from the top. Then read it from the bottom.
    </p>
    """)

    df = pd.DataFrame(CHARACTER_DATA)
    df["years_developed"] = df["mcu_year"] - df["first_year"]
    df = df.sort_values("years_developed", ascending=True)

    # --- Chart 1: Development Lead Time (The Hero Chart) ---
    section_heading("Years from First Comic Appearance to MCU Debut")

    fig1 = go.Figure()

    for _, row in df.iterrows():
        color = ERA_COLORS.get(row["era"], "#888")
        emoji = CHARACTER_EMOJI.get(row["character"], "")
        label = f"{emoji} {row['character']}" if emoji else row["character"]
        fig1.add_trace(go.Bar(
            x=[row["years_developed"]],
            y=[label],
            orientation="h",
            marker_color=color,
            marker_opacity=0.9,
            name=row["era"],
            legendgroup=row["era"],
            showlegend=False,
            text=f"  {row['years_developed']} yrs",
            textposition="outside",
            textfont=dict(size=9, color="#888"),
            hovertemplate=(
                f"<b>{emoji} {row['character']}</b><br>"
                f"First appeared: {row['first_year']}<br>"
                f"MCU debut: {row['mcu_year']}<br>"
                f"Years developed: {row['years_developed']}<br>"
                f"Era: {row['era']}<br>"
                f"Creator: {row['creator']}<br>"
                f"Key run: {row['source_run']}"
                "<extra></extra>"
            ),
        ))

    # Era legend using paper coordinates
    for i, (era, color) in enumerate(ERA_COLORS.items()):
        fig1.add_annotation(
            x=1.01, y=1.0 - i * 0.08,
            xref="paper", yref="paper",
            text=f"● {era}",
            showarrow=False,
            font=dict(size=10, color=color),
            xanchor="left",
        )

    fig1.update_layout(**dict(PLOTLY_LAYOUT))
    fig1.update_layout(
        height=980,
        xaxis=dict(**AXIS_STYLE, title="Years from First Comic Appearance to MCU Debut", range=[0, 82]),
        yaxis=dict(**AXIS_STYLE, autorange=True),
        margin=dict(t=40, b=50, l=240, r=130),
        title=dict(
            text="MCU Characters: Years of Story Development Before Filming",
            font=dict(size=14, color="#ccc"), x=0.0,
        ),
        showlegend=False,
    )

    st.plotly_chart(fig1, use_container_width=True)

    chart_annotation(
        "The top of this chart is the foundation of the MCU. Captain America: 70 years. "
        "Kang: 58. Doctor Strange: 53. Groot: 54. "
        "The characters at the top of the chart arrived at the MCU with decades of comics-built mythology, "
        "deep villain histories, earned emotional arcs, and a reader base that already loved them. "
        "Now look at the bottom. Winter Soldier: 9 years (Ed Brubaker's character, genuinely exceptional). "
        "Ms. Marvel: 9 years. America Chavez: 11 years. Ironheart: 6 years. "
        "These are characters being developed for the screen at the same time "
        "they're being developed on the page. That's a very short runway to build something lasting, "
        "and it's worth asking what those characters might become with more time."
    )

    # --- Chart 2: MCU Characters by Era of Comic Origin ---
    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("Where Did the MCU's Characters Come From?")

    era_counts = df.groupby(["era", "role"]).size().reset_index(name="count")
    era_counts["era"] = pd.Categorical(era_counts["era"], categories=ERA_ORDER, ordered=True)
    era_counts = era_counts.sort_values("era")

    fig2 = go.Figure()
    for role, pattern in [("Lead", ""), ("Supporting", "/")]:
        subset = era_counts[era_counts["role"] == role]
        counts_by_era = subset.set_index("era")["count"].reindex(ERA_ORDER, fill_value=0)
        fig2.add_trace(go.Bar(
            x=ERA_ORDER,
            y=counts_by_era.values,
            name=role,
            marker_color=[ERA_COLORS[e] for e in ERA_ORDER],
            marker_opacity=0.9 if role == "Lead" else 0.45,
            marker_pattern_shape="" if role == "Lead" else "/",
            hovertemplate=(
                f"<b>%{{x}}</b>, {role}<br>"
                "Characters: %{y}"
                "<extra></extra>"
            ),
            text=counts_by_era.values,
            textposition="inside",
            textfont=dict(size=11, color="#fff"),
        ))

    fig2.update_layout(
        **dict(PLOTLY_LAYOUT),
        height=380,
        barmode="stack",
        xaxis=dict(**AXIS_STYLE, title="Comic Book Era"),
        yaxis=dict(**AXIS_STYLE, title="Number of MCU Characters"),
        legend=dict(bgcolor="#111", bordercolor="#333", borderwidth=1, font=dict(size=11)),
        title=dict(
            text="MCU Characters by Comic Era of Origin (Lead vs. Supporting)",
            font=dict(size=14, color="#ccc"), x=0.0,
        ),
    )
    st.plotly_chart(fig2, use_container_width=True)

    chart_annotation(
        "Silver Age alone accounts for more than half of all tracked MCU characters. "
        "Bronze Age adds another significant cluster, including Jim Starlin's cosmic characters, "
        "Steve Englehart's work, and Roy Thomas's contributions. "
        "Contemporary (2010+) characters are present but small, and they're the ones "
        "being deployed into films with the least accumulated story depth. "
        "The Silver and Bronze Age characters are not infinite. They are a fixed inventory "
        "that is being drawn down."
    )

    # --- Chart 3: Scatter (First Appearance Year vs. Years Developed) ---
    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("The Compression Is Accelerating")

    fig3 = go.Figure()
    for era in ERA_ORDER:
        subset = df[df["era"] == era]
        if subset.empty:
            continue
        emoji_labels = [CHARACTER_EMOJI.get(c, "·") for c in subset["character"]]
        fig3.add_trace(go.Scatter(
            x=subset["first_year"],
            y=subset["years_developed"],
            mode="markers+text",
            name=era,
            marker=dict(
                color=ERA_COLORS[era],
                size=13,
                opacity=0.85,
                line=dict(width=1, color="#222"),
            ),
            text=emoji_labels,
            textposition="top center",
            textfont=dict(size=14),
            customdata=subset["character"],
            hovertemplate=(
                "<b>%{customdata}</b><br>"
                "First appeared: %{x}<br>"
                "Years developed: %{y}<br>"
                "<extra></extra>"
            ),
        ))

    # Add a trend annotation line (visual only)
    fig3.add_annotation(
        x=1975, y=15,
        text="Characters created after 1990<br>average under 20 years of<br>story development at MCU debut",
        showarrow=True,
        arrowhead=2,
        ax=80,
        ay=-40,
        font=dict(size=10, color="#888"),
        arrowcolor="#555",
    )

    fig3.update_layout(
        **dict(PLOTLY_LAYOUT),
        height=420,
        xaxis=dict(**AXIS_STYLE, title="Year of First Comic Appearance", range=[1935, 2020]),
        yaxis=dict(**AXIS_STYLE, title="Years Developed Before MCU Debut", range=[-2, 80]),
        legend=dict(bgcolor="#111", bordercolor="#333", borderwidth=1, font=dict(size=11)),
        title=dict(
            text="First Appearance Year vs. Years of Story Development at MCU Debut",
            font=dict(size=14, color="#ccc"), x=0.0,
        ),
    )
    st.plotly_chart(fig3, use_container_width=True)

    chart_annotation(
        "Characters created in the 1960s and 70s arrived at the MCU with 40–70 years of story capital. "
        "Characters created in the 1990s and 2000s arrived with 10–30 years. "
        "Characters created in the 2010s arrived with under 12. "
        "This is not a coincidence. It is the direct result of a publishing model that has spent "
        "25 years relaunching existing titles instead of investing in new long-form character development. "
        "Building the next Black Panther, the next Guardians of the Galaxy, "
        "the next Iron Man takes a decade of committed writing to make feel real. "
        "The characters at the bottom of this chart are at the beginning of that journey. "
        "The question is how much runway they'll be given to finish it."
    )

    # --- Chart 4: Issue Appearance Count from ComicVine ---
    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("Story Capital: Total Comic Issue Appearances")

    cv_df = None
    try:
        if DB_PATH.exists():
            conn = sqlite3.connect(DB_PATH)
            cv_df = pd.read_sql_query(
                "SELECT character, count_of_issue_appearances "
                "FROM comic_characters "
                "WHERE count_of_issue_appearances IS NOT NULL "
                "ORDER BY count_of_issue_appearances ASC",
                conn,
            )
            conn.close()
    except Exception:
        cv_df = None

    if cv_df is not None and not cv_df.empty:
        # Color bars: highlight the outlier tiers
        def bar_color(count):
            if count >= 10000:
                return "#e23636"    # red — dominant
            elif count >= 5000:
                return "#e8b84b"    # gold — deep
            elif count >= 2000:
                return "#5b8dbf"    # blue — established
            else:
                return "#555"       # grey — limited

        colors = [bar_color(c) for c in cv_df["count_of_issue_appearances"]]
        emoji_labels = [CHARACTER_EMOJI.get(c, "") for c in cv_df["character"]]
        display_labels = [
            f"{e} {c}" if e else c
            for e, c in zip(emoji_labels, cv_df["character"])
        ]

        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=cv_df["count_of_issue_appearances"],
            y=display_labels,
            orientation="h",
            marker_color=colors,
            marker_opacity=0.9,
            text=[f"  {v:,}" for v in cv_df["count_of_issue_appearances"]],
            textposition="outside",
            textfont=dict(size=9, color="#888"),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Issue appearances: %{x:,}"
                "<extra></extra>"
            ),
        ))

        # Tier reference lines
        for threshold, label in [(2000, "2,000"), (5000, "5,000"), (10000, "10,000")]:
            fig4.add_vline(
                x=threshold,
                line_width=1,
                line_dash="dot",
                line_color="#444",
                annotation_text=label,
                annotation_position="top",
                annotation_font=dict(size=9, color="#555"),
            )

        fig4.update_layout(
            **dict(PLOTLY_LAYOUT),
            height=520,
            xaxis=dict(**AXIS_STYLE, title="Total Issue Appearances (ComicVine)", range=[0, 21000]),
            yaxis=dict(**AXIS_STYLE, autorange=True),
            margin=dict(t=40, b=50, l=240, r=100),
            title=dict(
                text="MCU Characters by Total Comic Issue Appearances",
                font=dict(size=14, color="#ccc"), x=0.0,
            ),
            showlegend=False,
        )
        st.plotly_chart(fig4, use_container_width=True)

        chart_annotation(
            "Spider-Man has appeared in 17,970 tracked issues — nearly 6,000 more than "
            "Captain America (12,218), and more than five times Iron Man (11,699). "
            "Black Panther, at 3,612, has substantial depth by any reasonable measure. "
            "Contrast that with Star-Lord (908), Thanos (1,323), and Rocket Raccoon (1,102). "
            "These characters are not thin — but they are drawing on a much shallower well. "
            "When the MCU adapts them, it is working from a shorter source text. "
            "Issue appearance volume is a proxy for narrative depth: the more issues a character "
            "has anchored, the richer the mythology of villains, supporting casts, and earned arcs "
            "available to screenwriters."
        )
    else:
        prose("<p><em>Appearance data unavailable. Run <code>python scripts/ingest.py</code> to populate.</em></p>")

    cv_fetch_date = "N/A"
    if DB_PATH.exists():
        try:
            _conn = sqlite3.connect(DB_PATH)
            _row = _conn.execute("SELECT MAX(fetched_at) FROM comic_characters").fetchone()
            _conn.close()
            if _row and _row[0]:
                cv_fetch_date = _row[0][:10]
        except Exception:
            pass

    data_note(
        "MCU debut dates: first theatrical or confirmed Disney+ appearance. "
        "First appearance years: first comic publication per Marvel's records. "
        "Winter Soldier listed at 2005 (Ed Brubaker's creation of the identity/arc), "
        "not 1941 (Bucky Barnes first appearance), as the MCU story drew from Brubaker's run. "
        f"Issue appearance counts via ComicVine API (pulled {cv_fetch_date}). "
        "Character list is representative, not exhaustive. Author-compiled from published Marvel records."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    prose("""
    <p>
    The argument is not that newer characters cannot be good. Ms. Marvel is a genuinely excellent
    character, well-written, culturally resonant, with a strong authorial voice behind her creation.
    The argument is structural: the MCU's ability to adapt characters at the level it adapted
    <em>The Winter Soldier</em>, <em>Black Panther</em>, and <em>Guardians of the Galaxy</em>
    depends on those characters having the story depth those adaptations required. Brubaker's Captain America
    run existed. Christopher Priest's Black Panther run existed. Abnett and Lanning's Guardians run existed.
    </p>
    <p>
    Those runs exist because the writers behind them were given the tenure and editorial support to
    finish what they started. The current publishing model does not provide that support.
    It provides 18-month windows, crossover obligations, and relaunch announcements.
    The characters being created under those conditions are not getting the development time
    that made the MCU's best films possible.
    </p>
    <p>
    Section 03 showed the compression in writer tenure. This section shows what that compression costs
    in the currency the MCU actually runs on: story depth. Section 06 shows what the data above looks like
    on a balance sheet.
    </p>
    """)

    pull_quote(
        "The characters at the top of that chart, the ones with 40, 50, 60 years of development, "
        "are a remarkable inheritance. "
        "What Marvel is writing today is what the next generation of storytellers will have to work with. "
        "There is still time to build something just as rich."
    )
