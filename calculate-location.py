import pandas as pd 
import os
import re

from utility import signal_strength_to_distance, intersection_of_three_circel

df_loc_aps = pd.read_csv('location_APs_feets.csv')

f = os.listdir('best_mac_mod_logs/')

f = [j for j in f if ('2018' in j) or ('2017' in j)]

for file in f:
	df = pd.read_csv('best_mac_mod_logs/'+file+'/log.csv')
	df = df[df['count'] >= 3]
	df.reset_index(drop=True, inplace=True)

	for i in range(len(df)):
		cid_arr = df.loc[i, 'controllerid']
		pwr_arr = df.loc[i, 'pwr']

		# print cid_arr
		cid_arr = cid_arr[1:-1]
		# print cid_arr
		cid_arr = cid_arr.split(',')
		# print cid_arr
		cid_arr = map(float, cid_arr)
		# print cid_arr
		cid_arr = map(int, cid_arr)
		# print cid_arr

		pwr_arr = pwr_arr[1:-1]
		# print pwr_arr
		pwr_arr = pwr_arr.split(',')
		# print pwr_arr
		pwr_arr = map(float, pwr_arr)
		# print pwr_arr

		slice1 = df_loc_aps[df_loc_aps['Controller Id'] == int(cid_arr[0])]
		x1 = slice1.loc[slice1.index[0], 'X']
		y1 = slice1.loc[slice1.index[0], 'Y']
		r1 = signal_strength_to_distance(pwr_arr[0])

		slice2 = df_loc_aps[df_loc_aps['Controller Id'] == int(cid_arr[1])]
		x2 = slice1.loc[slice1.index[0], 'X']
		y2 = slice1.loc[slice1.index[0], 'Y']
		r2 = signal_strength_to_distance(pwr_arr[1])

		slice3 = df_loc_aps[df_loc_aps['Controller Id'] == int(cid_arr[2])]
		x3 = slice1.loc[slice1.index[0], 'X']
		y3 = slice1.loc[slice1.index[0], 'Y']
		r3 = signal_strength_to_distance(pwr_arr[2])


		l = [x1, y1, r1, x2, y2, r2, x3, y3, r3]
		print l
		loc = intersection_of_three_circel(x1, y1, r1, x2, y2, r2, x3, y3, r3)
		print loc