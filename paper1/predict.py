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
ax.set_xlim(-50,50)
ax.set_ylim(-50,50)

aps_plot, = ax.plot([-22, 0, 0, -22], [1, 1, 24, 26], marker='o', markersize=10, ls='')
validation, = ax.plot([], [], marker='o', markersize=3, color='g')
path, = ax.plot([], [], marker='+', markersize=3, color='red')

para_file = open("path1_params.csv", "r")
param = {}
for line in para_file:
    line = list(map(float, line.split(',')))
    param[int(line[0])] = line[1:]

print(param)


def update(obj, x, y):
    x_old = obj.get_xdata()
    y_old = obj.get_ydata()
    x_old = np.append(x_old, x)
    y_old = np.append(y_old, y)
    obj.set_data(x_old, y_old)
    plt.pause(0.2)


f = os.listdir('../spencers_data')
f.sort()

# reading and plotting validation data
df_path = pd.read_csv("outputs_path1.csv")
df_path['Start_time'] = pd.to_datetime(df_path['Start_time'], infer_datetime_format=True)
# df_path['Start_time'] = df_path['Start_time'].apply(lambda x: x + datetime.timedelta(hours=12))  # todo write proper code
df_path['Start_time'] = df_path['Start_time'].apply(lambda x: x.strftime('%H:%M'))
x_validation = df_path['X'].tolist()
y_validation = df_path['Y'].tolist()
ts1 = df_path['Start_time'].tolist()

dict_path2 = {}
for a, b, c in zip(ts1, x_validation, y_validation):
    dict_path2[a] = (b, c)

print(ts1)
test_dict = {}

mac = macs[0]
name = names[0]
for file in f:
    base, ext = os.path.splitext(file)
    if(ext == ".log"):
        print(file)
        df = pd.read_json("../spencers_data/%s" % (file), lines=True)  # reading data
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

        x1, y1 = (0, 0)
        x2, y2 = (0, 1)
        for index, row in df_loc_track.iterrows():
            if row['count'] >= 2:
                controllers = list(map(int, row['controllerid'].split()))
                powers = list(map(float, row['pwr'].split()))
                mac = row['mac']
                ts = row['ts']
                print(ts)
                circles = []

                for cid, power in zip(controllers, powers):
                    radial_distance = utility.rssi_to_dis(power, param[cid][1], param[cid][0])
                    circles.append((aps[int(cid)], radial_distance))

                intersection = utility.heuristic_3(circles)

                ds = []
                for cid, power in zip(controllers, powers):
                    radial_distance = utility.rssi_to_dis(power, param[cid][1], param[cid][0])
                    ds.append(radial_distance)
                
                intersection = utility.optimum(controllers, powers, param, (x1, y1), x1, y1, x2, y2)
                
                intersection_arr = []
                intersection_arr.append(utility.optimum(controllers, powers, param, (x1, y1), x1, y1, x2, y2))
                for i in range(5):
                    intersection_arr.append(utility.optimum(controllers, powers+5*np.random.randn(len(powers)), param, (x1, y1), x1, y1, x2, y2))

                intersection = [0, 0]
                for x in intersection_arr:
                    intersection[0] += x[0]
                    intersection[1] += x[1]
                intersection[0] = intersection[0]/len(intersection_arr)
                intersection[1] = intersection[1]/len(intersection_arr)

                x1, y1 = x2, y2
                x2, y2 = intersection
                # plot_circles(circles, mac, ts)

                if len(intersection) == 0:
                    pass
                elif (ts in ts1):
                    test_dict[ts] = intersection
                    print("Yo", test_dict[ts])
                else:
                    print("Not in path %s" % (ts))

count = 0
num_loc = 0
target = "plots/test/" + name
ax.legend([path, validation], ["# points: %d" % (num_loc)])

for ts in dict_path2:
    count += 1
    update(validation, [dict_path2[ts][0]], [dict_path2[ts][1]])
    if ts in test_dict:
        num_loc += 1
        update(path, [test_dict[ts][0]], [test_dict[ts][1]])
        ax.legend([path, validation], ["# points: %d\ntime: %s" % (num_loc, ts)])
        # for i in range(6):
        #     update(path, [test_dict[ts][i][0]], [test_dict[ts][i][1]])
        #     ax.legend([path, validation], ["# points: %d\ntime: %s" % (num_loc, ts)])

    # plt.savefig(target + "/%03d.png" % count)
    ax.set_title("%s\nHeurisitic 3" % (name))
    plt.pause(0.2)

print utility.root_mean_square_error(dict_path2, test_dict)
ax.set_title("%s\nHeurisitic 3\nRMSQ: %f" % (name, utility.root_mean_square_error(dict_path2, test_dict)))
# plt.savefig(target + "/%03d.png" % (count + 1))
plt.show()
