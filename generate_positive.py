import argparse
import os
import glob
import cv2
import numpy

parser = argparse.ArgumentParser(description='Generate positive training data file.')
parser.add_argument('-i', '--input', help='location of input images. Defaults to current directory', default=os.getcwd())
parser.add_argument('-o', '--output', help='output filename. Defaults to info.dat', default="info.dat")

args = parser.parse_args()
print args


pattern = os.path.join(args.input, "*.jpeg")
filepaths = sorted(glob.glob(pattern))
#for filepath in filepaths:
#    print filepath

#cv2.EM(                   cv2.EM_START_AUTO_STEP    cv2.EVENT_FLAG_LBUTTON    cv2.EVENT_MBUTTONDBLCLK
#cv2.EM_COV_MAT_DEFAULT    cv2.EM_START_E_STEP       cv2.EVENT_FLAG_MBUTTON    cv2.EVENT_MBUTTONDOWN
#cv2.EM_COV_MAT_DIAGONAL   cv2.EM_START_M_STEP       cv2.EVENT_FLAG_RBUTTON    cv2.EVENT_MBUTTONUP
#cv2.EM_COV_MAT_GENERIC    cv2.EPNP                  cv2.EVENT_FLAG_SHIFTKEY   cv2.EVENT_MOUSEMOVE
#cv2.EM_COV_MAT_SPHERICAL  cv2.ERTrees(              cv2.EVENT_LBUTTONDBLCLK   cv2.EVENT_RBUTTONDBLCLK
#cv2.EM_DEFAULT_MAX_ITERS  cv2.EVENT_FLAG_ALTKEY     cv2.EVENT_LBUTTONDOWN     cv2.EVENT_RBUTTONDOWN
#cv2.EM_DEFAULT_NCLUSTERS  cv2.EVENT_FLAG_CTRLKEY    cv2.EVENT_LBUTTONUP       cv2.EVENT_RBUTTONUP

NONE = 0
DRAG = 1
C_DRAG = 2

state = NONE
image = cv2.imread(filepaths[0])
height, width = image.shape[:2]

area_buffer = numpy.zeros_like(image)
areas = []
drag_start = None

def on_mouse(event, x, y, keys, *other):
    global state
    global NONE
    global DRAG
    global drag_start
    global areas
    global image
    global area_buffer
    #print event, keys
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
        areas.append((opposite, (x,y)))
        cv2.rectangle(area_buffer, opposite, (x,y), (0,100,0), 2)
        cv2.imshow("input_window", cv2.add(image, area_buffer))

cv2.namedWindow("input_window")
cv2.setMouseCallback("input_window", on_mouse)
cv2.imshow("input_window", image)

key = 0
while key != 13:
    key = cv2.waitKey()
    print key
    if key == 120: #x, undo
        areas = areas[:-1]
        area_buffer = numpy.zeros_like(image)
        for area in areas:
            cv2.rectangle(area_buffer, area[0], area[1], (0,100,0), 2)
        cv2.imshow("input_window", cv2.add(image, area_buffer))

print areas

