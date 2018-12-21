import pandas as pd
import numpy as np

aps = {
    1: (-22, 1),
    2: (0, 1),
    3: (0, 24),
    4: (-22, 26)
}


def ulr_normal(x, y):
    theta = np.matrix(x.T @ x)
    theta = theta.I @ x.T @ y
    theta = np.squeeze(np.asarray(theta))
    return theta


path_num = 2

for ap in aps:
    P = pd.read_csv('inputs_path%d.csv' % (path_num))
    # P = P.append(pd.read_csv('inputs_path%d.csv' % (path_num+1)))
    P = P[['ts', 'pwr']]
    P['pwr'] = P['pwr'].apply(lambda x: np.float64(x.split()[ap - 1]))
    P.sort_values('ts', inplace=True)

    D = pd.read_csv('outputs_path%d.csv' % (path_num))
    # D = D.append(pd.read_csv('outputs_path%d.csv' % (path_num+1)))
    D['X'] = D['X'].apply(lambda x: float(x))
    D['Y'] = D['Y'].apply(lambda x: float(x))
    D['d'] = np.sqrt((D['X'] - aps[ap][0])**2 + (D['Y'] - aps[ap][1])**2)
    D['d'] = D['d'] * (39.3701 / 34)
    D['d'] = (-10)*(np.log10(D['d']))
    D = D[['Start_time', 'd']]
    D = D.loc[D['Start_time'].isin(P['ts'].tolist())]

    D.sort_values('Start_time', inplace=True)
    D.drop(['Start_time'], axis=1, inplace=True)
    D = D.as_matrix()
    D = np.insert(D, 0, 1.0, axis=1)

    P = P['pwr'].tolist()
    theta = ulr_normal(D, P)
    print(str(ap) + ",", str(theta[0]) + ",", str(theta[1]))
