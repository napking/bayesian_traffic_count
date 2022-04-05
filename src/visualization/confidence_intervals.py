# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 22:02:46 2022

@author: Dave
#visualization/confidence_invervals.py
"""

import scipy.stats as st
import pandas as pd
import sys

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))


import util

sites = util.get_midblock_data(PROJECT_ROOT.parent.joinpath('data/interim') )

#%%

# temporary method: merge all dataframes

data = pd.DataFrame()

for key, value in sites.items():
    data = pd.concat([data, sites[key]['data']] )

data = data[ ~data['Weekday'].str.contains('avg', case=False)]
data = data[ ~data['Direction'].str.contains('total', case=False)]

data['Weekend_TF'] = data['Weekday'].str.contains('Saturday|Sunday', case=False)

group_count = data.groupby(['Site Number','Direction','Obs_Hour','Weekend_TF'])['count']
stats = group_count.agg(['mean','std','count']).sort_values(by=['count','mean','std'])

# create a tuple of confidence intervals
ci = st.t.interval(alpha=0.95, df=stats['count'] - 1, loc=stats['mean'], scale=stats['std'])
# convert the tuple into a dataframe (transposed)
ci = pd.DataFrame(list(zip(*ci)), columns=['95_lower','95_upper'])
# merge the confidence intervals into the stats
stats = pd.merge(stats.reset_index(), ci, how = 'outer', left_index = True, right_index = True)
# get the total range of the 95% confidence interval
stats['ci_range'] = stats['95_upper'] - stats['95_lower']
stats.sort_values(by=['ci_range'], ascending=False, inplace=True)
