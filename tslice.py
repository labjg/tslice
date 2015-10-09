# By James Gilbert (@labjg) 2015-03-20; feel free to take, use, fix, hack etc.

import glob
from PIL import Image
import numpy as np


class TimeSlice:

    def __init__(self, filePath, fileExt, imRotate=None, verbose=False):
        # Create a timeslice object and set up the file directory and
        # image rotation options, then list the files in name order
        #   filePath: directory containing image files to slice
        #   fileExt: file extension (only PIL-supported types, e.g. ".jpg")
        #   imRotate: for files that use an EXIF rotation flag, you need
        #     to enter this manually; becomes clear if output is the wrong way!
        #   verbose: print detailed info about the process

        if filePath[-1] == '/':
            self.filePath = filePath
        else:
            self.filePath = filePath + '/'  # Path must end with a slash

        self.fileExt = fileExt

        if imRotate == None:
            self.imRotate = None
        elif imRotate == 90:
            self.imRotate = Image.ROTATE_90
        elif imRotate == 180:
            self.imRotate = Image.ROTATE_180
        elif imRotate == 270:
            self.imRotate = Image.ROTATE_270
        else:
            print "Warning: invalid image rotation"

        self.files = sorted(glob.glob(self.filePath + '*' + self.fileExt))
        self.numFiles = len(self.files)
        if verbose:
            print "Found %d %s files in dir %s" % (self.numFiles,
                                                   self.fileExt,
                                                   self.filePath)


    def slice(self, interval=1, outfile="out.jpg", borderWidth=0,
        borderCol=(128,128,128), sliceDir=0, imShow=False, verbose=False):
        # Produce a sliced image. The number of slices is inferred from the
        # number of images in the target folder and the specified interval
        # (it alwys starts with the first image in the folder, namewise).
        # The output image size is calculated from the number of slices, to
        # ensure it's a multiple of the slice width.  All input images must
        # have the same dimensions, otherwise things will probably go funny.
        #   interval: the number of files between one slice and the next
        #   (e.g. 2 will skip every other image)
        #   outfile: the output filename including extension and directory
        #   borderWidth: the width of the border around each slice in pixels
        #   borderCol (tuple): the 8-bit RGB colour value for the slice borders
        #   sliceDir: direction of progression (0=L->R; 1=T->B; 2=R->L; 3=B->T)
        #   imShow: pop up and show the result
        #   verbose: print detailed info about the process



        #  OTHER SLICE DIRECTIONS NEED IMPLEMENTING

        if not interval > 0:
            raise ValueError("Invalid interval")
        if not sliceDir in (0,1,2,3):
            raise ValueError("Invalid slice direction")

        numSlices = int(self.numFiles / interval)
        if verbose:
            print "Number of slices: %i" % numSlices

        im_temp = Image.open(self.files[0])
        if self.imRotate != None:
            im_temp = im_temp.transpose(self.imRotate)
        if sliceDir == 0 or sliceDir == 2:
            sliceWidth = int(im_temp.size[0] / numSlices)
            imSize = (sliceWidth * numSlices, im_temp.size[1])
        elif sliceDir == 1 or sliceDir == 3:
            sliceWidth = int(im_temp.size[1] / numSlices)
            imSize = (im_temp.size[0], sliceWidth * numSlices)
        im_main = Image.new(im_temp.mode, imSize)
        del im_temp

        if verbose:
            print "Slice width is", sliceWidth, "px"
            print "Output image size is %i x %i px" % imSize
        
        for i in range(numSlices):

            if verbose:
                print "Slicing image %i of %i..." % (i+1, numSlices)

            im_slice = Image.open(self.files[i*interval])
            if verbose:
                print "Image number is %i of %i" % ((i*interval)+1,
                                                    self.numFiles)
                print "Image file path is %s" % self.files[i*interval]
            if self.imRotate != None:
                im_slice = im_slice.transpose(self.imRotate)

            if sliceDir == 0:
                sliceBox = (i*sliceWidth, 0, (i+1)*sliceWidth, imSize[1])
            elif sliceDir == 1:
                sliceBox = (0, i*sliceWidth, imSize[0], (i+1)*sliceWidth)
            elif sliceDir == 2:
                sliceBox = ((numSlices-1-i)*sliceWidth, 0,
                            (numSlices-1-i+1)*sliceWidth, imSize[1])
            elif sliceDir == 3:
                sliceBox = (0, (numSlices-1-i)*sliceWidth,
                            imSize[0], (numSlices-1-i+1)*sliceWidth)
            im_slice = im_slice.crop(sliceBox)

            if borderWidth > 0:
                for x in range(im_slice.size[0]):
                    for y in range(borderWidth):
                        im_slice.putpixel((x,y), borderCol)
                        im_slice.putpixel((x,im_slice.size[1]-1-y), borderCol)
                for y in range (im_slice.size[1]):
                    for x in range(borderWidth):
                        im_slice.putpixel((x,y), borderCol)
                        im_slice.putpixel((im_slice.size[0]-1-x,y), borderCol)
            im_main.paste(im_slice, sliceBox)
            del im_slice

        if verbose:
            print "Saving output image to \"%s\"..." % outfile

        im_main.save(outfile)

        if imShow:
            im_main.show()

        if verbose:
            print "Done"
