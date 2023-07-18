#!/usr/bin/env python

import cv2
from cv2 import aruco
import pandas



# current progress as of 07/18/23
# am going to use argparse to get the necessary values for the data capture in the main function (which should be coming from the crontab script - run command)
# then am going to feed those into the array_capture function (not done yet)
# then am going to track the tags from the frames_list object using the trackTagsfromRAM function
# a nice thing would be to make the tracking parameters associated with the custom box and the koppert box toggle-able 

def array_capture(recording_time=20, quality="maximum", fps=6, outdir='/mnt/bombusbox/', filename='testpicam2_yuv2vid', imtype="yuv"):
	
	picam2 = Picamera2()
	preview = picam2.create_preview_configuration({"format": "YUV420", "size": (4032,3040)})
	picam2.configure(preview)
	picam2.start()

	time.sleep(2)
	start_time = time.time()
	
	frames_list = []
	i = 0
	
	print("beginning video capture")
	while ( (time.time() - start_time) < recording_time): #or (i <= fps*recording_time):
		
		timestamp = time.time() - start_time
		yuv420 = picam2.capture_array()
		#print(yuv420.shape)
		frames_list.append([yuv420])
		#yuv420 = yuv420[0:3040, :]
		#frames_dict[f"frame_{i:03d}"] = [yuv420, timestamp]
		time.sleep(1/(fps+1))
		i += 1
		
	print(f'finished capturing frames to arrays, captured {i} frames in {time.time()-start_time}')
	#sizeof = getsizeof(frames_dict)
	sizeof = getsizeof(frames_list)
	print(f"Size of list storing the frames: {sizeof} bytes")
	
	return frames_list
		
		
		
def trackTagsFromRAM(frames_list):
	
	#edit dict to be passed from outer function?
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
		
		try:
		   gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		   clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
		   cl1 = clahe.apply(gray)
		   gray = cv2.cvtColor(cl1,cv2.COLOR_GRAY2RGB)
			
		except:
			continue
			
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
	df.to_csv(identified_csv, index=False)
	df2 = pandas.DataFrame(noID)
	df2 = pandas.DataFrame(noID)
	df2 = df2.rename(columns = {0:'frame', 1:'ID', 2:'centroidX', 3:'centroidY', 4:'frontX', 5:'frontY', 6:'1cm', 7:'check'})
	df2.to_csv(potential_csv, index=False)

	print("Average number of tags found: " + str(len(df.index)/frame_num))
	
	return df, df2, frame_num
	
	
	
def main():
	
	parser = argparse.ArgumentParser(prog='Record frames to RAM and find tags in them without saving a video. Outputs a csv (comma separated values) text file with the tag coordinates.')
	parser.add_argument('-p', '--data_folder_path', type=str, default='/mnt/bumblebox/data/', help='a path to the folder you want to collect data in. Default path is: /mnt/bumblebox/data/')
	parser.add_argument('-t', '--recording_time', type=int, default=20, help='the video recording time in seconds')
	parser.add_argument('-q', '--quality', type=int, default=95, choices=range(0,100), help='jpg image quality setting from 0-100. The higher the number, the better quality, and the bigger the file.')
	parser.add_argument('-fps', '--frames_per_second', type=int, default=6, help='the number of frames recorded per second of video capture. At the moment this is still a bit experimental, we have gotten up to 6fps to work.')
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
	print(args.quality)
	print(args.frames_per_second)
	
	picam2_record_mjpeg(filename,todays_folder_path, args.recording_time, args.quality, args.frames_per_second)
	
	
if __name__ == '__main__':
	
	main()
