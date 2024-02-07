#!/usr/bin/env python3

"""Label nest components in bumblebee nest."""

__appname__ = 'labelnests.py'
__author__ = 'August Easton-Calabria (eastoncalabr@wisc.edu), 206-919-8233'
__version__ = '0.0.1'

import os
import sys
import csv
import subprocess
import glob
import json
import cv2
import numpy as np
import pandas as pd
import skvideo.io
#import io
from PIL import Image as pil_im
import tkinter as tk
from tkinter import filedialog
import setup

'''
def count_frames(video):
    #Finds # of frames in a video - this will allow us to store the vids data for each frame in order to compress them into a single picture!
    #cv2.PROP_FRAME_COUNT seems not to work for these mjpegs, will explore
    #instead this function will manually loop over video to count frames
    cap = cv2.VideoCapture(video)
    frameCount = 0
    while True:
        ret, img = cap.read()
        if ret == True:
            frameCount += 1
        else:
            return frameCount


def convert2numpy(video):
    video_array = skvideo.io.vread(video)
    print(video_array.shape)
    f,h,w,d = video_array.shape
    new_array = np.empty([f,h,w])
    for i in range(0,f):    #f:video_array[i,:,:,:]:#np.ndindex(video_array.shape[0]):
        frame = video_array[i,:,:,:]
        print(frame.shape)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = np.float32(gray)
        new_array[i,:,:] = gray
    print(new_array.shape)
    #print(type(video_array))
    #video_array = skvideo.io.vreader(video)
    #print('video array type')
    #print(type(video_array))
    #return video_array
    return new_array

    
    #Converts each frame of a video into a matrix of number which correspond to the frame's pixel values
    #Then stores each of these frames into a big matrix - I think of it in 3 dimensions, like stacking paper on top of each other
    #BUT, there are actually 4 dimensions to the matrix, because each frame has 3 color channels, 
    #so we're actually stacking a (width X height X color channel (3)) matrix for each frame

    #cap = cv2.VideoCapture(video)
    #frameCount = count_frames(video)                                    #get video frame count from the count_frames function I wrote
    #frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))                 #this gets video width in pixels
    #frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))               #this gets video height
    
    #we use those values to make an empty matrix that is the size of our video (#frames x frameHeight, frameWidth)
    #which we will then save the pixel values into, using the cap.read() function below
    
    #buf = np.empty((frameCount, frameHeight, frameWidth, 3), np.dtype('uint8'))  

    #loop over each frame in our video, making sure that there's a valid frame there. cap.read() pulls the current frame data 
    #and the ret value (True if it's a valid frame, False if there's no frame, most likely meaning the end of the video)
    
    #fc = 0                  #frame counter
    #ret = True              #ret starts off as true, the while loop ends if it becomes false

    #while (fc < frameCount  and ret==True): 
    #    ret, buf[fc] = cap.read()                                       #frame data is read into matrix at buf["current frame number"], if there's no frame, ret becomes False
    #    fc += 1                                                         #frame counter is updated by 1                
    
    #cap.release()
    #return buf
    

def vids2medianimg(directory):
    #take in a list of videos of the same shape (except for frame number) 
    #Could be one, could be multiple, concatenates them

    #the below code is being blocked out to try to get tkinter dialoging to work

    #print(Hi! I'm going to turn your colony video into an altered picture so that you can label it more easily (wow!). 
    #If you want to stitch multiple together, I can do that too! Just make sure you've copied your colony video(s) into the 
    #\"For Labelling\" folder, which is inside the Videos folder. FYI the video processing might take a bit, so be patient! 
    #See you on the other side!)

    #if not os.path.isdir(dir + "/Videos/For Labelling"):
    #    subprocess.run(['mkdir', dir + "/Videos/For Labelling"]) #make a directory called LabeledNest inside dir not not already made

    def on_button_click():
        filenames = filedialog.askopenfilenames()
        with open(f"{setup.bumblebox_dir}/LabelNests_filepaths.txt", "w") as file:
            for path in filenames:
                file.write(path + "\n")
        return filenames

    def exit_window():
        win.destroy()
        
    win = tk.Tk()
    win.title("Choose your video files")
    win.geometry("600x140")
    label = tk.Label(win, text="    Please choose the video files you want to use to create an image for nest labelling.\n   Please choose no more than five for each colony. If youre not getting a good composite image, \ntry adding more videos or choosing videos that are spaced further apart.\nAfter you have chosen your files, please click 'Done'\nto continue processing your videos. This will take some time!")
    label.grid(row=3, column=1, columnspan=2)
    #label.pack()
    b1 = tk.Button(win, text="Done", command=exit_window)
    b1.grid(row=7, column=2)
    #b1.pack()
    #captured_output = io.StringIO()
    #sys.stdout = captured_output
    b2 = tk.Button(win, text="Choose files", command=on_button_click)
    b2.grid(row=7, column=1)
    # b2.pack()
    #sys.stdout = sys.__stdout__
    #global bee_video_file_paths
    #bee_video_file_paths = captured_output.getvalue()
    #captured_output.close()
    #print('here are the paths: ' + bee_video_file_paths)
    win.mainloop()

    f = open(f"{setup.bumblebox_dir}/LabelNests_filepaths.txt", "r")
    filenames = f.read()
    filenames = filenames.split(sep='\n')
    filenames = [i for i in filenames if i != '']
    filenames_copy = filenames.copy()
    buffer_list = [] #list to hold the video matrices before joining them together
    #for mjpeg in sorted(glob.glob(os.path.join(dir + "/Videos/For Labelling", '*.mjpeg'))):
    for video in filenames: #loops over each video selected
        if video in filenames_copy: #file_paths_copy starts as an exact copy, but videos will be removed from it as once theyre processed
            print(video)
            col_num = os.path.basename(video)[0:12] #saves the first part of each video name: col_xx CHANGE THIS TO NOT BE HARDCODED
            print(col_num)
            same_colony_vids = [ i for i in filenames if col_num in i ] #searches for every item with the substring equal to col_num
            print(same_colony_vids)
            vid2array = [] #empty list to store the video data from each colony so that we can smush them together 
            for vid in same_colony_vids: #for each video in same_colony_vids: BUT vid doesnt have the full path name soo....
                buf = convert2numpy(vid) #convert the video to a numpy array 
                vid2array.append(buf) #add this array to the list vid2array, created above
            joined = np.vstack(vid2array) #outside of the for loop now, smush together all the videos in vid2array
            print(joined.shape)
            print(joined)
            buffer_list.append([col_num, joined]) #append this smushed video to buffer_list
            filenames_copy = [ i for i in filenames_copy if i not in same_colony_vids ] #rewrites file_paths_copy to exclude the videos in same_colony_vids, so that these videos wont be looped through again   

    #this calculates the median image from the video(s)
    print('Calculating the median value of each pixel! Bear with me, this takes a while, especially when using multiple videos.')
    for col_vids in buffer_list:
        #print(type(col_vids))
        #print(col_vids[1].shape)
        #print(col_vids.shape)
        
        median_im = np.median(col_vids[1], axis=0)
        #convert numpy matrix into image type using PIL Image, making sure data type is uint8 and color format is RGB
        print('Converting the median numpy matrix back into an image!')
        median_im_v2 = pil_im.fromarray((median_im * 1).astype(np.uint8)).convert('RGB')
        print('Okay, finished with that. Now Im going to save the image!')
        #return median_im_new
        # saving the final output as a PNG file
        #will save the image as the name of the last video file
        #Ok, instead of saving the picture in this script, how about we save it in the script that will run this script, so that the same script can access the name of the file 
    
        img_path = (directory + '/' + col_vids[0] + '_nest_image.png') #os.path.basename(video)[0:6].strip(extension) + '.png')
        median_im_v2.save(img_path)
        print(img_path + ' is saved!')
    return print('Done creating colony nest images! Check for them in ' + directory )

    '''
def labelNest(directory):
    #with this code, have set up my own labelmerc file in the BumbleBox folder with config settings.
    #also went in and changed the __init__ file in the config folder, hashing out this code: (in order to have labels with repeating words)
    #if key == "labels" and value is not None and len(value) != len(set(value)):
    #    raise ValueError(
    #        "Duplicates are detected for config key 'labels': {}".format(value)
    #    )
    
    print('Running Labelme now... I have preloaded the labels to use for these images. Of course, you dont need to use labels that dont apply to your circumstances. Use the designated shapes for each label that is provided. For example, in order to draw the perimeter of the nest, Ill use the polygon tool, because the label says Nest perimeter (polygon). Right click to choose what types of shapes you want to use!')
    print(directory)
    print(type(directory))

    bumblebox_dir = os.path.dirname(os.path.realpath(__file__))
    print(bumblebox_dir)
    
    subprocess.run(['labelme', bumblebox_dir, '--config', bumblebox_dir + '/labelmerc', '--output', directory + '/Labelled Nest Files' ])
    #subprocess.run(['labelme', dir, '--labels', 'Arena perimeter (polygon),Nest perimeter (polygon),Eggs perimeter (polygons),Eggs (points),Larvae (circles),Pupae (circles),Queen larva (circles),Queen pupae,Wax pots (circles),full nectar pot (circles),empty wax pots (circles),pollen balls (circles), nectar source (circle)'])

    #subprocess.run(['labelme', dir, '--labels', 'nest perimeter,eggs (perimeter),eggs (circles),larvae,pupae,queen cell,wax pot,full nectar pot,empty wax pot,pollen ball, nectar source',
    #                '--shapes', 'polygon,polygon,points,cirlce,circle,circle,circle,circle,circle,circle,circle,circle', '--colors', 'yellow,orange,red,green,blue,purple,turquoise,magenta,pink'
    #                ]) #edit this line to add colours
    print('huh... is this on?')
    jsons = sorted(glob.glob(os.path.join(directory + '/Labelled Nest Files', '*.json')))
    if len(jsons) < 1:
        print('''Looks like you didn't save your work into a .json file inside Labelme, or you didnt save it to the Labelled Nest Files.\n''')
        print(directory + '/Labelled Nest Files')
    for file in jsons: #to do: check whether a CSV already exists? Or just overwrite the old one, depending on how long it takes?
        with open(file.strip(".json") + ".csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["object index","label","shape","x", "y", "radius"])
            nest = json.load(open(file))
            object_index = -1
            for shape in nest['shapes']:
                object_index += 1
                label = shape['label']
                shape_type = shape['shape_type']
                if shape_type == "circle":
                    x_center = shape['points'][0][0] #x coordinate of point defining center of circle
                    y_center = shape['points'][0][1] #y coordinate of point defining center of circle
                    x_perimeter = shape['points'][1][0] #x coordinate of point defining the perimeter of the cirlce
                    y_perimeter = shape['points'][1][1] #y coordinate of point defining the perimeter of the cirlce

                    radius = ((x_center-x_perimeter)**2 + (y_center-y_perimeter)**2) ** 0.5
                    writer.writerow([object_index, label, shape_type, x_center, y_center, radius])
                
                if shape_type == "point":
                    x = shape['points'][0][0]
                    y = shape['points'][0][1]
                    writer.writerow([object_index, label, shape_type, x, y, np.nan])

                if shape_type == "polygon":
                    for point in shape['points']:
                        x = point[0]
                        y = point[1]
                        writer.writerow([object_index,label, shape_type, x, y, np.nan])
    print('''Okay, just finished! Before quitting Labelme, you should have saved your work in a .json file by pressing save inside the popup label GUI.
          \nIf you did that, I just generated an accompanying CSV file that you can open and check out.\nIt has all your saved points in it.''') 
    return 0

"------------------------------------------------------"

def main(argv):
    
    directory = input("Please provide the folder with your nest images, and please make sure its on the computer that you're working on, and not a drive.\nInside that folder we'll make a folder called Labelled Nest Files, where we will store the data from our nest labelling\n\nNest data folder path:")
    if not os.path.exists(directory + '/Labelled Nest Files'):
        os.makedirs(directory + '/Labelled Nest Files')
    #if not os.path.exists('/Users/aec/Desktop/2023 bombus workshop pngs' + '/Nest Images/Labelled Nest Files'):
        #os.makedirs('/Users/aec/Desktop/2023 bombus workshop pngs' + '/Nest Images/Labelled Nest Files')
    #directory = directory + '/Nest Images'
    
    
    #vids2medianimg(directory)
    labelNest(directory)


if __name__ == "__main__": 
    """Makes sure the "main" function is called from command line"""  
    import sys
    status = main(sys.argv)
    sys.exit(status)
