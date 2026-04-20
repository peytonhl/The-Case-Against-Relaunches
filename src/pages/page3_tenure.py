import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.utils.styling import (
    page_header, prose, pull_quote, chart_annotation, section_heading, data_note,
    PLOTLY_LAYOUT, AXIS_STYLE
)

WRITER_DATA = [
    {"writer": "Stan Lee",                  "start_year": 1963, "end_year": 1972, "issues": 110, "era": "Silver Age"},
    {"writer": "Gerry Conway",              "start_year": 1972, "end_year": 1975, "issues": 40,  "era": "Bronze Age"},
    {"writer": "Len Wein",                  "start_year": 1975, "end_year": 1976, "issues": 8,   "era": "Bronze Age"},
    {"writer": "Marv Wolfman",              "start_year": 1976, "end_year": 1980, "issues": 36,  "era": "Bronze Age"},
    {"writer": "Denny O'Neil",              "start_year": 1980, "end_year": 1982, "issues": 18,  "era": "Bronze Age"},
    {"writer": "Roger Stern",               "start_year": 1982, "end_year": 1984, "issues": 29,  "era": "Copper Age"},
    {"writer": "Tom DeFalco",               "start_year": 1984, "end_year": 1987, "issues": 36,  "era": "Copper Age"},
    {"writer": "J.M. DeMatteis",            "start_year": 1987, "end_year": 1988, "issues": 12,  "era": "Copper Age"},
    {"writer": "David Michelinie",          "start_year": 1988, "end_year": 1993, "issues": 93,  "era": "Copper Age"},
    {"writer": "J.M. DeMatteis (2nd run)",  "start_year": 1993, "end_year": 1994, "issues": 20,  "era": "90s"},
    {"writer": "Howard Mackie",             "start_year": 1994, "end_year": 2001, "issues": 55,  "era": "90s"},
    {"writer": "J. Michael Straczynski",    "start_year": 2001, "end_year": 2007, "issues": 73,  "era": "2000s"},
    {"writer": "Brand New Day (rotating)",  "start_year": 2008, "end_year": 2010, "issues": 25,  "era": "Modern"},
    {"writer": "Dan Slott",                 "start_year": 2010, "end_year": 2018, "issues": 153, "era": "Modern"},
    {"writer": "Nick Spencer",              "start_year": 2018, "end_year": 2021, "issues": 74,  "era": "Modern"},
    {"writer": "Zeb Wells",                 "start_year": 2022, "end_year": 2024, "issues": 40,  "era": "Modern"},
]

ERA_COLORS = {
    "Silver Age":  "#e8b84b",
    "Bronze Age":  "#b07d3e",
    "Copper Age":  "#c97c4e",
    "90s":         "#9e6b8a",
    "2000s":       "#5b8dbf",
    "Modern":      "#e23636",
}


def render():
    page_header(
        kicker="Section 03",
        title="Writer Tenure Analysis",
        subtitle="Amazing Spider-Man, 1963 – 2024: how long creators were trusted to tell a story."
    )

    prose("""
    <p>
    The chart below is a sixty-year record of creative trust. Each bar represents a single writer's
    primary run on <em>Amazing Spider-Man</em>, ordered chronologically from Stan Lee's 1963 launch
    to the present. Bar length equals issues written. The color indicates the publishing era.
    </p>
    <p>
    The left side of the chart tells the story of how Marvel's most enduring characters were built.
    The right side raises a question worth sitting with.
    </p>
    """)

    df = pd.DataFrame(WRITER_DATA)
    df = df.sort_values("start_year", ascending=True)

    fig = go.Figure()

    for _, row in df.iterrows():
        color = ERA_COLORS.get(row["era"], "#888888")
        opacity = 0.5 if row["writer"] == "Brand New Day (rotating)" else 1.0
        fig.add_trace(go.Bar(
            x=[row["issues"]],
            y=[f"{row['writer']} ({row['start_year']})"],
            orientation="h",
            marker_color=color,
            marker_opacity=opacity,
            text=f"  {row['issues']} issues",
            textposition="outside",
            textfont=dict(size=10, color="#888"),
            hovertemplate=(
                f"<b>{row['writer']}</b><br>"
                f"{row['start_year']}–{row['end_year']}<br>"
                f"{row['issues']} issues<br>"
                f"Era: {row['era']}"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=620,
        barmode="overlay",
        xaxis=dict(**AXIS_STYLE, title="Issues Written", range=[0, 175]),
        yaxis=dict(**AXIS_STYLE, autorange="reversed"),
        margin=dict(t=40, b=50, l=230, r=80),
        title=dict(
            text="Amazing Spider-Man: Primary Writer Tenure by Issues",
            font=dict(size=14, color="#cccccc"),
            x=0.0,
        ),
    )

    # Add era legend as annotations
    legend_x = 155
    legend_y_start = 3.5
    for i, (era, color) in enumerate(ERA_COLORS.items()):
        fig.add_annotation(
            x=legend_x, y=i * 0.8,
            text=f"● {era}",
            showarrow=False,
            font=dict(size=10, color=color),
            xanchor="left",
            xref="x", yref="y",
        )

    st.plotly_chart(fig, use_container_width=True)

    chart_annotation(
        "The Silver and Bronze Age writers averaged 40+ issues per run. "
        "David Michelinie's Copper Age run, which gave us Venom and Carnage, lasted 93 issues. "
        "J. Michael Straczynski's run lasted 73. Dan Slott's solo tenure was 153. "
        "Since Slott's departure in 2018, the average primary writer tenure has been under 57 issues, "
        "with two relaunches in that window. The bars on the right reflect real choices about how "
        "long a writer gets to develop their vision — and what becomes possible when that window is longer."
    )
    data_note("Data: approximate issue counts from primary writer tenure on Amazing Spider-Man (vol. 1 legacy numbering). "
              "Multi-writer or fill-in periods excluded. Brand New Day (2008–10) shown at ~25 issues per writer in the rotation. "
              "Data is author-verified from published records; minor corrections welcome.")

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
    Roger Stern gave us the Hobgoblin and left before he could resolve the mystery because he was
    pushed out. Tom DeFalco inherited the plot and did his best with it. The Hobgoblin storyline
    is still remembered as unresolved, decades later, not because anyone failed, but because the
    story needed more time than the circumstances allowed. That is the cost of a shortened tenure,
    and it compounds: the villain is diminished, the arc is incomplete, and future writers have
    less to build on.
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
        "Venom. The Winter Soldier. The modern Black Panther. "
        "Every one of them was the product of a writer "
        "who was left alone long enough to finish a thought. "
        "That is still the most powerful tool in comics."
    )
