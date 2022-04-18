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
    
def get_inverted_sites(sites):
    lookup = {}
    for site_num, info in sites.items():
        if info['meta']['Main Street'] in lookup:
            lookup[info['meta']['Main Street']].append({site_num: info['meta']['Cross Street']})
        else:
            lookup[info['meta']['Main Street']] = [{site_num: info['meta']['Cross Street']}]
    return lookup

def get_sites_from_street_name(name, suffix: str, sites, **kwargs):
    
    name = str(name)
    full_name = name + ' ' + suffix
    
    lookup = get_inverted_sites(sites)
    
    if kwargs.get('as_list', False):
        return [list(site.keys())[0] for site in lookup[full_name]]    
    return lookup[full_name]


#%%

if __name__ == '__main__':
    from pathlib import Path
    
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    DATA_DIR = PROJECT_ROOT.parent.joinpath('data/interim')
    
    while True:
        try:
            response = input("Do you want to retrieve(r) or store(s) midblock data?").lower().strip()
            if response == "r" or response == "retrieve":
                sites = sites = get_midblock_data(DATA_DIR)
                print('~~\nThe midblock information in interim data is now in the "sites" variable')
                break
            elif response == "s" or response == "store":
                store_midblock_data(DATA_DIR, sites)
                print('~~\nThe data currently stored in the "sites" variable was saved')
                break
            elif response == "exit":
                print('~~\nNo data was stored or retrieved')
                break
            else:
                print('Invalid input. Try Again. \n -> Type "exit" to leave.')
        except:
            print('Invalid input. Try Again')
    