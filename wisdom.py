"""
Represents one item of wisdom and its analysis.
"""

import math
import cv2
import os
import numpy

# Tuning ================
# Angle resolution: smallest angle used in levelling
ANGLE_RESOLUTION = 5
# Levelling width: distance to stretch pixels during levelling.
# Chosen by trial and error over sample wisdom, gets 94%
LEVELLING_WIDTH = 85
# Miminum ink: below this number of pixels, image is considered blank
MIMINUM_INK = 100


class Wisdom():
    """
    Represents one item of wisdom and its analysis.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self._original = None
        self._prepared = None
        self._prepared_rotated = None
        self._best_angle = None
        self._drawing = None


    @property
    def filename(self):
        """
        The filename of this wisdom.
        """
        return os.path.basename(self.filepath)

    @property
    def original(self):
        """
        The original wisdom image.
        """
        if self._original is None:
            self._original = cv2.imread(self.filepath)
        return self._original

    @property
    def prepared(self):
        """
        Original image greyscaled, shrunk, inverted and thresholded.
        Result: a white-on-black version ready for further processing.
        """
        if self._prepared is None:
            image = self.original
            # change to greyscale
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # resize, 10%
            image = cv2.resize(image, (0, 0), fx=0.1, fy=0.1)
            # invert and threshold (white on black)
            threshold = 230 # if a pixel is below this...
            output_value = 255 # output white (otherwise black)
            _, image = cv2.threshold(image, 
                                     threshold, 
                                     output_value, 
                                     cv2.THRESH_BINARY_INV)
            self._prepared = image
        return self._prepared

    def _rotate(self, angle):
        """
        Rotate the prepared image.
        Return a square image that contains the rotated image.
        Square size is the same, regardless of angle.
        """
        image = self.prepared
        # ensure nothing is rotated by 0, otherwise it looks brighter
        # than the rest
        angle += 1
        (height, width) = image.shape[:2]
        longest_diagonal = math.sqrt(height**2 + width**2)
        # extend "canvas"
        extend_h = int((longest_diagonal - height) / 2 )
        extend_w = int((longest_diagonal - width) / 2 )
        extended_image = cv2.copyMakeBorder(image,
                                            top=extend_h,
                                            bottom=extend_h,
                                            left=extend_w,
                                            right=extend_w,
                                            borderType=cv2.BORDER_CONSTANT,
                                            value=0)

        # rotate
        (height, width) = extended_image.shape[:2]
        center = (width / 2, height / 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_image = cv2.warpAffine(extended_image,
                                       matrix,
                                       (width, height),
                                       borderMode=cv2.BORDER_CONSTANT,
                                       borderValue=0)

        return rotated_image
    
    @property
    def best_angle(self):
        """
        The angle at which this wisdom looks most level.
        """
        if self._best_angle is None:
            if self.blank == True:
                self._best_angle = 0
            else:
                ink_areas = {}
                search_start = 0
                search_end = 180
                sample_distance = 30 # searches
                best_angle = 0

                while sample_distance > ANGLE_RESOLUTION:
                    for angle in xrange(search_start,
                                        search_end,
                                        sample_distance):
                        if angle not in ink_areas:
                            ink_area = self._get_area_for_levelling(angle % 180)
                            ink_areas[angle] = ink_area

                    best_angle = min(ink_areas.items(), key=lambda x: x[1])

                    new_search_space = (search_end - search_start) / 2
                    search_start = best_angle[0] - (new_search_space / 2)
                    search_end = best_angle[0] + (new_search_space / 2)
                    sample_distance = sample_distance / 2

                self._best_angle = best_angle[0]
        return self._best_angle

    def _get_area_for_levelling(self, angle):
        """
        Calculate the horizontal spread area at the given angle.
        """
        image = self._rotate(angle)
        # rotation loses some ink brightness, re-threshold
        threshold = 20 # if a pixel is above this...
        output_value = 255 # output white (otherwise black)
        _, image = cv2.threshold(image,
                                 threshold,
                                 output_value,
                                 cv2.THRESH_BINARY)

        # blur letters together
        element = cv2.getStructuringElement(cv2.MORPH_RECT,
                                            (LEVELLING_WIDTH,1))
        image = cv2.dilate(image, element)

        return sum([sum(row) / 255 for row in image])

    @property
    def prepared_rotated(self):
        """
        Return the prepared image, rotated to the best angle
        """
        if self._prepared_rotated is None:
            self._prepared_rotated = self._rotate(self.best_angle)
        return self._prepared_rotated
   
    @property
    def blank(self):
        """
        Return True if this wisdom is blank
        """
        image = self.prepared
        ink = sum([sum(row) / 255 for row in image])
        return ink <= MIMINUM_INK

    @property
    def drawing(self):
        """
        Return True if this wisdom contains an image
        """
        if self._drawing == None:
            if self.blank:
                self._drawing = False
            else:
                #lines = cv2.HoughLines(image=self.prepared,
                #                       rho=10,
                #                       theta=math.radians(1),
                #                       threshold=1)
                ##print lines
                #print len(lines[0])

                # basically a Hough transform
                data = self._get_histogram_at_angles()
                hough = numpy.array(data)
                #hough = cv2.normalize(src=hough,alpha=0, beta=255, dtype=cv2.NORM_MINMAX)
                hough = cv2.convertScaleAbs(hough) # -> 8 bit
                cv2.normalize(hough, hough, 0, 255, cv2.NORM_MINMAX)
                #hough = cv2.GaussianBlur(hough, (5,5),0)
                #for x in xrange(0, 255):
                #    _, threshold = cv2.threshold(hough, x, 255, cv2.THRESH_BINARY)
                #    cv2.imwrite("analysis/%s.%d.jpeg" % (self.filename,x), threshold)
                cv2.imwrite("hough/%s" % self.filename, hough)


                #hough = cv.fromarray(numpy.array(data))
                #hough = cv2.cvtColor(hough, cv2.COLOR_BGR2GRAY)
                # Set up the detector with default parameters.
                # Setup SimpleBlobDetector parameters.
                #params = cv2.SimpleBlobDetector_Params()
                # 
                ## Change thresholds
                ##params.minThreshold = 0
                ##params.maxThreshold = 100
                ##params.thresholdStep = 10
                #  
                ## Filter by Area.
                #params.filterByArea = False
                #params.minArea = 1500
                #   
                ## Filter by Circularity
                #params.filterByCircularity = False
                #params.minCircularity = 0.1
                #    
                ## Filter by Convexity
                #params.filterByConvexity = False
                #params.minConvexity = 0.87
                #     
                ## Filter by Inertia
                #params.filterByInertia = False
                #params.minInertiaRatio = 0.01
                #detector = cv2.SimpleBlobDetector(params)
                # 
                ## Detect blobs.
                #keypoints = detector.detect(hough)
                #print keypoints
                #print len(keypoints)
                #im_with_keypoints = cv2.drawKeypoints(hough, keypoints, numpy.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS) 
                #cv2.imwrite("analysis/%s" % self.filename, im_with_keypoints)
                #self._drawing = (len(keypoints) == 0)
        return self._drawing

    def _get_histogram_at_angles(self):
        # there's a much faster way to do this, how does opencv do it?
        data = []
        for angle in xrange(0, 180):
            image = self._rotate(angle)
            data.append([int(sum(row) / 255) for row in image])
        return data
