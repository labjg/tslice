"""Generate time-slice images from digital image files. This module reuqires
SciPy for reading images into arrays and NumPy for the slicing and dicing.

By James Gilbert (@labjg) 2015.
Feel free to take, use, fix, hack etc.
"""

import glob
import numpy as np
from scipy import misc


class TimeSlice:

    def __init__(self, filePath, fileExt, imRotate=None, verbose=False):
        """Creates a sorted list of file paths for the given extension, in the
        given directory. These are the files used for slicing operations. It's
        assumed that they are named in order.

        Only 8-bit colour (RGB) images are expected.

        Args:
            filePath: directory containing image files to slice
            fileExt: file extension (only PIL-supported types, e.g. ".jpg")
            imRotate: For files that use an EXIF rotation flag, you need to
                      enter this manually, in counter-clockwise degrees,
                      as either 90, 180 or 270
            verbose: Flag for printing detailed info
        """

        if filePath[-1] == '/':
            self.filePath = filePath
        else:
            self.filePath = filePath + '/'  # Path must end with a slash

        self.fileExt = fileExt

        if not imRotate in (0,90,180,270):
            raise ValueError("Invalid rotation angle")
        self.imRotate = imRotate

        self.files = sorted(glob.glob(self.filePath + '*' + self.fileExt))
        self.numFiles = len(self.files)
        if verbose:
            print "Found %d %s files in dir %s" % (self.numFiles,
                                                   self.fileExt,
                                                   self.filePath)

    def slice(self, interval=1, outfile="out.jpg", sliceDir=0, trim=(0,0,0,0),
        borderWidth=0, borderCol=(128,128,128), verbose=False):
        """Produce a sliced image. The number of slices is inferred from the
        number of images in the target folder and the specified interval (it
        always starts with the first image in the folder, namewise). The output
        image size is calculated from the number of slices, to ensure it's a
        multiple of the slice width. All input images must have the same
        dimensions, otherwise things will probably go funny.

        Images are opened as numpy arrays, meaning we have to be careful with
        mixing x,y and i,j notation (i.e. column first vs. row first).
           
        Args:
            interval: The number of files between one slice and the next (e.g.
                      2 will skip every other image)
            outfile: The output filename including extension and directory
            sliceDir: Direction of progression (0=L->R; 1=T->B; 2=R->L; 3=B->T)
            trim: Number of pixels to trim from around the edge of every image,
                  after any rotation, as a tuple or array in the form
                  (left, top, right, bottom)
            borderWidth: The width of the border around each slice, in pixels
            borderCol: The 8-bit RGB colour value for the slice borders
            verbose: Flag for printing detailed info

        Returns:
            Sweet Fanny Adams.
        """
        trim = np.asarray(trim, dtype='uint16')
        borderCol = np.asarray(borderCol, dtype='uint8')

        if not interval > 0:
            raise ValueError("Invalid interval")
        if not sliceDir in (0,1,2,3):
            raise ValueError("Invalid slice direction")
        if not trim.shape[0] == 4:
            raise IndexError("Invalid number of trim parameters")

        numSlices = int(self.numFiles / interval)
        if verbose:  print "Number of slices: %i" % numSlices

        im_temp = misc.imread(self.files[0])

        if self.imRotate != None:
            if self.imRotate == 90:
                im_temp = np.rot90(im_temp,1)
            if self.imRotate == 180:
                im_temp = np.rot90(im_temp,2)
            if self.imRotate == 270:
                im_temp = np.rot90(im_temp,3)

        im_temp = im_temp[trim[1]:im_temp.shape[0]-trim[3],
                          trim[0]:im_temp.shape[1]-trim[2]]

        if sliceDir == 0 or sliceDir == 2:
            sliceWidth = int(im_temp.shape[1] / numSlices)
            imShape_ij = (im_temp.shape[0], sliceWidth*numSlices, 3)  # RGB
        elif sliceDir == 1 or sliceDir == 3:
            sliceWidth = int(im_temp.shape[0] / numSlices)
            imShape_ij = (sliceWidth*numSlices, im_temp.shape[1], 3)  # RGB

        im_main = np.zeros(shape=imShape_ij, dtype='uint8')
        del im_temp

        if verbose:
            print "Slice width is", sliceWidth, "px"
            print "Output image size is %i x %i px" % (imShape_ij[1],
                                                       imShape_ij[0])
        
        for i in range(numSlices):
            if verbose:  print "Slicing image %i of %i..." % (i+1, numSlices)

            im_this = misc.imread(self.files[i*interval])

            if verbose:
                print "Image number is %i of %i" % ((i*interval)+1,
                                                    self.numFiles)
                print "Image file path is %s" % self.files[i*interval]

            if self.imRotate != None:
                if self.imRotate == 90:
                    im_this = np.rot90(im_this,1)
                if self.imRotate == 180:
                    im_this = np.rot90(im_this,2)
                if self.imRotate == 270:
                    im_this = np.rot90(im_this,3)

            im_this = im_this[trim[1]:im_this.shape[0]-trim[3],
                              trim[0]:im_this.shape[1]-trim[2]]

            if sliceDir == 0:
                slice_TL_i = 0
                slice_TL_j = i*sliceWidth
                slice_BR_i = imShape_ij[0]-1
                slice_BR_j = (i+1)*sliceWidth-1
            elif sliceDir == 1:
                slice_TL_i = i*sliceWidth
                slice_TL_j = 0
                slice_BR_i = (i+1)*sliceWidth-1
                slice_BR_j = imShape_ij[1]-1
            elif sliceDir == 2:
                slice_TL_i = 0
                slice_TL_j = (numSlices-1-i)*sliceWidth
                slice_BR_i = imShape_ij[0]-1
                slice_BR_j = (numSlices-1-i+1)*sliceWidth-1
            elif sliceDir == 3:
                slice_TL_i = (numSlices-1-i)*sliceWidth
                slice_TL_j = 0
                slice_BR_i = (numSlices-1-i+1)*sliceWidth-1
                slice_BR_j = imShape_ij[1]-1

            im_slice = im_this[slice_TL_i:slice_BR_i+1,
                                slice_TL_j:slice_BR_j+1]
            del im_this
            
            if borderWidth > 0:
                im_slice[0:0+borderWidth,:] = borderCol
                im_slice[im_slice.shape[0]-borderWidth:im_slice.shape[0],:] \
                    = borderCol
                im_slice[:,0:0+borderWidth] = borderCol
                im_slice[:,im_slice.shape[0]-borderWidth:im_slice.shape[1]] \
                    = borderCol

            im_main[slice_TL_i:slice_BR_i+1,slice_TL_j:slice_BR_j+1] = im_slice
            del im_slice

        if verbose:  print "Saving output image to \"%s\"..." % outfile

        misc.imsave(outfile, im_main)

        if verbose:  print "Done"
