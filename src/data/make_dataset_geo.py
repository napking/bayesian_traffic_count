# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 18:39:04 2022

@author: Dave
"""

from pathlib import Path
from datetime import datetime
import pandas as pd
import geopandas
from config.definitions import ROOT_DIR, DATA_DIR
#%%
## Pseudo Code

## get shapefile path
#%% Geo Shapefile

shapefiles = [file for file in Path(ROOT_DIR / 'data/raw/Road Network').
              glob(pattern='*.shp')]

## load into geo dataframe

yeg_network = geopandas.read_file(shapefiles[0])

## need a system to cross-reference sites from shapefile against sites from count data
## count data has meta data as follows:
"""
    {'ADT': 729,
     'Site Number': 237730,
     'Location': ' 81 Avenue West of 104 Street',
     'Peak Hour AM': 42,
     'Peak Hour AM ref': '8:05 AM-9:05 AM',
     'Peak Hour PM': 59,
     'Peak Hour PM ref': '5:30 PM-6:30 PM',
     'Main Street': '81 avenue',
     'Cross Street': '104 street',
     'Cross Reference': 'west of'}
"""

## shapefile has meta data as follows:
'''
    	ID        STREET_NAM	START_MARK	    END_MARK	    FUNCTION
37015	299729    81 AVENUE NW	104 STREET NW	105 STREET NW	C-R
'''

## Goal is to translate one into the other and get a cross-reference table for shapefile ID against sites ID

## First Assumption:
    # Start Mark is Always further east than end mark.
    # this can be confirmed using only the sites that have numerical start and end marks.
    
## Extract numerical portion and 