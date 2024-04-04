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
#import skvideo.io
#import io
#from PIL import Image as pil_im
#import tkinter as tk
#from tkinter import filedialog
#import setup


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
