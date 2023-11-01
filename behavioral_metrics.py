#!/usr/bin/env python

import pandas as pd
import numpy as np
import logging
import setup
from datetime import datetime as dt

logfile_folder = setup.bumblebox_dir
logging.basicConfig(filename='behavioral_metrics.log',encoding='utf-8',format='%(filename)s %(asctime)s: %(message)s', filemode='a', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.debug("importing behavioral metrics")

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
    


def compute_video_averages(df: pd.DataFrame, todays_folder_path: str, filename: str) -> pd.DataFrame:
    print('computing averages')
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
    try:
        video_tally = video_tally[['filename','ID','average distance from center','average speed','frames tracked in video']]
    except Exception as e:
        logger.debug("Exception occurred: %s", str(e))
    try:    
        video_tally.to_csv(f'{todays_folder_path}/{filename}_averages.csv', mode='w', index=False, header=True)
        logger.debug(f"data written to {todays_folder_path}/{filename}_averages.csv', but as a 1D list:\n%s", str(video_tally.values.flatten()))
    except Exception as e:
        logger.debug("Exception occurred: %s", str(e))
    return video_tally
    
    
    
def compile_dfs(directory_path, start_filename, end_filename = None, format = None, end_of_filename = 'averages.csv'):
    #not done yet!
    if format == None:
        format = '%Y-%m-%d_%H-%M-%S'
        
    hostname, date, time, ext = start_filename.split("_")
    hostname2, date2, time2, ext2 = end_filename.split("_")
    start_datetime = date + "_" + time
    end_datetime = date2 + "_" + time2
    print(end_datetime)
    
    start_datetime = dt.strptime(start_datetime, format)
    end_datetime = dt.strptime(end_datetime, format)
    
    df_list = []
    
    for paths, dirs, files in os.walk(directory_path):
        for path in paths:
            for filename in files:
                hostname3, date3, time3, ext3 = file.split("_")
                if ext3 == end_of_filename:
                    datetime = date3 + time3
                    datetime = datetime.strptime(datetime, format)
                    
                    if start_datetime <= datetime <= end_datetime:
                        print(path)
                        df = pd.DataFrame(path)
                        
            
            
            
            
            

def store_cumulative_averages(filename: str):
    #finished?
    #datetimes need to be strings in this format: "yyyy-mm-dd_HH-MM-SS"
    
    #if type(start_datetime) == str and type(end_datetime) == str:
    #    try:
    #        start_filename = 
    #        end_filename = 
            
            
    print('computing cumulative averages')
    try:
        df = pd.read_csv('behavior_quantification.csv', index_col=None, header=0)
    except Exception as e:
        logger.debug("Exception occurred: %s", str(e))
        
    try:    
        df_sorted = df.sort_values(by=['ID'])
    except Exception as e:
        logger.debug("Exception occurred: %s", str(e))
        
    average_distances = df_sorted.groupby('ID')['average distance from center'].mean()
    average_speed = df_sorted.groupby('ID')['average speed'].mean()
    frame_count = df_sorted.groupby('ID')['frames tracked in video'].sum()
    df_sorted2 = df.sort_values(by=['filename'])
    latest_filename = df_sorted2['filename'].iloc[-1]
    logger.info("latest_filename: %s", latest_filename)
    cumulative_tally = pd.DataFrame({'filename': latest_filename,
                                  'average distance from center': round(average_distances,2),
                                  'average speed': round(average_speed,2),
                                  'total tracked frames':frame_count})
    cumulative_tally.reset_index(inplace=True, drop=False)
    try:
        cumulative_tally = cumulative_tally[['filename','ID','average distance from center','average speed','total tracked frames']]
    except Exception as e:
        logger.debug("Exception occurred: %s", str(e))
    try:    
        cumulative_tally.to_csv('cumulative_averages.csv', mode='w', index=False, header=True)
    except Exception as e:
        logger.debug("Exception occurred: %s", str(e))
    
    return cumulative_tally
    


def calculate_behavior_metrics(data_object, actual_frames_per_second): #accept a path to a file or a path to a dataframe
    #not finished!
    if type(data_object) == str: #path to csv file
        df = pd.read_csv(data_object, header=True)
        
    elif type(data_object) == pd.DataFrame: #dataframe 
        df = data_object
        
    if "speed" in setup.behavior_metrics:
        try:
            df = behavioral_metrics.compute_speed(df,actual_frames_per_second,4)
            print('just computed speed')
        except Exception as e:
            logger.debug("Exception occurred: %s", str(e))
				
    if "distance from center" in setup.behavior_metrics:
        try:
            df = behavioral_metrics.compute_social_center_distance(df)
            print('just computed distance from center')
        except Exception as e:
            logger.debug("Exception occurred: %s", str(e))
    
    if "video averages" in setup.behavior_metrics:
        try:	
            video_averages = behavioral_metrics.compute_video_averages(df, todays_folder_path, filename)
            print('just computed video averages!')
        except Exception as e:
            logger.debug("Exception occurred: %s", str(e))
    
    if "cumulative averages" in setup.behavior_metrics:
        try:
            running_averages = behavioral_metrics.store_cumulative_averages(filename)
            print('just computed running averages!')
        except Exception as e:
            logger.debug("Exception occurred: %s", str(e))
		
            if running_averages.empty == True:
                pass
