# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 21:54:31 2022

@author: Dave

#util/get_data.py
"""

#%%
import shelve

def store_midblock_data(directory, interim_data):
    with shelve.open(str(directory / 'traffic_data')) as shelf:
        shelf['midblock_sites'] = interim_data
    return

def get_midblock_data(directory):
    with shelve.open(str(directory / 'traffic_data')) as shelf:
        return shelf['midblock_sites']