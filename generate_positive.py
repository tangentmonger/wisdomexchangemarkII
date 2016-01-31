"""
Quick and dirty tool to assist with generating the metadata for training
OpenCV cascade classifiers. Go through images and drag or shift-drag to select
areas of interest. (x to undo a selection, n and p for next/previous image). Hit
Enter when complete. The resulting data file can be passed in to the 
opencv_createsamples utility.
"""
import argparse
import os
import glob
import cv2
import numpy

parser = argparse.ArgumentParser(description='Generate positive training data file.')
parser.add_argument('-i', '--input', help='location of input images. Defaults to current directory', default=os.getcwd())
parser.add_argument('-o', '--output', help='output filename. Defaults to info.dat', default="info.dat")

args = parser.parse_args()
pattern = os.path.join(args.input, "*.jpeg")
filepaths = sorted(glob.glob(pattern))
output = {filename: [] for filename in filepaths}

NONE = 0
DRAG = 1
C_DRAG = 2

state = NONE
current_image = 0
print filepaths[current_image]
image = cv2.imread(filepaths[current_image])
area_buffer = numpy.zeros_like(image)
areas = output[filepaths[current_image]]
drag_start = None

def on_mouse(event, x, y, keys, *other):
    global state
    global NONE
    global DRAG
    global drag_start
    global areas
    global image
    global area_buffer
    if state == NONE and event == cv2.EVENT_LBUTTONDOWN and keys == (cv2.EVENT_FLAG_LBUTTON):
        state = DRAG
        drag_start = (x, y)
        cv2.imshow("input_window", cv2.add(image, area_buffer))
    elif state == DRAG and event == cv2.EVENT_MOUSEMOVE:
        drag_buffer = numpy.zeros_like(image)
        cv2.rectangle(drag_buffer, drag_start, (x,y), (0,0,255), 2)
        cv2.imshow("input_window", cv2.add(cv2.add(image, area_buffer), drag_buffer))
    elif state == DRAG and event == cv2.EVENT_LBUTTONUP:
        state = NONE
        if (x,y) != drag_start:
            areas.append((drag_start, (x,y)))
            cv2.rectangle(area_buffer, drag_start, (x,y), (0,100,0), 2)
        cv2.imshow("input_window", cv2.add(image, area_buffer))

    elif state == NONE and event == cv2.EVENT_LBUTTONDOWN and keys == (cv2.EVENT_FLAG_LBUTTON + cv2.EVENT_FLAG_SHIFTKEY):
        state = C_DRAG
        drag_start = (x, y)
        cv2.imshow("input_window", cv2.add(image, area_buffer))
    elif state == C_DRAG and event == cv2.EVENT_MOUSEMOVE:
        drag_buffer = numpy.zeros_like(image)
        opposite = ((drag_start[0]*2)-x,(drag_start[1]*2)-y)
        cv2.rectangle(drag_buffer, opposite, (x,y), (0,0,255), 2)
        cv2.imshow("input_window", cv2.add(cv2.add(image, area_buffer), drag_buffer))
    elif state == C_DRAG and event == cv2.EVENT_LBUTTONUP:
        state = NONE
        opposite = ((drag_start[0]*2)-x,(drag_start[1]*2)-y)
        if opposite != (x,y):
            areas.append((opposite, (x,y)))
            cv2.rectangle(area_buffer, opposite, (x,y), (0,100,0), 2)
        cv2.imshow("input_window", cv2.add(image, area_buffer))

cv2.namedWindow("input_window")
cv2.setMouseCallback("input_window", on_mouse)
cv2.imshow("input_window", image)

key = 0
while key != 13: #enter, finished
    key = cv2.waitKey()
    if key == 120: #x, undo
        areas = areas[:-1]
        area_buffer = numpy.zeros_like(image)
        for area in areas:
            cv2.rectangle(area_buffer, area[0], area[1], (0,100,0), 2)
        cv2.imshow("input_window", cv2.add(image, area_buffer))
    elif key == 110: #n, next
        current_image = (current_image+1) % len(filepaths)
        state = NONE
        print filepaths[current_image]
        image = cv2.imread(filepaths[current_image])
        area_buffer = numpy.zeros_like(image)
        areas = output[filepaths[current_image]]
        for area in areas:
            cv2.rectangle(area_buffer, area[0], area[1], (0,100,0), 2)
        drag_start = None
        cv2.imshow("input_window", cv2.add(image, area_buffer))
    elif key == 112: #p, previous
        current_image = (current_image-1) % len(filepaths)
        state = NONE
        print filepaths[current_image]
        image = cv2.imread(filepaths[current_image])
        area_buffer = numpy.zeros_like(image)
        areas = output[filepaths[current_image]]
        for area in areas:
            cv2.rectangle(area_buffer, area[0], area[1], (0,100,0), 2)
        drag_start = None
        cv2.imshow("input_window", cv2.add(image, area_buffer))

with open(args.output, "w") as output_file:
    area_data = sorted(output.items(), key=lambda x: x[0])
    for data in area_data:
        areas = data[1]
        if len(areas) > 0:
            coords = []
            for area in areas:
                x1 = min(area[0][0], area[1][0])
                y1 = min(area[0][1], area[1][1])
                x2 = max(area[0][0], area[1][0])
                y2 = max(area[0][1], area[1][1])
                coords.append("{0} {1} {2} {3}".format(x1, y1, x2-x1, y2-y1))
            output_file.write("{0}\t{1}\t{2}\n".format(data[0], len(data[1]), "\t".join(coords)))    

print "Output file generated: {}".format(args.output)
print "numPos = {}".format(sum([len(data[1]) for data in area_data]))

