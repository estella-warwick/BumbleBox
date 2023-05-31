#!/usr/bin/env python

from picamera2 import Picamera2, Preview
from picamera2.encoders import JpegEncoder
from picamera2.encoders import H264Encoder
from sys import getsizeof
import time
import numpy
import cv2
from PIL import Image
import os

def picam2_record_mjpeg(filename, outdir, recording_time=20, quality=95, size=(4056,3040), imformat="RGB888", fps=6, buffer_count=2):
	frame_duration_us = int(1/fps * 10**6)
	picam2 = Picamera2()
	video_config = picam2.create_video_configuration(main={"size": size, "format": imformat}, controls={"FrameDurationLimits": (frame_duration_us, frame_duration_us)}, buffer_count=2)
	picam2.align_configuration(video_config)
	picam2.configure(video_config)

	picam2.start_preview()
	encoder = JpegEncoder(q=quality)
	output = outdir+filename

	picam2.start()
	time.sleep(2)
	picam2.start_encoder(encoder,output,pts=outdir+filename+"_pts.txt")
	#picam2.start_recording(encoder,output,pts=outdir+filename+"_pts.txt")

	time.sleep(recording_time)
	
	picam2.stop()
	picam2.stop_encoder()
	
	


	
def folder_jpgs2mjpeg(dirpath):
	cmd = 'for i in ' + dirpath + '*.jpg: do ffmpeg -i "$i" "${i%.*}.mjpeg"; done'
	os.system(cmd)
	




def picam2_YUV420array2mjpeg(recording_time=5, quality="maximum", fps=6, outdir='/mnt/bombusbox/burstcapturejpgs/', filename='testpicam2_yuv2vid', imtype="yuv"): #make options "yuv", "rgb", "y", "all"
	
	picam2 = Picamera2()
	preview = picam2.create_preview_configuration({"format": "YUV420", "size": (4032,3040)})
	picam2.configure(preview)
	picam2.start()

	time.sleep(2)
	start_time = time.time()
	
	frames_dict = {}
	i = 0
	
	print("beginning video capture")
	while ( (time.time() - start_time) < recording_time) or (i <= fps*recording_time):
		timestamp = time.time() - start_time

		yuv420 = picam2.capture_array()
		
		if imtype == "y":
			yuv420 = yuv420[0:3040, :]
		frames_dict[f"frame_{i:03d}"] = [yuv420, timestamp]
		time.sleep(1/(fps+1))
		i += 1
	print(f'finished capturing frames to arrays, captured {i} frames in {time.time()-start_time}')
	sizeof = getsizeof(frames_dict)
	print(f"Size of dictionary storing the frames: {sizeof}")
	
	if imtype =="y":
		for frame_number in frames_dict:
			imlist = frames_dict[frame_number]
			array = imlist[0]
			y_im = Image.fromarray(array, mode="L") #L meaning a single 8-bit channel, greyscale
			y_im.save(outdir+frame_number+".jpg", quality=quality)
	
	elif imtype =="yuv":
		for frame_number in frames_dict:
			imlist = frames_dict[frame_number]
			array = imlist[0]
			yuv_im = Image.fromarray(array, mode="YCbCr") #YCbCr meaning 3x8-bit channels for YUV
			yuv_im.save(outdir+filename+".jpg", quality=quality)
	
	elif imtype =="rgb":
		for frame_number in frames_dict:
			imlist = frames_dict[frame_number]
			array = imlist[0]
			yuv_im = Image.fromarray(array, mode="YCbCr")
			rgb_im = cv2.cvtColor(yuv_im, cv2.COLOR_YUV420p2RGB)
			rgb_im.save(outdir+filename+".jpg", quality=quality)
	
	elif imtype == "all":
		for frame_number in frames_dict:
			imlist = frames_dict[frame_number]
			array = imlist[0]
			yuv_im = Image.fromarray(array, mode="YCbCr")
			y_im = Image.fromarray(array, mode="L")
			rgb_im = cv2.cvtColor(yuv_im, cv2.COLOR_YUV420p2RGB)
			y_im.save(outdir+filename+".jpg", quality=quality)
			yuv_im.save(outdir+filename+".jpg", quality=quality)
			rgb_im.save(outdir+filename+".jpg", quality=quality)
	
	else:
		print("Error: imtype must equal either 'y', 'yuv', 'rgb', or 'all'")
		return print("Exit code: 1")

	cmd = 'for i in ' + outdir + '*.jpg: do ffmpeg -i "$i" "${i%.*}.mjpeg"; done'
	os.system(cmd)


def write_jpgs2mp4(numframes, jpgdir='/mnt/bombusbox/burstcapturejpgs', cv2.VideoWriter_fourcc(*'mp4'), fps=10, size=(4032,3040):
	


def picam2_YUV420arraycapture_timetest(recording_time=10, fps=15, quality="maximum", outdir='/mnt/bombusbox/burstcapturejpgs/', filename='testpicam2_yuv2vid', container="dict",imtype="y"): #make options "yuv", "rgb", "y", "all"

	picam2 = Picamera2()
	preview = picam2.create_preview_configuration({"format": "YUV420", "size": (4032,3040)})
	picam2.configure(preview)
	picam2.start()

	time.sleep(2)
	start_time = time.time()
	
	frames_dict = {}
	i = 0
	
	print("beginning video capture")
	while ( (time.time() - start_time) < recording_time): #or (i <= fps*recording_time):
		timestamp = time.time() - start_time
		
		yuv420 = picam2.capture_array()
		
		if imtype=="y" and container=="dict": 
			yuv420 = yuv420[0:3040, :]
			frames_dict[f"frame_{i:03d}"] = [yuv420, timestamp]
			#time.sleep(1/(fps+10))
			i += 1
		
	print(f'finished capturing frames to arrays, captured {i} frames in {time.time()-start_time}')
	sizeof = getsizeof(frames_dict)
	print(f"Size of dictionary storing the frames: {sizeof}")
	
	for frame_number in frames_dict:
		print(frame_number, frames_dict[frame_number][1])
		
	if imtype =="y":
		timestamps = {}
		save_time = time.time()
		for frame_number in frames_dict:
			imlist = frames_dict[frame_number]
			frame_array = imlist[0]
			y_im = Image.fromarray(frame_array, mode="L") #L meaning a single 8-bit channel, greyscale
			y_im.save(outdir+frame_number+".jpg", quality=quality)
			timestamps[frame_number] = time.time() - save_time
		
		end_time = time.time()
		
		for frame_number in timestamps:
			print(f'{frame_number}: {timestamps[frame_number]} seconds')
			
		print(f'wrote {int(len(frames_dict))} images in {end_time - save_time} seconds.\nThats an average of {int(len(frames_dict)) / (end_time - save_time)} frames per second!')


### date is 5/30, trying to use just opencv to write to .mp4 or h265
def cv2_arraycapture():
	

		
if __name__ == '__main__':
	
    picam2_YUV420arraycapture_timetest()
		 
