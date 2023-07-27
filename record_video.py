#!/usr/bin/env python

from picamera2 import Picamera2, Preview
from picamera2.encoders import JpegEncoder
import time
from datetime import date
from datetime import datetime
import socket
import argparse
import os
import subprocess
from sys import getsizeof
import cv2
from libcamera import controls







def picam2_record_mp4(filename, outdir, recording_time, fps, shutter_speed, width, height, tuning_file, noise_reduction_mode, digital_zoom): #imformat="yuv" #have excluded imformat input because right now only functions by grabbing YUV frames, then converts them to RGB video. Maybe have a grayscale vs color option if possible?
	
	tuning = Picamera2.load_tuning_file(tuning_file)
	picam2 = Picamera2(tuning=tuning)
	preview = picam2.create_preview_configuration({"format": "YUV420", "size": (width, height)})
	picam2.align_configuration(preview) #might cause an issue?
	picam2.configure(preview)
	
	'''set shutterspeed (or exposure time)'''
	picam2.set_controls({"ExposureTime": shutter_speed}) #"NoiseReductionMode": controls.draft.NoiseReductionModeEnum.Fast})
	
	'''set noise reduction mode'''
	if noise_reduction_mode != "Auto":
		try:
			noise_reduction_mode = getattr(controls.draft.NoiseReductionModeEnum, noise_reduction_mode)
			picam2.set_controls({"NoiseReductionMode": noise_reduction_mode})
		except:
			print("The variable 'noise_reduction_mode' in the setup.py script is set incorrectly. Please change it and save that script. It should be 'Auto', 'Off', 'Fast', or 'HighQuality'")
	
	'''set digital zoom'''
	if digital_zoom == type(tuple) and len(digital_zoom) == 4:
		picam2.set_controls({"ScalerCrop": digital_zoom})
	
	elif digital_zoom != None:
		print("The variable 'recording_digital_zoom' in the setup.py script is set incorrectly. It should be either 'None' or a value that looks like this: (offset_x,offset_y,new_width,new_height) for ex. (1000,2000,300,300)")
	
	'''start the camera'''
	picam2.start()
	
	print("Initializing recording...")
	print("Recording parameters:\n")
	print(f"	filename: {filename}")
	print(f"	directory: {outdir}")
	print(f"	recording time: {recording_time}s")
	print(f"	frames per second: {fps}")
	print(f"	image width: {width}")
	print(f"	image width: {height}")
	print(f"	output image format: RGB888")

	time.sleep(2)
	start_time = time.time()
	
	#frames_dict = {}
	frames_list = []
	i = 0
	
	print("beginning video capture")
	while ( (time.time() - start_time) < recording_time):
		timestamp = time.time() - start_time
		
		yuv420 = picam2.capture_array()
		print(yuv420.shape)
		frames_list.append([yuv420])
		#yuv420 = yuv420[0:3040, :]
		#frames_dict[f"frame_{i:03d}"] = [yuv420, timestamp]
		time.sleep(1/(fps+1))
		i += 1
		
	finished = time.time()-start_time
	print(f'finished capturing frames to arrays, captured {i} frames in {finished} seconds')
	rate = i / finished
	print(f'thats {rate} frames per second!\nMake sure this corresponds well to your desired framerate. FPS is a bit experimental for tag tracking and mp4 recording at the moment... Thats the tradeoff for allowing a higher framerate.')
	
	output = outdir+filename+'.mp4'
	vid_fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	out = cv2.VideoWriter(output,vid_fourcc,10,(4032,3040))
	print("got here!")
	for i, im_array in enumerate(frames_list):
		frame = im_array[0]
		#gray_im = cv2.cvtColor(frame, cv2.COLOR_YUV2GRAY_I420)
		rgb_im = cv2.cvtColor(frame, cv2.COLOR_YUV420p2RGB)
		out.write(rgb_im)
		print("wrote another frame!")
		#out.write(gray_im)

	out.release()
	cv2.destroyAllWindows()







def picam2_record_mjpeg(filename, outdir, recording_time, quality, fps, shutter_speed, width, height, tuning_file, noise_reduction_mode, digital_zoom, imformat="RGB888", buffer_count=2):
	
	print("Initializing recording...")
	print("Recording parameters:\n")
	print(f"	filename: {filename}")
	print(f"	directory: {outdir}")
	print(f"	recording time: {recording_time}s")
	print(f"	quality (0-100): {quality}")
	print(f"	frames per second: {fps}")
	print(f"	image width: {width}")
	print(f"	image width: {height}")
	print(f"	image format: {imformat}")
	print(f"	buffer count: {buffer_count}")
		    
		    
	frame_duration_microseconds = int(1/fps * 10**6)
	
	tuning = Picamera2.load_tuning_file(tuning_file)
	picam2 = Picamera2(tuning=tuning)
	picam2.set_controls({"ExposureTime": shutter_speed})
	video_config = picam2.create_video_configuration(main={"size": (width, height), "format": imformat}, controls={"FrameDurationLimits": (frame_duration_microseconds, frame_duration_microseconds)}, buffer_count=2)
	picam2.align_configuration(video_config)
	picam2.configure(video_config)

	picam2.start_preview()
	encoder = JpegEncoder(q=quality)
	output = outdir+filename+'.mjpeg'

	picam2.start()
	time.sleep(2)
	picam2.start_encoder(encoder,output,pts=outdir+filename+"_pts.txt")

	time.sleep(recording_time)
	
	picam2.stop()
	picam2.stop_encoder()
	
	
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
	






	
def main():
	
	parser = argparse.ArgumentParser(prog='Record a video, either an mp4 or mjpeg video! Program defaults to mp4 currently.')
	parser.add_argument('-p', '--data_folder_path', type=str, default='/mnt/bumblebox/data/', help='a path to the folder you want to collect data in. Default path is: /mnt/bumblebox/data/')
	parser.add_argument('-t', '--recording_time', type=int, default=20, help='the video recording time in seconds')
	parser.add_argument('-q', '--quality', type=int, default=95, choices=range(0,100), help='jpg image quality setting from 0-100. The higher the number, the better quality, and the bigger the file.')
	parser.add_argument('-fps', '--frames_per_second', type=int, default=6, choices=range(0,10), help='the number of frames recorded per second of video capture. At the moment this is still a bit experimental, we have gotten up to 6fps to work for mjpeg, and up to 10fps for mp4 videos.')
	parser.add_argument('-sh', '--shutter', type=int, default=2500, help='the exposure time, or shutter speed, of the camera in microseconds (1,000,000 microseconds in a second!!)')
	parser.add_argument('-w', '--width', type=int, default=4056, help='the width of the image in pixels')
	parser.add_argument('-ht', '--height', type=int, default=3040, help='the height of the image in pixels')
	parser.add_argument('-cd', '--codec', type=str, default='mp4', choices=['mp4','mjpeg'], help='choose to save either mp4 videos or mjpeg videos!')
	parser.add_argument('-tf', '--tuning_file', type=str, default='imx477_noir.json', help='this is a file that helps improve image quality by running algorithms tailored to particular camera sensors.\nBecause the BumbleBox by default images in IR, we use the \'imx477_noir.json\' file by default')
	parser.add_argument('-nr', '--noise_reduction', type=str, default='Auto', choices=['Auto', 'Off', 'Fast', 'HighQuality'], help='an option to "digitally zoom in" by just recording from a portion of the sensor. This overrides height and width values, and can be useful to crop out glare that is negatively impacting image quality. Takes 4 values inside parentheses, separated by commas: 1: number of pixels to offset from the left side of the image 2: number of pixels to offset from the top of the image 3: width of the new cropped frame in pixels 4: height of the new cropped frame in pixels')
	parser.add_argument('-z', '--digital_zoom', type=tuple, default=None, help='an option to "digitally zoom in" by just recording from a portion of the sensor. This overrides height and width values, and can be useful to crop out glare that is negatively impacting image quality. Takes 4 values inside parentheses, separated by commas: 1: number of pixels to offset from the left side of the image 2: number of pixels to offset from the top of the image 3: width of the new cropped frame in pixels 4: height of the new cropped frame in pixels')
	args = parser.parse_args()
    
	ret, todays_folder_path = create_todays_folder(args.data_folder_path)
	
	if ret == 1:
	
		print("Couldn't create todays folder to store data in. Exiting program. Sad!")
		return 1
		
	hostname = socket.gethostname()
	
	now = datetime.now()
	now = now.strftime('_%Y-%m-%d_%H_%M_%S')
	
	filename = hostname + now
	
	print(filename)
	print(args.data_folder_path)
	print(todays_folder_path)
	print(args.recording_time)
	print(args.quality)
	print(args.frames_per_second)
	
	if args.codec == 'mp4':
		picam2_record_mp4(filename,todays_folder_path, args.recording_time, args.frames_per_second, args.shutter, args.width, args.height, args.tuning_file, args.noise_reduction, args.digital_zoom)
	if args.codec == 'mjpeg':
		picam2_record_mjpeg(filename,todays_folder_path, args.recording_time, args.quality, args.frames_per_second, args.width, args.height, args.tuning_file, args.noise_reduction, args.digital_zoom)
	
	
if __name__ == '__main__':
	
	main()
	
	
