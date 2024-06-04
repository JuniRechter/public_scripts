# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 09:29:07 2024

@author: Juniper Rechter

This file contains functions checking if either an original camera trap (CT) image (.JPG)
was taken with infrared at nighttime. These functions will
open images and check the mean saturation of the image; if saturation < 5.0, the image was likely 
taken at night with infrared, and the script will assign Night: True.
This will output a .CSV file (containing the image filename and its boolean Night value) that 
can be merged with other dataframes along the filename to update the main dataset. 

This script is quite fast: for ~50,000 full-sized crops (~20GB images), it only requires ~1GB memory, and will
complete Time-of-Day check in ~10-15 mins. Can easily be run on laptops and potatoes. 

Command-line arguments:
    - image_directory: str, path to directory of images.
    - save: str, enter filename for the created CSV file.

Example Command-line usage:
    python Time_of_Day.py CT_Images CT_Images_ToD
will result in reading through all subfolders and images in the folder 'CT_Images'
and returning the final df as 'CT_Images_ToD.csv'.

Example usage in Python:
    df = check_ToD("CT_Images")
will run the same, but the df will be provided to you in the environment.
You will need to manually save it from here if you want to keep a copy.
"""

import os   # To access computer's folders
import sys
import pandas as pd   # To manipulate dataframes
import cv2   # To open images and read individual channels, calculate values
import argparse   # To create a command-line level function and arguments.
import time   # To add timestamps if you want to get an estimation of timing
import humanfriendly   # Converts timestamps to a human-friendly format for reading

#%%
def check_ToD(image_directory="image_directory"): 

    """
    This function checks images to determine if they were taken at night with infrared or during 
    the day with full colour.
    Note that this version works for three-channel CT images, but not for image masks/crops or PNG images with transparent backgrounds. 
    
    Inputs:
    - image_directory: str, set the directory to pull images from. 
    
    """
    data=[]
    for directory, subdirs, files in os.walk(image_directory):
        rel_subdir = os.path.relpath(directory, start=image_directory)
        for f in files:
            if f.endswith('.JPG' or '.jpg' or'.JPEG' or '.jpeg'):
                image = cv2.imread(directory + "/" + f)
                img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                saturation = img_hsv[:, :, 1].mean()
                value = img_hsv[:, :, 2].mean()
                if saturation <5.0:   # Can be lowered if desired. If no coloured logo in image, saturation should be between 0.0-1.0 for infrared images (fully greyscale)
                    data.append({'filename':rel_subdir +'/' + f, 'saturation':saturation,
                                 'value': value, 'Night':True})
                elif saturation >5.0:
                    data.append({'filename':rel_subdir +'/' + f, 'saturation':saturation,
                        'value': value, 'Night':False})
    df = pd.DataFrame(data)
    return df

#%% Command-line driver  

def main():
    
    parser = argparse.ArgumentParser(
        description='Program to check CT images for saturation and value, and determine whether an image was taken at night.')
    parser.add_argument('image_directory', 
                        type=str,
                        help='Path to directory of images.')
    parser.add_argument('save', 
                        type=str,
                        help='Enter filename for the created CSV file.')

    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    assert os.path.exists(args.image_directory), \
        'Image directory {} does not exist'.format(args.image_directory)
    if os.path.exists(args.output_directory):
        print('Warning: output_file {} already exists and will be overwritten'.format(
            args.output_directory))

    start_time = time.time()
    print("Starting check.")
    df = check_ToD(image_directory=args.image_directory)

    elapsed = time.time() - start_time

    df.to_csv(args.save + ".csv", index=False)

    print(('Finished checking Time of Day in {:.3f} seconds.').format(elapsed))
    print(('Finished resizing images in {}.').format(humanfriendly.format_timespan(elapsed)))

if __name__ == '__main__':
    main()