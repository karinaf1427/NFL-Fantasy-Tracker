import pandas as pd

#wk0.csv is the week baseline for data compararon wk0DF.csv Will work the same, but for Defense
#wk1.csv is the current week for data compararon wk1DF.csv Will work the same, but for Defense
# Caculation Will be Data from wk1 minus wk0

wk0 = pd.read_csv('/content/wk0.csv') #Add the baseline file
wk0 = pd.DataFrame(wk0)

wk0 = wk0.rename(columns={'Total_targets': 'wk0Total_Targets', 'Fantasy_PPR': 'wk0Fantasy_PPR'})

wk1 = pd.read_csv('/content/wk1.csv') #Add the file with the current week
wk1 = pd.DataFrame(wk1)

wk1 = wk1.rename(columns={'Total_targets': 'wk1Total_Targets', 'Fantasy_PPR': 'wk1Fantasy_PPR'})

merged_data = []
merged_data = pd.merge(wk0, wk1, on='Player2', how='left')

#merged_data.head()

merged_data = merged_data.rename(columns={'Total_Targets_x': 'wk0Total_Targets', 'Fantasy_PPR_x': 'wk0Fantasy_PPR', 'Total_Targets_y': 'wk1Total_Targets', 'Fantasy_PPR_y': 'wk1Fantasy_PPR'})
merged_data['wk0Fantasy_PPR'] = pd.to_numeric(merged_data['wk0Fantasy_PPR'], errors='coerce')
merged_data['wk1Fantasy_PPR'] = pd.to_numeric(merged_data['wk1Fantasy_PPR'], errors='coerce')
merged_data['Dif_Targets'] = merged_data['wk1Total_Targets'] - merged_data['wk0Total_Targets']
merged_data['Dif_Fantasy'] = merged_data['wk1Fantasy_PPR'] - merged_data['wk0Fantasy_PPR']

#merged_data.head()

merged_data = merged_data.sort_values(by='Dif_Targets', ascending=False)
#merged_data.head()

merged_data = merged_data.drop(columns=['position_x', 'position_y', 'fantasy_team_x', 'Fantasy_OvRank_x', 'Fantasy_PosRank_x', 'Player_y', 'Team_y', 'Position1_y', 'Fantasy_OvRank_y', 'Fantasy_PosRank_y'])

#merged_data.head()

merged_data = merged_data.rename(columns={'Player_x': 'Player', 'Team_x': 'Team', 'Position1_x': 'Position', 'fantasy_team_y': 'fantasy_team'})
#merged_data.head()

merged_data = merged_data.rename(columns={'Rushing_Att_x': 'wk0Rushing_Att_x', 'Receiving_Tgt_x': 'Receiving_Tgt_xwk0', 'Rushing_Att_y': 'wk1Rushing_Att_y', 'Receiving_Tgt_y': 'wk1Receiving_Tgt_y'})
#merged_data.head()

from datetime import date
today = date.today()
merged_data.to_csv(f"{today.strftime('%Y-%m-%d')}_DifferenceFF.csv", index=False)

wk0DF = pd.read_csv('/content/wk0DF.csv')
wk0DF = pd.DataFrame(wk0DF)

wk1DF = pd.read_csv('/content/wk1DF.csv')
wk1DF = pd.DataFrame(wk1DF)

merged_data = []
merged_data = pd.merge(wk0DF, wk1DF, on='Team', how='left')

merged_data.head()

merged_data = merged_data.rename(columns={'Pass Yds_x': 'wk0Pass_Yds', 'Rush Yds_x': 'wk0Rush_Yds', 'Total Yds_x': 'wk0Total_Yds', 'Rush Yds_y': 'wk1Rush_Yds', 'Pass Yds_y': 'wk1Pass_Yds', 'Total Yds_y': 'wk1Total_Yds'})

merged_data.head()

merged_data['wk0Pass_Yds'] = pd.to_numeric(merged_data['wk0Pass_Yds'], errors='coerce')
merged_data['wk0Rush_Yds'] = pd.to_numeric(merged_data['wk0Rush_Yds'], errors='coerce')
merged_data['wk0Total_Yds'] = pd.to_numeric(merged_data['wk0Total_Yds'], errors='coerce')

merged_data['wk1Pass_Yds'] = pd.to_numeric(merged_data['wk1Pass_Yds'], errors='coerce')
merged_data['wk1Rush_Yds'] = pd.to_numeric(merged_data['wk1Rush_Yds'], errors='coerce')
merged_data['wk1Total_Yds'] = pd.to_numeric(merged_data['wk1Total_Yds'], errors='coerce')


merged_data['Dif_Pass_Yds'] = merged_data['wk1Pass_Yds'] - merged_data['wk0Pass_Yds']
merged_data['Dif_Rush_Yds'] = merged_data['wk1Rush_Yds'] - merged_data['wk0Rush_Yds']
merged_data['Dif_Total_Yds'] = merged_data['wk1Total_Yds'] - merged_data['wk0Total_Yds']

merged_data = merged_data.sort_values(by='Dif_Total_Yds', ascending=True)

merged_data = merged_data.drop(columns=['Ranking_Pass_Yds_x', 'Ranking_Rush_Yds_x', 'Ranking_Pass_Yds_y', 'Ranking_Rush_Yds_y'])

from datetime import date
today = date.today()
merged_data.to_csv(f"{today.strftime('%Y-%m-%d')}_DifferenceFFDEF.csv", index=False)