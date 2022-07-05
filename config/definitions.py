# -*- coding: utf-8 -*-
"""
Created on Thu May 26 14:05:48 2022

@author: Dave
"""

from pathlib import Path
ROOT_DIR = Path(__file__).parents[1]

DATA_DIR = ROOT_DIR / 'data'
DATA_INTERIM_DIR = DATA_DIR / 'interim'
SHELF_NAME = 'interim_data'

REPORT_DIR = ROOT_DIR / 'reports'
VIS_DIR = ROOT_DIR / 'reports/figures/'

MODELS_DIR = ROOT_DIR / 'models'
