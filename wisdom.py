"""
Represents one item of wisdom and its analysis.
"""

import math
import cv2
import os

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

        # tuning
        self._angle_resolution = 5
        # levelling_width chosen by trial and error over sample wisdom, gets 94%
        self._levelling_width = 85 

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
        if self._original == None:
            self._original = cv2.imread(self.filepath)
        return self._original

    @property
    def prepared(self):
        """
        Original image greyscaled, shrunk, inverted and thresholded.
        Result: a white-on-black version ready for further processing.
        """
        if self._prepared == None:
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
        if self._best_angle == None:
            best_angle = 0
            smallest_ink_area = None
           
            # only 180 degrees needed, results will repeat after that 
            for angle in xrange(0, 180, self._angle_resolution):
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
                                                    (self._levelling_width,1))
                image = cv2.dilate(image, element)

                ink_area = sum([sum(row) / 255 for row in image])
                if not smallest_ink_area or ink_area < smallest_ink_area:
                    smallest_ink_area = ink_area
                    best_angle = angle

            self._best_angle = best_angle
        return self._best_angle

    @property
    def prepared_rotated(self):
        """
        Return the prepared image, rotated to the best angle
        """
        if self._prepared_rotated == None:
            self._prepared_rotated = self._rotate(self.best_angle)
        return self._prepared_rotated
   

