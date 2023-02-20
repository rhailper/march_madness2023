import os
import time
import pandas as pd
from tqdm import tqdm

def get_data_coaches_poll_and_conf_summary(year):
    '''reads in the data from the web and does some basic cleaning'''
    # read in the data from sportsref
    dfs = pd.read_html(
        f'https://www.sports-reference.com/cbb/seasons/{year}.html')
    # Coaches poll
    # remove unessary rows/columns
    coaches_poll = dfs[1].droplevel([0, 2], axis=1)
    coaches_poll = coaches_poll.drop(index=[20, 21])
    # rename columns
    coaches_poll = coaches_poll.rename(
        {'Unnamed: 0_level_1': 'school', 'Unnamed: 1_level_1': 'conference'}, axis=1)
    # set school and conference as index
    coaches_poll = coaches_poll.set_index(['school', 'conference'])
    # convert columns to floats
    for col in coaches_poll.columns:
        coaches_poll[col] = coaches_poll[col].astype(float)
    # add mean and median
    coaches_poll['median'] = coaches_poll.median(axis=1, skipna=True)
    coaches_poll['mean'] = coaches_poll.mean(axis=1, skipna=True)
    # reset index
    coaches_poll = coaches_poll.reset_index()
    # Conference Summary
    conf_summary = dfs[0]
    # rename columns
    conf_summary.columns = [col.lower().replace(' ', '_')
                            for col in conf_summary.columns]
    conf_summary = conf_summary.rename(
        {'Schls': 'num_schools', 'rk': 'rank'}, axis=1)
    return conf_summary, coaches_poll

def get_ratings(year):
    # read in df
    df = pd.read_html(f'https://www.sports-reference.com/cbb/seasons/men/{year}-ratings.html')[0].droplevel(0,axis=1)
    # rename columns
    df.columns = [col.lower().replace(' ', '_')
                            for col in df.columns]
    # drop blank columns
    df = df.drop(['unnamed:_3_level_1','unnamed:_9_level_1','unnamed:_11_level_1'],axis=1)
    # drop bad rows
    rows_to_drop = sorted(list(range(21,len(df),22)) + list(range(20,len(df),22)))
    df = df.drop(rows_to_drop)
    return df

# read in the data from 2013 to 2022 and save each to csv file
conf_dfs = []
coaches_dfs = []
ratings_dfs = []
for year in tqdm(range(2013, 2023)):

    # check to see if df is already there (coaches polls and conference summaries)
    if f'coaches_polls_{year}.csv' in os.listdir('../data/coaches_polls/'):
        conf_df = pd.read_csv(f'../data/conference_summaries/conference_summary_{year}.csv')
        coach_df = pd.read_csv(f'../data/coaches_polls/coaches_polls_{year}.csv')
    else:
        conf_df, coach_df = get_data_coaches_poll_and_conf_summary(year)
        # wait 12 seconds before making another call
        time.sleep(12)
        # add year columns
        conf_df['year'] = year
        coach_df['year'] = year
        # save each to csv
        conf_df.to_csv(
            f'../data/conference_summaries/conference_summary_{year}.csv', index=False)
        coach_df.to_csv(f'../data/coaches_polls/coaches_polls_{year}.csv', index=False) 
    
    # team ratings
    if f'ratings_{year}.csv' in os.listdir('../data/ratings/'):
        ratings_df = pd.read_csv(f'../data/ratings/ratings_{year}.csv')
    else:
        ratings_df = get_ratings(year)
        ratings_df['year']='year'
        # wait 12 seconds before making another call
        time.sleep(12)
        ratings_df.to_csv(f'../data/ratings/ratings_{year}.csv')
    # append to larger list
    conf_dfs.append(conf_df)
    coaches_dfs.append(coach_df)
    ratings_dfs.append(ratings_df)

# combine all dfs into large dfs
final_conf_df = pd.concat(conf_dfs)
final_coaches_df = pd.concat(coaches_dfs)
final_ratings_dfs = ratings_dfs.append(ratings_dfs)

# save both to csv's
final_conf_df.to_csv('../data/conference_summaries/conference_summaries.csv', index=False)
final_coaches_df.to_csv('../data/coaches_polls/coaches_polls.csv', index=False)
final_coaches_df.to_csv('../data/ratings/ratings.csv', index=False)
