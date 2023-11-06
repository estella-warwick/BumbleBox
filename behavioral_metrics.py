#!/usr/bin/env python

import pandas as pd
import numpy as np
import logging
import setup
from datetime import datetime as dt

#logfile_folder = setup.bumblebox_dir
#logging.basicConfig(filename='behavioral_metrics.log',encoding='utf-8',format='%(filename)s %(asctime)s: %(message)s', filemode='a', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.debug("importing behavioral metrics")

def compute_speed(df: pd.DataFrame, fps: int, speed_cutoff_seconds: int, todays_folder_path: str, filename: str) -> pd.DataFrame:
    
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
    df_sorted.to_csv(todays_folder_path + "/" + filename + '_updated.csv', index=False)
    return df_sorted
    
    

def compute_social_center_distance(df: pd.DataFrame, todays_folder_path: str, filename: str) -> pd.DataFrame:
    # Compute the social center for each frame
    social_centers = df.groupby('frame')[['centroidX', 'centroidY']].mean()
    social_centers.columns = ['centerX', 'centerY']
   
    # Merge the social centers with the main dataframe to calculate distances
    df = df.merge(social_centers, left_on='frame', right_index=True)

    # Compute the distance of each bee from the social center of its frame
    df['distance_from_center'] = np.sqrt((df['centroidX'] - df['centerX'])**2 + (df['centroidY'] - df['centerY'])**2)
   
    # Drop temporary columns used for computations
    df.drop(columns=['centerX', 'centerY'], inplace=True)
    df_sorted = df.sort_values(by=['frame','ID'])
    df_sorted.to_csv(todays_folder_path + "/" + filename + '_updated.csv', index=False)
    return df_sorted
    
    
# function to calculate the average distance of each bee to every other tagged bee by frame of video
def video_avg_min_max_distances(pairwise_distance_df):

    avg_pd_df = 'None'

    pairwise_v1 = pairwise_distance_df.drop(columns={'bee ID','frame number'}) #drop non-data columns from new dataframe in order to calculate the min, max of the data without interference
    pairwise_distance_df['avg_distance'] = pairwise_v1.mean(axis=1, numeric_only=True, skipna=True)
    pairwise_distance_df['min_distance'] = pairwise_v1.min(axis=1, numeric_only=True, skipna=True) #makes sure to get the min from each row, excluding nans 
    pairwise_distance_df['max_distance'] = pairwise_v1.max(axis=1, numeric_only=True, skipna=True)

    return pairwise_distance_df


def pairwise_distance(df: pd.DataFrame, todays_folder_path: str, filename: str) -> pd.DataFrame:

    video_pd_df = 'None'
    for frame_num, frame_df in df.groupby(['frame']): #now for the subdataframe of each frame of a video of a colony, reset the index so its not a multiindex

        xy_array = frame_df[['centroidX','centroidY']].to_numpy() #make these two columns into an array of [x,y] for numpy to use
        dist_matrix = spatial.distance.pdist(xy_array)
        squareform = spatial.distance.squareform(dist_matrix) #turns the pairwise distance vector into a 2d array (which has double values but allows us to do row based operations)
        squareform[ squareform == 0 ] = np.nan
        pairwise_distance_df = pd.DataFrame(squareform, columns=frame_df['ID']) #make the squareform array into a dataframe, with the bee IDs as the columns
        bee_id_column = frame_df.loc[:,'ID'].reset_index(drop=True) #make a new bee ID column to add to the dataframe
        pairwise_distance_df.insert(0, 'ID', bee_id_column)
        pairwise_distance_df.columns.name = None #this stops bee ID showing up as the name of all the columns in the df, it looks weird and is confusing
        pairwise_distance_df['frame'] = int(frame_num[0])
        #pairwise_distance_df = pd.concat((frame_df['bee ID'], pd.DataFrame(squareform, columns=frame_df['bee ID'])), axis=1) #turns the squareform array into a dataframe indexed by bee ID
        #pairwise_distance_df.replace(0, np.nan, inplace=True) #replace zeros with nan values in order to exclude them from calculations 

        try:
            pairwise_distance_df['ID'] = pairwise_distance_df['ID'].astype('int')
        except ValueError:
            print('ValueError: are there any Nans in the bee IDs? Why would there be though...')
            print(frame_num, frame_df)
            return pairwise_distance_df['ID']

        if 'None' in video_pd_df:
            #print('avg_pd_df is equal to None!')
            video_pd_df = pairwise_distance_df

        else:
            
            pairwise_distance_df = pairwise_distance_df.loc[~pairwise_distance_df.index.duplicated(),:] #need these two lines to add to video level dataframe for some reason
            pairwise_distance_df = pairwise_distance_df.loc[:,~pairwise_distance_df.columns.duplicated()]
            video_pd_df = pd.concat([video_pd_df,pairwise_distance_df], axis=0, sort=True) #ignore_index=True)
    
    #calculate frame averages, mins, and maxes
    pairwise_distance_df = frame_avg_min_max_distances_to_other_bees(pairwise_distance_df)
    
    #extract frame_number column to bring it to the front of the df
    frame_column = video_pd_df['frame']
    bee_id_column = video_pd_df['ID']
    #drop the columns
    video_pd_df.drop(labels=['frame', 'ID'], axis=1, inplace=True)

    #then reinsert frame number at the beginning and averages at the end of the dataframe
    video_pd_df.insert(0, 'ID', bee_id_column)
    video_pd_df.insert(0, 'frame', frame_column)
    video_pd_df.reset_index(drop=True, inplace=True)
    video_pd_df.to_csv(todays_folder_path + '/' + filename + '_pairwise_distance.csv')

    return video_pd_df


#this function is called within the pairwise distance function and adds the average distance (and min and max) of each bee to every other bee in each frame
def frame_avg_min_max_distances_to_other_bees(pairwise_distance_df):

    pairwise_v1 = pairwise_distance_df.drop(columns={'bee ID','frame number'}) #drop non-data columns from new dataframe in order to calculate the min, max of the data without interference
    pairwise_distance_df['avg_distance'] = pairwise_v1.mean(axis=1, numeric_only=True, skipna=True)
    pairwise_distance_df['min_distance'] = pairwise_v1.min(axis=1, numeric_only=True, skipna=True) #makes sure to get the min from each row, excluding nans 
    pairwise_distance_df['max_distance'] = pairwise_v1.max(axis=1, numeric_only=True, skipna=True)

    return pairwise_distance_df


def contact_matrix(df, pixel_contact_distance):
    
    df_copy = df.copy() # make a copy to store the bee ID and frame number columns, which will be changed to a 1 or 0 in the original dataframe
    df[ df <= pixel_contact_distance ] = 1
    df[ df > pixel_contact_distance ] = 0
    df['bee ID'] = df_copy['bee ID'] # add the correct column back in by overwriting 'bee ID'
    df['frame number'] = df_copy['frame number'] # add the correct column back in by overwriting 'frame number'
    
    df.to_csv(todays_folder_path + '/' + filename + '_contacts.csv')
    
    return df


def summary_contact_df(contact_df):

    contact_df.drop(columns={'frame number'}, inplace=True)
    video_summary_contact_df = contact_df.groupby('bee ID').sum()
    video_summary_contact_df.to_csv(todays_folder_path + '/' + filename + 'summary_contacts.csv')
    return video_summary_contact_df
    












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
                                  'average contact rate': 
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
    
    




def compile_dfs(directory_path, start_filename = None, end_filename = None, format = None, end_of_filename = 'averages.csv'):
    #not done yet!
    if format == None:
        format = '%Y-%m-%d_%H-%M-%S'
    
    if start_filename != None:
        hostname, date, time, ext = start_filename.split("_")
        start_datetime = date + "_" + time
        start_datetime = dt.strptime(start_datetime, format)
        
    if end_filename != None:
        hostname2, date2, time2, ext2 = end_filename.split("_")
        end_datetime = date2 + "_" + time2
        end_datetime = dt.strptime(end_datetime, format)
    
    df_list = []
    
    if start_filename != None and end_filename != None:
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
    


def calculate_behavior_metrics(data_object, actual_frames_per_second, todays_folder_path, filename): #accept a path to a file or a path to a dataframe
    #not finished!
    if type(data_object) == str: #path to csv file
        df = pd.read_csv(data_object, header=True)
        
    elif type(data_object) == pd.DataFrame: #dataframe 
        df = data_object
        
    if "speed" in setup.behavior_metrics:
        try:
            df = behavioral_metrics.compute_speed(df,actual_frames_per_second,4, todays_folder_path, filename)
            print('just computed speed')
        except Exception as e:
            logger.debug("Exception occurred: %s", str(e))
				
    if "distance from center" in setup.behavior_metrics:
        try:
            df = behavioral_metrics.compute_social_center_distance(df, todays_folder_path, filename)
            print('just computed distance from center')
        except Exception as e:
            logger.debug("Exception occurred: %s", str(e))
            
    if "pairwise distance" in setup.behavior_metrics:
        try:
            df = behavioral_metrics.pairwise_distance(df, todays_folder_path, filename)
            
    if "contacts" in setup.behavior_metrics:
        try:
            contact_df = contact_matrix(df, setup.pixel_contact_distance)
    
    
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
