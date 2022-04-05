# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 22:02:46 2022

@author: Dave
#visualization/confidence_invervals.py
"""



import sys

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))


import util
print(util.get_length("Hello"))

