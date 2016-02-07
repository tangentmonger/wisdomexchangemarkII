"""
Represents one item of wisdom and its analysis.
"""

import math
import cv2
import os
import numpy
import scipy
import scipy.ndimage.filters as filters
import scipy.ndimage.morphology as morphology

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
        if not os.path.isfile(filepath):
            raise IOError("File '%s' not found." % os.path.abspath(filepath))
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
            # resize, 5%
            image = cv2.resize(image, (0, 0), fx=0.05, fy=0.05)
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
        height, width = image.shape[:2]
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
        height, width = extended_image.shape[:2]
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



    def detect_local_peaks(self, image, detect_maxima=True):
        # http://stackoverflow.com/questions/3684484/peak-detection-in-a-2d-array/3689710#3689710
        """
        Takes an array and detects the troughs using the local maximum filter.
        Returns a boolean mask of the troughs (i.e. 1 when
        the pixel's value is the neighborhood maximum, 0 otherwise)
        """
        # define an connected neighborhood
        # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology.html#generate_binary_structure
        neighborhood = morphology.generate_binary_structure(len(image.shape),2)
        # apply the local minimum filter; all locations of minimum value 
        # in their neighborhood are set to 1
        # http://www.scipy.org/doc/api_docs/SciPy.ndimage.filters.html#minimum_filter
        if detect_maxima:
            local_peaks = (filters.maximum_filter(image, footprint=neighborhood)==image)
        else:
            local_peaks = (filters.minimum_filter(image, footprint=neighborhood)==image)
        # local_peaks is a mask that contains the peaks we are 
        # looking for, but also the background.
        # In order to isolate the peaks we must remove the background from the mask.
        # 
        # we create the mask of the background
        background = (image==0)
        # 
        # a little technicality: we must erode the background in order to 
        # successfully subtract it from local_min, otherwise a line will 
        # appear along the background border (artifact of the local minimum filter)
        # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology.html#binary_erosion
        eroded_background = morphology.binary_erosion(
            background, structure=neighborhood, border_value=1)
        # 
        # we obtain the final mask, containing only peaks, 
        # by removing the background from the local_min mask
        detected_minima = local_peaks - eroded_background
        return detected_minima


    def drawing(self):
        """
        Return True if this wisdom contains an image
        """
        if self._drawing == None:
            if self.blank:
                self._drawing = 0
            else:
                hough = self._get_hough_transform(straighten=True)
                
                full_hough = numpy.concatenate((hough, numpy.fliplr(hough)))
                print full_hough.shape

    

                minima = self.detect_local_peaks(cv2.blur(full_hough, (10,10)))
                locations = numpy.where(minima)
                print len(locations[0])

                #minima = cv2.cvtColor(minima, cv2.COLOR_BGR2GRAY)
                #cv2.normalize(minima, minima, 0, 255, cv2.NORM_MINMAX)
                print minima.shape
                print type(minima)
                print minima.dtype

                peak_points = zip(locations[0], locations[1])

                for peak in peak_points:
                    full_hough[peak[0]][peak[1]][0] = 255
                cv2.imwrite("analysis/%s" % self.filename, full_hough)
                return 0





                threshold = int( numpy.percentile(hough, 99.8))
                output_value = 255 # output white (otherwise black)
                _, hough = cv2.threshold(hough,
                                         threshold,
                                         output_value,
                                         cv2.THRESH_BINARY)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
                hough = cv2.morphologyEx(hough, cv2.MORPH_OPEN, kernel)
                #hough = cv2.imread("hough/%s" % self.filename)
                #hough = cv2.cvtColor(hough, cv2.COLOR_BGR2GRAY)

                hough = numpy.transpose(hough)
                row_sums = sum(line for line in hough).tolist()
                split = 0 - row_sums.index(0)
                hough = numpy.roll(hough, split)

                contours, h =  cv2.findContours(hough, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(hough, contours, -1, 127)
                #print len(contours)
                # Set up the detector with default parameters.
                #detector = cv2.SimpleBlobDetector()
                 
                # Detect blobs.
                #keypoints = detector.detect(hough)
                #print keypoints

                # Draw detected blobs as red circles.
                # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
                #im_with_keypoints = cv2.drawKeypoints(hough, keypoints, numpy.array([]), 127, cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                   

                cv2.imwrite("analysis/%s" % self.filename, hough)

                self.drawing = len(contours)
            return self._drawing

    def _get_hough_transform(self, straighten=False):
        """
        Return Hough transform accumulator array for the prepared image.
        Use straightened accumulator for easier analysis, or the default
        unstraightened for display.
        #full_hough = numpy.concatenate((hough, numpy.fliplr(hough)))
        to generate 360 degree representation
        """
        image = self.prepared
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        #cv2.imshow("", image)
        #cv2.waitKey(0)

        height, width = image.shape[:2]

        centre_x = width/2
        centre_y = height/2
        if straighten:
            # use centre of mass of image as the centre for the
            # Hough transform to reduce skew
            moments = cv2.moments(image, binaryImage=True)
            centre_x = int(moments['m10']/moments['m00'])
            centre_y = int(moments['m01']/moments['m00'])

        # max distance from centre point to a possible pixel gives
        # the required size of the accumulator array
        max_x = max(centre_x, width-centre_x)
        max_y = max(centre_y, height-centre_y)

        accumulator_width = math.ceil(math.sqrt((max_x**2) + (max_y**2))) * 2
        accumulator = numpy.zeros((180, accumulator_width, 1), numpy.uint8)

        for theta_deg in xrange(-90, 90):
            theta_rad = math.radians(theta_deg)
            cos_theta = math.cos(theta_rad)
            sin_theta = math.sin(theta_rad)
            # convert image to sparse array
            for (pixel_y, pixel_x) in numpy.transpose(numpy.nonzero(image)):
                # get location relative to centre point
                pixel_x -= centre_x
                pixel_y -= centre_y
                rho = math.floor((pixel_x*cos_theta) + (pixel_y*sin_theta))
                rho += accumulator_width / 2
                #if accumulator[theta_deg - 90][rho] == 255:
                #    print "exceeded limit"
                #    ... didn't happen from sample data
                accumulator[theta_deg - 90][rho] += 1
        
        cv2.normalize(accumulator, accumulator, 0, 255, cv2.NORM_MINMAX)
        return accumulator
