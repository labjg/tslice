# Example of how to generate a time-slice image

import tslice

foo = tslice.TimeSlice("infiles/example_inputs/", ".jpg", verbose=True)

foo.slice(1, "outfiles/example_outputs/l2r_all_thinWhiteBorder.jpg",
          borderWidth=1, borderCol=(255,255,255), sliceDir=0, verbose=True)
foo.slice(2, "outfiles/example_outputs/t2b_half_thickRedBorder.tif",
          borderWidth=10, borderCol=(255,0,0), sliceDir=1, verbose=True)

del foo
