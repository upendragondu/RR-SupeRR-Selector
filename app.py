from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------------
st.set_page_config(
    page_title="SupeRR Selector | Pressure Analytics",
    page_icon="🏏",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
PINK = "#C2185B"
PALE_PINK = "#FCE4EC"

# White background, black text, dark-pink highlights.
st.markdown(
    """
    <style>
      .stApp { background: #FFFFFF; color: #111111; }
      h1, h2, h3, h4, p, label, span { color: #111111; }
      div[data-testid="stMetric"] {
        background: #FFF4F8;
        border: 1px solid #F1B6CE;
        padding: 12px;
        border-radius: 10px;
      }
      div[data-testid="stMetric"] label,
      div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #111111 !important;
      }
      .pink-rule {
        height: 4px;
        background: #C2185B;
        border-radius: 5px;
        margin: 8px 0 18px 0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# LOAD THE ACTUAL FINAL CSV FILES
# ---------------------------------------------------------
@st.cache_data
def load_csv(filename):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        return None
    return pd.read_csv(file_path)


batters = load_csv("batting_rankings_final.csv")
bowlers = load_csv("bowling_rankings_final.csv")

missing_files = [
    name for name in [
        "batting_rankings_final.csv",
        "bowling_rankings_final.csv",
    ]
    if not (OUTPUT_DIR / name).exists()
]

if missing_files:
    st.error("Required ranking CSV files are missing from the outputs folder.")
    st.write(missing_files)
    st.code(
        "RR_super_selector/\n"
        "├── app.py\n"
        "└── outputs/\n"
        "    ├── batting_rankings_final.csv\n"
        "    └── bowling_rankings_final.csv"
    )
    st.stop()

if batters is None or bowlers is None:
    st.error("Could not read the ranking CSV files.")
    st.stop()

required_batter_columns = {
    "striker_id", "striker_name", "batting_score",
    "formats", "pressure_runs", "pressure_balls", "pressure_matches"
}
required_bowler_columns = {
    "bowler_id", "bowler_name", "bowling_score",
    "formats", "pressure_wickets", "pressure_legal_balls", "pressure_matches"
}

if not required_batter_columns.issubset(batters.columns):
    st.error(f"Unexpected batting CSV columns: {list(batters.columns)}")
    st.stop()

if not required_bowler_columns.issubset(bowlers.columns):
    st.error(f"Unexpected bowling CSV columns: {list(bowlers.columns)}")
    st.stop()

# Use final Version 2 scores; do not calculate a new ranking.
batters = batters.sort_values("batting_score", ascending=False).reset_index(drop=True)
bowlers = bowlers.sort_values("bowling_score", ascending=False).reset_index(drop=True)

top_batters = batters.head(10).copy()
top_bowlers = bowlers.head(10).copy()


# ---------------------------------------------------------
# HEADER + OVERVIEW
# ---------------------------------------------------------
st.title("🏏 SupeRR Selector")
st.subheader("Most Reliable Players Under Pressure")
st.markdown('<div class="pink-rule"></div>', unsafe_allow_html=True)

st.write(
    "A data-driven shortlist of IPL and Men's T20I players based on "
    "their performance in high-pressure second-innings chases (2022–2026)."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Batters analysed", len(batters))
c2.metric("Bowlers analysed", len(bowlers))
c3.metric("IPL high-pressure deliveries", "27.46%")
c4.metric("T20I high-pressure deliveries", "25.13%")

st.markdown("---")


# ---------------------------------------------------------
# PRESSURE DISTRIBUTION - SIMPLE PROGRESS BARS
# ---------------------------------------------------------
st.header("High-Pressure Delivery Distribution")
left, right = st.columns(2)

with left:
    st.markdown("**IPL**")
    st.progress(0.2746, text="27.46% high-pressure deliveries")

with right:
    st.markdown("**Men's T20I**")
    st.progress(0.2513, text="25.13% high-pressure deliveries")

st.caption(
    "High pressure is defined as required run rate ≥ 12, OR at least "
    "6 wickets lost with required run rate ≥ 9. Analysis covers "
    "second-innings chases."
)

st.markdown("---")


# ---------------------------------------------------------
# TOP 10 BATTERS
# ---------------------------------------------------------
st.header("🏏 Top 10 Pressure Batters")
st.caption("Ranked using the final Version 2 batting score.")

batter_display = top_batters[
    [
        "striker_name", "batting_score", "formats",
        "pressure_runs", "pressure_balls", "pressure_matches"
    ]
].copy()

batter_display.insert(0, "Rank", range(1, len(batter_display) + 1))
batter_display = batter_display.rename(
    columns={
        "striker_name": "Batter",
        "batting_score": "Score",
        "formats": "Formats",
        "pressure_runs": "Pressure Runs",
        "pressure_balls": "Pressure Balls",
        "pressure_matches": "Pressure Matches",
    }
)
batter_display["Score"] = batter_display["Score"].round(2)

st.dataframe(
    batter_display,
    width="stretch",
    hide_index=True,
)

batter_chart_data = top_batters[["striker_name", "batting_score"]].copy()
batter_chart_data["batting_score"] = pd.to_numeric(
    batter_chart_data["batting_score"], errors="coerce"
)
batter_chart_data = batter_chart_data.sort_values("batting_score", ascending=True)

fig_batters = px.bar(
    batter_chart_data,
    x="batting_score",
    y="striker_name",
    orientation="h",
    text="batting_score",
    color_discrete_sequence=[PINK],
)
fig_batters.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside",
    cliponaxis=False,
)
fig_batters.update_layout(
    title="Top 10 Batting Scores",
    template="plotly_white",
    height=430,
    margin=dict(l=15, r=65, t=55, b=20),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(color="#111111"),
    xaxis=dict(
        title="Batting score",
        range=[0, 105],
        gridcolor="#F2D7E2",
        color="#111111",
    ),
    yaxis=dict(title="", automargin=True, color="#111111"),
    showlegend=False,
)
st.plotly_chart(fig_batters, width="stretch")


# ---------------------------------------------------------
# TOP 10 BOWLERS
# ---------------------------------------------------------
st.markdown("---")
st.header("🎯 Top 10 Pressure Bowlers")
st.caption("Ranked using the final Version 2 bowling score.")

bowler_display = top_bowlers[
    [
        "bowler_name", "bowling_score", "formats",
        "pressure_wickets", "pressure_legal_balls", "pressure_matches"
    ]
].copy()

bowler_display.insert(0, "Rank", range(1, len(bowler_display) + 1))
bowler_display = bowler_display.rename(
    columns={
        "bowler_name": "Bowler",
        "bowling_score": "Score",
        "formats": "Formats",
        "pressure_wickets": "Pressure Wickets",
        "pressure_legal_balls": "Pressure Legal Balls",
        "pressure_matches": "Pressure Matches",
    }
)
bowler_display["Score"] = bowler_display["Score"].round(2)

st.dataframe(
    bowler_display,
    width="stretch",
    hide_index=True,
)

bowler_chart_data = top_bowlers[["bowler_name", "bowling_score"]].copy()
bowler_chart_data["bowling_score"] = pd.to_numeric(
    bowler_chart_data["bowling_score"], errors="coerce"
)
bowler_chart_data = bowler_chart_data.sort_values("bowling_score", ascending=True)

fig_bowlers = px.bar(
    bowler_chart_data,
    x="bowling_score",
    y="bowler_name",
    orientation="h",
    text="bowling_score",
    color_discrete_sequence=[PINK],
)
fig_bowlers.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside",
    cliponaxis=False,
)
fig_bowlers.update_layout(
    title="Top 10 Bowling Scores",
    template="plotly_white",
    height=430,
    margin=dict(l=15, r=65, t=55, b=20),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(color="#111111"),
    xaxis=dict(
        title="Bowling score",
        range=[0, 105],
        gridcolor="#F2D7E2",
        color="#111111",
    ),
    yaxis=dict(title="", automargin=True, color="#111111"),
    showlegend=False,
)
st.plotly_chart(fig_bowlers, width="stretch")


# ---------------------------------------------------------
# OPTIONAL PLAYER SEARCH - ON SAME PAGE, COLLAPSED
# ---------------------------------------------------------
st.markdown("---")
with st.expander("Search and inspect a player"):
    player_type = st.radio(
        "Choose player category",
        ["Batters", "Bowlers"],
        horizontal=True,
    )

    if player_type == "Batters":
        source = batters
        player_col = "striker_name"
        score_col = "batting_score"
        stat_cols = [
            "striker_id", "striker_name", "batting_score",
            "formats", "pressure_runs", "pressure_balls", "pressure_matches"
        ]
    else:
        source = bowlers
        player_col = "bowler_name"
        score_col = "bowling_score"
        stat_cols = [
            "bowler_id", "bowler_name", "bowling_score",
            "formats", "pressure_wickets", "pressure_legal_balls", "pressure_matches"
        ]

    search_name = st.text_input("Enter player name")
    matches = source[
        source[player_col].astype(str).str.contains(
            search_name, case=False, na=False
        )
    ] if search_name else source

    st.caption(f"{len(matches)} matching player(s)")
    st.dataframe(matches[stat_cols], width="stretch", hide_index=True)


# ---------------------------------------------------------
# METHODOLOGY - ON SAME PAGE, COLLAPSED
# ---------------------------------------------------------
with st.expander("View pressure definition and scoring methodology"):
    st.markdown("**High-pressure condition**")
    st.latex(
        r"(RRR \\geq 12)\\quad\\text{OR}\\quad"
        r"(\\text{Wickets lost}\\geq 6\\;\\text{AND}\\;RRR\\geq 9)"
    )

    m1, m2 = st.columns(2)
    with m1:
        st.markdown("**Batting score weights**")
        st.write(
            "- Pressure strike rate: 25%\n"
            "- Pressure average: 15%\n"
            "- Strike-rate difference: 20%\n"
            "- Pressure runs: 20%\n"
            "- Pressure matches: 10%\n"
            "- Pressure balls: 10%"
        )
    with m2:
        st.markdown("**Bowling score weights**")
        st.write(
            "- Pressure economy: 25%\n"
            "- Economy difference: 20%\n"
            "- Pressure bowling strike rate: 20%\n"
            "- Pressure wickets: 20%\n"
            "- Pressure matches: 10%\n"
            "- Pressure legal balls: 5%"
        )

    st.write(
        "Format-specific percentile scores are calculated separately for IPL "
        "and T20I. Scores are averaged for players appearing in both formats. "
        "The dashboard displays the saved final rankings and does not recalculate them."
    )
    st.warning(
        "This analysis measures pressure during second-innings chases; "
        "it does not cover every possible match-pressure situation."
    )


st.markdown("---")
st.caption("SupeRR Selector Season 2 • Round 1 • Pressure Performance Analysis")
