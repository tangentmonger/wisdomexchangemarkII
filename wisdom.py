"""
Represents one item of wisdom and its analysis.
"""

import math
import cv2
import os
from scipy import optimize
#from numpy import *
import numpy
import re

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
        self._lines = None

        # tuning
        self._angle_resolution = 5
        # levelling_width chosen by trial and error over sample wisdom, gets 94%
        self._levelling_width = 85
        self._smoothing = 5

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
            ink_areas = {}
            search_start = 0
            search_end = 180
            sample_distance = 30 # searches
            best_angle = 0

            while sample_distance > self._angle_resolution:
                for angle in xrange(search_start, search_end, sample_distance):
                    if angle not in ink_areas:
                        ink_areas[angle] = self._get_area_for_levelling(angle % 180)

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
                                            (self._levelling_width,1))
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
    def lines(self):
        if self._lines == None:
            image = self.prepared_rotated

            #get smoothed ink data
            self._smoothing = 5

            horizontal_ink = [sum(row) / 255 for row in image]
            smoothed = [0]*self._smoothing + [sum(horizontal_ink[index - self._smoothing: index+self._smoothing]) / (self._smoothing*2) for index in xrange(self._smoothing, len(horizontal_ink) - self._smoothing)] + [0]*self._smoothing
            #smoothed= horizontal_ink

            ##remove lower portion
            #smoothed_r = [x-threshold if x>threshold else 0 for x in smoothed]
            #smoothed = smoothed_r
            #
            ##trim
            threshold = int(max(smoothed) / 4)
            start = 0
            while smoothed[start] < threshold:
                start += 1
            while int(smoothed[start]) > 0:
                start -= 1

            end = len(smoothed) - 1
            while smoothed[end] < threshold:
                end -= 1
            while int(smoothed[end]) > 0:
                end += 1


            #for row, amount in enumerate(smoothed):
            #    if int(amount) > 0:
            #        #cv2.line(image, (0,row), (int(amount), row), 127, 1)
            #        pass

            #cv2.line(image, (0, start), (300, start), 255, 1)
            #cv2.line(image, (0, end), (300, end), 255, 1)
            # detour: detect blanks first and factor that in to this
            # looks like there are 60 wisdoms that line detect easily, then the rest...
            # given suspected peaks, try to fit gaussians there, check difference...?
            # use troughs also? must be a zigzag
            self._lines = 0

            

            data = smoothed[start:end]

            d_data = [data[x+1] - data[x] for x in xrange(0, len(data)-1)]
            #print [d_data[x+1] - d_data[x] for x in xrange(0, len(d_data)-1)]
            #5, 0 -> 52
            #5, 1 -> 64
            #5, 2 -> 60 
            #6, 1 -> 63
            #6, 2 -> 55
            #7, 1 -> 57 
            smoothing = 1
            #smoothed_d_data = d_data
            smoothed_d_data =  [sum(d_data[index - smoothing: index+smoothing]) / (smoothing*2) for index in xrange(smoothing, len(d_data) - smoothing)] + [0]*smoothing
            #smoothed_d_data = filter(lambda x: x != 0, smoothed_d_data)


            text = "".join(["U" if amount>0 else "D" if amount<0 else "0" for amount in smoothed_d_data])

            #print text
            for row, amount in enumerate(smoothed_d_data):
                #cv2.line(image, (0,start+row), (20+(int(amount) * 5), start +row), 255 if amount>0 else 160, 1)
                cv2.line(image, (0,start+row), (20, start +row), 255 if amount>0 else 160 if amount<0 else 0, 1)

            #print smoothed_d_data
            #print len(filter(lambda x:x>0, smoothed_d_data)) - len(filter(lambda x:x<0, smoothed_d_data))
            #max_infill = 3
            n = 5

            matches = re.findall("U+0*D+", text)
            #matches = re.findall("U*0{,3}U+0*D+0{,3}D*", text)
            if not matches:
                self._lines = 0
            else:
                #print "\n".join(matches)
                # remove matches that are too short to be lines)
                #matches = filter(lambda x: len(x) > 10, matches)
                # remove matches with more 0 than U or D
                #matches = filter(lambda x: x.count("U") >= x.count("0"), matches)
                #matches = filter(lambda x: x.count("D") >= x.count("0"), matches)
                #66% - 20 - 14
                #more 0 than U and D combined
                #65 - 22 - 13
                #matches = filter(lambda x: x.count("D") + x.count("U") >= x.count("0"), matches)
                #lengths = sorted([len(x) for x in matches])
                #if min(lengths[0], lengths[-1]) / max(lengths[0], lengths[-1]) > 0.5:
                #    self._lines = 0
                #else:
                leftover = len(text) - sum([len(match) for match in matches])
                print leftover
                print float(leftover) / len(text)

                self._lines = len(matches)
            
                if (float(leftover) / len(text)) > 0.7:
                    self._lines = 0

            

            #crossings = 0
            #for x in xrange(0, len(smoothed_d_data) - 1):
            #    if smoothed_d_data[x] > 0 and smoothed_d_data[x+1] < 0:
            #        crossings += 1

            #self._lines = crossings

            #if sum(horizontal_ink) < 100:
            #    self._lines = 0

            #print "len(data): %d" % len(data)
            #height = max(data)
           
            #differences = []

            #min_line_height = 20

            #max_possible_lines = int(len(data) / min_line_height)
            #for n in xrange(1, max_possible_lines + 1):
            #    difference = 0
            #    peak_length = int(float(len(data) - 1) / n)
            #    for peak in xrange(0, n):
            #        peak_start = peak_length * peak
            #        for x in xrange(0, peak_length / 2):
            #            model_height = int((float(x) / (peak_length/2)) * height)
            #            #cv2.circle(image, (model_height, start+peak_start + x), 0, 255)
            #            line_difference = abs(model_height - data[peak_start+x])
            #            difference += line_difference
            #        for x in xrange(0, peak_length / 2):
            #            model_height = int((1.0-(float(x) / (peak_length/2))) * height)
            #            #cv2.circle(image, (model_height, start+peak_start + (peak_length/2)+ x), 0, 255)
            #            #total difference
            #            line_difference = abs(model_height - data[peak_start+(peak_length/2)+x])
            #            #real data that is not covered
            #            #line_difference = data[peak_start+(peak_length/2)+x] - model_height
            #            #line_difference = line_difference if line_difference > 0 else 0
            #            difference += line_difference
            #    print "\t%d peaks: %d" % (n, difference)
            #    differences.append(difference)
            #self._lines = differences.index(min(differences)) + 1
            #print "lines: %d" % self._lines
            #    
            #peak = self._lines
            #peak_length = int(float(len(data) - 1) / peak)
            #for peak in xrange(0, peak):
            #    peak_start = peak_length * peak
            #    for x in xrange(0, peak_length / 2):
            #        model_height = int((float(x) / (peak_length/2)) * height)
            #        cv2.circle(image, (model_height, start+peak_start + x), 0, 255)
            #        line_difference = abs(model_height - data[peak_start+x])
            #        difference += line_difference
            #    for x in xrange(0, peak_length / 2):
            #        model_height = int((1.0-(float(x) / (peak_length/2))) * height)
            #        cv2.circle(image, (model_height, start+peak_start + (peak_length/2)+ x), 0, 255)


            #data = smoothed[start:-end]
            #print len(data)
            #if len(data) > 0:
            #    fft_results = numpy.fft.fft(data)
            #    print fft_results
            #    self._lines = int(fft_results[1].imag / len(data))
            #else:
            #    self._lines = 0



            #from detect_peaks import detect_peaks
            #self._lines = 0
            ##detect peaks
            #min_line_height = 15
            #if len(smoothed) > 0:
            #    threshold = max(smoothed) / 4
            #    #threshold = 0

            #    peaks = list(detect_peaks(smoothed, mph=threshold, mpd=min_line_height, edge="both"))

            #    valleys = list(detect_peaks(smoothed, mph=-threshold, mpd=min_line_height, valley=True, edge="both"))
            #    valleys.append(start)
            #    #print valleys
            #    self._lines = len(peaks)
            #    
            #    #for peak in peaks:
            #        #cv2.circle(image, (int(smoothed[peak]), peak),3, 255, 1)
            #    #for valley in valleys:
            #        #cv2.circle(image, (int(smoothed[valley]), valley),3, 255, -1)

            #    #print sorted(valleys+peaks)
            #    #for peak in peaks:
            #        #print filter(lambda x: x<peak, valleys)
            #        #valley_before = sorted(filter(lambda x: x<peak, valleys))[-1]
            #        #valley_after = sorted(filter(lambda x: x>peak, valleys))[0]
            #        #print "%d - %d - %d" % (valley_before, peak, valley_after)



            #    self._lines = len(peaks)

            #fit curves

            # https://scipy.github.io/old-wiki/pages/Cookbook/FittingData
            #gaussian = lambda x: 3*exp(-(30-x)**2/20.)
            #data = array(smoothed[start:-end])
            #if len(data) > 10:
            #    X = arange(data.size)
            #    x = sum(X*data)/sum(data)
            #    width = sqrt(abs(sum((X-x)**2*data)/sum(data)))
            #    maximum = data.max()
            #    fit = lambda t : maximum*exp(-(t-x)**2/(2*width**2))
            #    #print fit(X)


            #    for row, amount in enumerate(fit(X)):
            #        cv2.line(image, (0,row+self._smoothing+start), (int(amount), row+self._smoothing+start), 255, 1)


            #    #ok so: guess at peaks and try to curve fit them, and examine fit quality.

            cv2.imwrite("analysis/%s" % self.filename, image)
        return self._lines

def func(x, y):
    return a * np.exp(-b * x) + c
