from __future__ import division
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import utility
import descartes
import os
import numpy as np


macs = ["00:0c:e7:4f:38:a5", "84:38:38:f6:58:40", "c0:ee:fb:72:0c:27", "18:dc:56:8c:27:56", "80:58:f8:d8:ad:e1"]
names = ["Micromax", "Samsung S5", "oneplus x", "Yureka", "Moto"]
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
ax.set_title("Heurisitic 3")
ax.autoscale()

aps_plot, = ax.plot([-22, 0, 0, -22], [1, 1, 24, 26], marker='o', markersize=10, ls='')
validation, = ax.plot([], [], marker='o', markersize=3, color='g')
path, = ax.plot([], [], marker='+', markersize=3, color='red')


def plot_circles(circles, mac, ts):
    ax.cla()
    ax.set_title(mac + '\n' + str(ts))

    for circle in circles:
        print(circle)
        c = plt.Circle(circle[0], circle[1], color='b', fill=False)
        ax.add_artist(c)


def update(obj, x, y):
    x_old = obj.get_xdata()
    y_old = obj.get_ydata()
    x_old = np.append(x_old, x)
    y_old = np.append(y_old, y)
    obj.set_data(x_old, y_old)


f = os.listdir('spencers_data')
f.sort()

# reading and plotting validation data
validation_data1 = pd.read_csv("spencers_data/path1.csv")
validation_data1['Start_time'] = pd.to_datetime(validation_data1['Start_time'], infer_datetime_format=True)
validation_data1['Start_time'] = validation_data1['Start_time'].apply(lambda x: x + datetime.timedelta(hours=12))  # todo write proper code
validation_data1['Start_time'] = validation_data1['Start_time'].apply(lambda x: x.strftime('%H:%M'))
x_validation1 = validation_data1['X'].tolist()
y_validation1 = validation_data1['Y'].tolist()
ts1 = validation_data1['Start_time'].tolist()

validation_dict1 = {}
for a, b, c in zip(ts1, x_validation1, y_validation1):
    validation_dict1[a] = (b, c)


test_dict1 = {}

mac = macs[0]
name = names[0]
for file in f:
    base, ext = os.path.splitext(file)
    if(ext == ".log"):
        print(file)
        df = pd.read_json("spencers_data/%s" % (file), lines=True)  # reading data
        df['ts'] = pd.to_datetime(df['ts'], infer_datetime_format=True)

        df['ts'] = df['ts'].apply(lambda x: x + datetime.timedelta(hours=5, minutes=30))  # converrting utc time ist

        df = df.loc[df['mac'].isin([mac])]  # filtering out data corresponding to our macs

        # making code granular by per minute
        df['ts'] = df['ts'].apply(lambda x: x.strftime('%H:%M'))
        df = df.groupby(['nasid', 'controllerid', 'position', 'ts', 'mac']).mean()
        df.reset_index(inplace=True)

        df = df.groupby(['nasid', 'position', 'ts', 'mac'])
        lst = list(df)
        df_loc_track = pd.DataFrame(columns=['nasid', 'position', 'ts', 'mac', 'controllerid', 'pwr', 'count'], dtype=object)

        for i in range(len(lst)):
            x = lst[i]

            cid_list = list(map(str, x[1]['controllerid'].tolist()))
            pwr_list = list(map(str, x[1]['pwr'].tolist()))

            df_loc_track.loc[i, :] = [x[0][0], x[0][1], x[0][2], x[0][3], " ".join(cid_list), " ".join(pwr_list), len(cid_list)]

        df_loc_track.reset_index(inplace=True)

        for index, row in df_loc_track.iterrows():
            print(row['ts'])

            if row['count'] >= 2:
                controllers = list(map(int, row['controllerid'].split()))
                powers = list(map(float, row['pwr'].split()))
                mac = row['mac']
                ts = row['ts']
                print(ts)
                circles = []

                for cid, power in zip(controllers, powers):
                    radial_distance = utility.rssi_to_dis(power)
                    circles.append((aps[int(cid)], radial_distance))

                intersection = utility.heuristic_3(circles)

                # plot_circles(circles, mac, ts)

                if intersection == None:
                    pass
                elif (ts in ts1):
                    test_dict1[ts] = (intersection.x, intersection.y)
                    print(test_dict1[ts])
                else:
                    print("Not in path %s" % (ts))

count = 0
num_loc = 0
target = "plots/heuristic3/" + name
ax.legend([path, validation], ["# points: %d" % (num_loc)])

for ts in validation_dict1:
    count += 1
    update(validation, [validation_dict1[ts][0]], [validation_dict1[ts][1]])
    if ts in test_dict1:
        num_loc += 1
        update(path, [test_dict1[ts][0]], [test_dict1[ts][1]])
        ax.legend([path, validation], ["# points: %d\ntime: %s" % (num_loc, ts)])

    if not os.path.exists(target):
        os.makedirs(target)

    plt.savefig(target + "/%03d.png" % count)
    ax.set_title("%s\nHeurisitic 3" % (name))
    plt.pause(0.2)

ax.set_title("%s\nHeurisitic 3\nRMSQ: %f" % (name, utility.root_mean_square_error(validation_dict1, test_dict1)))
plt.savefig(target + "/%03d.png" % (count + 1))
plt.show()
