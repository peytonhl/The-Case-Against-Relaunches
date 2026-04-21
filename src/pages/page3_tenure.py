import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.utils.styling import (
    page_header, prose, pull_quote, chart_annotation, section_heading, data_note,
    stat_cards, PLOTLY_LAYOUT, AXIS_STYLE
)

WRITER_DATA = [
    {"writer": "Stan Lee",                  "start_year": 1963, "end_year": 1972, "issues": 110, "years": 9,  "era": "Silver Age"},
    {"writer": "Gerry Conway",              "start_year": 1972, "end_year": 1975, "issues": 40,  "years": 3,  "era": "Bronze Age"},
    {"writer": "Len Wein",                  "start_year": 1975, "end_year": 1976, "issues": 8,   "years": 1,  "era": "Bronze Age"},
    {"writer": "Marv Wolfman",              "start_year": 1976, "end_year": 1980, "issues": 36,  "years": 4,  "era": "Bronze Age"},
    {"writer": "Denny O'Neil",              "start_year": 1980, "end_year": 1982, "issues": 18,  "years": 2,  "era": "Bronze Age"},
    {"writer": "Roger Stern",               "start_year": 1982, "end_year": 1984, "issues": 29,  "years": 2,  "era": "Copper Age"},
    {"writer": "Tom DeFalco",               "start_year": 1984, "end_year": 1987, "issues": 36,  "years": 3,  "era": "Copper Age"},
    {"writer": "J.M. DeMatteis",            "start_year": 1987, "end_year": 1988, "issues": 12,  "years": 1,  "era": "Copper Age"},
    {"writer": "David Michelinie",          "start_year": 1988, "end_year": 1993, "issues": 93,  "years": 5,  "era": "Copper Age"},
    {"writer": "J.M. DeMatteis (2nd run)",  "start_year": 1993, "end_year": 1994, "issues": 20,  "years": 1,  "era": "90s"},
    {"writer": "Howard Mackie",             "start_year": 1994, "end_year": 2001, "issues": 55,  "years": 7,  "era": "90s"},
    {"writer": "J. Michael Straczynski",    "start_year": 2001, "end_year": 2007, "issues": 73,  "years": 6,  "era": "2000s"},
    {"writer": "Brand New Day (rotating)",  "start_year": 2008, "end_year": 2010, "issues": 25,  "years": 2,  "era": "Modern"},
    {"writer": "Dan Slott",                 "start_year": 2010, "end_year": 2018, "issues": 153, "years": 8,  "era": "Modern"},
    {"writer": "Nick Spencer",              "start_year": 2018, "end_year": 2021, "issues": 74,  "years": 3,  "era": "Modern"},
    {"writer": "Zeb Wells",                 "start_year": 2022, "end_year": 2024, "issues": 40,  "years": 2,  "era": "Modern"},
]

ERA_COLORS = {
    "Silver Age":  "#e8b84b",
    "Bronze Age":  "#b07d3e",
    "Copper Age":  "#c97c4e",
    "90s":         "#9e6b8a",
    "2000s":       "#5b8dbf",
    "Modern":      "#e23636",
}

LANDMARK_RUNS = {
    "David Michelinie":       "Created Venom & Carnage",
    "J. Michael Straczynski": "Created Morlun; redefining run",
    "Dan Slott":              "Superior Spider-Man; longest modern run",
    "Nick Spencer":           "Spider-Man/Peter Parker identity arc",
}


def render():
    page_header(
        kicker="Section 03",
        title="Writer Tenure Analysis",
        subtitle="Amazing Spider-Man, 1963 – 2024: how long creators were trusted to tell a story."
    )

    st.markdown(
        '<div style="font-size:4rem;text-align:center;margin:0.5rem 0 1.5rem;opacity:0.15;'
        'letter-spacing:0.5rem;">🕷 🕷 🕷</div>',
        unsafe_allow_html=True
    )

    prose("""
    <p>
    The chart below is a sixty-year record of run length on <em>Amazing Spider-Man</em>.
    Each bar represents a single writer's primary run, ordered chronologically from Stan Lee's
    1963 launch to the present. Bar length equals issues written. The color indicates the publishing era.
    </p>
    <p>
    Writer change frequency is roughly similar across eras — the 1980s actually had more new writers
    per decade than the 2010s. What has changed is the mechanism behind the changes.
    Most historical transitions were organic: a writer finished their story and moved on, or editorial
    decided to try something new. Since 2018, each transition has been driven by a full series relaunch —
    the title cancelled, the numbering reset to #1, a new creative team starting fresh.
    That structural difference is what this data is about.
    </p>
    """)

    df = pd.DataFrame(WRITER_DATA)
    df = df.sort_values("start_year", ascending=True)

    # --- Chart 1: Horizontal bar by issues written ---
    section_heading("Issues Written per Primary Run")

    fig = go.Figure()

    for era in ERA_COLORS:
        era_df = df[df["era"] == era]
        for _, row in era_df.iterrows():
            color = ERA_COLORS[row["era"]]
            opacity = 0.5 if row["writer"] == "Brand New Day (rotating)" else 1.0
            landmark = LANDMARK_RUNS.get(row["writer"], "")
            landmark_str = f"<i>{landmark}</i><br>" if landmark else ""
            era_str = str(row["era"])
            hover = (
                f"<b>{row['writer']}</b><br>"
                f"{row['start_year']}-{row['end_year']}<br>"
                f"{row['issues']} issues | {row['years']} years<br>"
                f"{landmark_str}"
                f"Era: {era_str}"
                f"<extra></extra>"
            )
            fig.add_trace(go.Bar(
                x=[row["issues"]],
                y=[f"{row['writer']} ({row['start_year']})"],
                orientation="h",
                marker_color=color,
                marker_opacity=opacity,
                text=f"  {row['issues']} issues",
                textposition="outside",
                textfont=dict(size=10, color="#888"),
                hovertemplate=hover,
                showlegend=False,
            ))

    # Era legend using paper coordinates so it doesn't collide with bars
    for i, (era, color) in enumerate(ERA_COLORS.items()):
        fig.add_annotation(
            x=1.01, y=1.0 - i * 0.09,
            xref="paper", yref="paper",
            text=f"● {era}",
            showarrow=False,
            font=dict(size=10, color=color),
            xanchor="left",
        )

    fig.update_layout(**dict(PLOTLY_LAYOUT))
    fig.update_layout(
        height=620,
        barmode="overlay",
        xaxis=dict(**AXIS_STYLE, title="Issues Written", range=[0, 175]),
        yaxis=dict(**AXIS_STYLE, autorange="reversed"),
        margin=dict(t=40, b=50, l=230, r=130),
        title=dict(
            text="Amazing Spider-Man: Primary Writer Tenure by Issues",
            font=dict(size=14, color="#cccccc"),
            x=0.0,
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    chart_annotation(
        "The Silver and Bronze Age writers averaged 40+ issues per run. "
        "David Michelinie's Copper Age run, which gave us Venom and Carnage, lasted 93 issues. "
        "J. Michael Straczynski's run lasted 73. Dan Slott's solo tenure was 153. "
        "Since Slott's departure in 2018, there have been two complete relaunch cycles on Amazing Spider-Man. "
        "Spencer's run ended not because his story concluded, but because the series was cancelled and relaunched. "
        "Wells's run ended the same way. Each relaunch reset the counter before either run could develop "
        "the kind of sustained momentum that produced Venom, the Superior Spider-Man arc, or the black costume saga."
    )
    data_note("Data: approximate issue counts from primary writer tenure on Amazing Spider-Man (vol. 1 legacy numbering). "
              "Multi-writer or fill-in periods excluded. Brand New Day (2008–10) shown at ~25 issues per writer in the rotation. "
              "Data is author-verified from published records; minor corrections welcome.")

    # --- Chart 2: Years on title (runway) ---
    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("Runway: Years Before the Next Relaunch")

    prose("""
    <p>
    Issue counts overstate recent tenures. Biweekly publishing schedules mean a writer can
    accumulate 70+ issues in three years. The more honest measure of creative runway is calendar
    time — how many years passed before the next relaunch reset the series.
    The chart below replots the same runs measured in years.
    </p>
    """)

    fig2 = go.Figure()

    runway_df = df[df["writer"] != "Brand New Day (rotating)"].copy()

    for _, row in runway_df.iterrows():
        color = ERA_COLORS.get(row["era"], "#888")
        is_landmark = row["writer"] in LANDMARK_RUNS
        landmark = LANDMARK_RUNS.get(row["writer"], "")
        fig2.add_trace(go.Scatter(
            x=[row["start_year"]],
            y=[row["years"]],
            mode="markers+text",
            marker=dict(
                size=row["issues"] / 6,
                color=color,
                opacity=0.85,
                line=dict(width=1.5, color="#111"),
            ),
            text=["🕷" if is_landmark else ""],
            textposition="top center",
            textfont=dict(size=14),
            name=row["writer"],
            showlegend=False,
            hovertemplate=(
                f"<b>{row['writer']}</b><br>"
                f"{row['start_year']}-{row['end_year']}<br>"
                f"{row['years']} years | {row['issues']} issues<br>"
                f"{'<i>' + landmark + '</i>' if landmark else ''}"
                f"<extra></extra>"
            ),
        ))
        # Label notable runs
        if row["years"] >= 5 or row["writer"] in LANDMARK_RUNS:
            fig2.add_annotation(
                x=row["start_year"],
                y=row["years"],
                text=f"  {row['writer'].split()[0]} {row['writer'].split()[-1] if len(row['writer'].split()) > 1 else ''} ({row['years']}y)",
                showarrow=False,
                font=dict(size=9, color="#999"),
                xanchor="left",
                yanchor="middle",
            )

    # Reference line: 5-year threshold
    fig2.add_hline(
        y=5, line_dash="dash", line_color="#444",
        annotation_text="5-year threshold — minimum runway for a complete creative arc",
        annotation_font=dict(color="#555", size=10),
        annotation_position="top left",
    )

    # Shade the post-2018 era
    fig2.add_vrect(
        x0=2018, x1=2025,
        fillcolor="#e23636", opacity=0.05,
        line_width=0,
        annotation_text="Post-2018",
        annotation_position="top left",
        annotation_font=dict(color="#e23636", size=10),
    )

    fig2.update_layout(
        **dict(PLOTLY_LAYOUT),
        height=400,
        xaxis=dict(**AXIS_STYLE, title="Year Run Began", range=[1960, 2026]),
        yaxis=dict(**AXIS_STYLE, title="Years on Title", range=[0, 11]),
        title=dict(text="ASM Writer Tenure: Years on Title (bubble size = issues written)",
                   font=dict(size=13, color="#ccc"), x=0.0),
    )

    st.plotly_chart(fig2, use_container_width=True)

    # Stat cards: pre/post comparison
    pre_2018 = [r for r in WRITER_DATA if r["end_year"] <= 2018 and r["writer"] != "Brand New Day (rotating)"]
    post_2018 = [r for r in WRITER_DATA if r["start_year"] >= 2018]
    pre_avg_years = sum(r["years"] for r in pre_2018) / len(pre_2018)
    post_avg_years = sum(r["years"] for r in post_2018) / len(post_2018)
    pre_avg_issues = sum(r["issues"] for r in pre_2018) / len(pre_2018)
    post_avg_issues = sum(r["issues"] for r in post_2018) / len(post_2018)
    runs_above_5yr = sum(1 for r in WRITER_DATA if r["years"] >= 5 and r["end_year"] <= 2018)

    stat_cards([
        (f"{pre_avg_years:.1f} yrs", "Avg tenure — pre-2018 writers"),
        (f"{post_avg_years:.1f} yrs", "Avg tenure — post-2018 writers"),
        (f"{runs_above_5yr}", "Runs ≥ 5 years (pre-2018)"),
        ("0", "Runs ≥ 5 years (post-2018)"),
    ])

    chart_annotation(
        "The 🕷 markers flag the runs that produced landmark characters and arcs. "
        "Every one of them clears the 5-year line. Michelinie (5 years, Venom + Carnage). "
        "Straczynski (6 years, Morlun, the redefining of Peter's origin). "
        "Slott (8 years, Superior Spider-Man). "
        "The post-2018 runs are not shorter because the writers ran out of ideas — "
        "Spencer and Wells are both capable writers with strong bodies of work. "
        "They're shorter because each run was ended by a series relaunch before it could develop "
        "into something with that kind of depth. The relaunch is doing the interrupting."
    )

    # --- Chart 3: Writer change frequency by decade ---
    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("Relaunch-Driven Writer Changes by Decade")

    decades = list(range(1960, 2030, 10))
    decade_labels = [f"{d}s" for d in decades]
    decade_counts = []
    for d in decades:
        count = sum(1 for r in WRITER_DATA
                    if r["start_year"] >= d and r["start_year"] < d + 10
                    and r["writer"] != "Brand New Day (rotating)")
        decade_counts.append(count)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=decade_labels,
        y=decade_counts,
        marker_color=["#e23636" if d >= 2010 else "#5b8dbf" for d in decades],
        text=decade_counts,
        textposition="outside",
        textfont=dict(size=12, color="#ccc"),
        hovertemplate="<b>%{x}</b><br>Writer changes: %{y}<extra></extra>",
    ))

    fig3.update_layout(
        **dict(PLOTLY_LAYOUT),
        height=320,
        xaxis=dict(**AXIS_STYLE),
        yaxis=dict(**AXIS_STYLE, title="New Primary Writers", range=[0, 6]),
        title=dict(text="ASM Primary Writer Changes per Decade",
                   font=dict(size=13, color="#ccc"), x=0.0),
        showlegend=False,
    )

    st.plotly_chart(fig3, use_container_width=True)

    chart_annotation(
        "The 1980s saw the most writer changes of any decade — five new primary writers — "
        "and still produced Michelinie's 93-issue run and the creation of Venom. "
        "High writer turnover has always been part of the title. The difference is what drove it. "
        "Historical transitions were largely organic: a writer finished their arc, "
        "editorial made a change, someone moved to another title. "
        "Post-2018, each transition is a relaunch — a deliberate series cancellation and reset "
        "designed to generate a #1 issue sales spike. The writer changes are a symptom. "
        "The relaunch is the cause."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("What Tenure Makes Possible")

    prose("""
    <p>
    The most remarkable thing about the long-tenure runs is what they were able to build that
    shorter runs simply cannot. Character development, villain mythology, and reader attachment
    are all functions of time and narrative accumulation. Venom did not become a cultural
    phenomenon from a single issue. He was teased for 25 issues across the black costume arc
    before his first full reveal, and spent another full year as an antagonist before becoming
    legible to casual readers. That kind of patient, layered storytelling is only possible when
    a writer knows they will be around to pay it off.
    </p>
    <p>
    The relaunch creates a specific structural problem for long-form storytelling: it forces
    incoming writers to start fresh rather than build on what came before. Nick Spencer spent
    three years re-establishing Peter Parker's identity and setting up threads that were never paid off.
    Zeb Wells inherited a reset, not a handoff. When Wells's run ended in another relaunch,
    those threads reset again. Each cycle leaves less accumulated story for the next writer to work with,
    and readers who invested in an ongoing arc get a #1 issue instead of a resolution.
    </p>
    <p>
    The MCU built its first three phases on characters with decades of accumulated story depth.
    The comics that defined those characters were largely written by people who had long enough
    tenures to develop themes, establish supporting casts, and earn emotional payoffs. Section 04
    maps exactly which characters brought that depth to the screen, and what the gap looks like
    for the characters being developed now.
    </p>
    """)

    pull_quote(
        "Venom took 25 issues to set up and a full year to pay off. "
        "The relaunch gives you a #1 and a fresh start. "
        "Those are not the same thing."
    )
