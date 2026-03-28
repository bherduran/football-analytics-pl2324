# Football Analytics — Premier League 2023/24

A complete end-to-end data analysis project built in Python, covering player performance, match statistics, and statistical testing on real Premier League data.

## Project Overview

This project analyzes 298 players and 381 matches from the 2023/24 Premier League season to answer real analytical questions using Python, Pandas, SQL, and statistics.

## Key Findings

1. **Penalty inflation** — Cole Palmer scored 40.9% of goals from penalties. Trossard and Richarlison are more efficient open-play scorers despite lower raw tallies.

2. **Position-adjusted metrics reveal a different hierarchy** — Cole Palmer and De Bruyne overperform their position average by 0.80 and 0.70 respectively — more than Haaland's 0.56 as a forward.

3. **Injury-adjusted projections** — De Bruyne projected over a full season would produce 32 contributions, surpassing Salah's actual total of 30.

4. **Undervalued players identified** — Beto (Everton, 0.29 non-penalty per 90) and Alfie Doughty (Luton, 8 assists) represent strong hidden value.

5. **Home advantage statistically proven** — p-value of 0.0009 across 381 matches. Home teams win 45.9% vs 32.3% for away teams. Result is robust to outlier removal (p = 0.0003).

6. **Home advantage varies dramatically by team** — Aston Villa +1.06 goals per home match vs Burnley -0.16.

## Tools & Technologies

| Tool | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data manipulation and analysis |
| SQLite + SQL | Structured querying of match data |
| SciPy | Statistical hypothesis testing |
| Matplotlib + Seaborn | Static visualizations |
| Plotly | Interactive charts and dashboards |

## Dataset

- **Source:** Premier League 23/24 Stats — Kaggle (Kamran Ali)
- **Players:** 298 Premier League players
- **Matches:** 381 Premier League matches
- **Player positions:** Manually curated dataset

## How to Run

1. Clone the repository
2. Upload CSV files to Google Colab
3. Open `football_analytics_portfolio.ipynb`
4. Run all cells top to bottom

## Author

Bilge Han Erduran — CS Student | Aspiring Data Analyst
github.com/bherduran
