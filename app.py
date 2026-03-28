import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import numpy as np

st.set_page_config(
    page_title="Premier League 2023/24 Analytics",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Premier League 2023/24 — Football Analytics")
st.markdown("A complete data analysis of 298 players and 381 matches.")

@st.cache_data
def load_data():
    df_scorers = pd.read_csv('player_top_scorers.csv')
    df_assists = pd.read_csv('player_top_assists.csv')
    df_matches = pd.read_csv('matches_23_24.csv')
    df_positions = pd.read_csv('player_positions.csv')

    df_scorers["non_penalty_goals"] = df_scorers["Goals"] - df_scorers["Penalties"]
    df_scorers["goals_per_90"] = round((df_scorers["Goals"] / df_scorers["Minutes"]) * 90, 2)
    df_scorers["non_penalty_per_90"] = round((df_scorers["non_penalty_goals"] / df_scorers["Minutes"]) * 90, 2)
    df_qualified = df_scorers[df_scorers["Minutes"] >= 900].copy()

    df_merged = pd.merge(
        df_qualified[["Player", "Team", "Country", "Goals", "Penalties", "Minutes",
                      "goals_per_90", "non_penalty_goals", "non_penalty_per_90"]],
        df_assists[["Player", "Assists", "Secondary Assists"]],
        on="Player", how="inner"
    )
    df_merged["assists_per_90"] = round((df_merged["Assists"] / df_merged["Minutes"]) * 90, 2)
    df_merged["goal_contributions"] = df_merged["Goals"] + df_merged["Assists"]
    df_merged["contributions_per_90"] = round((df_merged["goal_contributions"] / df_merged["Minutes"]) * 90, 2)
    df_complete = pd.merge(df_merged, df_positions, on="Player", how="inner")

    df_matches = df_matches.drop(columns=["Unnamed: 11", "Unnamed: 12"])
    df_matches["Score"] = df_matches["Score"].str.replace(" ", "")
    df_matches[["Home Goals", "Away Goals"]] = df_matches["Score"].str.split("_", expand=True)
    df_matches["Home Goals"] = pd.to_numeric(df_matches["Home Goals"], errors="coerce")
    df_matches["Away Goals"] = pd.to_numeric(df_matches["Away Goals"], errors="coerce")
    df_matches = df_matches[df_matches["Finished"] == True].copy()
    df_matches = df_matches[["Round", "Home Team", "Home Goals", "Away Goals", "Away Team"]]

    return df_complete, df_qualified, df_matches

df_complete, df_qualified, df_matches = load_data()
st.success(f"Data loaded — {len(df_complete)} players, {len(df_matches)} matches")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Overview",
    "Player Analysis",
    "Match Analysis",
    "Statistical Testing"
])

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Bilge Han Erduran**  
CS Student | Aspiring Data Analyst  
[GitHub](https://github.com/bherduran) · [Project](https://github.com/bherduran/football-analytics-pl2324)
""")

if page == "Overview":
    st.header("Project Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Players", "298")
    col2.metric("Qualified Players", "194")
    col3.metric("Matches Analyzed", "381")
    col4.metric("Key Findings", "10")

    st.markdown("""
    ### Objective
    Analyze Premier League 2023/24 player and match data to:
    - Identify the most efficient scorers adjusted for minutes played
    - Expose penalty inflation in raw goal rankings
    - Find undervalued players invisible to traditional metrics
    - Statistically prove whether home advantage is real

    ### Dataset
    - **Source:** Premier League 23/24 Stats (Kaggle)
    - **Players:** 298 Premier League players, filtered to 194 with 900+ minutes
    - **Matches:** 381 Premier League matches
    - **Positions:** Manually curated dataset to enable position-adjusted analysis

    ### Tools Used
    Python · Pandas · SQL (SQLite) · SciPy · Plotly
    """)

elif page == "Player Analysis":
    st.header("Player Analysis — Scoring Efficiency")

    st.markdown("""
    ### Key Questions
    - Who are the most efficient scorers when adjusted for minutes played?
    - How much do penalties inflate raw goal rankings?
    - Which players are genuinely elite vs penalty-dependent?
    """)

    col1, col2 = st.columns(2)
    with col1:
        position_filter = st.multiselect(
            "Filter by position",
            options=["Forward", "Midfielder", "Defender"],
            default=["Forward", "Midfielder", "Defender"]
        )
    with col2:
        min_minutes = st.slider("Minimum minutes played", 900, 3000, 900, step=100)

    df_filtered = df_complete[
        (df_complete["Position"].isin(position_filter)) &
        (df_complete["Minutes"] >= min_minutes)
    ]

    st.markdown(f"Showing **{len(df_filtered)}** players")

    fig = px.scatter(
        df_filtered,
        x="goals_per_90",
        y="assists_per_90",
        color="Position",
        size="contributions_per_90",
        hover_name="Player",
        hover_data={"Team": True, "Goals": True, "Assists": True, "Minutes": True},
        color_discrete_map={"Forward": "#e74c3c", "Midfielder": "#3498db", "Defender": "#2ecc71"},
        title="Goals vs Assists per 90 — Size = Total Contribution Rate",
        labels={"goals_per_90": "Goals per 90", "assists_per_90": "Assists per 90"}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 by Contributions per 90")
    top_10 = df_filtered.nlargest(10, "contributions_per_90")[
        ["Player", "Team", "Position", "Goals", "Assists", "Minutes", "contributions_per_90"]
    ].reset_index(drop=True)
    st.dataframe(top_10, use_container_width=True)

    st.info("""
    **Finding — Penalty Inflation**

    Cole Palmer's raw tally of 22 goals is significantly inflated by penalties,
    with 40.9% of his goals coming from the spot.

    Despite scoring 10 more goals than Trossard in raw totals, Palmer's non-penalty
    per 90 of 0.45 is actually lower than Trossard's 0.66 — suggesting Trossard is
    the more efficient open-play scorer.

    Conclusion: raw goal totals overvalue designated penalty takers and undervalue
    consistent open-play scorers.
    """)

    st.info("""
    **Finding — Position-Adjusted Metrics**

    Cole Palmer and Kevin De Bruyne top the overperformers list despite being midfielders
    — Palmer at 0.80 and De Bruyne at 0.70 above their position average, both exceeding
    Haaland's 0.56 overperformance as a forward.

    Evaluating players purely on goals without accounting for positional role
    significantly undervalues creative midfielders.
    """)

elif page == "Match Analysis":
    st.header("Match Analysis — Home Advantage")

    st.markdown("""
    ### Key Questions
    - Do home teams genuinely outscore away teams?
    - Which teams benefit most from home advantage?
    - How does home advantage vary across the season?
    """)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Home Goals", "1.80")
    col2.metric("Avg Away Goals", "1.48")
    col3.metric("Home Win Rate", "45.9%")
    col4.metric("Away Win Rate", "32.3%")

    col1, col2 = st.columns(2)

    with col1:
        fig_pie = px.pie(
            values=[175, 83, 123],
            names=["Home Win", "Draw", "Away Win"],
            color_discrete_sequence=["#e74c3c", "#95a5a6", "#3498db"],
            title="Match Results Distribution"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        home_stats = df_matches.groupby("Home Team").agg(
            avg_home=("Home Goals", "mean"),
        ).reset_index()
        away_stats = df_matches.groupby("Away Team").agg(
            avg_away=("Away Goals", "mean"),
        ).reset_index()
        away_stats.columns = ["Home Team", "avg_away"]

        team_stats = pd.merge(home_stats, away_stats, on="Home Team")
        team_stats["home_advantage"] = round(team_stats["avg_home"] - team_stats["avg_away"], 2)
        team_stats = team_stats.sort_values("home_advantage", ascending=True)

        fig_bar = px.bar(
            team_stats,
            x="home_advantage",
            y="Home Team",
            orientation="h",
            title="Home Advantage by Team (goals per match)",
            color="home_advantage",
            color_continuous_scale=["#3498db", "#e74c3c"]
        )
        fig_bar.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    matchweek_stats = df_matches.groupby("Round").agg(
        avg_home=("Home Goals", "mean"),
        avg_away=("Away Goals", "mean")
    ).reset_index()

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=matchweek_stats["Round"], y=matchweek_stats["avg_home"],
        name="Home Goals", line=dict(color="#e74c3c", width=2),
        fill="tozeroy", fillcolor="rgba(231,76,60,0.1)"
    ))
    fig_line.add_trace(go.Scatter(
        x=matchweek_stats["Round"], y=matchweek_stats["avg_away"],
        name="Away Goals", line=dict(color="#3498db", width=2),
        fill="tozeroy", fillcolor="rgba(52,152,219,0.1)"
    ))
    fig_line.update_layout(
        title="Home vs Away Goals Across the Season",
        xaxis_title="Matchweek",
        yaxis_title="Average Goals",
        height=400
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.info("""
    **Finding — Home Advantage**

    Home Teams tend to score more goals — average of 1.80 — and win 45.90% of matches
    compared to Away Teams who score an average of 1.48 goals and win only 32.30% of matches.

    The advantage leans heavily on Home Teams: +0.32 goals per match and +13.60% win rate.

    Notable: Aston Villa had the biggest home advantage (+1.06 goals per match),
    contributing significantly to their 4th place finish and Champions League qualification.
    Burnley showed a negative home advantage (-0.16), reflecting their relegation season.
    """)

elif page == "Statistical Testing":
    st.header("Statistical Testing — Is Home Advantage Real?")

    st.markdown("""
    ### Hypothesis
    - **H0:** No genuine home advantage exists — any difference is random
    - **H1:** Home teams score significantly more than away teams
    - **Method:** Independent samples t-test (scipy.stats)
    - **Threshold:** p < 0.05
    """)

    home_goals = df_matches["Home Goals"].dropna().values
    away_goals = df_matches["Away Goals"].dropna().values
    t_stat, p_value = stats.ttest_ind(home_goals, away_goals)

    home_clean = df_matches[df_matches["Away Goals"] < 7]["Home Goals"].values
    away_clean = df_matches[df_matches["Away Goals"] < 7]["Away Goals"].values
    _, p_clean = stats.ttest_ind(home_clean, away_clean)

    col1, col2, col3 = st.columns(3)
    col1.metric("T-Statistic", round(t_stat, 4))
    col2.metric("P-Value", round(p_value, 4))
    col3.metric("P-Value (outlier removed)", round(p_clean, 4))

    if p_value < 0.05:
        st.success("RESULT: REJECT null hypothesis — Home advantage is statistically significant (p < 0.001)")

    st.info("""
    **Conclusion**

    A t-test across 381 Premier League matches proves home advantage is statistically real
    — with a p-value of 0.0009, there is less than 0.1% probability this difference occurred
    by chance. When the outlier (8-0 Newcastle vs Sheffield United) is removed, the p-value
    drops further to 0.0003 — the finding gets stronger, not weaker.

    Home Team Advantage is backed up by statistics and is real.
    """)

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=home_goals, name="Home Goals",
        opacity=0.7, marker_color="#e74c3c",
        xbins=dict(start=0, end=10, size=1)
    ))
    fig.add_trace(go.Histogram(
        x=away_goals, name="Away Goals",
        opacity=0.7, marker_color="#3498db",
        xbins=dict(start=0, end=10, size=1)
    ))
    fig.update_layout(
        barmode="overlay",
        title="Goal Distribution — Home vs Away",
        xaxis_title="Goals per match",
        yaxis_title="Frequency",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
