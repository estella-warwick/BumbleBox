#!/usr/bin/env python

import pandas as pd
import numpy as np

def compute_speed(df: pd.DataFrame, fps: int, speed_cutoff_seconds: int) -> pd.DataFrame:
    
    speed_cutoff_frames = fps*speed_cutoff_seconds
    # Sorting by ID and frame ensures that we compare positions of the same bee across consecutive frames
    df_sorted = df.sort_values(by=['ID', 'frame'])
   
    # Compute the difference between consecutive rows for centroidX and centroidY
    df_sorted['deltaX'] = df_sorted.groupby('ID')['centroidX'].diff()
    df_sorted['deltaY'] = df_sorted.groupby('ID')['centroidY'].diff()
    
    df_sorted['elapsed frames'] = df_sorted.groupby('ID')['frame'].diff()
    # Compute the Euclidean distance, which gives speed (assuming frame rate is constant)
    sub_df = df_sorted[ df_sorted['elapsed frames'] < speed_cutoff_frames ]
    sub_df['speed'] = np.sqrt(sub_df['deltaX']**2 + sub_df['deltaY']**2)
    df_sorted.loc[:, 'speed'] = sub_df.loc[:, 'speed']
    # Drop temporary columns used for computations
    df_sorted.drop(columns=['deltaX', 'deltaY'], inplace=True)
    return df_sorted
    
    

def compute_social_center_distance(df: pd.DataFrame) -> pd.DataFrame:
    # Compute the social center for each frame
    social_centers = df.groupby('frame')[['centroidX', 'centroidY']].mean()
    social_centers.columns = ['centerX', 'centerY']
   
    # Merge the social centers with the main dataframe to calculate distances
    df = df.merge(social_centers, left_on='frame', right_index=True)

    # Compute the distance of each bee from the social center of its frame
    df['distance_from_center'] = np.sqrt((df['centroidX'] - df['centerX'])**2 + (df['centroidY'] - df['centerY'])**2)
   
    # Drop temporary columns used for computations
    df.drop(columns=['centerX', 'centerY'], inplace=True)
   
    return df
    


def compute_average_distance_and_speed_per_video(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    # Setup logging
    df_sorted = df.sort_values(by=['ID','frame'])
    average_distances = df_sorted.groupby('ID')['distance_from_center'].mean()
    average_speed = df_sorted.groupby('ID')['speed'].mean()
    speed_count = df_sorted.groupby('ID')['speed'].count()
    frame_count = df_sorted.groupby('ID')['ID'].count()
    #datetime = df_sorted['datetime']
    video_tally = pd.DataFrame({'filename': filename,
                                  'average distance from center': round(average_distances),
                                  'average speed': round(average_speed),
                                  'frames tracked in video':frame_count})
    video_tally.reset_index(inplace=True)
	#rearrange columns so filename comes first
    video_tally = video_tally[['filename','ID','average distance from center','average speed','frames tracked in video']]
    video_tally.to_csv('behavior_quantification.csv', mode='a', index=False, header=False)
    return video_tally
    

def store_cumulative_averages(filename: str):
    df = pd.read_csv('behavior_quantification.csv', index_col=None, header=0)
    print(df.columns.values)
    df_sorted = df.sort_values(by=['ID'])
    average_distances = df_sorted.groupby('ID')['average distance from center'].mean()
    average_speed = df_sorted.groupby('ID')['average speed'].mean()
    frame_count = df_sorted.groupby('ID')['frames tracked in video'].sum()
    cumulative_tally = pd.DataFrame({'filename': df_sorted['filename'].iloc[-1],
                                  'average distance from center': round(average_distances,2),
                                  'average speed': round(average_speed,2),
                                  'total tracked frames':frame_count})
    cumulative_tally.reset_index(inplace=True, drop=False)
    cumulative_tally = cumulative_tally[['filename','ID','average distance from center','average speed','total tracked frames']]
    cumulative_tally.to_csv('cumulative_averages.csv', mode='w', index=False, header=True)
