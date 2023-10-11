#!/usr/bin/env python

def compute_speed(df: pd.DataFrame, fps: int, speed_cutoff_seconds, int) -> pd.DataFrame:
    
    speed_cutoff_frames = fps*speed_cutoff_seconds
    # Sorting by ID and frame ensures that we compare positions of the same bee across consecutive frames
    df_sorted = df.sort_values(by=['ID', 'frame'])
   
    # Compute the difference between consecutive rows for centroidX and centroidY
    df_sorted['deltaX'] = df_sorted.groupby('ID')['centroidX'].diff()
    df_sorted['deltaY'] = df_sorted.groupby('ID')['centroidY'].diff()
    
    df_sorted['elapsed frames'] = df_sorted.groupby('ID')['frames'].diff()
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
    


def compute_average_distance_and_speed_per_video(df: pd.DataFrame) -> pd.DataFrame:
    # Setup logging
    logging.basicConfig(filename='behavior_quantification.log', level=logging.INFO, format='%(asctime)s - %(message)s')
    df_sorted = df.sort_values(by=['ID','frame'])
    average_distances = df_sorted.groupby('ID')['distance_from_center'].mean()
    average_speed = df_sorted.groupby('ID')['speed'].mean()
    speed_count = df_sorted.groupby('ID')['speed'].count()
    frame_count = df_sorted.groupby('ID')['ID'].count()
    #datetime = df_sorted['datetime']
    running_tally = pd.DataFrame({#'datetime': np.empty((len(average_distances),)),
                                  'average distance from center': average_distances,
                                  'average speed': average_speed,
                                  'frames tracked in video':frame_count})
    running_tally.reset_index(inplace=True)
    #running_tally.merge(datetime, how='left')
    print(running_tally)
    running_tally.to_csv('behavior_quantification.csv', mode='a', index=False, header=False)
    return running_tally
    

def store_cumulative_averages():
    df = pd.read_csv('behavior_quantification.csv', index_col=None, header=0)
    df_sorted = df.sort_values(by=['ID'])
    average_distances = df_sorted.groupby('ID')['average distance from center'].mean()
    average_speed = df_sorted.groupby('ID')['average speed'].mean()
    frame_count = df_sorted.groupby('ID')['frames tracked in video'].sum()
    running_tally = pd.DataFrame({#'datetime': np.empty((len(average_distances),)),
                                  'ID': df_sorted['ID'].unique(),
                                  'average distance from center': average_distances,
                                  'average speed': average_speed,
                                  'total tracked frames':frame_count})
    running_tally.reset_index(inplace=True, drop=True)
    running_tally.to_csv('cumulative_averages.csv', mode='a', index=False, header=False)
