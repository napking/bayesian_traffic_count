# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 22:02:46 2022

@author: Dave
#visualization/confidence_invervals.py
"""

import scipy.stats as st
import pandas as pd
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))
DATA_DIR = PROJECT_ROOT.parent.joinpath('data/interim')

import util

sites = util.get_midblock_data(DATA_DIR)

#%% temporary method: merge all dataframes

data = pd.DataFrame()

for key, value in sites.items():
    data = pd.concat([data, sites[key]['data']] )

data = data[ ~data['Weekday'].str.contains('avg', case=False)]
data = data[ ~data['Direction'].str.contains('total', case=False)]

data['Weekend_TF'] = data['Weekday'].str.contains('Saturday|Sunday', case=False)
data['Obs Hour'] = data['Obs Period'].dt.hour
#data['Site Number'] = data['Site Number'].astype('category')

group_count = data.groupby(['Site Number','Direction','Obs Hour','Weekend_TF'])['count']
stats = group_count.agg(['mean','std','count']).sort_values(by=['count','mean','std'])

# create a tuple of confidence intervals
ci = st.t.interval(confidence=0.95, df=stats['count'] - 1, loc=stats['mean'], scale=stats['std'])
# convert the tuple into a dataframe (transposed)
ci = pd.DataFrame(list(zip(*ci)), columns=['95_lower','95_upper'])
# merge the confidence intervals into the stats
stats = pd.merge(stats.reset_index(), ci, how = 'outer', left_index = True, right_index = True)
# get the total range of the 95% confidence interval
stats['ci_range'] = stats['95_upper'] - stats['95_lower']
stats.sort_values(by=['ci_range'], ascending=False, inplace=True)

#%% get specific sites by name

mask = util.get_sites_from_street_name(82, 'avenue', sites, as_list=True)
subset = stats[stats['Site Number'].isin(mask)]

#%% Rough method to get get some kind of chart
fig, ax = plt.subplots()

chosen_site = [522128, 522168]
for x in chosen_site:
    double_subset = subset[subset['Site Number'] == x] \
        .query("~Weekend_TF") \
            .query("Direction == 'EBD'") \
                .sort_values('Obs Hour')
    
    ax.errorbar(x=double_subset['Obs Hour'], 
            y=double_subset['mean'], 
            yerr=double_subset['ci_range'])
    
    
#%% New method, but using seaborn now to calculate the error bars

subset = data[data['Site Number'].isin(np.random.choice(mask, 3, replace=False))].copy()
subset['Site Number'] = subset['Site Number'].astype('category')
sns.lineplot(data=subset,
             x='Obs Hour', y='count',
             hue='Direction', style='Site Number',
             err_style="bars", ci=95)