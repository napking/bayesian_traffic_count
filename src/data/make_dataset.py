# -*- coding: utf-8 -*-

import logging
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
from tqdm import tqdm
# import geopandas
from config.definitions import ROOT_DIR, DATA_DIR

logger = logging.getLogger(__name__)

# Useful for finding various files
# TODO: Update to use ROOT_DIR from config/definitions.py
project_dir = Path(__file__).resolve().parents[2]
midblock_dir = project_dir / 'data/raw/My Traffic Volumes'

#%%

def get_random_file(directory=DATA_DIR / 'raw/My Traffic Volumes'):
    logger.debug('start'.center(20,'~'))
    from random import choice    
    files = [f for f in Path(directory).glob(pattern = '*.xls')] #glob yields all files matching the pattern argument. '*' means all    
    return choice(files)

#%%

def main():
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger.debug('start'.center(20,'~'))
    logger.info('making final data set from raw data')

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    
    # create logger Handlers
    f_handler = logging.FileHandler('make_dataset.log', mode='w')
    c_handler = logging.StreamHandler()
    f_handler.setLevel(logging.DEBUG)
    c_handler.setLevel(logging.WARNING)
    log_fmt = "[%(filename)s:%(lineno)s@%(asctime)s - %(funcName)40s():%(levelname)9s ] %(message)s"
    f_handler.setFormatter(logging.Formatter(log_fmt))
    c_log_fmt = "[%(lineno)s@%(asctime)s - %(funcName)s(): %(message)s"
    c_handler.setFormatter(logging.Formatter(c_log_fmt))
    
    # add handlers to the logger
    logging.getLogger('').addHandler(f_handler)
    logging.getLogger('').addHandler(c_handler)

    main()

#%%

def file_loop_test(directory=midblock_dir):
    '''
    Parameters
    ----------
    midblock_dir : TYPE PATH

    Returns
    -------
    print out of all files

    '''
    logger.debug('start'.center(20,'~'))
    logger.info("Files and directories in the specified path:")
    files = Path(directory).glob(pattern = '*.xls') #glob yields all files matching the pattern argument. '*' means all
    for file in tqdm(files):
        logger.info(file.stem)
        logger.warning('function output recorded in the log file')
    return file

#%%

def get_names_from_location(string):
    '''
    Parameters
    ----------
    string : TYPE
        DESCRIPTION.

    Returns
    -------
    dict
        DESCRIPTION.

    '''
    logger.debug('start'.center(20,'~'))
    regex_pattern = ('^\s*' # start of string followed by one or more whitespace
                    '(?P<mainName>\d{2,3}|Gateway)\s*' # mainName group - 2 or 3 digits OR Gateway ; the name of the main street
                    '(\(Whyte\))?\s*'   # OPTIONAL - Phrase '(Whyte)' is sometimes used to describe 82 Ave
                                        # Omitting this part of the pattern will fail the entire match for any string that contains it
                    '(?P<mainType>Street|Boulevard|Avenue)\s*' # mainType group - either Street, Boulevard or Aveneue ; the type part of the main street name
                    '(?P<reference>\w* of)\s*' # reference group - one or more of a word character (Upper/Lower agnostic) followed by ' of'
                    '(?P<crossName>\d{2,3}\w?|Gateway)\s*' # crossName group - 2 or 3 digits OR Gateway
                    '(\(Whyte\))?\s*'   # OPTIONAL - Phrase '(Whyte)' is sometimes used to describe 82 Ave
                                        # Omitting this part of the pattern will fail the entire match for any string that contains it
                    '(?P<crossType>Street|Boulevard|Avenue)' # crossType group - either Street or Boulevard or Avenue
                )
    result = re.search(regex_pattern, string)
    main_street = result.group('mainName') + ' ' + result.group('mainType').lower()
    cross_street = result.group('crossName') + ' ' + result.group('crossType').lower()
    reference = result.group('reference').lower()
    
    # TODO
    '''
        Could do a method to change all Cross Reference to either 'West of' or 'North of'
            ie. convert 'East of' and 'South of'
            problem: needs to assume a relationship for streets
    '''
    
    return {'Main Street': main_street, 'Cross Street': cross_street, 'Cross Reference': reference}

#%%

def get_date_from_filename(filename = '083 Avenue West of 098 Street 2015-Sep-23-2015-Sep-28.xls'):
    '''
    Parameters
    ----------
    filename : string
        get the filename from a Path object through {file}.stem

    Returns
    -------
    dictionary
    year as int, month as string, date as int

    '''
    logger.debug('start'.center(20,'~'))
    regex_pattern = r'(?P<year>\d{4})-(?P<month>\w{3})-(?P<date>\d{2})\s*$'
    # Pattern group 1: { name: 'year', value: 4 digits } \
        # group 2: { name: 'month', value: 3 word characters } \
        # group 3: { name: 'date', value: 2 digits } \
        # all found at the end of the string ($-anchor) with one or more whitespace characters {\s*}
    result = re.search(regex_pattern , filename)
    year = int(result.group('year'))
    month = result.group('month').lower()
    date = int(result.group('date'))
    return {'year':year, 'month':month, 'date':date}

#%%

def parse_midblock_excel(file = midblock_dir / '083 Avenue West of 098 Street 2015-Sep-23-2015-Sep-28.xls'):
    '''
    Parameters
    ----------
    file : PATH to excel file

    Returns
    -------
    DataFrame in tall format
    meta data of the analysis site
    '''    
    logger.debug('start'.center(20,'~'))
    df = pd.read_excel(file, header=None)  
    meta = get_meta_data(df)
    
    # Get First Row of data table
    # look at the 0th column and find the first row that is not NaN
    start = df[0].first_valid_index()
    
    # Get the Last Row of the data table
    # look for the value "Total" in the first column
    end = df.index[df[0] == 'Total'][0]
    
    # Send this stuff to get the data table only
    data_table = get_midblock_data_table(df,start,end,meta)
    
    
    return data_table, meta

    '''    
    What is the output of this function?
        -A dict of meta data
        -the data key contains a Tall format, multi-indexed dataframe
    '''

#%%
def get_midblock_data_table(df,start,end,meta,num_header_rows=3):
    '''
    Parameters
    ----------
    df : dataFrame
        the dataframe to be analyzed
    start : int
        start row of the data table
    end : int
        last row of the data table
    meta : dict
        meta data of the site being analyzed
    num_header_rows : int
        default value of 3
        number of rows that act as column / value identifiers
    
    '''
    logger.debug('start'.center(20,'~'))
    # strip down to only the data table and headers
    df = df.iloc[start - num_header_rows : end]
    df = df.reset_index(drop=True)
    
    '''
    *** want to clean up the merged cells from excel and use the multiple rows that act as headers
    This is what the header looks like at this point:
                                 Merged Cells     Merged Cells
                                 _____________________________________________
                                 1    2      3     4    5      6   7    8
    Header 1 | NaN             Saturday  NaN    NaN  Avg.  NaN    NaN NaN  NaN
    Header 2 | NaN  2017-08-15 00:00:00  NaN    NaN   NaN  NaN    NaN NaN  NaN
    Header 3 | NaN                  NBD  SBD  Total   NBD  SBD  Total NaN  NaN    
    
    '''
    
    # forward fill "Avg." into the second header row
    idx_avg = get_index(df, 'Avg.')
    df = df.loc[idx_avg[0]:].fillna(method='ffill', axis=0)
    
    # forward fill the cells with NA. method='ffill' propagates last valid observation forward to next
    df.iloc[0 : num_header_rows] = df.iloc[0 : num_header_rows].fillna(method='ffill', axis=1)
    
    # fill in the remaining NaNs with an empty string
    df.iloc[0 : num_header_rows].fillna(value='')
    
    # set the index to observation hour
    df = df.set_index(0)
    df.index.name = 'Obs Hour'
    
    # set columns from the header rows and drop them
    df.columns = [df.iloc[i] for i in range(num_header_rows) ]
    df = df.iloc[num_header_rows:]
    
    # set column names
    df.columns.names = ['Weekday', 'Date', 'Direction']
    
    # remove any columns that are entirely NA
    df = df.dropna(axis='columns', how='all')
    
    # convert to Tall format
    df = df.melt(value_name='count', ignore_index=False)
    # no longer need to have "observation hour" as the index
    df.reset_index(inplace=True)
    # remove Avg. values
    df = df[~df['Date'].astype(str).str.contains('avg', case=False)]
    # fix date and time information
    df['Obs Hour'] = pd.to_datetime(df['Obs Hour'].astype(str), format='%H:%M:%S').dt.time
    df['Date'] = pd.to_datetime(df['Date'].astype(str), format='%Y-%m-%d').dt.date
    df['Obs Period'] = df.apply(
        lambda r : pd.Timestamp.combine(r['Date'], 
                                        r['Obs Hour']), 
        axis=1).dt.to_period('H')
    '''
    At this point, the "Date", "Obs Hour", and "Weekday" columns are redundant.
    All this information is captured within the "Obs Period" datetime object
    #TODO: Remove redundant columns
        Waiting to confirm that downstream pipeline can retrieve the necessary
        information from the datetime object
    '''
    # add site identifying values
    df['Site Number'] = meta['Site Number']
    # set street names as identifying values
    df['Main Street'] = meta['Main Street']
    df['Location'] = meta['Location']
    

    
    return df

#%%    
def get_meta_data(df):
    '''
    continue working here
    
    want to find specific values in dataframe (ADT, Site Number) w/o knowing which row or column they are in
    
    
    '''
    logger.debug('start'.center(20,'~'))
    meta = {}
    search_pattern = ['ADT','Site Number','Location']
    for pat in search_pattern:
        # For ADT, Site Number and Location, just assume that the value is offset by 0 rows, 3 columns
        idx = get_index(df, pat)
        meta[pat] = df.iloc[idx[0], idx[1] + 3]
    
    search_pattern = ['Peak Hour AM', 'Peak Hour PM']
    for pat in search_pattern:
        # For Peak Hour, just assume that the value is offset by 2 rows, 1 columns
        idx = get_index(df, pat)
        meta[pat] = df.iloc[idx[0] + 2, idx[1] + 1]
        # also assume the reference hour is offset by 1 row, 1 column
        meta[pat + ' ref'] =df.iloc[idx[0] + 1, idx[1] + 1]
        
    meta.update( 
        get_names_from_location(meta['Location']) 
        )
    
    return meta
        

#%%   
def get_index(df, search_pattern):
    logger.debug('start'.center(20,'~'))
    #explanation of this code:
        #df.isin([*]) returns a true/false table of the entire dataframe where * is found
        #df[ above_blah ] returns a NaN / value table as above
        # {}.stack() reshapes the dataframe into a multiIndex dataframe with rows only where * was found
            #multiIndex contains the row/column of * from the original dataframe
        # {}.index[0] gets the first found instance and returns a tuple of (row, column)
    return df[df.isin([search_pattern])].stack().index[0]
    

#%%

def get_traffic_sites(directory=midblock_dir, start_year=1999, **kwargs):
    logger.debug('start'.center(20,'~'))
    
    sites = {}
    
    if kwargs.get('midblock') or kwargs.get('link'):
        # do get midblock sites
        # run custom function which returns sites dict
        midblock_sites = get_midblock_sites(directory, start_year)
        if midblock_sites:
            logger.debug('merging sites dict')
            sites = sites | midblock_sites
            logger.debug(f'sites dict has {len(sites)} entries')
    
    if kwargs.get('node') or kwargs.get('intersection') or kwargs.get('turning'):
        # do get turning movement sites
        # run custom function which returns sites dict
        dummy = True
    
    return sites
    
def get_midblock_sites(directory, start_year):
    logger.debug('start'.center(20,'~'))
    
    sites = {}
    
    # confirm that directory is good
    if directory.name != 'My Traffic Volumes':
        logger.error('~~ Incorrect Directory for get_midblock_sites()')
        return None
    
    logger.debug('Start loop of all files')
    # Start a Loop of all files
    # glob searches for all files that match the given pattern. "*.xls" only finds excel files
    midblock_files = Path(directory).glob(pattern = "*.xls")
    for file in tqdm(midblock_files, desc='looping midblock excel files', unit='Files'):
        logger.debug('<>new file<>')
        logger.debug(f'{file.stem}')
        try:
            file_date = get_date_from_filename(file.stem)
            logger.info(f'{file.stem} date found')
        except:
            file_date['year'] = 'None'
            logger.warning(f'{file.stem} could not be parsed')
            continue
            
        # Select only files after a specific year.
        if file_date['year'] >= start_year:
            logger.debug(f'{file.stem} year is good')
            data_table, meta = parse_midblock_excel(file)
            logger.debug(f'{file.stem} got data_table and meta')
            if not meta['Site Number'] in sites:
                # If site number is not already in sites, simply create a new key-value pair
                sites[meta['Site Number'] ] = {'meta': meta, 'data': data_table}
                logger.info(f'{file.stem} successfully added')
            else:
                # merge meta and data
                logger.info(f'Site number {meta["Site Number"]} already exists. \n' \
                      f'~{file.stem} Attempting merge')
                
                # Try to append meta-data into sites
                if not append_duplicate_site_meta(
                        master_meta= sites[meta['Site Number']]['meta'], 
                        append_meta= meta):
                    # if immutable keys are not identical, create a new site
                    sites[meta['Site Number'] ] = {'meta': meta, 'data': data_table}
                    logger.debug(f'{file.stem} successfully added')
                
                # Try to append dataframe into sites
                sites[meta['Site Number']]['data']= append_duplicate_site_data(
                    master_data= sites[meta['Site Number']]['data'], 
                    append_data= data_table)
                logger.info(f'{file.stem} count data added to dataframe')
        else:
            continue
    
    logger.debug('done'.center(20,'~'))
    return sites


#%%
def parse_turning_excel(file = project_dir / 'data/raw/My Turning Movements/081 Avenue and 104 Street 2014-Mar-11.xls'):
    logger.debug('start'.center(20,'~'))
    return None

#%%
def append_duplicate_site_meta(master_meta, append_meta):
    '''
    master_meta and append_meta _*should*_ have the same key->value structure
        (if not, then something has gone horribly wrong)
    Certain values should be the same between dictionaries, they are identifiers for the site:
        Cross Reference
        Cross Street
        Location
        Main Street
        Site Number
            (if these aren't the same then something has gone horribly wrong)
    Other values are unique for the specific observation "blitz" that collected the data:
        ADT
        Peak Hour AM
        Peak Hour AM ref
        Peak Hour PM
        Peak Hour PM ref
            These values should be converted into a list
            The order of this list *should never change*, otherwise the relationship between lists is lost
            
            *** The alternate solution is to assign keys to values representing the source excel file
    '''
    logger.debug('start'.center(20,'~'))
    # Check the immutable, aka. common values, between the dictionaries
    immutable_keys = {'Cross Reference','Cross Street','Main Street','Site Number'}
    master_immutable = {key:value for key,value in master_meta.items() if key in immutable_keys}
    append_immutable = {key:value for key,value in append_meta.items() if key in immutable_keys}
    if not master_immutable == append_immutable:
        logger.error(f'The meta data for Site Number {master_meta["Site Number"]} is not the same between master and append')
        # TODO: Do something when this error occurs
        # initial experience susggests the source is in "Location" names from excel files
            # see the regex in get_names_from_location
            
        # perhaps an intermediary step is to create a new entry in sites, eg. site_number: ######-A
        append_meta['Site Number'] = str(append_meta['Site Number']) + 'A'
        logger.error(f'\t  Changed Site Number: {append_meta["Site Number"]}')
        return False
        
    # Check the mutable, aka. the varrying values
    mutable_keys = {'ADT', 'Peak Hour AM', 'Peak Hour AM ref', 'Peak Hour PM', 
                    'Peak Hour PM ref'}
    # loop through master_meta
    for key,value in master_meta.items():
        if key not in mutable_keys:
            # do nothing
            continue
        elif not type(master_meta[key]) == list:
            # convert to a list type
            master_meta[key] = [master_meta[key]]
        # append the meta[key] into the list for the master[key]
        master_meta[key].append(append_meta[key])
        
    # check the 'Location' tag. This is raw from the excel file, with little processing.
        # possibility of erroneous/non-standard entries
        
    
    logger.info(f'Site: {master_meta["Site Number"]} has appended the new values')
    
    return True

#%%
def append_duplicate_site_data(master_data, append_data):
    logger.debug('start'.center(20,'~'))
    return pd.concat([master_data, append_data]).reset_index(drop=True)