import pandas as pd 
import os

dates = os.listdir('spencers/')
for date in dates:
	df_date = pd.DataFrame(columns=['nasid', 'controllerid', 'position', 'ts', 'pwr', 'mac'])

	nasids = os.listdir('spencers/'+date+'/')
	nasids = [j for j in nasids if ('NAS' in j) & ('.' not in j)]
	for nasid in nasids:
		hours = os.listdir('spencers/'+date+'/'+nasid+'/')
		hours = [j for j in hours if ('.log' in j) & ('_' not in j)]
		for hour in hours:
			print nasid + ' ' + hour
			df_hour = pd.read_json('spencers/'+date+'/'+nasid+'/'+hour, lines=True)
			df_date = pd.concat([df_date, df_hour])

	df_date.to_csv('spencers/'+date+'/modified.csv')
	print date + ' done.'