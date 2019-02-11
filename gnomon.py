#!/usr/bin/env python

import numpy as np
import pandas as pd

from skimage.transform import rotate
from skimage.transform import resize
from skimage import io

import glob
import os
import copy
import tempfile
import imageio
import datetime

from IPython.display import clear_output
from PIL import Image

"""
Includes Husk object and the function husk2imgDf.
"""

# GNOMON CLASSES

class husk:
    """
    A husk object holds a list of images and data about those images. After uniformity of image dimensions
    and orientation is ensured, a blended image of all the images can be created.
    
    METHODS:
    
    constructor - 
    read_dir - Read in an entire directory of images
    add_image - Add a single image 
    rotation_check - 
    rotate_all -
    resize_imgs - 
    save_imgs - 
    blend - 
    show_img - 
    show_comp -
    
    """
    
    # CLASS VARIABLES
    
    imgs = [] # list holding vectorized versions of images
    comp_img = [] # image vector holding the composite image
    data = pd.DataFrame()
    
    def __init__(self):
        """
        
        """
        self.imgs = []
        self.comp_img = []
        self.data = pd.DataFrame()
            
    def read_dir(self, path):
        """
        read_dir(path)
        Populate list of images from directory.

        ARGS:
        path - directory name with full path needed to reach it
        """
        self.data = pd.DataFrame()
        self.imgs = []

        for filename in glob.glob(os.path.join(path, '*.jpg')):
            try:
                date = Image.open(filename)._getexif()[36867]
                date = datetime.datetime.strptime(date, "%Y:%m:%d %H:%M:%S")
            except:
                date = np.NaN

            img = io.imread(filename)
            self.imgs.append(img)

            d = {'Datetime': date, 
                 'Name': filename, 
                 'imgs_ind': len(self.imgs) - 1, 
                 'Shape': img.shape}
            self.data = self.data.append(d, ignore_index=True)
            
    def add_image(self, filename):
        """
        add_image(filename)

        Adds an image to the collection of images in the object.

        ARGS:

        filename - name of image file (with path if necessary) to be added to the list
        """
        img = io.imread(filename)
        self.imgs.append(img)
        
        try:
            date = Image.open(filename)._getexif()[36867]
            date = datetime.datetime.strptime(date, "%Y:%m:%d %H:%M:%S")
        except:
            date = np.NaN
        
        d = {'Datetime': date, 
             'Name': filename, 
             'imgs_ind': len(self.imgs) - 1, 
             'Shape': img.shape}
        self.data = self.data.append(d, ignore_index=True)
            
    def shape_test(self):
        """
        Tests whether all images have the same dimensions. If one does not, 
        displays it and prompts the user for how it should be rotated.
        """
        
        rot_D = {'l': 90, 'r': -90, 'u': 180, 'n': 0}
        
        for i in range(1, len(self.imgs)):
            if self.imgs[i].shape != self.imgs[0].shape:
                print("Image %d is of different dimensions." %(i))
                io.imshow(self.imgs[i])
                io.show()
                print("Which way would you like to rotate it?\n"
                     "l - left 90 degrees\n"
                     "r - right 90 degrees\n"
                     "u - 180 degrees\n"
                     "n - no rotation")
                inp = input("? ")
                
                while inp not in rot_D:
                    inp = input("? ")
                    
                if inp!='n':
                    self.imgs[i] = rotate(self.imgs[i], rot_D[inp], resize=True)
                clear_output()
                
    def rotation_check(self):
        """
        Display each image in imgs and prompt the user for rotations. They can
        choose to rotate the picture 90, 180, or 270 degrees.
        
        ARGS: none
        """
        
        rot_D = {'l': 90, 'r': -90, 'u': 180}
        
        # display instructions for user
        s = "ROTATION CHECK"
        print("%s\n%s" % (s, '-' * len(s)))
        
        print("You'll see all the images in the directory one by one.\n"
              "For each, you can select to rotate it: (l) left, 90\n"
              "degrees, (r) right 90 degrees, (u) for 180 degrees, or\n"
              "([ENTER]) to keep as is. Type \"stop\" at any point to halt.")
        
        for i in self.data.index.values:
            if self.data.loc[i, 'Shape'][0] < self.data.loc[i, 'Shape'][1]:
                io.imshow(self.imgs[i])
                io.show()
                inp = input("How to rotate (l, r, u, or 'stop'? ")
                if inp=='stop':
                    # stop checking
                    break
                else:
                    try:
                        self.imgs[i] = rotate(self.imgs[i], rot_D[inp], resize=True)
                        self.data.at[i, 'Shape'] = self.imgs[i].shape
                    except:
                        print("Error: unrecognized command.")
                        continue
                clear_output()
    
    def rotate_all(self, rotation):
        """
        Rotate all images in uniform direction.
        l - left 90 degrees
        r - right 90 degrees
        u - 180 degrees
        """
        rot_D = {'l': 90, 'r': -90, 'u': 180}
        
        for i in range(len(self.imgs)):
            self.imgs[i] = rotate(self.imgs[i], rot_D[rotation], resize=True)
            self.data.at[i, 'Shape'] = self.imgs[i].shape
            
    def resize_imgs(self):
        """
        Standardize size of images.
        
        ARGS - none
        """
        
        for i in range(len(self.imgs)):
            if self.imgs[i].shape != self.imgs[0].shape:
                self.imgs[i] = resize(self.imgs[i], self.imgs[0].shape)
                self.data.at[i, 'Shape'] = self.imgs[i].shape
                
    def blend(self, save_filename=""):
        """
        Combine the pictures. Automatically saves as a new file.

        save_filename - gives the filename for the saved image file
        """
            
        tot = copy.copy(self.imgs[0])
        for i in range(1, len(self.imgs)):
            if self.imgs[i].shape == self.imgs[0].shape:
                tot += self.imgs[i]
            else:
                print('Picture resolutions are not identical. Resizing images...')
                self.resize_imgs()
                print('Images resized.')
                tot += self.imgs[i]

        self.comp_img = ((tot - tot.min()) / (tot.max() - tot.min()))
        
        if len(save_filename) > 0:
            # file = tempfile.TemporaryFile(prefix='compositeImage_', suffix='.jpg', dir='comp_imgs').name
            file = os.path.join('comp_imgs', save_filename)
            imageio.imwrite(file, self.comp_img)
            print("Saving image as: %s" % (save_filename))
        
    def show_img(self, i):
        """
        Display the image at index i (given as argument).
        """
        io.imshow(self.imgs[i])
        io.show()
    
    def show_comp(self):
        """
        Display the composite image.
        """
        io.imshow(self.comp_img)
        io.show()
        
 


# GNOMON FUNCTIONS

  
def husk2imgDF(husk_obj):
    """
    Takes a husk object and converts its image list into an array of
    flattened arrays.
    """

    data = []
    for i in range(len(husk_obj.imgs)):
        data.append(husk_obj.imgs[i].flatten())
    
    return np.array(data)