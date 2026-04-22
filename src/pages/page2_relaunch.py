import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import sqlite3
from pathlib import Path
from src.utils.styling import (
    page_header, prose, pull_quote, chart_annotation, section_heading,
    stat_cards, data_note, PLOTLY_LAYOUT, AXIS_STYLE
)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "marvel.db"

VOLUME_META = {
    2: {"label": "Vol. 2 (1999)", "color": "#e8b84b", "writer": "Howard Mackie"},
    3: {"label": "Vol. 3 (2014)", "color": "#5b8dbf", "writer": "Dan Slott"},
    4: {"label": "Vol. 4 (2015)", "color": "#6fbf7a", "writer": "Dan Slott"},
    5: {"label": "Vol. 5 (2018)", "color": "#bf8f5b", "writer": "Nick Spencer"},
    6: {"label": "Vol. 6 (2022)", "color": "#e23636", "writer": "Zeb Wells"},
}

CONFIDENCE_DASH = {
    "Confirmed":                   "solid",
    "Confirmed - Variant Inflated": "dot",
    "Confirmed - Event Boosted":   "solid",
    "PRH Estimate":                "dash",
    "Estimate":                    "dash",
}
CONFIDENCE_OPACITY = {
    "Confirmed":                   1.0,
    "Confirmed - Variant Inflated": 0.4,
    "Confirmed - Event Boosted":   0.85,
    "PRH Estimate":                0.65,
    "Estimate":                    0.65,
}


def load_data():
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT * FROM asm_relaunches", conn)
            conn.close()
            return df
        except Exception:
            pass
    return pd.DataFrame()


def render():
    page_header(
        kicker="Section 02",
        title="Relaunch Bump Decay",
        subtitle="What the sales data shows when you look past the first-issue spike."
    )

    prose("""
    <p>
    The relaunch is one of Marvel's most consistent sales tools. Publish a new #1, generate
    first-issue excitement, and watch the numbers spike. The strategy has a genuine rationale:
    new entry points are valuable, and a fresh creative team can reinvigorate a title that has
    lost momentum. What makes the data interesting is what it shows about the full cycle: not
    just the spike, but the baseline readership that follows, and how that baseline has shifted
    across multiple relaunch cycles over two decades.
    </p>
    <p>
    A note on methodology: <strong>Issue #1 figures are excluded from trajectory comparisons
    and marked separately.</strong> First issues carry dozens to hundreds of variant cover editions,
    each ordered separately by retailers. ASM Vol. 3 #1 (2014) reported 532,586 units, but issue
    #2 the following month came in at 123,945. That 77% single-issue drop was not reader attrition.
    It was the speculator market clearing. Issue #2 is used as the readership baseline throughout.
    See the Appendix for full methodology.
    </p>
    """)

    df = load_data()

    if df.empty:
        st.warning(
            "⚠ Sales data not found. Run `python scripts/ingest.py` to populate the database."
        )
        return

    # Separate variant-inflated #1 from rest
    df_v1 = df[df["data_confidence"] == "Confirmed - Variant Inflated"]
    df_main = df[df["data_confidence"] != "Confirmed - Variant Inflated"]

    # --- Chart 1: Multi-line trajectory (starting from #2) ---
    section_heading("Sustained Readership Trajectories")

    fig1 = go.Figure()

    for vol, meta in VOLUME_META.items():
        subset = df_main[(df_main["relaunch_volume"] == vol) & (df_main["issue_num"] >= 2)].sort_values("issue_num")
        if subset.empty:
            continue

        # Build line with variable opacity per segment based on confidence
        x_vals = subset["issue_num"].tolist()
        y_vals = (subset["orders"] / 1000).tolist()
        conf_vals = subset["data_confidence"].tolist()

        is_estimate = any(c in ("Estimate", "PRH Estimate") for c in conf_vals)
        dash_style = "dash" if is_estimate else "solid"
        opacity = 0.7 if is_estimate else 1.0

        fig1.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines+markers",
            name=meta["label"],
            line=dict(color=meta["color"], width=2.5, dash=dash_style),
            marker=dict(
                size=[9 if c.startswith("Confirmed") else 6 for c in conf_vals],
                color=meta["color"],
                opacity=[CONFIDENCE_OPACITY.get(c, 0.65) for c in conf_vals],
                symbol=["circle" if c.startswith("Confirmed") else "circle-open" for c in conf_vals],
            ),
            opacity=opacity,
            hovertemplate=(
                f"<b>{meta['label']}</b>, {meta['writer']}<br>"
                "Issue #%{x}<br>"
                "Orders: %{y:.1f}k<br>"
                "%{customdata}"
                "<extra></extra>"
            ),
            customdata=conf_vals,
        ))

    # --- OLS trend lines per volume ---
    decay_stats = {}
    for vol, meta in VOLUME_META.items():
        subset = df_main[
            (df_main["relaunch_volume"] == vol) &
            (df_main["issue_num"] >= 2) &
            (~df_main["data_confidence"].isin(["Estimate", "PRH Estimate"]))
        ].sort_values("issue_num")
        if len(subset) < 3:
            continue
        x = subset["issue_num"].values
        y = (subset["orders"] / 1000).values
        coeffs = np.polyfit(x, y, 1)          # slope, intercept
        y_hat  = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_hat) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2     = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        slope  = coeffs[0]                    # thousands of copies per issue
        x_line = np.linspace(x.min(), x.max(), 80)
        y_line = np.polyval(coeffs, x_line)
        decay_stats[vol] = {"slope": slope, "r2": r2, "label": meta["label"]}
        fig1.add_trace(go.Scatter(
            x=x_line, y=y_line,
            mode="lines",
            name=f"{meta['label']} trend",
            line=dict(color=meta["color"], width=1, dash="dot"),
            opacity=0.45,
            showlegend=False,
            hoverinfo="skip",
        ))

    layout1 = dict(PLOTLY_LAYOUT)
    fig1.update_layout(
        **layout1,
        height=440,
        xaxis=dict(**AXIS_STYLE, title="Issue Number Within Run",
            tickvals=[2, 6, 12, 24, 36],
        ),
        yaxis=dict(**AXIS_STYLE, title="Estimated Orders (thousands)",
        ),
        legend=dict(bgcolor="#111", bordercolor="#333", borderwidth=1, font=dict(size=11)),
        title=dict(
            text="ASM Sales Trajectory by Relaunch (Issue #2 Baseline)",
            font=dict(size=13, color="#ccc"), x=0.0,
        ),
    )

    # Annotation explaining dashed = estimate
    fig1.add_annotation(
        x=0.01, y=0.02, xref="paper", yref="paper",
        text="Solid line = Confirmed Comichron data · Dashed = Estimate or PRH-normalized",
        showarrow=False,
        font=dict(size=9, color="#555"),
        xanchor="left",
    )

    st.plotly_chart(fig1, use_container_width=True)

    # Build decay summary for annotation
    decay_lines = []
    for vol in sorted(decay_stats):
        d = decay_stats[vol]
        decay_lines.append(
            f"{d['label']}: {d['slope']*-1:.2f}k copies/issue lost (R²={d['r2']:.2f})"
        )
    decay_summary = " · ".join(decay_lines)

    chart_annotation(
        "Dotted lines show OLS trend fits for each run (confirmed data only). "
        "The slope quantifies the rate of sustained readership decay per issue. "
        + (f"Decay rates: {decay_summary}. " if decay_summary else "")
        + "Vol. 4 (2015) and Vol. 5 (2018) both opened around 111–114k readers at issue #2, "
        "essentially flat across relaunch cycles. Both fell to similar floors by issue 12 (~75–76k). "
        "R² values above 0.7 indicate a consistent linear decay rather than random noise. "
        "Solid circles are confirmed Comichron figures; hollow circles are estimates or "
        "PRH-normalized approximations. Full confidence data is in the Appendix."
    )

    # --- Chart 2: #1 spike vs #2 baseline comparison ---
    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("The #1 Spike vs. Real Readership")

    issue_ones = df[df["issue_num"] == 1].copy()
    issue_twos = df_main[df_main["issue_num"] == 2].copy()

    meta_df = pd.DataFrame([
        {"relaunch_volume": k, "label": v["label"], "writer": v["writer"], "color": v["color"]}
        for k, v in VOLUME_META.items()
    ])
    issue_ones = issue_ones.merge(meta_df, on="relaunch_volume").sort_values("relaunch_year")
    issue_twos = issue_twos.merge(meta_df, on="relaunch_volume").sort_values("relaunch_year")

    fig2 = go.Figure()

    # #1 bars (faded — speculator inflated)
    fig2.add_trace(go.Bar(
        name="Issue #1 (variant-inflated)",
        x=issue_ones["label"],
        y=issue_ones["orders"] / 1000,
        marker_color=[VOLUME_META[v]["color"] for v in issue_ones["relaunch_volume"]],
        marker_opacity=0.25,
        marker_pattern_shape="/",
        hovertemplate=(
            "<b>%{x}, Issue #1</b><br>"
            "%{y:.0f}k orders<br>"
            "<i>Includes variant covers; not a readership figure</i>"
            "<extra></extra>"
        ),
    ))

    # #2 bars (solid — real readership)
    fig2.add_trace(go.Bar(
        name="Issue #2 (readership baseline)",
        x=issue_twos["label"],
        y=issue_twos["orders"] / 1000,
        marker_color=[VOLUME_META[v]["color"] for v in issue_twos["relaunch_volume"]],
        marker_opacity=0.9,
        hovertemplate=(
            "<b>%{x}, Issue #2</b><br>"
            "%{y:.0f}k orders<br>"
            "<i>First variant-free issue; actual reader demand</i>"
            "<extra></extra>"
        ),
        text=[f"{o/1000:.0f}k" for o in issue_twos["orders"]],
        textposition="outside",
        textfont=dict(size=11, color="#ccc"),
    ))

    fig2.update_layout(**dict(PLOTLY_LAYOUT))
    fig2.update_layout(
        height=430,
        barmode="group",
        xaxis=dict(**AXIS_STYLE, tickangle=-40),
        yaxis=dict(**AXIS_STYLE, title="Orders (thousands)",
            range=[0, 620],
        ),
        legend=dict(bgcolor="#111", bordercolor="#333", borderwidth=1, font=dict(size=11)),
        title=dict(
            text="Issue #1 Orders (variant-inflated) vs. Issue #2 (real readership baseline)",
            font=dict(size=13, color="#ccc"), x=0.0,
        ),
        margin=dict(t=40, b=100, l=60, r=40),
    )
    st.plotly_chart(fig2, use_container_width=True)

    chart_annotation(
        "The faded bars show issue #1 orders including all variants. The solid bars show issue #2. "
        "The 2014 gap (532k reported vs. 124k actual readers) is the most extreme example, "
        "but the gap exists in every relaunch. What the variant-adjusted data actually shows is "
        "something interesting: the real Spider-Man audience at issue #2 has been remarkably stable, "
        "sitting between 111–124k across 1999–2022. These are loyal readers who show up for the character "
        "regardless of volume number. The opportunity is converting that loyalty into sustained readership "
        "deeper into each run, rather than resetting the counter every few years."
    )

    # --- Chart 3: Drop-off rate from #2 to #12 ---
    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("The Same Ceiling, Every Time")

    issue_12 = df_main[df_main["issue_num"] == 12][["relaunch_volume", "orders", "data_confidence"]].rename(
        columns={"orders": "orders_12", "data_confidence": "conf_12"}
    )
    dropoff = issue_twos[["relaunch_volume", "relaunch_year", "orders", "label"]].merge(
        issue_12, on="relaunch_volume", how="inner"
    )
    dropoff["retention_pct"] = (dropoff["orders_12"] / dropoff["orders"]) * 100
    dropoff["floor_12k"] = dropoff["orders_12"] / 1000
    dropoff = dropoff.sort_values("relaunch_year")

    fig3 = go.Figure()
    for _, row in dropoff.iterrows():
        vol = row["relaunch_volume"]
        is_est = row["conf_12"] in ("Estimate", "PRH Estimate")
        fig3.add_trace(go.Scatter(
            x=[row["label"]],
            y=[row["floor_12k"]],
            mode="markers+text",
            marker=dict(
                size=14,
                color=VOLUME_META[vol]["color"],
                opacity=0.65 if is_est else 1.0,
                symbol="diamond-open" if is_est else "diamond",
                line=dict(width=2, color=VOLUME_META[vol]["color"]),
            ),
            text=[f"  {row['floor_12k']:.0f}k"],
            textposition="middle right",
            textfont=dict(size=11, color="#ccc"),
            name=row["label"],
            showlegend=False,
            hovertemplate=(
                f"<b>{row['label']}</b><br>"
                f"Issue #12: {row['floor_12k']:.1f}k<br>"
                f"Retention: {row['retention_pct']:.1f}% of #2<br>"
                f"Confidence: {row['conf_12']}"
                "<extra></extra>"
            ),
        ))

    # Connect dots with a line
    fig3.add_trace(go.Scatter(
        x=dropoff["label"].tolist(),
        y=dropoff["floor_12k"].tolist(),
        mode="lines",
        line=dict(color="#444", width=1.5, dash="dot"),
        showlegend=False,
        hoverinfo="skip",
    ))

    fig3.update_layout(
        **dict(PLOTLY_LAYOUT),
        height=320,
        xaxis=dict(**AXIS_STYLE),
        yaxis=dict(**AXIS_STYLE, title="Issue #12 Orders (thousands)",
            range=[35, 115],
        ),
        title=dict(
            text="Issue #12 Sustained Readership by Relaunch",
            font=dict(size=13, color="#ccc"), x=0.0,
        ),
    )
    st.plotly_chart(fig3, use_container_width=True)

    chart_annotation(
        "How many readers are still buying twelve issues in? "
        "Vol. 4 (2015) and Vol. 5 (2018) both confirm around 75–76k at issue #12, a ceiling rather than a floor. "
        "Solid diamonds are confirmed Comichron figures. Hollow diamonds are estimates. "
        "What the confirmed data shows is that each run tends to settle at roughly the same level "
        "as the previous one. The audience is there and it is loyal. The interesting question is "
        "what a publishing strategy optimized for holding that audience, rather than repeatedly "
        "resetting it, might look like over time."
    )

    data_note(
        "Sources: Comichron.com monthly Diamond order charts. "
        "Confirmed figures from direct Comichron monthly chart lookups. "
        "Estimates interpolated from confirmed data points within the same run. "
        "2022 figures use Comichron's combined Diamond+PRH estimates where available, "
        "otherwise normalized using a 0.35 Diamond/total factor (per Comichron's published methodology). "
        "See Appendix for full confidence table and source documentation."
    )

    pull_quote(
        "110,000 people showing up for every Amazing Spider-Man relaunch "
        "is not a problem to be solved. "
        "It is a foundation to build on."
    )

    # --- Multi-title comparison ---
    st.markdown("<br>", unsafe_allow_html=True)
    section_heading("Spider-Man Holds. The Rest of the Catalog Doesn't.")

    prose("""
    <p>
    The Spider-Man data reveals something important before we look at the other titles:
    Amazing Spider-Man's issue #2 baseline has held between 110–125k across five relaunches
    and 25 years. The character is resilient enough that readers keep showing up regardless
    of volume number. That is genuinely impressive brand equity, and it matters for what
    comes next.
    </p>
    <p>
    The chart below plots issue #2 orders (the variant-free readership baseline) for every
    tracked relaunch across five flagship Marvel titles. With more titles in view, the pattern
    becomes harder to dismiss: ASM's stability is the outlier, not the norm.
    </p>
    """)

    mdf = pd.DataFrame()
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            mdf = pd.read_sql_query("SELECT * FROM relaunch_multi", conn)
            conn.close()
        except Exception:
            pass
    if mdf.empty:
        st.warning("Multi-title data not found. Run `python scripts/ingest.py` to populate the database.")
    else:

        TITLE_COLORS = {
            "Amazing Spider-Man": "#e23636",
            "Avengers":           "#5b8dbf",
            "Daredevil":          "#e8b84b",
            "Captain America":    "#2aa198",
            "Thor":               "#bf6f30",
        }
        TITLE_EMOJI = {
            "Amazing Spider-Man": "🕷",
            "Avengers":           "⭐",
            "Daredevil":          "⚖",
            "Captain America":    "🛡",
            "Thor":               "⚡",
        }

        fig_multi = go.Figure()

        for title in ["Amazing Spider-Man", "Avengers", "Daredevil", "Captain America", "Thor"]:
            subset = mdf[mdf["title"] == title].sort_values("relaunch_year")
            if subset.empty:
                continue
            is_confirmed = subset["data_confidence"].str.startswith("Confirmed")
            emoji = TITLE_EMOJI[title]
            fig_multi.add_trace(go.Scatter(
                x=subset["relaunch_year"],
                y=subset["orders"] / 1000,
                mode="lines+markers+text",
                name=title,
                line=dict(color=TITLE_COLORS[title], width=2.5),
                marker=dict(
                    color=TITLE_COLORS[title],
                    size=18,
                    opacity=0,
                ),
                text=[emoji] * len(subset),
                textposition="middle center",
                textfont=dict(size=16),
                customdata=list(zip(subset["run_label"], subset["data_confidence"])),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Year: %{x}<br>"
                    "Issue #2 orders: %{y:.1f}k<br>"
                    "%{customdata[1]}"
                    "<extra></extra>"
                ),
            ))

        fig_multi.add_annotation(
            x=0.01, y=0.02, xref="paper", yref="paper",
            text="All points = Issue #2 baseline · 🕷 ASM · ⭐ Avengers · ⚖ Daredevil · 🛡 Cap · ⚡ Thor · Dashed = estimate or PRH-normalized",
            showarrow=False, font=dict(size=9, color="#555"), xanchor="left",
        )

        fig_multi.update_layout(
            **dict(PLOTLY_LAYOUT),
            height=460,
            xaxis=dict(**AXIS_STYLE, title="Relaunch Year", dtick=6),
            yaxis=dict(**AXIS_STYLE, title="Issue #2 Orders (thousands)", range=[20, 180]),
            legend=dict(bgcolor="#111", bordercolor="#333", borderwidth=1, font=dict(size=11)),
            title=dict(
                text="Issue #2 Readership at Relaunch: Five Marvel Flagship Titles",
                font=dict(size=13, color="#ccc"), x=0.0,
            ),
        )
        st.plotly_chart(fig_multi, use_container_width=True)

        chart_annotation(
            "Four of the five titles show a consistent downward trend across relaunch cycles. "
            "Avengers drops from 153k (Bendis, 2004) to 67k (Aaron, 2018), a 56% decline. "
            "Captain America falls from ~90k (Brubaker, 2004) to ~57k (Coates, 2018), down 37%. "
            "Thor declines from ~78k (Straczynski, 2007) to ~50k (Aaron, 2018), down 36%. "
            "Daredevil goes from 83k (1998) to 41k (Waid, 2011), down 51%. "
            "Amazing Spider-Man held between 110–125k from 1999 through 2018 on confirmed Comichron data, "
            "the only title in this set without a meaningful downward trend across the same period. "
            "Captain America and Thor figures are estimates derived from Comichron's monthly charts; "
            "see the Appendix for confidence classifications. "
            "The ASM 2022 data point (170k) is a PRH estimate and carries wider error bars."
        )

        prose("""
        <p>
        Why does Spider-Man hold when comparably well-crafted titles don't? The data can't answer
        that directly, but the pattern is consistent with something that is easy to overlook in a
        sales analysis: <strong>readers aren't just buying Spider-Man. They're buying Peter Parker.</strong>
        </p>
        <p>
        Most Marvel characters are defined primarily by their powers, their costume, or their
        mission. Captain America is the shield and the ideal. Daredevil is the radar sense and
        Hell's Kitchen. The Avengers are a rotating lineup organized around a concept. Strip away
        the costume and there isn't much story left to tell. Spider-Man is different. Peter Parker
        is the character: the broke photographer, the overcommitted grad student, the kid who can
        never catch a break. The powers are almost incidental. The stories that made Spider-Man a cultural
        force weren't about what he could do. They were about what it cost him to keep doing it.
        </p>
        <p>
        That depth of alter-ego investment insulates ASM from the worst effects of the relaunch
        cycle. A reader who cares about Peter Parker will show up for the new #1 because the
        character they love is still in it. A reader who cares about "Avengers" as a concept has
        less reason to follow when the roster, creative team, and direction all reset simultaneously.
        Daredevil had Frank Miller, Brian Michael Bendis, and Mark Waid, three of the strongest
        sustained creative runs in Marvel's catalog, and the readership still declined 50% over
        15 years. The relaunch cycle erodes even the best-built audiences over time.
        </p>
        <p>
        The implication for the business case is direct: <em>Peter Parker's resilience is not an
        argument for continuing to relaunch Amazing Spider-Man.</em> It's an argument for
        investing that same alter-ego depth into the characters who currently lack it.
        The Avengers lineup doesn't have a Peter Parker. Neither does most of the Marvel catalog.
        That is a gap that long-form character development is best positioned to fill. A new #1 doesn't do it.
        </p>
        """)

    pull_quote(
        "The readers who kept showing up for Avengers and Daredevil through every relaunch "
        "are exactly the audience worth building for. "
        "The data suggests there is an opportunity to hold more of them, longer."
    )
