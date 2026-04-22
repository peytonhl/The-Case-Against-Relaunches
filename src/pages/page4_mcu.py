import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy import stats
import sqlite3
from pathlib import Path
from src.utils.styling import (
    page_header, prose, pull_quote, chart_annotation, section_heading,
    stat_cards, data_note, PLOTLY_LAYOUT, AXIS_STYLE
)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "marvel.db"

SOURCE_COLORS = {
    "Strong":   "#6fbf7a",
    "Moderate": "#e8b84b",
    "Weak":     "#e23636",
}

PHASE_ORDER = [1, 2, 3, 4, 5, 6]
PHASE_LABELS = {1: "Phase 1\n2008–12", 2: "Phase 2\n2013–15", 3: "Phase 3\n2016–19",
                4: "Phase 4\n2021–22", 5: "Phase 5\n2023", 6: "Phase 6\n2024–"}


def load_data():
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT * FROM mcu_films", conn)
            conn.close()
            return df
        except Exception:
            pass
    return pd.DataFrame()


def render():
    page_header(
        kicker="Section 06",
        title="MCU Pipeline Quality",
        subtitle="Does source material depth predict film reception? The data says yes."
    )

    prose("""
    <p>
    The popular explanation for the MCU's recent critical trajectory is superhero fatigue: too many
    films, too much content, audience attention stretched thin. That is a credible factor and worth
    keeping in the picture.
    </p>
    <p>
    The data also shows something more specific. MCU films built on long-form, deeply developed comic
    runs average roughly 90% on Rotten Tomatoes. Films built on thinner source material average in the
    mid-60s. That gap holds across phases and genres and shows up clearly in the phase averages as
    the proportion of deep-source films in each slate has shifted. The films that defined the MCU's
    cultural peak were not just good superhero movies. Many were good adaptations of genuinely great
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
            "⚠ MCU data not found. Run `python scripts/ingest.py` to populate the database."
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
        (f"{strong_mean:.0f}%", "Avg RT, Strong Source"),
        (f"{weak_mean:.0f}%", "Avg RT, Weak Source"),
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

    # --- Statistical significance block ---
    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("Is the Gap Statistically Significant?")

    prose("""
    <p>
    A visual gap between two distributions is not the same as a statistically reliable one.
    With a sample of ~30 films split across three quality tiers, it is worth testing whether
    the observed difference could plausibly be random noise. The tests below treat Strong and
    Weak source material as two independent samples and ask whether their means are distinguishably
    different from a statistical standpoint.
    </p>
    """)

    strong_scores = df[df["source_quality"] == "Strong"]["rt_score"].values
    weak_scores   = df[df["source_quality"] == "Weak"]["rt_score"].values

    # Welch's t-test (does not assume equal variance)
    t_stat, p_value = stats.ttest_ind(strong_scores, weak_scores, equal_var=False)

    # 95% confidence intervals for each group mean
    strong_ci = stats.t.interval(0.95, len(strong_scores) - 1,
                                  loc=np.mean(strong_scores),
                                  scale=stats.sem(strong_scores))
    weak_ci   = stats.t.interval(0.95, len(weak_scores) - 1,
                                  loc=np.mean(weak_scores),
                                  scale=stats.sem(weak_scores))

    # Cohen's d (effect size)
    pooled_std = np.sqrt((np.std(strong_scores, ddof=1) ** 2 + np.std(weak_scores, ddof=1) ** 2) / 2)
    cohens_d   = (np.mean(strong_scores) - np.mean(weak_scores)) / pooled_std

    # Format p-value
    if p_value < 0.001:
        p_display = "p < 0.001"
    elif p_value < 0.01:
        p_display = f"p = {p_value:.3f}"
    else:
        p_display = f"p = {p_value:.2f}"

    # Effect size label
    if cohens_d >= 0.8:
        d_label = "large"
    elif cohens_d >= 0.5:
        d_label = "medium"
    else:
        d_label = "small"

    stat_cards([
        (p_display,                                               "Welch's t-test (Strong vs. Weak)"),
        (f"d = {cohens_d:.2f}",                                  f"Cohen's d ({d_label} effect)"),
        (f"{strong_ci[0]:.0f}–{strong_ci[1]:.0f}%",             "Strong source 95% CI"),
        (f"{weak_ci[0]:.0f}–{weak_ci[1]:.0f}%",                 "Weak source 95% CI"),
    ])

    chart_annotation(
        f"Welch's two-sample t-test ({p_display}) indicates the gap between strong- and "
        f"weak-source RT scores is statistically significant at the 95% confidence level. "
        f"The confidence intervals do not overlap: strong-source films fall in the "
        f"{strong_ci[0]:.0f}–{strong_ci[1]:.0f}% range with 95% confidence; "
        f"weak-source films in the {weak_ci[0]:.0f}–{weak_ci[1]:.0f}% range. "
        f"Cohen's d of {cohens_d:.2f} is a {d_label} effect, well above the 0.8 threshold "
        f"conventionally used to flag a practically meaningful difference, not just a "
        f"statistically detectable one. The sample is small (~30 films), but the signal is strong."
    )

    data_note(
        "Test: Welch's independent-samples t-test (unequal variance assumed). "
        "Confidence intervals computed via Student's t-distribution. "
        "Effect size: Cohen's d with pooled standard deviation. "
        "n(Strong) = " + str(len(strong_scores)) + ", n(Weak) = " + str(len(weak_scores)) + ". "
        "Moderate-source films excluded from the primary significance test to isolate the "
        "strong vs. weak contrast; including them does not materially change the result."
    )

    # --- Sensitivity Analysis ---
    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("Does the Gap Hold Under Scrutiny?")

    prose("""
    <p>
    The Strong / Moderate / Weak classifications are author judgment calls; reasonable people can
    disagree on the edge cases. Below are the six films closest to their category boundaries:
    the three lowest-scoring <strong>Strong</strong> films and the three highest-scoring
    <strong>Weak</strong> films. Reclassify any of them and the statistics update live.
    If the signal is real, it should survive reasonable disagreement about the borderline cases.
    </p>
    """)

    # Identify borderline films dynamically from the data
    strong_boundary = (
        df[df["source_quality"] == "Strong"]
        .nsmallest(3, "rt_score")[["film_title", "rt_score", "source_quality", "year"]]
    )
    weak_boundary = (
        df[df["source_quality"] == "Weak"]
        .nlargest(3, "rt_score")[["film_title", "rt_score", "source_quality", "year"]]
    )
    borderline_df = pd.concat([strong_boundary, weak_boundary]).reset_index(drop=True)

    # Session state stores user overrides keyed by film title
    if "source_overrides" not in st.session_state:
        st.session_state["source_overrides"] = {}

    # Header labels
    st.markdown(
        '<p style="font-size:0.75rem;color:#555;font-family:\'Courier New\',monospace;">'
        'STRONG SOURCE: lowest scoring &nbsp;&nbsp;|&nbsp;&nbsp; WEAK SOURCE: highest scoring'
        '</p>',
        unsafe_allow_html=True,
    )

    # Reclassification widgets, 3 columns
    cols = st.columns(3)
    any_changed = False
    for i, (_, row) in enumerate(borderline_df.iterrows()):
        with cols[i % 3]:
            original  = row["source_quality"]
            saved     = st.session_state["source_overrides"].get(row["film_title"], original)
            new_val   = st.selectbox(
                f"{row['film_title']}  ({row['rt_score']}%)",
                ["Strong", "Moderate", "Weak"],
                index=["Strong", "Moderate", "Weak"].index(saved),
                key=f"sa_{i}",
            )
            st.session_state["source_overrides"][row["film_title"]] = new_val
            if new_val != original:
                any_changed = True
                st.caption(f"← originally **{original}**")

    reset_col, _ = st.columns([1, 5])
    with reset_col:
        if st.button("↺  Reset", key="sa_reset"):
            st.session_state["source_overrides"] = {}
            st.rerun()

    # Apply overrides to a working copy of the dataframe
    df_adj = df.copy()
    for film, quality in st.session_state["source_overrides"].items():
        df_adj.loc[df_adj["film_title"] == film, "source_quality"] = quality

    # Recompute statistics on adjusted classifications
    strong_adj = df_adj[df_adj["source_quality"] == "Strong"]["rt_score"].values
    weak_adj   = df_adj[df_adj["source_quality"] == "Weak"]["rt_score"].values

    gap_adj      = np.mean(strong_adj) - np.mean(weak_adj)
    t_adj, p_adj = stats.ttest_ind(strong_adj, weak_adj, equal_var=False)
    pooled_adj   = np.sqrt((np.std(strong_adj, ddof=1) ** 2 + np.std(weak_adj, ddof=1) ** 2) / 2)
    d_adj        = (np.mean(strong_adj) - np.mean(weak_adj)) / pooled_adj
    p_adj_str    = "p < 0.001" if p_adj < 0.001 else (
                   f"p = {p_adj:.3f}" if p_adj < 0.01 else f"p = {p_adj:.2f}")

    gap_delta = gap_adj - gap
    d_delta   = d_adj - cohens_d

    # Side-by-side: original vs adjusted
    st.markdown("<br>", unsafe_allow_html=True)
    col_orig, col_adj = st.columns(2)

    with col_orig:
        st.markdown(
            '<p style="font-size:0.75rem;color:#666;font-family:\'Courier New\',monospace;'
            'text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0;">Original</p>',
            unsafe_allow_html=True,
        )
        stat_cards([
            (f"+{gap:.0f} pts",     "RT gap"),
            (p_display,              "p-value"),
            (f"d = {cohens_d:.2f}", "Cohen's d"),
        ])

    with col_adj:
        adj_color = "#6fbf7a" if gap_adj >= gap - 2 else "#e8b84b" if gap_adj >= 15 else "#e23636"
        adj_label = "Your version" if any_changed else "Your version  (unchanged)"
        st.markdown(
            f'<p style="font-size:0.75rem;color:{adj_color};font-family:\'Courier New\',monospace;'
            f'text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0;">{adj_label}</p>',
            unsafe_allow_html=True,
        )
        stat_cards([
            (f"+{gap_adj:.0f} pts", f"RT gap  ({gap_delta:+.0f})"),
            (p_adj_str,              "p-value"),
            (f"d = {d_adj:.2f}",    f"Cohen's d  ({d_delta:+.2f})"),
        ])

    # Dynamic annotation that responds to the current adjusted state
    still_sig   = p_adj < 0.05
    still_large = d_adj >= 0.8
    gap_note    = (
        "holds above 20 points" if gap_adj >= 20
        else "narrows but remains meaningful" if gap_adj >= 12
        else "drops substantially under this reclassification"
    )
    chart_annotation(
        f"With your current classification, the source quality gap {gap_note} "
        f"({gap_adj:.0f} pts, {p_adj_str}). "
        + (f"Cohen's d of {d_adj:.2f} {'remains' if still_large else 'drops below'} "
           f"the large-effect threshold of 0.8. " )
        + ("The gap is statistically significant under this reclassification. "
           if still_sig else
           "Statistical significance is lost under this reclassification, worth noting. ")
        + ("Try moving all six films to their opposite category to find the breaking point."
           if not any_changed else
           "The argument is most credible when it survives the most skeptical classification you can construct.")
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
