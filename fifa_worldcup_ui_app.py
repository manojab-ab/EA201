# fifa_worldcup_ui_app.py
"""
Improved Streamlit UI for FIFA World Cup winner prediction.
- Loads CSV (or uses default file if present under /mnt/data/WorldCupMatches (1).csv)
- Cleans data, creates team-level features per tournament year
- Trains models (Logistic Regression & Random Forest)
- Shows interactive Teams & Stats table
- Allows user to select teams and predict winner (probabilities + Monte Carlo simulation)
- Provides charts and CSV downloads
"""

import os
import io
from typing import List

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="FIFA World Cup Predictor — Interactive UI", layout="wide")

# -------------------------
# Utility functions
# -------------------------
@st.cache_data
def try_load_default():
    possible = [
        "/mnt/data/WorldCupMatches (1).csv",
        "/mnt/data/WorldCupMatches.csv",
        "/mnt/data/worldcup_matches.csv",
        "/mnt/data/worldcup.csv",
        "/mnt/data/cleaned_fifa.csv"
    ]
    for p in possible:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p)
                return df, p
            except Exception:
                continue
    return None, None

def read_uploaded(file):
    try:
        return pd.read_csv(file)
    except Exception:
        file.seek(0)
        return pd.read_excel(file)

def normalize_matches_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # map common column names to standard internal names
    col_map = {}
    for c in df.columns:
        lc = c.strip().lower()
        if 'home' in lc and 'team' in lc:
            col_map[c] = 'HomeTeam'
        elif 'away' in lc and 'team' in lc:
            col_map[c] = 'AwayTeam'
        elif ('home' in lc) and ('goal' in lc or 'score' in lc):
            col_map[c] = 'HomeGoals'
        elif ('away' in lc) and ('goal' in lc or 'score' in lc):
            col_map[c] = 'AwayGoals'
        elif lc == 'year':
            col_map[c] = 'Year'
        elif 'date' == lc or 'match date' in lc:
            col_map[c] = 'Date'
        elif 'stage' in lc or 'round' in lc:
            col_map[c] = 'Stage'
    df = df.rename(columns=col_map)
    # Year from Date if missing
    if 'Year' not in df.columns and 'Date' in df.columns:
        try:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Year'] = df['Date'].dt.year
        except Exception:
            pass
    # check required columns
    required = ['Year','HomeTeam','AwayTeam','HomeGoals','AwayGoals']
    for r in required:
        if r not in df.columns:
            raise ValueError(f"Could not find required column '{r}' after normalization. Found: {list(df.columns)}")
    df['HomeGoals'] = pd.to_numeric(df['HomeGoals'], errors='coerce').fillna(0).astype(int)
    df['AwayGoals'] = pd.to_numeric(df['AwayGoals'], errors='coerce').fillna(0).astype(int)
    # WinnerTeam
    def winner(r):
        if r['HomeGoals'] > r['AwayGoals']:
            return r['HomeTeam']
        elif r['AwayGoals'] > r['HomeGoals']:
            return r['AwayTeam']
        else:
            return 'Draw'
    df['WinnerTeam'] = df.apply(winner, axis=1)
    df = df.drop_duplicates().reset_index(drop=True)
    return df

@st.cache_data
def create_team_features(matches: pd.DataFrame) -> pd.DataFrame:
    matches = matches.copy()
    years = sorted(matches['Year'].dropna().unique())
    rows = []
    for year in years:
        sub = matches[matches['Year'] == year]
        teams = pd.unique(sub[['HomeTeam','AwayTeam']].values.ravel('K'))
        for t in teams:
            home = sub[sub['HomeTeam'] == t]
            away = sub[sub['AwayTeam'] == t]
            mp = len(home) + len(away)
            gf = home['HomeGoals'].sum() + away['AwayGoals'].sum()
            ga = home['AwayGoals'].sum() + away['HomeGoals'].sum()
            wins = ((home['HomeGoals'] > home['AwayGoals']).sum() +
                    (away['AwayGoals'] > away['HomeGoals']).sum())
            draws = ((home['HomeGoals'] == home['AwayGoals']).sum() +
                    (away['AwayGoals'] == away['HomeGoals']).sum())
            losses = mp - wins - draws
            gd = gf - ga
            win_rate = wins / mp if mp > 0 else 0
            avg_gf = gf / mp if mp > 0 else 0
            avg_ga = ga / mp if mp > 0 else 0
            past_tourns = len({y for y in matches.loc[((matches['HomeTeam']==t)|(matches['AwayTeam']==t)) & (matches['Year']<year),'Year'].unique()})
            rows.append({
                'Team': t,
                'Year': int(year),
                'matches_played': int(mp),
                'wins': int(wins),
                'draws': int(draws),
                'losses': int(losses),
                'goals_for': int(gf),
                'goals_against': int(ga),
                'goal_diff': int(gd),
                'win_rate': float(round(win_rate,3)),
                'avg_goals_for': float(round(avg_gf,3)),
                'avg_goals_against': float(round(avg_ga,3)),
                'past_tournaments': int(past_tourns)
            })
    tdf = pd.DataFrame(rows)
    # Ensure types
    return tdf

def label_winners(team_df: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    df = team_df.copy()
    df['is_winner'] = 0
    df['is_finalist'] = 0
    years = sorted(df['Year'].unique())
    for y in years:
        subs = matches[matches['Year'] == y]
        if subs.empty:
            continue
        # try find final by Stage if available
        final_row = None
        stage_cols = [c for c in subs.columns if 'stage' in c.lower() or 'round' in c.lower()]
        if stage_cols:
            for c in stage_cols:
                finals = subs[subs[c].str.contains('final', case=False, na=False)]
                if not finals.empty:
                    final_row = finals.iloc[-1]
                    break
        if final_row is None:
            # fallback to last match by date or last row
            if 'Date' in subs.columns:
                try:
                    subs['Date_parsed'] = pd.to_datetime(subs['Date'], errors='coerce')
                    final_row = subs.sort_values('Date_parsed').iloc[-1]
                except Exception:
                    final_row = subs.iloc[-1]
            else:
                final_row = subs.iloc[-1]
        winner_team = final_row.get('WinnerTeam', None)
        if winner_team and winner_team != 'Draw':
            df.loc[(df['Year']==y) & (df['Team']==winner_team), 'is_winner'] = 1
        # finalists
        try:
            ht = final_row.get('HomeTeam', None)
            at = final_row.get('AwayTeam', None)
            if ht:
                df.loc[(df['Year']==y) & (df['Team']==ht), 'is_finalist'] = 1
            if at:
                df.loc[(df['Year']==y) & (df['Team']==at), 'is_finalist'] = 1
        except Exception:
            pass
    return df

def prepare_model(team_df: pd.DataFrame, matches: pd.DataFrame, target='is_winner'):
    df = label_winners(team_df, matches)
    df = df[df['matches_played'] > 0].reset_index(drop=True)
    features = ['matches_played','wins','draws','losses','goals_for','goals_against','goal_diff','win_rate','avg_goals_for','avg_goals_against','past_tournaments']
    for f in features:
        if f not in df.columns:
            df[f] = 0
    X = df[features].fillna(0)
    y = df[target].fillna(0).astype(int)
    # train a simple robust pipeline: StandardScaler + RandomForest + LogisticRegression as backup
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42) if len(y.unique())>1 else (X,X,y,y)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    rf = RandomForestClassifier(n_estimators=200, random_state=42)
    rf.fit(Xs, y)
    lr = LogisticRegression(max_iter=1000)
    lr.fit(Xs, y)
    return {
        'scaler': scaler,
        'rf': rf,
        'lr': lr,
        'features': features,
        'model_df': df
    }

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode('utf-8')

# -------------------------
# App layout & behavior
# -------------------------
st.title("⚽ FIFA World Cup — Interactive Predictor (Improved UI)")
st.markdown("Upload historical matches CSV (or auto-load if present). Clean data, explore teams, choose teams and predict winner using ML + simulation.")

# Sidebar: data load options & controls
st.sidebar.header("Data & Modeling")
default_df, default_path = try_load_default()
if default_df is not None:
    st.sidebar.success(f"Found default file: {default_path}")
use_default = st.sidebar.button("Use default file") if default_df is not None else False
uploaded = st.sidebar.file_uploader("Upload matches CSV / XLSX", type=['csv','xlsx'])
if use_default:
    raw_df = default_df.copy()
elif uploaded is not None:
    try:
        raw_df = read_uploaded(uploaded)
    except Exception as e:
        st.sidebar.error(f"Could not read uploaded file: {e}")
        st.stop()
else:
    raw_df = None

if raw_df is None:
    st.info("No dataset loaded. You can upload a CSV or use a sample dataset to explore the UI.")
    if st.button("Use sample data to explore UI"):
        sample = {
            'Year':[2018,2018,2018,2018,2014,2014,2014,2014],
            'Date':['2018-07-15','2018-07-15','2018-07-15','2018-07-15','2014-07-13','2014-07-13','2014-07-13','2014-07-13'],
            'HomeTeam':['France','Croatia','Belgium','England','Germany','Argentina','Netherlands','Spain'],
            'AwayTeam':['Croatia','France','England','Belgium','Argentina','Germany','Spain','Netherlands'],
            'HomeGoals':[4,2,1,2,1,0,1,0],
            'AwayGoals':[2,1,0,1,2,1,0,1]
        }
        raw_df = pd.DataFrame(sample)
    else:
        st.stop()

# Clean dataset
try:
    matches = normalize_matches_columns(raw_df)
except Exception as e:
    st.error(f"Data normalization failed: {e}")
    st.stop()

# Display basic info & allow download of cleaned matches
st.subheader("Loaded dataset — preview")
c1, c2 = st.columns([2,1])
with c1:
    st.dataframe(matches.head(10))
with c2:
    st.write(f"Rows: {matches.shape[0]}")
    st.write(f"Columns: {matches.shape[1]}")
    st.download_button("Download cleaned matches CSV", data=df_to_csv_bytes(matches), file_name="cleaned_matches.csv", mime="text/csv")

# Create team-level features
team_df = create_team_features(matches)
st.markdown("---")

# Top area: select year to analyze
st.subheader("Teams & Stats")
years = sorted(team_df['Year'].unique())
if not years:
    st.error("No Year values found in the dataset.")
    st.stop()
sel_year = st.selectbox("Select tournament year", options=years, index=len(years)-1)

teams_for_year = team_df[team_df['Year'] == sel_year].copy()
teams_for_year = teams_for_year.sort_values(by='win_rate', ascending=False).reset_index(drop=True)
st.write(f"Teams found for year {sel_year}: {teams_for_year.shape[0]}")

# Two-column layout: left = teams table, right = controls & selected team info
left, right = st.columns([2.5,1])

with left:
    st.markdown("### All teams — stats table")
    # interactive table
    st.dataframe(teams_for_year.style.format({
        'win_rate':'{:.3f}',
        'avg_goals_for':'{:.2f}',
        'avg_goals_against':'{:.2f}'
    }), use_container_width=True)
    st.download_button("Download team features CSV", data=df_to_csv_bytes(teams_for_year), file_name=f"team_features_{sel_year}.csv", mime="text/csv")

with right:
    st.markdown("### Choose teams to evaluate")
    team_list = teams_for_year['Team'].tolist()
    selected = st.multiselect("Select teams (choose 2 or more)", options=team_list, default=team_list[:8])
    st.write(f"Selected {len(selected)} teams")
    st.markdown("**Prediction controls**")
    sim_runs = st.number_input("Simulation runs (Monte Carlo)", min_value=100, max_value=20000, value=2000, step=100)
    pick_model = st.selectbox("Model to use for probabilities", options=['Random Forest','Logistic Regression'])
    pred_button = st.button("Predict & Simulate Winner")

# Prepare models (train on all available historic team data)
model_pack = prepare_model(team_df, matches, target='is_winner')
scaler = model_pack['scaler']
rf = model_pack['rf']
lr = model_pack['lr']
features = model_pack['features']
model_df = model_pack['model_df']

# Show feature summary
with st.expander("Show modeling feature set & example rows"):
    st.write("Features used for modeling:", features)
    st.dataframe(model_df.head(8))

# Function: compute probability scores for a list of teams
def compute_team_probabilities(selected_teams: List[str], year: int):
    cand = teams_for_year[teams_for_year['Team'].isin(selected_teams)].copy()
    if cand.empty:
        return cand
    X = cand[features].fillna(0)
    Xs = scaler.transform(X)
    if pick_model == 'Random Forest':
        proba_all = rf.predict_proba(Xs)[:,1]
    else:
        proba_all = lr.predict_proba(Xs)[:,1]
    cand['model_prob'] = proba_all
    # normalize to sum 1 across selected teams, so we can simulate a tournament among them
    # if all probs are zero, fallback to equal probabilities
    if cand['model_prob'].sum() == 0:
        cand['norm_prob'] = 1.0 / len(cand)
    else:
        cand['norm_prob'] = cand['model_prob'] / cand['model_prob'].sum()
    cand = cand.sort_values('norm_prob', ascending=False).reset_index(drop=True)
    return cand

# Prediction action
if pred_button:
    if len(selected) < 2:
        st.warning("Please select at least 2 teams.")
    else:
        with st.spinner("Computing probabilities and running simulation..."):
            cand_df = compute_team_probabilities(selected, sel_year)
            # Show predicted probabilities table
            st.subheader("Predicted probabilities (model scores -> normalized among selected teams)")
            st.dataframe(cand_df[['Team','model_prob','norm_prob'] + features].round(3))

            # Bar chart for probabilities
            fig_bar = px.bar(cand_df.sort_values('norm_prob', ascending=True), x='norm_prob', y='Team',
                             orientation='h', labels={'norm_prob':'Normalized Win Probability'},
                             title="Predicted Win Probability (normalized among selected teams)")
            st.plotly_chart(fig_bar, use_container_width=True)

            # Monte Carlo simulation: pick winner according to normalized probabilities sim_runs times
            rng = np.random.default_rng(seed=42)
            team_names = cand_df['Team'].values
            probs = cand_df['norm_prob'].values
            # safety: ensure probs sum to 1
            probs = probs / probs.sum() if probs.sum()>0 else np.ones_like(probs)/len(probs)
            sim_wins = rng.choice(team_names, size=sim_runs, p=probs)
            sim_counts = pd.Series(sim_wins).value_counts(normalize=True).reindex(team_names).fillna(0)
            sim_df = pd.DataFrame({'Team': team_names, 'sim_win_rate': sim_counts.values, 'model_prob': cand_df['norm_prob'].values})
            sim_df = sim_df.sort_values('sim_win_rate', ascending=False).reset_index(drop=True)

            st.subheader(f"Simulation results — {sim_runs} runs")
            st.dataframe(sim_df.round(3))

            # Donut chart of simulation distribution
            fig_pie = go.Figure(data=[go.Pie(labels=sim_df['Team'], values=sim_df['sim_win_rate'], hole=0.5)])
            fig_pie.update_layout(title_text="Simulated Tournament Winner Distribution")
            st.plotly_chart(fig_pie, use_container_width=True)

            # Quick pick: predicted winner by model and by simulation
            top_by_model = cand_df.sort_values('norm_prob', ascending=False).iloc[0]
            top_by_sim = sim_df.sort_values('sim_win_rate', ascending=False).iloc[0]
            st.success(f"Model top pick: {top_by_model['Team']} (model norm prob: {top_by_model['norm_prob']:.3f})")
            st.success(f"Simulation top pick: {top_by_sim['Team']} (sim win rate: {top_by_sim['sim_win_rate']:.3f})")

            # Allow download of predictions & sim
            st.download_button("Download predictions CSV", data=df_to_csv_bytes(cand_df), file_name=f"predictions_{sel_year}.csv", mime="text/csv")
            st.download_button("Download simulation results CSV", data=df_to_csv_bytes(sim_df), file_name=f"simulation_{sel_year}.csv", mime="text/csv")

# Extra: show team comparison charts when user clicks a single team in the right panel
st.markdown("---")
st.subheader("Inspect a team")
inspect_team = st.selectbox("Select a team to inspect stats", options=team_list, index=0)
if inspect_team:
    row = teams_for_year[teams_for_year['Team'] == inspect_team]
    if not row.empty:
        st.metric(label=f"{inspect_team} — Matches played", value=int(row['matches_played'].values[0]))
        cols = st.columns(3)
        cols[0].metric("Wins", int(row['wins'].values[0]))
        cols[1].metric("Losses", int(row['losses'].values[0]))
        cols[2].metric("Draws", int(row['draws'].values[0]))
        st.write("Detailed stats")
        st.table(row.T.rename(columns={row.index[0]: 'value'})[['value']])
    else:
        st.write("No stats available for this team in selected year.")

st.markdown("---")
st.caption("Notes: Predictions are statistical estimates based on past tournament aggregated features (team-level). For better accuracy include up-to-date FIFA rankings, player-level features (minutes, goals), injuries, and roster changes.")

