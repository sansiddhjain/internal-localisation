from __future__ import division
import pandas as pd
import os

f = os.listdir('logs')
# f = [j for j in f if '2018' in j]

for file in f:
	f_sub = os.listdir('logs/'+file+'/')
	f_sub = [j for j in f_sub if '.log' in j]
	df_day = pd.read_json('logs/'+file+'/'+f_sub[0], lines=True)
	df_day['ts'] = pd.to_datetime(df_day['ts'], infer_datetime_format=True)
	for log_file in f_sub[1:]:
		# try:
		df_hour = pd.read_json('logs/'+file+'/'+log_file, lines=True)
		# except:
		# 	continue
		df_hour['ts'] = pd.to_datetime(df_hour['ts'], infer_datetime_format=True)
		df_day = df_day.append(df_hour, ignore_index=True)

	df_day.reset_index(inplace=True)
	del df_day['index']	

	df1 = df_day.groupby('mac')
	df1 = df1.count()
	df1.sort_values('nasid', inplace=True, ascending=False)
	mac = df1.index[0]

	count_probes = df1.loc[mac, 'nasid']
	total_probes = len(df_day)

	print file + ', mac - ' + str(mac) + ', count_probes - ' + str(count_probes) + ', total_probes - ' + str(total_probes) + ', %tage - ' + str(count_probes*100/total_probes)

	df_slice = df_day[df_day['mac'] == mac]
	df_slice['ts']= df_slice['ts'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
	df_slice['ts'] = pd.to_datetime(df_slice['ts'], infer_datetime_format=True)
	df_ts1s = df_slice.groupby(['nasid', 'controllerid', 'position', 'ts', 'mac'])
	df_ts1s = df_ts1s.mean()
	df_ts1s.reset_index(inplace=True)

	df_group_ap = df_ts1s.groupby(['nasid', 'position', 'ts', 'mac'])
	lst = list(df_group_ap)
	df_loc_track = pd.DataFrame(columns=['nasid', 'position', 'ts', 'mac', 'controllerid', 'pwr', 'count'])
	for i in range(len(lst)):
		x = lst[i]

		cid_list = x[1]['controllerid'].tolist()
		pwr_list = x[1]['pwr'].tolist()

		df_loc_track.loc[i, :] = [x[0][0], x[0][1], x[0][2], x[0][3], cid_list, pwr_list, len(cid_list)]

	if not os.path.exists('best_mac_mod_logs/'+file+'/'):
		os.makedirs('best_mac_mod_logs/'+file+'/')
	df_loc_track.to_csv('best_mac_mod_logs/'+file+'/log.csv')
	print df_loc_track.loc[:5]
	print file + ' done.'

