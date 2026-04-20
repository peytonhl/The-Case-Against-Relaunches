import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from src.utils.styling import (
    page_header, prose, pull_quote, chart_annotation, section_heading,
    stat_cards, data_note, PLOTLY_LAYOUT, AXIS_STYLE
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "mcu_films.csv")

SOURCE_COLORS = {
    "Strong":   "#6fbf7a",
    "Moderate": "#e8b84b",
    "Weak":     "#e23636",
}

PHASE_ORDER = [1, 2, 3, 4, 5, 6]
PHASE_LABELS = {1: "Phase 1\n2008–12", 2: "Phase 2\n2013–15", 3: "Phase 3\n2016–19",
                4: "Phase 4\n2021–22", 5: "Phase 5\n2023", 6: "Phase 6\n2024–"}


def load_data():
    path = os.path.normpath(DATA_PATH)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


def render():
    page_header(
        kicker="Section 05",
        title="MCU Pipeline Quality",
        subtitle="Does source material depth predict film reception? The data says yes."
    )

    prose("""
    <p>
    The popular explanation for the MCU's recent critical trajectory is superhero fatigue — too many
    films, too much content, audience attention stretched thin. That is a credible factor and worth
    keeping in the picture.
    </p>
    <p>
    The data also shows something more specific. MCU films built on long-form, deeply developed comic
    runs average roughly 90% on Rotten Tomatoes. Films built on thinner source material average in the
    mid-60s. That gap holds across phases and genres and shows up clearly in the phase averages as
    the proportion of deep-source films in each slate has shifted. The films that defined the MCU's
    cultural peak were not just good superhero movies — many were good adaptations of genuinely great
    comics, written by people who had years to develop the characters, villains, and emotional logic
    that the films then translated to the screen.
    </p>
    <p>
    The charts below plot RT scores for every MCU theatrical release against a qualitative assessment
    of source material depth. Adaptation quality, casting, and direction all matter, and the correlation
    is not perfect. But it is consistent enough to be the strongest signal in this dataset.
    </p>
    """)

    df = load_data()

    if df.empty:
        st.warning(
            "⚠ MCU data not found. Expected: `data/mcu_films.csv`\n\n"
            "CSV schema: `film_title, year, rt_score, phase, source_quality, source_run, source_writer`"
        )
        return

    df["source_quality"] = pd.Categorical(df["source_quality"], categories=["Weak", "Moderate", "Strong"], ordered=True)

    # --- Chart 1: Scatter plot by film, colored by source quality ---
    section_heading("RT Score vs. Source Material Depth")

    fig1 = go.Figure()
    for quality in ["Strong", "Moderate", "Weak"]:
        subset = df[df["source_quality"] == quality]
        fig1.add_trace(go.Scatter(
            x=subset["year"],
            y=subset["rt_score"],
            mode="markers",
            name=quality + " Source",
            marker=dict(
                color=SOURCE_COLORS[quality],
                size=12,
                opacity=0.85,
                line=dict(width=1, color="#222"),
            ),
            text=subset["film_title"],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Year: %{x}<br>"
                "RT Score: %{y}%<br>"
                "Source: %{customdata}"
                "<extra></extra>"
            ),
            customdata=subset["source_run"],
        ))

    # Add phase dividers
    phase_boundaries = [2012.5, 2015.5, 2019.5, 2022.5, 2023.5]
    phase_labels_x = [2010, 2014, 2017.5, 2021, 2023, 2025]
    phase_label_text = ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5", "Phase 6"]
    for x in phase_boundaries:
        fig1.add_vline(x=x, line_dash="dot", line_color="#2a2a2a")
    for x, label in zip(phase_labels_x, phase_label_text):
        fig1.add_annotation(
            x=x, y=44, text=label,
            showarrow=False,
            font=dict(size=9, color="#444"),
            xref="x", yref="y",
        )

    fig1.update_layout(
        **dict(PLOTLY_LAYOUT),
        height=460,
        xaxis=dict(**AXIS_STYLE, title="Release Year"),
        yaxis=dict(**AXIS_STYLE, title="Rotten Tomatoes Score (%)", range=[40, 100]),
        legend=dict(bgcolor="#111", bordercolor="#333", borderwidth=1, font=dict(size=11)),
        title=dict(text="MCU Films: RT Score by Source Material Depth", font=dict(size=14, color="#ccc"), x=0.0),
    )
    st.plotly_chart(fig1, use_container_width=True)

    chart_annotation(
        "Green dots cluster at the top. Red dots cluster at the bottom. The pattern is consistent. "
        "Films with strong source material, including The Winter Soldier (Brubaker's Cap run), "
        "Black Panther (Christopher Priest's run), Guardians of the Galaxy (Abnett/Lanning), "
        "and Doctor Strange (Ditko's original Strange Tales), average ~90% on RT. "
        "Films with thinner source material, including Eternals, Quantumania, and The Marvels, "
        "average in the low-to-mid 60s. The gap is over 25 points. "
        "Superhero fatigue may be real, but it does not explain why strong-source films continue "
        "to land well. The depth of the source material appears to matter."
    )

    # --- Chart 2: Box plot by source quality ---
    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("The Source Quality Gap, Quantified")

    # Convert hex to rgba for fill (Plotly doesn't support 8-digit hex alpha)
    def hex_to_rgba(hex_color, alpha=0.15):
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    fig2 = go.Figure()
    for quality in ["Strong", "Moderate", "Weak"]:
        subset = df[df["source_quality"] == quality]
        fig2.add_trace(go.Box(
            y=subset["rt_score"],
            name=quality + " Source",
            marker_color=SOURCE_COLORS[quality],
            line_color=SOURCE_COLORS[quality],
            fillcolor=hex_to_rgba(SOURCE_COLORS[quality]),
            boxmean="sd",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "RT Score: %{y}%"
                "<extra></extra>"
            ),
        ))

    fig2.update_layout(
        **dict(PLOTLY_LAYOUT),
        height=380,
        xaxis=dict(**AXIS_STYLE),
        yaxis=dict(**AXIS_STYLE, title="Rotten Tomatoes Score (%)", range=[35, 105]),
        title=dict(text="RT Score Distribution by Source Material Depth", font=dict(size=14, color="#ccc"), x=0.0),
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Compute and display stats
    strong_mean = df[df["source_quality"] == "Strong"]["rt_score"].mean()
    weak_mean = df[df["source_quality"] == "Weak"]["rt_score"].mean()
    gap = strong_mean - weak_mean
    phase_avgs = df.groupby("phase")["rt_score"].mean()

    stat_cards([
        (f"{strong_mean:.0f}%", "Avg RT — Strong Source"),
        (f"{weak_mean:.0f}%", "Avg RT — Weak Source"),
        (f"+{gap:.0f} pts", "Source quality gap"),
        (f"{phase_avgs.get(3, 0):.0f}% → {phase_avgs.get(5, 0):.0f}%", "Phase 3 → Phase 5 avg RT"),
    ])

    chart_annotation(
        "The median RT score for films with strong source material sits around 91%. "
        "For weak source films, the median is in the mid-to-low 60s. "
        "The standard deviation for weak-source films is also higher. A few outliers land well, "
        "but the floor is much lower and the variance is much higher. "
        "Strong source material does not guarantee a good film. But it meaningfully increases the floor."
    )

    # --- Chart 3: Phase average over time ---
    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("Average RT Score by Phase: A Downward Trend")

    phase_data = df.groupby("phase").agg(
        avg_rt=("rt_score", "mean"),
        film_count=("rt_score", "count"),
        strong_pct=("source_quality", lambda x: (x == "Strong").mean() * 100),
    ).reset_index()

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=[f"Phase {p}" for p in phase_data["phase"]],
        y=phase_data["avg_rt"],
        marker_color=["#6fbf7a" if s >= 50 else "#e8b84b" if s >= 30 else "#e23636"
                      for s in phase_data["strong_pct"]],
        text=[f"{v:.0f}%" for v in phase_data["avg_rt"]],
        textposition="outside",
        textfont=dict(size=12, color="#ccc"),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Avg RT: %{y:.1f}%<br>"
            "Films: %{customdata[0]}<br>"
            "Strong source: %{customdata[1]:.0f}%"
            "<extra></extra>"
        ),
        customdata=list(zip(phase_data["film_count"], phase_data["strong_pct"])),
    ))
    fig3.add_hline(y=80, line_dash="dash", line_color="#444",
                   annotation_text="80% benchmark", annotation_font=dict(color="#555", size=10))

    fig3.update_layout(
        **dict(PLOTLY_LAYOUT),
        height=360,
        xaxis=dict(**AXIS_STYLE),
        yaxis=dict(**AXIS_STYLE, title="Average RT Score (%)", range=[40, 100]),
        title=dict(text="MCU Average RT Score by Phase", font=dict(size=14, color="#ccc"), x=0.0),
        showlegend=False,
    )
    st.plotly_chart(fig3, use_container_width=True)

    chart_annotation(
        "Phase 3 was the MCU's creative peak, with an average RT score of ~88% built on deep source material "
        "for nearly every major film in the slate. Phase 4 dropped to ~76%. Phase 5 to ~67%. "
        "The color coding maps to the proportion of films in each phase with strong source material. "
        "The correlation holds at the phase level as well as the individual film level. "
        "As the deep-source films get made, the remaining pipeline is weighted toward characters and concepts "
        "that lack the same decades of accumulated story development."
    )

    data_note(
        "Data: Rotten Tomatoes critical scores as of April 2025. "
        "Source quality classifications are author judgments based on run length, critical reputation, "
        "and documented influence on the film adaptation. Classifications are arguable at the margins; "
        "the aggregate pattern is robust to reasonable reclassification of individual films."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    prose("""
    <p>
    The argument here is not that every MCU film needs to be a direct adaptation. It does not.
    <em>Thor: Ragnarok</em> is a loose riff on <em>Planet Hulk</em> filtered through Taika Waititi's
    comedic sensibility, and it is one of the best films in the franchise. The point is not fidelity.
    The point is that the best MCU films tend to be built on characters and concepts that have been
    deeply explored in long-form comics, by writers who had the time and support to develop them fully.
    That depth gives filmmakers something real to work with, whether they adapt it faithfully or not.
    </p>
    <p>
    The good news is that this is a solvable problem. The comics pipeline is still running. There are
    writers working today building genuinely interesting things with Marvel characters. The question
    worth asking is whether the publishing strategy gives those writers enough runway to develop the
    kind of story depth that made the MCU's best films possible, and what it might look like to
    structure the pipeline with that goal explicitly in mind.
    </p>
    """)

    pull_quote(
        "The MCU succeeded because Marvel had spent 40 years making interesting characters. "
        "The next 40 years of great Marvel stories are being written right now. "
        "The question is how much time those writers are being given."
    )
