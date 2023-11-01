import numpy as np
import cv2
import skvideo.io
import os
#import zarr
import dask.array as da
import glob
import random
import datetime
from record_video import create_todays_folder
import setup
import socket
import argparse
import sys
import logging
import time

logging.basicConfig(filename=f'{setup.bumblebox_dir}/logs/generate_nest_images.log',encoding='utf-8',format='%(filename)s %(asctime)s: %(message)s', filemode='a', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#alternative code for compiling pngs
def generate_nest_image(todays_folder_path, today, number_of_images, hostname, shuffle=True):
    
    print(todays_folder_path)
    files = []
    for file in glob.glob(f"{todays_folder_path}/*.png"):
        print(file)
        files.append(file)
    if shuffle==True:
        random.shuffle(files)
        
    total_frames = len(files)
    print(total_frames)
    
    if total_frames > number_of_images:
        total_frames = number_of_images
        files = files[:total_frames]
    
    thirds = int(total_frames / 3)
    print(thirds)
    first_set = files[0:thirds]
    print(len(first_set))
    second_set = files[thirds:(thirds*2)]
    print(len(second_set))
    third_set = files[(thirds*2):(thirds*3 -1)]
    print(len(third_set))
    
    file_dimensions = []
    index = 0
    print("Trying to read image file!")
    imgdata = cv2.imread(files[0])
    print(type(imgdata))
    try:
        h,w,d = imgdata.shape
        x = da.zeros((len(first_set),h,w,d))
    except:
        h,w = imgdata.shape
        x = da.zeros((len(first_set),h,w))
    
    for file in first_set:
    #for file in files[:total_frames]:
        #filename = os.path.basename(filename)
        #fname, ext = os.path.splitext(filename)
        print(file)
        imgdata = cv2.imread(file)
        #videodata = skvideo.io.vread(file)
        #f,h,w,d = videodata.shape
        try:
            h,w,d = imgdata.shape
            dims = (h,w,d)
            print(h,w,d)
            file_dimensions.append(dims)
            print(file_dimensions[0])
            if dims != file_dimensions[0]:
                print('resizing')
                imgdata = cv2.resize(imgdata, (file_dimensions[0][1], file_dimensions[0][0]))
            print(imgdata.shape)
            x[index] = imgdata
            index += 1
        except:
            print('had a dimension issue')
            h,w = imgdata.shape
            file_dimensions.append((h,w))
            if h != file_dimensions[0][0] and w != file_dimensions[0][1]:
                imgdata = cv2.resize(imgdata, (file_dimensions[0][1], file_dimensions[0][0]))
            print(imgdata.shape)
            x[index] = imgdata
            index += 1
            
    print("Computing first set")
    a = da.median(x, axis=0)
    a1 = a.compute()
    
    del x
    del a
    
    index = 0
    
    try:
        h,w,d = imgdata.shape
        x = da.zeros((len(second_set),h,w,d))
    except:
        h,w = imgdata.shape
        x = da.zeros((len(second_set),h,w))
    
    for file in second_set:
    #for file in files[:total_frames]:
        #filename = os.path.basename(filename)
        #fname, ext = os.path.splitext(filename)
        print(file)
        imgdata = cv2.imread(file)
        #videodata = skvideo.io.vread(file)
        #f,h,w,d = videodata.shape
        try:
            h,w,d = imgdata.shape
            dims = (h,w,d)
            print(h,w,d)
            file_dimensions.append(dims)
            print(file_dimensions[0])
            if dims != file_dimensions[0]:
                print('resizing')
                imgdata = cv2.resize(imgdata, (file_dimensions[0][1], file_dimensions[0][0]))
            print(imgdata.shape)
            x[index] = imgdata
            index += 1
        except:
            print('had a dimension issue')
            h,w = imgdata.shape
            file_dimensions.append((h,w))
            if h != file_dimensions[0][0] and w != file_dimensions[0][1]:
                imgdata = cv2.resize(imgdata, (file_dimensions[0][1], file_dimensions[0][0]))
            print(imgdata.shape)
            x[index] = imgdata
            index += 1
    print("Computing second set")
    b = da.median(x, axis=0)
    b1 = x.compute()
    
    alpha = 0.5
    beta = 1.0 - alpha
    avg_image = cv2.addWeighted(b1, alpha, a1, beta, 0.0)
    
    del x
    del a1
    del b1
    
    index = 0
    
    try:
        h,w,d = imgdata.shape
        x = da.zeros((len(third_set),h,w,d))
    except:
        h,w = imgdata.shape
        x = da.zeros((len(third_set),h,w))
    
    for file in third_set:
    #for file in files[:total_frames]:
        #filename = os.path.basename(filename)
        #fname, ext = os.path.splitext(filename)
        print(file)
        imgdata = cv2.imread(file)
        #videodata = skvideo.io.vread(file)
        #f,h,w,d = videodata.shape
        try:
            h,w,d = imgdata.shape
            dims = (h,w,d)
            print(h,w,d)
            file_dimensions.append(dims)
            print(file_dimensions[0])
            if dims != file_dimensions[0]:
                print('resizing')
                imgdata = cv2.resize(imgdata, (file_dimensions[0][1], file_dimensions[0][0]))
            print(imgdata.shape)
            x[index] = imgdata
            index += 1
        except:
            print('had a dimension issue')
            h,w = imgdata.shape
            file_dimensions.append((h,w))
            if h != file_dimensions[0][0] and w != file_dimensions[0][1]:
                imgdata = cv2.resize(imgdata, (file_dimensions[0][1], file_dimensions[0][0]))
            print(imgdata.shape)
            x[index] = imgdata
            index += 1
    
    c = da.median(x, axis=0)
    c1 = x.compute()
    
    alpha = 0.5
    beta = 1.0 - alpha
    final_image = cv2.addWeighted(c1, alpha, avg_image, beta, 0.0)
    
    del c1
    del avg_image

    cv2.imwrite(f'{todays_folder_path}/{hostname}-{today}-nest_image.png', final_image)
    
    return total_frames

def main():
    
    start = time.time()
    
    parser = argparse.ArgumentParser(prog='Generate a composite nest image (from the images in todays folder) without bees in it! ')
    parser.add_argument('-p', '--data_folder_path', type=str, default=setup.data_folder_path, help='a path to the folder you want to collect data in. Default path is: /mnt/bumblebox/data/')
    parser.add_argument('-i', '--number_of_images', type=int, default=setup.number_of_images, help='the number of images you want to use to create your composite nest labelling image from todays images. The more you use, the longer this takes!')
    parser.add_argument('-sh', '--shuffle', type=bool, default=True, help='if shuffle is True, all the images from todays folder will be randomized so that this script isnt choosing just the earliest images from today. If you want images from a shorter timespan, choose this and a lower number of frames (youll have to do the time calculations yourself, based on how frequently recordings and images are generated and how many frames youve chosen. Default is True.')
    args = parser.parse_args()
    
    hostname = socket.gethostname()
    today = datetime.date.today()
    
    ret, todays_folder_path = create_todays_folder(args.data_folder_path)
    if ret == 1:
        print("Couldn't create todays folder to store data in. Exiting program. Sad!")
        return 1
    
    run_via_cron = None
    
    if sys.stdout.isatty():
        print("Running tag tracking script from terminal")
        logger.debug("Running tag tracking script from terminal")
        run_via_cron = False
        todays_folder_path = setup.nest_images_folder_path
        
        print(f"Running the generate_nest_images script! Remember, Im looking for images in:\n{setup.nest_images_folder_path}\nI set this path because you are running the script yourself and so are supposed to set the path yourself. I pulled the path from the variable nest_images_folder_path in the script setup.py.\nDo you want to use a different folder?")   
        print("\n")
        yes_or_no = input("Enter yes or no: ")
        
        while yes_or_no != "yes" and yes_or_no != "no":
            print("Do you want to use a different folder?")
            yes_or_no = input("Please enter either yes or no, all lowercase: ")
            
        if yes_or_no == "yes":
            print("Type the new path without a trailing \"/\" after the folder name - Example: /mnt/bumblebox/data/2023-10-23")
            todays_folder_path = input("Folder path: ")
            print(f"Using {todays_folder_path}. Moving on!")
        
        elif yes_or_no == "no":
            print("Moving on, then!")
        
        else:
            print("Type yes or no, all lowercase. Try again!")
            
        print(f"What do you want your new image filename to be? It will look like this: (computer hostname)-(your text here)-nest_image.png. Example: bumblebox-03-trial2_hr10-hr18-nest_image.png")
        today = input("Enter text: ")
        print(f"Filename: {hostname}-{today}-nest_image.png")

        
    else:
        logger.debug("Running tag tracking script via crontab")
        print("Running tag tracking script via crontab")
        run_via_cron = True
    
    
    total_frames = generate_nest_image(todays_folder_path, today, args.number_of_images, hostname, shuffle=True)
    
    end = time.time()
    
    print(f"Creation of composite image took {round(end - start,2)} seconds for {total_frames} images.")

if __name__ == '__main__':

    main()
