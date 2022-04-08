# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 21:54:31 2022

@author: Dave

#util/get_data.py
"""

#%%
import shelve



#%%
def store_midblock_data(directory, interim_data):
    with shelve.open(str(directory / 'traffic_data')) as shelf:
        shelf['midblock_sites'] = interim_data
    return

def get_midblock_data(directory):
    with shelve.open(str(directory / 'traffic_data')) as shelf:
        return shelf['midblock_sites']
    
def get_site_from_street_name(name, suffix: str, sites):
    
    name = str(name)
    full_name = name + ' ' + suffix
    return




#%%

if __name__ == '__main__':
    from pathlib import Path
    
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    DATA_DIR = PROJECT_ROOT.parent.joinpath('data/interim')
    
    sites = get_midblock_data(DATA_DIR)