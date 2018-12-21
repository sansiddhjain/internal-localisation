import datetime
import pandas as pd
import os

# Readng path1 data and setting granularity to 1 min
df_path1 = pd.read_csv('../spencers_data/path1.csv')
df_path1['Start_time'] = pd.to_datetime(df_path1['Start_time'])
df_path1['Start_time'] = df_path1['Start_time'].apply(lambda x: x.strftime('%Y-%m-13 %H:%M:%S'))
df_path1['Start_time'] = pd.to_datetime(df_path1['Start_time'])

count = len(df_path1)
for index, row in df_path1.iterrows():
    if (row['Duration (min)'] == 2):
        df_path1.loc[index, 'Duration (min)'] = 1
        df_path1.loc[count, :] = df_path1.loc[index, :]
        df_path1.loc[count, 'Start_time'] = df_path1.loc[count, 'Start_time'] + pd.Timedelta('1 minute')
        count += 1

df_path1.sort_values('Start_time', inplace=True)
df_path1.reset_index(drop=True, inplace=True)
df_path1['Start_time'] = df_path1['Start_time'] + pd.Timedelta('12 hours')
df_path1['Start_time'] = df_path1['Start_time'].apply(lambda x: x.strftime('%H:%M'))

# Reading path2 data and setting granularity to 1 min
df_path2 = pd.read_csv('../spencers_data/path2.csv')
df_path2['Start_time'] = pd.to_datetime(df_path2['Start_time'])
df_path2['Start_time'] = df_path2['Start_time'].apply(lambda x: x.strftime('%Y-%m-13 %H:%M'))
df_path2['Start_time'] = pd.to_datetime(df_path2['Start_time'])

count = len(df_path2)
for index, row in df_path2.iterrows():
    if (row['Duration (min)'] == 2):
        df_path2.loc[index, 'Duration (min)'] = 1
        df_path2.loc[count, :] = df_path2.loc[index, :]
        df_path2.loc[count, 'Start_time'] = df_path2.loc[count, 'Start_time'] + pd.Timedelta('1 minute')
        count += 1

df_path2.sort_values('Start_time', inplace=True)
df_path2.reset_index(drop=True, inplace=True)
df_path2['Start_time'] = df_path2['Start_time'] + pd.Timedelta('12 hours')
df_path2['Start_time'] = df_path2['Start_time'].apply(lambda x: x.strftime('%H:%M'))

target_ts = df_path2['Start_time'].tolist()

f = os.listdir('../spencers_data')
f.sort()

macs = ["00:0c:e7:4f:38:a5", "84:38:38:f6:58:40", "c0:ee:fb:72:0c:27", "18:dc:56:8c:27:56", "80:58:f8:d8:ad:e1"]
names = ["Micromax", "Samsung S5", "oneplus x", "Yureka", "Moto"]

final_df = pd.DataFrame(columns=['nasid', 'position', 'ts', 'controllerid', 'pwr', 'count'], dtype=object)
for file in f:
    base, ext = os.path.splitext(file)
    if(ext == ".log"):
        print(file)
        df = pd.read_json("../spencers_data/%s" % (file), lines=True)  # reading data
        df['ts'] = pd.to_datetime(df['ts'], infer_datetime_format=True)

        df['ts'] = df['ts'].apply(lambda x: x + datetime.timedelta(hours=5, minutes=30))  # converrting utc time ist

        df = df.loc[df['mac'].isin(macs)]  # filtering out data corresponding to our macs

        df.drop(['mac'], axis=1, inplace=True)  # macs not needed

        # making code granular by per minute
        df['ts'] = df['ts'].apply(lambda x: x.strftime('%H:%M'))
        df = df.groupby(['nasid', 'controllerid', 'position', 'ts']).mean()
        df.reset_index(inplace=True)

        df = df.groupby(['nasid', 'position', 'ts'])
        lst = list(df)
        df_loc_track = pd.DataFrame(columns=['nasid', 'position', 'ts', 'controllerid', 'pwr', 'count'], dtype=object)

        for i in range(len(lst)):
            x = lst[i]
            cid_list = list(map(str, x[1]['controllerid'].tolist()))
            pwr_list = list(map(str, x[1]['pwr'].tolist()))

            df_loc_track.loc[i, :] = [x[0][0], x[0][1], x[0][2], " ".join(cid_list), " ".join(pwr_list), len(cid_list)]

        df_loc_track.reset_index(inplace=True)

        df_loc_track = df_loc_track.loc[df_loc_track['ts'].isin(target_ts)]
        df_loc_track = df_loc_track.loc[df_loc_track['count'] == 4]  # only those instances where all aps receive a signal

        final_df = final_df.append(df_loc_track)

final_df.sort_values('ts', inplace=True)
# df_path1.to_csv("outputs_path1.csv", index=False)
# df_path2.to_csv("outputs_path2.csv", index=False)
final_df.to_csv("inputs_path2.csv", index=False)
