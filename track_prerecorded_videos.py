import os
import cv2
from cv2 import aruco
import pandas as pd
import behavioral_metrics
import time
import numpy as np

video_folder = '' #write the path of the video folder here inside the quotes
frames_per_second = None

#for file in x
#add my csv tracking alternative in for now, along with in the ram_capture script - this so I can add functions quickly 

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

def trackTagsFromVid(filepath, todays_folder_path, filename, tag_dictionary, box_type):
	
	print(tag_dictionary)
	if tag_dictionary is None:
		tag_dictionary = '4X4_50'
		if isinstance(tag_dictionary, str):
			if 'DICT' not in tag_dictionary:
				tag_dictionary = "DICT_%s" % tag_dictionary
			tag_dictionary = tag_dictionary.upper()
			if not hasattr(cv2.aruco, tag_dictionary):
				raise ValueError("Unknown tag dictionary: %s" % tag_dictionary)
			tag_dictionary = getattr(cv2.aruco, tag_dictionary)
	else:
		if 'DICT' not in tag_dictionary:
			tag_dictionary = "DICT_%s" % tag_dictionary
		tag_dictionary = tag_dictionary.upper()
		if not hasattr(cv2.aruco, tag_dictionary):
			raise ValueError("Unknown tag dictionary: %s" % tag_dictionary)
		tag_dictionary = getattr(cv2.aruco, tag_dictionary)
	tag_dictionary = aruco.getPredefinedDictionary(tag_dictionary) 
	parameters = aruco.DetectorParameters()
	detector = aruco.ArucoDetector(tag_dictionary, parameters)
	
	if box_type=='custom':
		#change these!
		parameters.minMarkerPerimeterRate=0.03
		parameters.adaptiveThreshWinSizeMin=5
		parameters.adaptiveThreshWinSizeStep=6
		parameters.polygonalApproxAccuracyRate=0.06
		
	elif box_type=='koppert':
		#change these!
		parameters.minMarkerPerimeterRate=0.03
		parameters.adaptiveThreshWinSizeMin=5
		parameters.adaptiveThreshWinSizeStep=6
		parameters.polygonalApproxAccuracyRate=0.06
		
	elif box_type==None:
		#change these!
		parameters.minMarkerPerimeterRate=0.03
		parameters.adaptiveThreshWinSizeMin=5
		parameters.adaptiveThreshWinSizeStep=6
		parameters.polygonalApproxAccuracyRate=0.06


	vid = cv2.VideoCapture(filepath)
	
	frame_num = 0
	noID = []
	raw = []
	augs_csv = []
	
	start = time.time()
	
	while(vid.Isopened()):
		
		ret,frame = vid.read()
		if ret == True:
			try:
				gray = cv2.cvtColor(frame, cv2.COLOR_YUV2GRAY_I420)
				clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
				cl1 = clahe.apply(gray)
				gray = cv2.cvtColor(cl1,cv2.COLOR_GRAY2RGB)
				
			except:
				print('converting to grayscale didnt work...')
				continue
				
			corners, ids, rejectedImgPoints = detector.detectMarkers(gray)

			for i in range(len(rejectedImgPoints)):
				c = rejectedImgPoints[i][0]
				xmean = c[:,0].mean() #for calculating the centroid
				ymean = c[:,1].mean() #for calculating the centroid
				xmean_top_point = (c[0,0] + c[1,0]) / 2 #for calculating the top point of the tag
				ymean_top_point = (c[0,1] + c[1,1]) / 2 #for calculating the top point of the tag
				noID.append( [frame_num, "X", float(xmean), float(ymean), float(xmean_top_point), float(ymean_top_point)] )
				#noID.append( [frame_num, "X", float(xmean), float(ymean), float(xmean_top_point), float(ymean_top_point), 100, None] ) #[[float(xmean), float(ymean)], [float(xmean_top_point), float(ymean_top_point)]] )
			
			if ids is not None:
				for i in range(len(ids)):
					c = corners[i][0]
					xmean = c[:,0].mean() #for calculating the centroid
					ymean = c[:,1].mean() #for calculating the centroid
					xmean_top_point = (c[0,0] + c[1,0]) / 2 #for calculating the top point of the tag
					ymean_top_point = (c[0,1] + c[1,1]) / 2 #for calculating the top point of the tag
					raw.append( [frame_num, int(ids[i]), float(xmean), float(ymean), float(xmean_top_point), float(ymean_top_point)] )
					#raw.append( [frame_num, int(ids[i]),float(xmean), float(ymean), float(xmean_top_point), float(ymean_top_point), 100, None] ) #[[float(xmean), float(ymean)], [float(xmean_top_point), float(ymean_top_point)]] )

			frame_num += 1
			print(f"processed frame {frame_num}")  
		
		df = pd.DataFrame(raw)
		df = df.rename(columns = {0:'frame', 1:'ID', 2:'centroidX', 3:'centroidY', 4:'frontX', 5:'frontY'})
		df.to_csv(todays_folder_path + filename + '_raw.csv')
		print('saved raw csv')
		#df.to_csv('/home/pi/Desktop/BumbleBox/testing/identified_csv.csv', index=False)
		df2 = pd.DataFrame(noID)
		df2 = df2.rename(columns = {0:'frame', 1:'ID', 2:'centroidX', 3:'centroidY', 4:'frontX', 5:'frontY'})
		df2.to_csv(todays_folder_path + filename + '_noID.csv')
		print('saved noID csv')
		#df2.to_csv('/home/pi/Desktop/BumbleBox/testing/potential_csv.csv', index=False)

		print("Average number of tags found: " + str(len(df.index)/frame_num))
		tracking_time = time.time() - start
		print(f"Tag tracking took {tracking_time} seconds, an average of {tracking_time / frame_num} seconds per frame") 
		return df, df2, frame_num
		
		

def main(video_folder, dictionary):
	
	for path, directories, files in os.walk(video_folder):
		
		for file in files:
			
			filename = os.path.basename(file)
			name, datetime = filename.split('_', maxsplit=1)
			
			print('starting to track tags from the saved video!')
			df, df2, frame_num = trackTagsFromVid(path, video_folder, filename, dictionary, "custom")
			
			if df.empty == False:
				df = behavioral_metrics.compute_speed(df,frames_per_second,4)
				df = compute_social_center_distance(df)
				df.to_csv(video_folder + '/' + filename + '_updated.csv', index=False)
				
				
