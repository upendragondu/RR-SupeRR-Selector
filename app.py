
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

# ---------------------------------------------------------
# CUSTOM DESIGN
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background: #FFFFFF;
            color: #111111;
        }

        h1, h2, h3, h4, p, label {
            color: #111111;
        }

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

        .section-note {
            color: #666666;
            font-size: 14px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# LOAD FINAL COMBINED RANKING FILES
# ---------------------------------------------------------
@st.cache_data
def load_csv(filename):
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        return None

    return pd.read_csv(file_path)


batters = load_csv("final_top_10_batters.csv")
bowlers = load_csv("final_top_10_bowlers.csv")

missing_files = [
    filename
    for filename in [
        "final_top_10_batters.csv",
        "final_top_10_bowlers.csv",
    ]
    if not (OUTPUT_DIR / filename).exists()
]

if missing_files:
    st.error("Final ranking files are missing.")

    st.write("Missing files:", missing_files)

    st.code(
        "RR_super_selector/\n"
        "├── app.py\n"
        "└── outputs/\n"
        "    ├── final_top_10_batters.csv\n"
        "    └── final_top_10_bowlers.csv"
    )

    st.stop()

if batters is None or bowlers is None:
    st.error("Unable to read the final ranking CSV files.")
    st.stop()


# ---------------------------------------------------------
# VALIDATE REQUIRED COLUMNS
# ---------------------------------------------------------
required_batter_columns = {
    "striker_name",
    "final_score",
    "pressure_runs",
    "pressure_sr",
    "pressure_matches",
}

required_bowler_columns = {
    "bowler_name",
    "final_score",
    "pressure_wickets",
    "pressure_economy",
    "pressure_matches",
}

if not required_batter_columns.issubset(batters.columns):
    st.error(
        "Unexpected batting CSV structure. "
        f"Available columns: {list(batters.columns)}"
    )
    st.stop()

if not required_bowler_columns.issubset(bowlers.columns):
    st.error(
        "Unexpected bowling CSV structure. "
        f"Available columns: {list(bowlers.columns)}"
    )
    st.stop()


# ---------------------------------------------------------
# PREPARE FINAL RANKINGS
# ---------------------------------------------------------
batters["final_score"] = pd.to_numeric(
    batters["final_score"], errors="coerce"
)

bowlers["final_score"] = pd.to_numeric(
    bowlers["final_score"], errors="coerce"
)

batters = batters.sort_values(
    "final_score", ascending=False
).reset_index(drop=True)

bowlers = bowlers.sort_values(
    "final_score", ascending=False
).reset_index(drop=True)

top_batters = batters.head(10).copy()
top_bowlers = bowlers.head(10).copy()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.title("🏏 SupeRR Selector")

st.subheader("Identifying the Most Reliable Players Under Pressure")

st.markdown(
    '<div class="pink-rule"></div>',
    unsafe_allow_html=True,
)

st.write(
    "A data-driven analysis of T20 players who performed in "
    "high-pressure second-innings chases between 2022 and 2026."
)

st.caption(
    "Competition: Rajasthan Royals IPL 2027 Auction Strategy | "
    "Formats: IPL and Men's T20 Internationals"
)

st.markdown("---")


# ---------------------------------------------------------
# OVERVIEW METRICS
# ---------------------------------------------------------
st.header("Analysis Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Top 10 Batters",
    len(top_batters),
)

c2.metric(
    "Top 10 Bowlers",
    len(top_bowlers),
)

c3.metric(
    "Pressure Deliveries",
    "25,729",
)

c4.metric(
    "Pressure Percentage",
    "27.04%",
)

st.markdown("---")


# ---------------------------------------------------------
# PRESSURE DISTRIBUTION
# ---------------------------------------------------------
st.header("High-Pressure Delivery Distribution")

st.write(
    "We analysed 95,145 deliveries from second-innings chases. "
    "Each delivery was classified as either high pressure or normal pressure."
)

pressure_data = pd.DataFrame(
    {
        "Delivery Type": [
            "High Pressure",
            "Normal Pressure",
        ],
        "Deliveries": [
            25729,
            69416,
        ],
    }
)

pressure_data["Percentage"] = (
    pressure_data["Deliveries"]
    / pressure_data["Deliveries"].sum()
    * 100
)

fig_pressure = px.pie(
    pressure_data,
    names="Delivery Type",
    values="Deliveries",
    hole=0.55,
    color="Delivery Type",
    color_discrete_map={
        "High Pressure": "#C2185B",
        "Normal Pressure": "#8ECAE6",
    },
)

fig_pressure.update_traces(
    textposition="inside",
    texttemplate="%{label}<br>%{percent}",
    hovertemplate=(
        "%{label}<br>"
        "Deliveries: %{value:,}<br>"
        "Percentage: %{percent}<extra></extra>"
    ),
)

fig_pressure.update_layout(
    template="plotly_white",
    height=390,
    paper_bgcolor="#FFFFFF",
    font=dict(color="#111111"),
    legend=dict(orientation="h", y=-0.1),
    margin=dict(t=30, b=40, l=20, r=20),
)

st.plotly_chart(fig_pressure, width="stretch")

p1, p2, p3 = st.columns(3)

p1.metric("Total Chase Deliveries", "95,145")
p2.metric("High-Pressure Deliveries", "25,729")
p3.metric("Normal-Pressure Deliveries", "69,416")

st.caption(
    "High pressure: Required run rate ≥ 12, OR at least "
    "6 wickets lost with required run rate ≥ 9."
)

st.markdown("---")


# ---------------------------------------------------------
# TOP 10 BATTERS
# ---------------------------------------------------------
st.header("🏏 Top 10 Pressure Batters")

st.caption(
    "Ranked using combined eligible IPL and T20I performance statistics."
)

batter_display_columns = [
    "striker_name",
    "final_score",
    "pressure_runs",
    "pressure_sr",
    "pressure_matches",
]

batter_display = top_batters[
    batter_display_columns
].copy()

batter_display.insert(
    0,
    "Rank",
    range(1, len(batter_display) + 1),
)

batter_display = batter_display.rename(
    columns={
        "striker_name": "Batter",
        "final_score": "Final Score",
        "pressure_runs": "Pressure Runs",
        "pressure_sr": "Pressure Strike Rate",
        "pressure_matches": "Pressure Matches",
    }
)

batter_display["Final Score"] = (
    batter_display["Final Score"].round(2)
)

batter_display["Pressure Strike Rate"] = (
    batter_display["Pressure Strike Rate"].round(2)
)

st.dataframe(
    batter_display,
    width="stretch",
    hide_index=True,
)

# Batting chart
batter_chart_data = top_batters[
    ["striker_name", "final_score"]
].copy()

batter_chart_data = batter_chart_data.sort_values(
    "final_score",
    ascending=True,
)

fig_batters = px.bar(
    batter_chart_data,
    x="final_score",
    y="striker_name",
    orientation="h",
    text="final_score",
    color_discrete_sequence=[PINK],
)

fig_batters.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside",
    cliponaxis=False,
)

fig_batters.update_layout(
    title="Final Top 10 Batting Scores",
    template="plotly_white",
    height=440,
    margin=dict(l=15, r=65, t=55, b=20),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(color="#111111"),
    xaxis=dict(
        title="Final Score",
        range=[0, 105],
        gridcolor="#F2D7E2",
    ),
    yaxis=dict(
        title="",
        automargin=True,
    ),
    showlegend=False,
)

st.plotly_chart(fig_batters, width="stretch")


# ---------------------------------------------------------
# TOP 10 BOWLERS
# ---------------------------------------------------------
st.markdown("---")

st.header("🎯 Top 10 Pressure Bowlers")

st.caption(
    "Ranked using combined eligible IPL and T20I performance statistics."
)

bowler_display_columns = [
    "bowler_name",
    "final_score",
    "pressure_wickets",
    "pressure_economy",
    "pressure_matches",
]

bowler_display = top_bowlers[
    bowler_display_columns
].copy()

bowler_display.insert(
    0,
    "Rank",
    range(1, len(bowler_display) + 1),
)

bowler_display = bowler_display.rename(
    columns={
        "bowler_name": "Bowler",
        "final_score": "Final Score",
        "pressure_wickets": "Pressure Wickets",
        "pressure_economy": "Pressure Economy",
        "pressure_matches": "Pressure Matches",
    }
)

bowler_display["Final Score"] = (
    bowler_display["Final Score"].round(2)
)

bowler_display["Pressure Economy"] = (
    bowler_display["Pressure Economy"].round(2)
)

st.dataframe(
    bowler_display,
    width="stretch",
    hide_index=True,
)

# Bowling chart
bowler_chart_data = top_bowlers[
    ["bowler_name", "final_score"]
].copy()

bowler_chart_data = bowler_chart_data.sort_values(
    "final_score",
    ascending=True,
)

fig_bowlers = px.bar(
    bowler_chart_data,
    x="final_score",
    y="bowler_name",
    orientation="h",
    text="final_score",
    color_discrete_sequence=[PINK],
)

fig_bowlers.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside",
    cliponaxis=False,
)

fig_bowlers.update_layout(
    title="Final Top 10 Bowling Scores",
    template="plotly_white",
    height=440,
    margin=dict(l=15, r=65, t=55, b=20),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(color="#111111"),
    xaxis=dict(
        title="Final Score",
        range=[0, 105],
        gridcolor="#F2D7E2",
    ),
    yaxis=dict(
        title="",
        automargin=True,
    ),
    showlegend=False,
)

st.plotly_chart(fig_bowlers, width="stretch")


# ---------------------------------------------------------
# PLAYER SEARCH
# ---------------------------------------------------------
st.markdown("---")

with st.expander("🔎 Search and inspect a player"):

    player_type = st.radio(
        "Select player category",
        ["Batters", "Bowlers"],
        horizontal=True,
    )

    if player_type == "Batters":
        source = batters
        player_col = "striker_name"
    else:
        source = bowlers
        player_col = "bowler_name"

    search_name = st.text_input(
        "Enter player name",
        placeholder="Example: Rinku Singh",
    )

    if search_name:
        matches = source[
            source[player_col].astype(str).str.contains(
                search_name,
                case=False,
                na=False,
            )
        ]
    else:
        matches = source

    st.caption(f"{len(matches)} matching player(s)")

    st.dataframe(
        matches,
        width="stretch",
        hide_index=True,
    )


# ---------------------------------------------------------
# METHODOLOGY
# ---------------------------------------------------------
st.markdown("---")

with st.expander("📊 View pressure definition and scoring methodology"):

    st.subheader("1. Identifying High Pressure")

    st.latex(
        r"(RRR \geq 12)"
        r"\quad \text{OR} \quad"
        r"(Wickets\ Lost \geq 6"
        r"\text{ AND } RRR \geq 9)"
    )

    st.write(
        "Required run rate is calculated using the runs needed "
        "and legal balls remaining before the current delivery."
    )

    st.subheader("2. Batting Score Weights")

    st.write(
        """
        - Pressure Strike Rate: 25%
        - Pressure Batting Average: 15%
        - Strike-Rate Difference: 20%
        - Pressure Runs: 20%
        - Pressure Matches: 10%
        - Pressure Balls: 10%
        """
    )

    st.subheader("3. Bowling Score Weights")

    st.write(
        """
        - Pressure Economy: 25%
        - Economy Improvement: 20%
        - Pressure Bowling Strike Rate: 20%
        - Pressure Wickets: 20%
        - Pressure Matches: 10%
        - Pressure Legal Balls: 5%
        """
    )

    st.subheader("4. Combined Ranking Method")

    st.write(
        """
        Eligible IPL and T20I player-level statistics were combined first.
        The relevant batting and bowling rates were recalculated from
        the combined totals.

        Percentile scores were then calculated across the combined
        eligible player pool. The weighted percentile scores were used
        to produce the final Top 10 batters and Top 10 bowlers.
        """
    )

    st.subheader("5. Minimum Sample Requirements")

    st.write(
        """
        **Batters**
        - At least 30 pressure balls.
        - At least 5 pressure matches.
        - At least 30 normal balls.
        - At least 5 normal matches.

        **Bowlers**
        - At least 60 pressure legal balls.
        - At least 5 pressure matches.
        - At least 60 normal legal balls.
        - At least 5 normal matches.
        - At least one pressure wicket.
        """
    )

    st.subheader("6. Important Limitations")

    st.warning(
        """
        This model evaluates second-innings chase performance only.
        The final candidate pool was built from existing format-wise
        eligible player records. Players excluded from both original
        format-wise eligible lists were not reconsidered.

        The final score is a relative historical ranking, not a
        prediction or guarantee of future performance.
        """
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")

st.caption(
    "SupeRR Selector Season 2 | Round 1 | "
    "Rajasthan Royals IPL 2027 Auction Strategy | "
    "Analysis Period: 2022–2026"
)
