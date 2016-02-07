"""
Represents one item of wisdom and its analysis.
"""

import math
import cv2
import os

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

    def watershed(self):

        from scipy.ndimage import label

        def segment_on_dt(a, img):
            border = cv2.dilate(img, None, iterations=5)
            cv2.imwrite("analysis/border-%s" % self.filename, border)
            border = border - cv2.erode(border, None)
            cv2.imwrite("analysis/border2-%s" % self.filename, border)

            dt = cv2.distanceTransform(img, 2, 3)
            dt = ((dt - dt.min()) / (dt.max() - dt.min()) * 255).astype(numpy.uint8)
            _, dt = cv2.threshold(dt, 30, 255, cv2.THRESH_BINARY)
            print dt
            print dt.max()
            print dt.min()
            cv2.imwrite("analysis/dt-%s" % self.filename, dt)
            lbl, ncc = label(dt)
            print ncc
            lbl = lbl * (255/ncc)
            # Completing the markers now. 
            lbl[border == 255] = 255
            print lbl
            print lbl.max()

            lbl = lbl.astype(numpy.int32)
            cv2.watershed(a, lbl)

            lbl[lbl == -1] = 0
            lbl = lbl.astype(numpy.uint8)
            return 255 - lbl


        img = self.original
        kernel = numpy.ones((3,3),numpy.uint8)
        img = cv2.erode(img,kernel,iterations=5)
        cv2.imwrite("analysis/img-start-%s" % self.filename, img)

        # Pre-processing.
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        _, img_bin = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        cv2.imwrite("analysis/img-bin-%s" % self.filename, img_bin)
        img_bin = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, numpy.ones((3, 3), dtype=int))
        cv2.imwrite("analysis/img-bin2-%s" % self.filename, img_bin)

        result = segment_on_dt(img, img_bin)
        cv2.imwrite("analysis/result-%s" % self.filename, result)

        result[result != 255] = 0
        result = cv2.dilate(result, None)
        img[result == 255] = (0, 0, 255)
        cv2.imwrite("analysis/img-%s" % self.filename, img)

        return

        #ret, thresh = cv2.threshold(image,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        #ret, thresh = cv2.threshold(image,0,255,cv2.THRESH_BINARY)
        thresh = image

        # noise removal
        kernel = numpy.ones((3,3),numpy.uint8)
        #opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)

        opening = image

        # sure background area
        sure_bg = cv2.dilate(opening,kernel,iterations=3)

        # Finding sure foreground area
        dist_transform = cv2.distanceTransform(opening,cv2.cv.CV_DIST_L2,5)
        ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)

        # Finding unknown region
        sure_fg = numpy.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg,sure_fg)
             

        cv2.imwrite("analysis/sure_bg-%s" % self.filename, sure_bg)
        cv2.imwrite("analysis/sure-fg-%s" % self.filename, sure_fg)
        cv2.imwrite("analysis/unknown-%s" % self.filename, unknown)

        # Marker labelling
        ret, markers = cv2.connectedComponents(sure_fg)

        # Add one to all labels so that sure background is not 0, but 1
        markers = markers+1

        # Now, mark the region of unknown with zero
        markers[unknown==255] = 0

        markers = cv2.watershed(image,markers)
        image[markers == -1] = [255,0,0]
        cv2.imwrite("analysis/result-%s" % self.filename, image)
