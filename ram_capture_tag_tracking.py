#!/usr/bin/env python

from picamera2 import Picamera2, Preview
import cv2
from cv2 import aruco
import pandas
import argparse
from record_mjpeg import create_todays_folder
import socket
import time
from datetime import date
from datetime import datetime
from sys import getsizeof


# current progress as of 07/18/23
# am going to use argparse to get the necessary values for the data capture in the main function (which should be coming from the crontab script - run command)
# then am going to feed those into the array_capture function (not done yet)
# then am going to track the tags from the frames_list object using the trackTagsfromRAM function
# a nice thing would be to make the tracking parameters associated with the custom box and the koppert box toggle-able 

def array_capture(recording_time, fps, width, height):
	
	picam2 = Picamera2()
	preview = picam2.create_preview_configuration({"format": "YUV420", "size": (width,height)})
	picam2.configure(preview)
	picam2.start()
	time.sleep(2)
	
	print("Initializing data capture...")
	print("Recording parameters:\n")
	#print(f"	filename: {filename}")
	#print(f"	directory: {outdir}")
	print(f"	recording time: {recording_time}s")
	print(f"	frames per second: {fps}")
	print(f"	image width: {width}")
	print(f"	image width: {height}")
	
	start_time = time.time()
	
	frames_list = []
	i = 0
	
	while ( (time.time() - start_time) < recording_time): #or (i <= fps*recording_time):
		
		timestamp = time.time() - start_time
		print(f'frame {i} timestamp: {timestamp} seconds')
		yuv420 = picam2.capture_array()
		#print(yuv420.shape)
		frames_list.append([yuv420])
		#yuv420 = yuv420[0:3040, :]
		#frames_dict[f"frame_{i:03d}"] = [yuv420, timestamp]
		time.sleep(1/(fps+1))
		i += 1
	
	finished = time.time()-start_time
	print(f'finished capturing frames to arrays, captured {i} frames in {finished}')
	rate = i / finished
	print(f'thats {rate} frames per second!')
	#sizeof = getsizeof(frames_dict)
	sizeof = getsizeof(frames_list)
	print(f"Size of list storing the frames: {sizeof} bytes")
	
	return frames_list
		
		
		
def trackTagsFromRAM(filename, todays_folder_path, frames_list, dictionary):
	
	#edit dict to be passed from outer function?
	print(dictionary)
	print(type(dictionary))
	aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50) 
	parameters = aruco.DetectorParameters_create()
	
	#edit these to be passed into it from outer function?
	parameters.minMarkerPerimeterRate=0.03
	parameters.adaptiveThreshWinSizeMin=5
	parameters.adaptiveThreshWinSizeStep=6
	parameters.polygonalApproxAccuracyRate=0.06

	frame_num = 0
	noID = []
	raw = []

	for i in frames_list:
		frame = i[0]
		
		#try:
		gray = cv2.cvtColor(frame, cv2.COLOR_YUV2GRAY_I420)
		print('1 done')
		clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
		print('2 done')
		cl1 = clahe.apply(gray)
		print('3 done')
		gray = cv2.cvtColor(cl1,cv2.COLOR_GRAY2RGB)
		print('4 done')
			
		#except:
		#	print('converting to grayscale didnt work...')
		#	continue
			
		corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters = parameters)

		for i in range(len(rejectedImgPoints)):
			c = rejectedImgPoints[i][0]
			xmean = c[:,0].mean() #for calculating the centroid
			ymean = c[:,1].mean() #for calculating the centroid
			xmean_top_point = (c[0,0] + c[1,0]) / 2 #for calculating the top point of the tag
			ymean_top_point = (c[0,1] + c[1,1]) / 2 #for calculating the top point of the tag
			noID.append( [frame_num, "X", float(xmean), float(ymean), float(xmean_top_point), float(ymean_top_point), 100, None] ) #[[float(xmean), float(ymean)], [float(xmean_top_point), float(ymean_top_point)]] )
		
		if ids is not None:
			for i in range(len(ids)):
				c = corners[i][0]
				xmean = c[:,0].mean() #for calculating the centroid
				ymean = c[:,1].mean() #for calculating the centroid
				xmean_top_point = (c[0,0] + c[1,0]) / 2 #for calculating the top point of the tag
				ymean_top_point = (c[0,1] + c[1,1]) / 2 #for calculating the top point of the tag
				raw.append( [frame_num, int(ids[i]),float(xmean), float(ymean), float(xmean_top_point), float(ymean_top_point), 100, None] ) #[[float(xmean), float(ymean)], [float(xmean_top_point), float(ymean_top_point)]] )

		frame_num += 1
	
	df = pandas.DataFrame(raw)
	df = pandas.DataFrame(raw)
	df = df.rename(columns = {0:'frame', 1:'ID', 2:'centroidX', 3:'centroidY', 4:'frontX', 5:'frontY', 6:'1cm', 7:'check'})
	df.to_csv('identified_csv.csv', index=False)
	df2 = pandas.DataFrame(noID)
	df2 = pandas.DataFrame(noID)
	df2 = df2.rename(columns = {0:'frame', 1:'ID', 2:'centroidX', 3:'centroidY', 4:'frontX', 5:'frontY', 6:'1cm', 7:'check'})
	df2.to_csv('potential_csv.csv', index=False)

	print("Average number of tags found: " + str(len(df.index)/frame_num))
	
	return df, df2, frame_num
	
	
	'''
	def create_todays_folder(dirpath):
	
	today = date.today()
	today = today.strftime('%Y-%m-%d')
	todays_folder_path = dirpath + today + '/'
	print(todays_folder_path)
	
	if not os.path.exists(todays_folder_path):
		
		try:
			os.makedirs(todays_folder_path)
			return 0, todays_folder_path
		
		except Exception as e:
			print(e)
			print(e.args)
			print("Couldn't make today's folder for some reason... trying subprocess!")
			try:
				subprocess.call(['sudo', 'mkdir', '-p', todays_folder_path])
				return 0, todays_folder_path
			except:
				print(e)
				print(e.args)
				print("That didn't work either! Huh...")
				return 1, todays_folder_path
	
	else:
		return 0, todays_folder_path
	'''
	
	
def main():
	
	parser = argparse.ArgumentParser(prog='Record a video, either an mp4 or mjpeg video! Program defaults to mp4 currently.')
	parser.add_argument('-p', '--data_folder_path', type=str, default='/mnt/bumblebox/data/', help='a path to the folder you want to collect data in. Default path is: /mnt/bumblebox/data/')
	parser.add_argument('-t', '--recording_time', type=int, default=2, help='the video recording time in seconds')
	parser.add_argument('-fps', '--frames_per_second', type=int, default=6, choices=range(0,10), help='the number of frames recorded per second of video capture. At the moment this is still a bit experimental, we have gotten up to 6fps to work for mjpeg, and up to 10fps for mp4 videos.')
	parser.add_argument('-w', '--width', type=int, default=4056, help='the width of the image in pixels')
	parser.add_argument('-ht', '--height', type=int, default=3040, help='the height of the image in pixels')
	parser.add_argument('-d', '--dictionary', default=aruco.DICT_4X4_50, help='type "aruco.DICT_" followed by the size of the tag youre using (either 4X4 (default), 5X5, 6X6, or 7X7) and the number of tags in the dictionary (either 50 (default), 100, 250, or 1000).')
	args = parser.parse_args()
    
	ret, todays_folder_path = create_todays_folder(args.data_folder_path)
	
	if ret == 1:
	
		print("Couldn't create todays folder to store data in. Exiting program. Sad!")
		return 1
		
	hostname = socket.gethostname()
	
	now = datetime.now()
	now = now.strftime('_%Y-%m-%d_%H_%M_%S')
	
	filename = hostname + now # + '.mjpeg'
	
	print(filename)
	print(args.data_folder_path)
	print(todays_folder_path)
	print(args.recording_time)
	print(args.frames_per_second)
	
	frames_list = array_capture(args.recording_time, args.frames_per_second, args.width, args.height)
	print(type(frames_list))
	print(len(frames_list))
	trackTagsFromRAM(filename,todays_folder_path, frames_list, args.dictionary) #args.recording_time, args.quality, args.frames_per_second, args.dictionary)
	
	
if __name__ == '__main__':
	
	main()
