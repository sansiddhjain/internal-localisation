from __future__ import division
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import utility
import descartes
import os

macs = ["74:23:44:33:2f:b7", "00:0c:e7:4f:38:a5", "88:36:5f:f8:3b:4a", "84:38:38:f6:58:40", "c0:ee:fb:72:0c:27", "18:dc:56:8c:27:56", "80:58:f8:d8:ad:e1"]

# factor to convert to inches (doesn't have any effect on the nature of plots as everything is just scaled up)
factor = 1

aps = {
    1: (-22 * factor, 1 * factor),
    2: (0 * factor, 1 * factor),
    3: (0 * factor, 24 * factor),
    4: (-22 * factor, 26 * factor)
}


fig = plt.figure(1)
ax = fig.add_subplot(1, 1, 1)


def plot_circles(circles, file, ts):
    ax.cla()
    ax.set_title(file + '\n' + str(ts))
    ax.set_xlim(-60, 40)
    ax.set_ylim(-20, 60)
    for circle in circles:
        print(circle)
        c = plt.Circle(circle[0], circle[1], color='b', fill=False)
        ax.add_artist(c)

def plot(ay, x, y, color='b'):
    ay.plot(x, y, 'ro', markersize=5)

def plot_polygon(p, mac, ts):

    ax = fig.add_subplot(1, 1, 1)
    ax.set_title(mac + '\n' + str(ts) + '\n' + str(p.centroid))
    ax.set_xlim(-100, 100)
    ax.set_ylim(-50, 100)
    ax.add_patch(descartes.PolygonPatch(p, fc='b', ec='k', alpha=0.2))
    plt.pause(2)

df_path = pd.read_csv('spencers_data/path1.csv')
df_path['Start_time'] = pd.to_datetime(df_path['Start_time'])
df_path['Start_time'] = df_path['Start_time'].apply(lambda x: x.strftime('%Y-%m-13 %H:%M:%S'))
df_path['Start_time'] = pd.to_datetime(df_path['Start_time'])

count = len(df_path)
for index, row in df_path.iterrows():
    if (row['Duration (min)'] == 2):
        df_path.loc[index, 'Duration (min)'] = 1
        df_path.loc[count, :] = df_path.loc[index, :]
        df_path.loc[count, 'Start_time'] = df_path.loc[count, 'Start_time'] + pd.Timedelta('1 minute')
        count += 1

df_path.sort_values('Start_time', inplace=True)
df_path.reset_index(drop=True, inplace=True)
df_path['Start_time'] = df_path['Start_time'] + pd.Timedelta('12 hours')

# print (df_path)

f = ['micromax', 'moto', 'oneplus', 'samsung', 'yureka']
for file in f:
    count = 0
    df_loc_track = pd.read_csv('spencers_data/device_modified_logs_min/'+str(file)+'.csv')
    df_loc_track['ts'] = pd.to_datetime(df_loc_track['ts'])
    df_loc_track['ts'] = df_loc_track['ts'] + pd.Timedelta('5 hours 30 minutes')

    print(len(df_loc_track))
    idx_lst = []
    for index, row in df_loc_track.iterrows():
        l = list(df_path['Start_time'])
        x = df_loc_track.loc[index, 'ts']
        if (x not in l):
            idx_lst.append(index)
    df_loc_track.drop(idx_lst, inplace=True)
    df_loc_track.reset_index(drop=True, inplace=True)

    print(len(df_loc_track))
    # hc = open("Weighted_mean/%s.csv" % (mac), 'a')
    # hc = open("smallest_area/%s.csv" % (mac), 'a')
    x = [-22, 0, 0, -22]
    y = [1, 1, 24, 26]
    for index, row in df_loc_track.iterrows():
        print(row['ts'])
        row['controllerid'] = row['controllerid'][1:-1]
        row['pwr'] = row['pwr'][1:-1]
        if row['count'] >= 2:
            controllers = list(map(int, row['controllerid'].split(',')))
            powers = list(map(float, row['pwr'].split(',')))
            mac = row['mac']
            ts = row['ts']

            circles = []
            for cid, power in zip(controllers, powers):
                radial_distance = utility.rssi_to_dis(power)
                circles.append((aps[int(cid)], radial_distance))

            intersection = utility.heuristic_3(circles)
            plot_circles(circles, file, ts)
            ax.plot(x, y, 'bo', markersize=5)
            ax.plot(df_path.loc[index, 'X'], df_path.loc[index, 'Y'], 'go', markersize=5)
            plot(ax, [intersection.x], [intersection.y], 'red')
            # plt.pause(1)
            count += 1
            dirs = 'plots/circles/%s' %(file) 
            if not os.path.exists(dirs):
                os.makedirs(dirs)
            plt.savefig(dirs+"/%03d.png" %(count))
            # plt.savefig('spencers_data/images/circles_'+str(file)+'_X'+str(int(df_path.loc[index, 'X']))+'_Y'+str(int(df_path.loc[index, 'Y']))+'.png')
            # if intersection == None:
            #     pass

            # else:
            # hc.write(str(ts) + "," + str(intersection.centroid.x) + "," + str(intersection.centroid.y) + "\n")
    # hc.close()
    # input()
    # fig.clf()
    # plot_circles(circles, mac, ts)

    # plt.show()
