#!/usr/bin/python3

import os

from PIL import Image   # can be used for cropping!
# import bpy    # can only be used in the built-in python interface with Blender!!!!!

import os
import argparse
import subprocess
import collections
import sqlite3
import h5py
import numpy as np

import time
import datetime
import random
import struct

import cv2   # can be used for resizing!



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_directory_path", required=True)
    parser.add_argument("--output_directory_path", required=True)
    # parser.add_argument("--image_scale", type=float, default=12)
    args = parser.parse_args()

    # input_dir = os.path.join(os.getcwd(), 'img')
    # output_dir = os.path.join(os.getcwd(), 'out')
    return args

INPUT_DIR = 'img'
OUTPUT_DIR = 'out'
TOLERANCE = 11

###### Function from PyCropper project  ######
def process(file, output_dir):
    # Print out some file information
    image = Image.open(file)
    image_width = image.size[0]
    image_height = image.size[1]

    print("Image type: " + image.format + "; mode: " + image.mode + "; dimensions: " +
          str(image_width) + "x" + str(image_height))

    # Sample background color
    def rgb_tuple_to_str(tuple):
        return 'rgb(' + str(tuple[0]) + ', ' + str(tuple[1]) + ', ' + str(tuple[2]) + ')'

    def is_like_bg_color(color):
        color_r, color_g, color_b = color[0], color[1], color[2]
        bg_r, bg_g, bg_b = bg_color[0], bg_color[1], bg_color[2]
        r_similar, g_similar, b_similar = False, False, False

        if color_r in range(bg_r - TOLERANCE, bg_r + TOLERANCE):
            r_similar = True

        if color_g in range(bg_g - TOLERANCE, bg_g + TOLERANCE):
            g_similar = True

        if color_b in range(bg_b - TOLERANCE, bg_b + TOLERANCE):
            b_similar = True

        return r_similar and g_similar and b_similar

    print("Sampling background color...")
    pixel_map = image.load()
    x_offset = image_width * 0.05
    y_offset = image_height * 0.05

    ul_color = pixel_map[x_offset, y_offset]
    ur_color = pixel_map[image_width - x_offset, y_offset]
    ll_color = pixel_map[x_offset, image_height - y_offset]
    lr_color = pixel_map[image_width - x_offset, image_height - y_offset]
    bg_color = ()

    # print("Upper left color sample: " + rgb_tuple_to_str(ul_color))
    # print("Upper right color sample: " + rgb_tuple_to_str(ur_color))
    # print("Lower left color sample: " + rgb_tuple_to_str(ll_color))
    # print("Lower right color sample: " + rgb_tuple_to_str(lr_color))

    if ul_color == ur_color and ur_color == ll_color and ll_color == lr_color:
        bg_color = ul_color
        print("Sampled background color: " + rgb_tuple_to_str(ul_color))

    # Search for top edge
    print("Searching for top edge...")
    top_edge_coords = []

    for i in range(0, image_width, int(image_width / 10)):
        for y in range(0, image_height - 1):
            if not is_like_bg_color(pixel_map[i, y]):
                top_edge_coords.append(y)
                break

    top_edge_coord = top_edge_coords[0]
    for c in top_edge_coords:
        if c < top_edge_coord:
            top_edge_coord = c

    print("Found top edge at y = " + str(top_edge_coord))

    # Search for bottom edge
    print("Searching for bottom edge...")
    bottom_edge_coords = []

    for i in range(0, image_width, int(image_width / 10)):
        for y in range(image_height - 1, 0, -1):
            if not is_like_bg_color(pixel_map[i, y]):
                bottom_edge_coords.append(y)
                break

    bottom_edge_coord = bottom_edge_coords[0]
    for c in bottom_edge_coords:
        if c > bottom_edge_coord:
            bottom_edge_coord = c

    print("Found bottom edge at y = " + str(bottom_edge_coord))

    # Search for left edge
    print("Searching for left edge...")
    left_edge_coords = []

    for i in range(0, image_height, int(image_height / 10)):
        for x in range(0, image_width - 1):
            if not is_like_bg_color(pixel_map[x, i]):
                left_edge_coords.append(x)
                break

    left_edge_coord = left_edge_coords[0]
    for c in left_edge_coords:
        if c < left_edge_coord:
            left_edge_coord = c

    print("Found left edge at x = " + str(left_edge_coord))

    # Search for right edge
    print("Searching for right edge...")
    right_edge_coords = []

    for i in range(0, image_height, int(image_height / 10)):
        for x in range(image_width - 1, 0, -1):
            try:
                if not is_like_bg_color(pixel_map[x, i]):
                    right_edge_coords.append(x)
                    break
            except IndexError:
                pass

    right_edge_coord = right_edge_coords[0]
    for c in right_edge_coords:
        if c > right_edge_coord:
            right_edge_coord = c

    print("Found right edge at x = " + str(right_edge_coord))

    # Crop image
    print("Cropping image...")
    cropped_image = image.crop((left_edge_coord, top_edge_coord, right_edge_coord, bottom_edge_coord))

    # Display original and cropped images
    # !!! - THIS WILL ONLY WORK ON WINDOWS - !!!
    # image.show()
    # cropped_image.show()
    # os.system('pause')
    # !!! - END THIS WILL ONLY WORK ON WINDOWS - !!!

    # Save image to output dir
    file_name, file_ext = os.path.splitext(file)
    output_file_name = os.path.basename(file_name) + '_processed' + file_ext
    # output_file_path = os.path.join(os.getcwd(), OUTPUT_DIR, output_file_name)
    output_file_path = os.path.join(output_dir, output_file_name)
    print("Saving image to " + output_file_path)
    cropped_image.save(output_file_path)

########################################################################################################################################################
####### Adapted from https://blender.stackexchange.com/questions/13422/crop-image-with-python-script
# can only be used in the built-in python interface with Blender!!!!!
def crop_image_for_DeMoN_inBlenderPython(orig_img_path, output_dir, AutoCropping = False, cropped_min_x = 0, cropped_max_x = 0, cropped_min_y = 0, cropped_max_y = 0):
    '''Crops an image object of type <class 'bpy.types.Image'>.  For example, for a 10x10 image, if you put cropped_min_x = 2 and cropped_max_x = 6,
    you would get back a cropped image with width 4, and pixels ranging from the 2 to 5 in the x-coordinate

    Note: here y increasing as you down the image.  So, if cropped_min_x and cropped_min_y are both zero, you'll get the top-left of the image (as in GIMP).

    Returns: An image of type  <class 'bpy.types.Image'>
    '''

    # Print out some file information
    # orig_img = Image.open(orig_img_path)
    orig_img = bpy.ops.image.open( filepath = orig_img_path )
    image_width = orig_img.size[0]
    image_height = orig_img.size[1]

    print("Image type: " + orig_img.format + "; mode: " + orig_img.mode + "; dimensions: " +
          str(image_width) + "x" + str(image_height))

    num_channels = orig_img.channels
    #calculate cropped image size
    cropped_size_x = cropped_max_x - cropped_min_x
    cropped_size_y = cropped_max_y - cropped_min_y
    #original image size
    orig_size_x = orig_img.size[0]
    orig_size_y = orig_img.size[1]

    cropped_img = bpy.data.images.new(name="cropped_img", width=cropped_size_x, height=cropped_size_y)

    print("Exctracting image fragment, this could take a while...")

    #loop through each row of the cropped image grabbing the appropriate pixels from original
    #the reason for the strange limits is because of the
    #order that Blender puts pixels into a 1-D array.
    current_cropped_row = 0
    for yy in range(orig_size_y - cropped_max_y, orig_size_y - cropped_min_y):
        #the index we start at for copying this row of pixels from the original image
        orig_start_index = (cropped_min_x + yy*orig_size_x) * num_channels
        #and to know where to stop we add the amount of pixels we must copy
        orig_end_index = orig_start_index + (cropped_size_x * num_channels)
        #the index we start at for the cropped image
        cropped_start_index = (current_cropped_row * cropped_size_x) * num_channels
        cropped_end_index = cropped_start_index + (cropped_size_x * num_channels)

        #copy over pixels
        cropped_img.pixels[cropped_start_index : cropped_end_index] = orig_img.pixels[orig_start_index : orig_end_index]

        #move to the next row before restarting loop
        current_cropped_row += 1

    # Save image to output dir
    file_name, file_ext = os.path.splitext(orig_img_path)
    output_file_name = os.path.basename(file_name) + '_processed' + file_ext
    # output_file_path = os.path.join(os.getcwd(), OUTPUT_DIR, output_file_name)
    output_file_path = os.path.join(output_dir, output_file_name)
    print("Saving image to " + output_file_path)
    cropped_image.save(output_file_path)

    # return cropped_img

########################################################################################################################################################
###### Cannot work with large images, which will lead to memory issue!!!!
def crop_image_for_DeMoN_PIL(orig_img_path, output_dir, focal_length = 2457.6, AutoCropping = True, AutoResizing = True, cropped_min_x = 0, cropped_max_x = 0, cropped_min_y = 0, cropped_max_y = 0):
    # Print out some original file information
    orig_img = Image.open(orig_img_path)
    image_width = orig_img.size[0]
    image_height = orig_img.size[1]

    print("Image type: " + orig_img.format + "; mode: " + orig_img.mode + "; dimensions: " + str(image_width) + "x" + str(image_height))

    half_the_width = image_width / 2
    half_the_height = image_height / 2

    if AutoCropping == True:
        # Calculate the new images to be cropped for DeMoN
        Wnew = (0.89115971 * 256 * image_width) / focal_length
        Hnew = (1.18821287 * 192 * image_height) / focal_length

        cropped_img = orig_img.crop( (half_the_width - Wnew/2, half_the_height - Hnew/2, half_the_width + Wnew/2, half_the_height + Hnew/2) )

    DeMoN_input_width = 256
    DeMoN_input_height = 192

    if AutoResizing == True:
        print("the cropped image is resized to %d by %d to be used as input for DeMoN!" % (DeMoN_input_width, DeMoN_input_height))
        resized_img = cropped_img.resize((DeMoN_input_width, DeMoN_input_height), Image.ANTIALIAS)
    else:
        resized_img = cropped_img

    # Save image to output dir
    file_name, file_ext = os.path.splitext(orig_img_path)
    output_file_name = os.path.basename(file_name) + '_processed' + file_ext
    # output_file_path = os.path.join(os.getcwd(), OUTPUT_DIR, output_file_name)
    output_file_path = os.path.join(output_dir, output_file_name)
    print("Saving image to " + output_file_path)
    resized_img.save(output_file_path)

    # return cropped_img


########################################################################################################################################################
def crop_image_for_DeMoN_OpenCV(orig_img_path, output_dir, focal_length_x = 2457.6, focal_length_y = 2457.6, AutoCropping = True, AutoResizing = True, cropped_min_x = 0, cropped_max_x = 0, cropped_min_y = 0, cropped_max_y = 0):
    '''Crops an OpenCV image object.  For example, for a 10x10 image, if you put cropped_min_x = 2 and cropped_max_x = 6,
    you would get back a cropped image with width 4, and pixels ranging from the 2 to 5 in the x-coordinate

    Note: here y increasing as you down the image.  So, if cropped_min_x and cropped_min_y are both zero, you'll get the top-left of the image (as in GIMP).

    If you set Boolean values "AutoCropping = True, AutoResizing = True" and provide correponding focal_length of your camera, you may pre-process images in input_directory_path to be inputs for DeMoN network, which will match the intrinsics of the original training dataset!
    '''

    # Print out some original file information
    # load the image and show it
    orig_img = cv2.imread(orig_img_path)
    # cv2.imshow("original", orig_img)
    # cv2.waitKey(0)
    image_width = orig_img.shape[1]
    image_height = orig_img.shape[0]

    print("Image dimensions: " + str(image_height) + "x" + str(image_width))

    half_the_width = image_width / 2
    half_the_height = image_height / 2
    print("half_the_height = ", half_the_height)
    print("half_the_width = ", half_the_width)

    if AutoCropping == True:
        # Calculate the new images to be cropped for DeMoN
        Wnew = (0.89115971 * 256 * image_width) / focal_length_x
        Hnew = (1.18821287 * 192 * image_height) / focal_length_y
        print(Wnew)
        print(Hnew)
        print(focal_length_x)
        print(focal_length_y)
        print("Image dimensions should be cropped (Height*Width): " + str(Hnew) + "x" + str(Wnew))

        cropped_img = orig_img[int(half_the_height - Hnew/2):int(half_the_height + Hnew/2), int(half_the_width - Wnew/2):int(half_the_width + Wnew/2)]
        # cv2.imshow("cropped_img", cropped_img)
        # cv2.waitKey(0)

    else:
        cropped_img = orig_img[int(cropped_min_y):int(cropped_max_y), int(cropped_min_x):int(cropped_max_x)]


    DeMoN_input_width = 256
    DeMoN_input_height = 192

    if AutoResizing == True:
        print("the cropped image is resized to %d by %d (height*width) to be used as input for DeMoN!" % (DeMoN_input_height, DeMoN_input_width))
        resized_img = cv2.resize( cropped_img, (DeMoN_input_width, DeMoN_input_height), interpolation = cv2.INTER_AREA )
        # cv2.imshow("resized", resized_img)
        # cv2.waitKey(0)
    else:
        resized_img = cropped_img

    # Save image to output dir
    file_name, file_ext = os.path.splitext(orig_img_path)
    #output_file_name = os.path.basename(file_name) + '_processed' + file_ext
    output_file_name = os.path.basename(file_name) + file_ext
    output_file_path = os.path.join(output_dir, output_file_name)
    print("Saving image to " + output_file_path)
    print("Image to be saved is of shape (Height*Width*Channels) = ", resized_img.shape)
    cv2.imwrite(output_file_path, resized_img)

    # return cropped_img


def main():
    args = parse_args()

    image_exts = [ '.jpg', '.JPG', '.jpeg', '.png' ]
    input_dir = args.input_directory_path
    output_dir = args.output_directory_path


    # Create output directory, if not present
    try:
        os.stat(output_dir)
    except:
        os.mkdir(output_dir)

    # Iterate over working directory
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        file_name, file_ext = os.path.splitext(file_path)

        # Check if file is an image file
        if file_ext not in image_exts:
            print("Skipping " + file + " (not an image file)")
            continue
        else:
            print()
            print("Processing " + file + "...")
            print("--- corresponding file path is " + file_path + "...")
            # process(file_path, output_dir)
            crop_image_for_DeMoN_OpenCV(file_path, output_dir, 2457.6, 2457.6, True, True, 200, 1000, 100, 200)

    # ###### Test on single image
    # file_path = os.path.join(input_dir, os.listdir(input_dir)[0])
    # file_name, file_ext = os.path.splitext(file_path)
    # crop_image_for_DeMoN_OpenCV(file_path, output_dir, 2457.6, 2457.6, True, True, 200, 1000, 100, 200)

if __name__ == '__main__':
    main()
