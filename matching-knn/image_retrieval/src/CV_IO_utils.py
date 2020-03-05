"""

 CV_IO_utils.py  (author: Anson Wong / git: ankonzoid)

"""
import os
import skimage.io
from multiprocessing import Pool

# Read image
def read_img(filePath):
    return skimage.io.imread(filePath, as_gray=False)

# Read images with common extensions from a directory
def read_imgs_dir(dirPath, extensions, parallel):
    args = [os.path.join(dirPath, filename)
            for filename in os.listdir(dirPath)
            if any(filename.lower().endswith(ext) for ext in extensions)]
    if parallel:
        pool = Pool()
        imgs = pool.map(read_img, args)
        pool.close()
        pool.join()
    else:
        imgs = [read_img(arg) for arg in args]
    args_=[]
    for i in args:
        args_.append(os.path.basename(i))
    return imgs,args_

# Save image to file
def save_img(filePath, img):
    skimage.io.imsave(filePath, img)
