import pandas as pd 
import os
import re

# from utility import rssi_to_dis, intersection_of_three_circel

df_loc_aps = pd.read_csv('location_APs_feets.csv')

f = ['micromax', 'moto', 'oneplus', 'samsung', 'yureka']

for file in f:
	print file
	df = pd.read_csv('spencers_data/device_modified_logs_min/'+file+'.csv')
	print 'Total probes (minute granularity) - ' + str(len(df))
	df = df[df['count'] >= 3]
	print 'Total probes (minute granularity, #APs >= 3) - ' + str(len(df))
	df = df[df['count'] >= 4]
	print 'Total probes (minute granularity, #APs >= 4) - ' + str(len(df))
	df.reset_index(drop=True, inplace=True)

	
	# for i in range(len(df)):
	# 	cid_arr = df.loc[i, 'controllerid']
	# 	pwr_arr = df.loc[i, 'pwr']

	# 	# print cid_arr
	# 	cid_arr = cid_arr[1:-1]
	# 	# print cid_arr
	# 	cid_arr = cid_arr.split(',')
	# 	# print cid_arr
	# 	cid_arr = map(float, cid_arr)
	# 	# print cid_arr
	# 	cid_arr = map(int, cid_arr)
	# 	# print cid_arr

	# 	pwr_arr = pwr_arr[1:-1]
	# 	# print pwr_arr
	# 	pwr_arr = pwr_arr.split(',')
	# 	# print pwr_arr
	# 	pwr_arr = map(float, pwr_arr)
	# 	# print pwr_arr

	# 	slice1 = df_loc_aps[df_loc_aps['Controller Id'] == int(cid_arr[0])]
	# 	x1 = slice1.loc[slice1.index[0], 'X']
	# 	y1 = slice1.loc[slice1.index[0], 'Y']
	# 	r1 = rssi_to_dis(pwr_arr[0])

	# 	slice2 = df_loc_aps[df_loc_aps['Controller Id'] == int(cid_arr[1])]
	# 	x2 = slice1.loc[slice1.index[0], 'X']
	# 	y2 = slice1.loc[slice1.index[0], 'Y']
	# 	r2 = rssi_to_dis(pwr_arr[1])

	# 	slice3 = df_loc_aps[df_loc_aps['Controller Id'] == int(cid_arr[2])]
	# 	x3 = slice1.loc[slice1.index[0], 'X']
	# 	y3 = slice1.loc[slice1.index[0], 'Y']
	# 	r3 = rssi_to_dis(pwr_arr[2])


	# 	l = [x1, y1, r1, x2, y2, r2, x3, y3, r3]
	# 	print l
	# 	loc = intersection_of_three_circel(x1, y1, r1, x2, y2, r2, x3, y3, r3)
	# 	print loc