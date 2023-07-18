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


def picam2_record_mjpeg(filename, outdir, recording_time, quality, fps, size=(4056,3040), imformat="RGB888", buffer_count=2):
	
	print("Initializing recording...")
	print("Recording parameters:\n")
	print(f"	filename: {filename}")
	print(f"	directory: {outdir}")
	print(f"	recording time: {recording_time}s")
	print(f"	quality (0-100): {quality}")
	print(f"	frames per second: {fps}")
	print(f"	image width and height: {size}")
	print(f"	image format: {imformat}")
	print(f"	buffer count: {buffer_count}")
		    
		    
	frame_duration_microseconds = int(1/fps * 10**6)
	picam2 = Picamera2()
	video_config = picam2.create_video_configuration(main={"size": size, "format": imformat}, controls={"FrameDurationLimits": (frame_duration_microseconds, frame_duration_microseconds)}, buffer_count=2)
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
	
	parser = argparse.ArgumentParser(prog='Record an mjpeg video!')
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
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
