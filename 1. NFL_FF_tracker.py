
import pandas as pd
from datetime import date


url = "https://www.pro-football-reference.com/years/2025/fantasy.htm"
tables = pd.read_html(url)
df = tables[0]
#df.head()
#df.info()

# Flatten the multi-level column names
df.columns = ['_'.join(col).strip() for col in df.columns.values]

# Rename the 'Unnamed: 1_level_0_Player' column to 'Player' and assign it back
df['Unnamed: 1_level_0_Player'] = df.rename(columns={'Unnamed: 1_level_0_Player': 'Player'})['Player']

#df.info()

df_split = df['Unnamed: 1_level_0_Player'].str.split(' ', expand=True)
df_split.columns = ['name', 'last_name', 'extra']
df['name2'] = df_split['name']
df['name3'] = df['name2'].str[0]
df['Player'] = df['name3'].astype(str) + '.' + df_split['last_name'].astype(str)
df = df.drop(columns=['name2', 'name3'])

#df.info()

#df.head()

#df = df['Player'].applymap(lambda x: x.strip() if isinstance(x, str) else x)
df['Player'] = df['Player'].str.replace(" ", "")

df.loc[df["Player"].fillna('').str.contains("J.Sm"), "Player"] = "J.Smith-Njigba"
df.loc[df["Player"].fillna('').str.contains("J.Cros"), "Player"] = "J.Croskey-Merritt"
df.loc[df["Player"].fillna('').str.contains("A.St"), "Player"] = "A.St-Brown"

today = date.today()
df.to_csv(f"{today.strftime('%Y-%m-%d')}_FullProFBData.csv", index=False)

!pip install requests beautifulsoup4 lxml

import requests
from bs4 import BeautifulSoup
import pandas as pd

cookies = {
   "NFL_FANTASY_ID": "*****@mail.com",#Add your credentials
   "NFL_FANTASY_AUTH": "*********"
}

teams = {
    1: "Team 1", #Provide each of the names in your League
    2: "Team 2",
    3: "Team 3",
    4: "Team 4",
    5: "Team 5",
    6: "Team 6",
    7: "Team 7",
    8: "Team 8",
    11: "Team 9",
    12: "Team 10",
    13: "Team 11",
    14: "Team 12"
}

BASE_URL = "https://fantasy.nfl.com/league/2026438/team/{}"

def get_team_roster(team_id: int, fantasy_team: str) -> pd.DataFrame:
    """Scrape and clean a single team's roster from NFL Fantasy."""
    url = BASE_URL.format(team_id)
    resp = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(resp.text, "lxml")

    players = []
    rows = soup.select("table.tableType-player tbody tr")

    for row in rows:
        player_tag = row.select_one(".playerNameAndInfo")
        if player_tag:
            players.append(player_tag.get_text(strip=True))

    if not players:
        return pd.DataFrame(columns=['name', 'position', 'team', 'fantasy_team'])

    # Split into name and NFL team
    roster_df = pd.Series(players).str.split('-', expand=True)

    # Check the number of columns after split and assign accordingly
    if roster_df.shape[1] == 2:
        roster_df.columns = ['name', 'team']
    elif roster_df.shape[1] == 3:
        # Assuming the third element is also part of the team name or additional info
        roster_df.columns = ['name', 'team', 'extra_info']
        # Concatenate team and extra_info, you might want to handle this differently
        roster_df['team'] = roster_df['team'] + '-' + roster_df['extra_info']
        roster_df = roster_df.drop(columns=['extra_info'])
    elif roster_df.shape[1] == 4:
        # Assuming the third element is also part of the team name or additional info
        roster_df.columns = ['name', 'team', 'extra_info']
        # Concatenate team and extra_info, you might want to handle this differently
        roster_df['team'] = roster_df['team'] + '-' + roster_df['extra_info']
        roster_df = roster_df.drop(columns=['extra_info'])
    else:
        # Handle cases with more or less than 2-3 splits if necessary
        # For now, we'll print a warning and skip these rows
        print(f"Warning: Unexpected number of splits for team {team_id}. Skipping rows.")
        return pd.DataFrame(columns=['name', 'position', 'team', 'fantasy_team'])


    # Extract position (last 3 chars of name field)
    roster_df['position'] = roster_df['name'].str[-3:]
    roster_df['name'] = roster_df['name'].str[:-3]

    # Format player name as F.LastName
    name_split = roster_df['name'].str.split(' ', expand=True)
    # Handle cases where splitting the name doesn't result in at least two parts
    if name_split.shape[1] >= 2:
        roster_df['name'] = name_split[0].str[0] + '.' + name_split[1]
    else:
        roster_df['name'] = roster_df['name'] # Keep original name if split fails


    # Add fantasy team
    roster_df['fantasy_team'] = fantasy_team

    return roster_df[['name', 'position', 'fantasy_team']]

all_rosters = pd.concat(
    [get_team_roster(team_id, name) for team_id, name in teams.items()],
    ignore_index=True
)

all_rosters.loc[all_rosters["name"].fillna('').str.contains("J.Sm"), "name"] = "J.Smith-Njigba"
all_rosters.loc[all_rosters["name"].fillna('').str.contains("J.Cros"), "name"] = "J.Croskey-Merritt"
all_rosters.loc[all_rosters["position"].fillna('').str.contains("ith"), "position"] = "WR"
all_rosters.loc[all_rosters["position"].fillna('').str.contains("key"), "position"] = "RB"
all_rosters.loc[all_rosters["position"].fillna('').str.contains("mon"), "position"] = "WR"

import numpy as np
all_rosters.loc[all_rosters["name"].fillna('').str.contains(str(np.nan)), "name"] = "A.St-Brown"

fantasy_roster = all_rosters.fillna({"name": 'nan', "name": "A.St-Brown"})

#fantasy_roster = fantasy_roster.drop(columns='team')

fantasy_roster = pd.DataFrame(fantasy_roster)

#fantasy_roster = pd.read_csv('/content/2025-09-27_roster.csv')
#fantasy_roster['position'] = fantasy_roster['position'].str[:-1]
#fantasy_roster.head()

fantasy_roster = fantasy_roster.rename(columns={'name': 'Player'})

fantasy_roster['Player'] = fantasy_roster['Player'].str.replace(" ", "")

#fantasy_roster.info()

#fantasy_roster.head()

merged_data = []
merged_data = pd.merge(df, fantasy_roster, on='Player', how='left')
#merged_data.head()

merged_data['fantasy_team'].fillna('Free Agent', inplace=True)
#merged_data = merged_data.sort_values('Fantasy_OvRank', ascending=False)
#merged_data.head()

#merged_data.info()

merged_data = merged_data.rename(columns={'Unnamed: 0_level_0_Rk': 'Ranking'})

merged_data = merged_data.rename(columns={'Unnamed: 1_level_0_Player': 'Player2'})
merged_data = merged_data.rename(columns={'Unnamed: 2_level_0_Tm': 'Team'})
merged_data = merged_data.rename(columns={'Unnamed: 3_level_0_FantPos': 'Position1'})
merged_data = merged_data.rename(columns={' Unnamed: 4_level_0_Age': 'Age'})

#merged_data.info()

merged_data['Rushing_Att'] = pd.to_numeric(merged_data['Rushing_Att'], errors='coerce')
merged_data['Receiving_Tgt'] = pd.to_numeric(merged_data['Receiving_Tgt'], errors='coerce')

#merged_data.info()

merged_data['Rushing_Att'] = pd.to_numeric(merged_data['Rushing_Att'], errors='coerce')
merged_data['Receiving_Tgt'] = pd.to_numeric(merged_data['Receiving_Tgt'], errors='coerce')

merged_data['Total_Targets'] = merged_data['Rushing_Att'] + merged_data['Receiving_Tgt']

#final_data = merged_data[['Player', 'Player2', 'Team', 'Position1', 'position', 'fantasy_team', 'Fantasy_OvRank', 'Fantasy_PosRank', 'Total_Targets', 'Rushing_Att', 'Receiving_Tgt']].sort_values('Total_Targets', ascending=False)
final_data = merged_data[['Player', 'Player2', 'Team', 'Position1', 'position', 'fantasy_team', 'Fantasy_OvRank', 'Fantasy_PosRank', 'Total_Targets', 'Rushing_Att', 'Receiving_Tgt', 'Fantasy_PPR']]

#final_data = final_data[['Total_Targets', 'Rushing_Att', 'Receiving_Tgt']].astype(float)

#final_data = final_data[(final_data['Player'] != 'P.None')]

final_data = final_data.sort_values('Total_Targets', ascending=False)

#final_data.head(30)

final_data.to_csv(f"{today.strftime('%Y-%m-%d')}_rosterFF.csv", index=False)

df = []
url = "https://www.nfl.com/stats/team-stats/defense/passing/2025/reg/all"
tables = pd.read_html(url)
df = tables[0]
#df = df.sort_values(by="Pass Yds", ascending=True)
#df

df['Ranking_Pass_Yds'] = df['Yds'].rank(method='dense', ascending=True).astype(int)
#df

df2 = []
url2 = "https://www.nfl.com/stats/team-stats/defense/rushing/2025/reg/all"
tables = pd.read_html(url2)
df2 = tables[0]
#df = df.sort_values(by="Pass Yds", ascending=True)
#df2

df2['Ranking_Rush_Yds'] = df2['Rush Yds'].rank(method='dense', ascending=True).astype(int)
#df2

merged_df = pd.merge(df, df2, on='Team', how='outer')

merged_df['Total Yds'] = merged_df['Yds'] + merged_df['Rush Yds']
#merged_df

merged_df = merged_df.sort_values(by="Total Yds", ascending=True)
#merged_df

merged_df.to_csv(f"{today.strftime('%Y-%m-%d')}_FullNFL_Defense.csv", index=False)

defense_df = merged_df[['Team', 'Ranking_Pass_Yds', 'Ranking_Rush_Yds', 'Yds', 'Rush Yds', 'Total Yds']]
defense_df = defense_df.rename(columns={'Yds': 'Pass Yds'})
#defense_df

defense_df.to_csv(f"{today.strftime('%Y-%m-%d')}_defFF.csv", index=False)

url3 = "https://www.nfl.com/stats/team-stats/offense/passing/2025/reg/all"
tables = pd.read_html(url3)
df3 = tables[0]
#df = df.sort_values(by="Pass Yds", ascending=True)
#df

df3['Ranking_Pass_Yds'] = df3['Pass Yds'].rank(method='dense', ascending=False).astype(int)
#df

url4 = "https://www.nfl.com/stats/team-stats/offense/rushing/2025/reg/all"
tables = pd.read_html(url4)
df4 = tables[0]
#df = df.sort_values(by="Pass Yds", ascending=True)
#df2

df4['Ranking_Rush_Yds'] = df4['Rush Yds'].rank(method='dense', ascending=False).astype(int)
#df2

merged_df = []
merged_df = pd.merge(df3, df4, on='Team', how='outer')
#merged_df

merged_df['Total Yds'] = merged_df['Pass Yds'] + merged_df['Rush Yds']
#merged_df

merged_df = merged_df.sort_values(by="Total Yds", ascending=False)
#merged_df

merged_df.to_csv(f"{today.strftime('%Y-%m-%d')}_FullNFL_Offense.csv", index=False)

offense_df = merged_df[['Team', 'Ranking_Pass_Yds', 'Ranking_Rush_Yds', 'Pass Yds', 'Rush Yds', 'Total Yds']]
offense_df = offense_df.rename(columns={'Yds': 'Pass Yds'})
#offense_df

offense_df.to_csv(f"{today.strftime('%Y-%m-%d')}_offFF.csv", index=False)

offense_df.head()

