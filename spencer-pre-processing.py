from __future__ import division
import pandas as pd
import os

list_of_macs = [['80:58:f8:d8:ad:e1', 'moto'], ['18:dc:56:8c:27:56', 'yureka'], ['c0:ee:fb:72:0c:27', 'oneplus'], ['84:38:38:f6:58:40', 'samsung'], \
    ['88:36:5f:f8:3b:4a', 'lg'], ['00:0c:e7:4f:38:a5', 'micromax'], ['74:23:44:33:2f:b7', 'redmi'], ['d8:c7:71:35:e8:19', 'honor']]

f_sub = os.listdir('spencers_data/validation_data/')
f_sub = [j for j in f_sub if '.log' in j]
df_day = pd.read_json('spencers_data/validation_data/'+f_sub[0], lines=True)
df_day['ts'] = pd.to_datetime(df_day['ts'], infer_datetime_format=True)
for log_file in f_sub[1:]:
    df_hour = pd.read_json('spencers_data/validation_data/'+log_file, lines=True)
    df_hour['ts'] = pd.to_datetime(df_hour['ts'], infer_datetime_format=True)
    df_day = df_day.append(df_hour, ignore_index=True)

df_day.reset_index(inplace=True)
del df_day['index'] 

# df1 = df_day.groupby('mac')
# df1 = df1.count()
# df1.sort_values('nasid', inplace=True, ascending=False)
# mac = df1.index[0]

# count_probes = df1.loc[mac, 'nasid']
total_probes = len(df_day)

# print file + ', mac - ' + str(mac) + ', count_probes - ' + str(count_probes) + ', total_probes - ' + str(total_probes) + ', %tage - ' + str(count_probes*100/total_probes)

df_day['ts']= df_day['ts'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:00'))
df_day['ts'] = pd.to_datetime(df_day['ts'], infer_datetime_format=True)
df_ts1s = df_day.groupby(['nasid', 'controllerid', 'position', 'ts', 'mac'])
df_ts1s_mean = df_ts1s.mean()
df_ts1s_std = df_ts1s.std()
df_ts1s_mean.reset_index(inplace=True)
df_ts1s_std.reset_index(inplace=True)
df_ts1s_mean.columns = ['nasid', 'controllerid', 'position', 'ts', 'mac', 'mean']
df_ts1s_std.columns = ['nasid', 'controllerid', 'position', 'ts', 'mac', 'std']

df_ts1s_mean['std'] = df_ts1s_std['std']

df = df_ts1s_mean.describe()
print df.loc['mean', 'mean']
print df.loc['mean', 'std']

for mac_device in list_of_macs:
    mac = mac_device[0]
    df_slice = df_day[df_day['mac'] == mac]
    print str(mac_device) + str(len(df_slice)) + '/' + str(total_probes)
    df_slice['ts']= df_slice['ts'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:00'))
    df_slice['ts'] = pd.to_datetime(df_slice['ts'], infer_datetime_format=True)
    df_ts1s = df_slice.groupby(['nasid', 'controllerid', 'position', 'ts', 'mac'])
    df_ts1s_mean = df_ts1s.mean()
    df_ts1s_std = df_ts1s.std()
    df_ts1s_mean.reset_index(inplace=True)
    df_ts1s_std.reset_index(inplace=True)
    df_ts1s_mean.columns = ['nasid', 'controllerid', 'position', 'ts', 'mac', 'mean']
    df_ts1s_std.columns = ['nasid', 'controllerid', 'position', 'ts', 'mac', 'std']

    df_ts1s_mean['std'] = df_ts1s_std['std']

    df_group_ap = df_ts1s.groupby(['nasid', 'position', 'ts', 'mac'])
    lst = list(df_group_ap)
    df_loc_track = pd.DataFrame(columns=['nasid', 'position', 'ts', 'mac', 'controllerid', 'pwr', 'count'])
    for i in range(len(lst)):
        x = lst[i]

        cid_list = x[1]['controllerid'].tolist()
        pwr_list = x[1]['pwr'].tolist()

        df_loc_track.loc[i, :] = [x[0][0], x[0][1], x[0][2], x[0][3], cid_list, pwr_list, len(cid_list)]

    if not os.path.exists('spencers_data/device_modified_logs_min/'):
        os.makedirs('spencers_data/device_modified_logs_min/')
    df_loc_track.to_csv('spencers_data/device_modified_logs_min/'+mac_device[1]+'.csv')
    print df_loc_track.loc[:5]
    print len(df_loc_track)
    print mac_device[1] + ' done.'

