import os
import numpy as np
import argparse
from PIL import Image, ImageFilter
import random


parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True, help='path to the input image to be converted')
parser.add_argument('--output', default='output/', help='path to the output image to be saved')
parser.add_argument('--density', type=float, default=0.01, help='number of amogi to add per pixel')
parser.add_argument('--visor', type=bool, default=True, help='tint visors blue')
parser.add_argument('--weight', type=int, default=0.9, help='0 to 1 weight of ommiting the placement of an amongus')
parser.add_argument('--flip', type=int, default=0.8, help='0 to 1 chance of fliping an amogus')
parser.add_argument('--resize', type=bool, default=False, help='if apply resizing to visualize beter the amongui')
parser.add_argument('--show', action='store_true',
    help='show a plot comparing the original image with its conversion')
args = parser.parse_args()

im = Image.open(args.input)
#if args.resize:
#    im = im.resize((450, 450))
im_gb = im.filter(ImageFilter.GaussianBlur(radius = 2))
img = np.asarray(im)
img = img.copy()
img_gb = np.asarray(im_gb)
y_len, x_len, _ = img.shape
mask = np.zeros((y_len, x_len))

print(img.shape)

amogus = np.array([
    [1.0, 1.0, 1.0, 0.0],
    [1.2, 1.2, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 0.0],
    [1.0, 0.0, 1.0, 0.0]
])

amogus = np.stack([amogus]*3, axis=2)

if args.visor:
    amogus[1, :2, 2] += 0.15

print(amogus.shape)

def validate_placement(x,y, img, mask, var=120):
    arr = img[y:y+5, x:x+4, :]
    if np.var(np.mean(arr, axis=2)) < var and np.max(mask[y:y+5, x:x+4]) == 0:
        val = True
        mask[y:y+5, x:x+4] += 1
    else:
        val = False
    return val, mask

def insert_amogus(x,y, img, img_gb, amogus):
    color = np.mean(img_gb[y:y+5, x:x+4, :], axis=(0,1)) + np.random.uniform(0, 15, 3) 
    color[color < 0] = 0
    color[color > 255] = 255
    flip = random.random() > args.flip
    if not flip:
        for i in range(5):
            for j in range(4):
                for k in range(3):
                    if amogus[i,j, k] > 0:
                        #img[y+i, x+j, k] = amogus[i, j, k]*color[k]
                        if amogus[i, j, k]*color[k] <= 255:
                            clr = amogus[i, j, k]*color[k]
                        else:
                            clr = 0.85*color[k]
                        img[y+i, x+j, k] = clr
    else:
        for i in range(5):
            for j in range(4):
                for k in range(3):
                    if amogus[i,3-j, k] > 0:
                        if amogus[i, 3-j, k]*color[k] <= 255:
                            clr = amogus[i, 3-j, k]*color[k]
                        else:
                            clr = 0.85*color[k]
                        img[y+i, x+j, k] = clr


    return img



print('x: ', len(img[0]))
print('y: ', len(img))

x = 0
y = 0

while x < x_len-4:
    while y < y_len-5:
        valid, mask = validate_placement(x, y, img_gb, mask)
        if valid and random.random() < args.weight:

            img = insert_amogus(x, y, img, img_gb, amogus)
            y += 5
        else:
            y += 1
    x += 1
    y = 0

file_name = os.path.basename(args.input)
file_name = os.path.splitext(file_name)[0]

im_amg = Image.fromarray(img.astype('uint8'), 'RGB')
#if args.resize:
#    im_amg = im_amg.resize((1200, 1200), Image.NEAREST)
im_amg.show()
im_amg.save(os.path.join(args.output, file_name+"_amongui.png"), format='png')