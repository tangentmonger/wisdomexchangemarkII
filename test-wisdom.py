import unittest
import os
import glob
import cv2
import time
import numpy

from wisdom import Wisdom
from expected import expected

TEST_DATA = "sample_wisdom" # contains 100 wisdom samples
TEST_DATA_SUBSAMPLE = "sample_wisdom_subsample" # contains 13 labelled wisdom samples

class TestWisdom(unittest.TestCase):

    def test_best_angle(self):
        """
        Check that sample wisdom can be levelled reasonably accurately.
        """
        tolerance = 5 # degrees
        texts = 0
        successes = 0
        pattern = os.path.join(TEST_DATA, "*.jpeg")
        filepaths = sorted(glob.glob(pattern))
        for filepath in filepaths:
            wisdom = Wisdom(filepath)
            answer = expected[wisdom.filename]
            print "Testing %s" % wisdom.filename

            actual_angle = wisdom.best_angle
            expected_angle = (answer.text_angle * -1) # * -1 because they are the opposite

            difference = abs(actual_angle - expected_angle)
            if difference > 90: # upside down is fine as long as it's level
                difference = abs(difference - 180)

            if answer.lines > 0:
                texts += 1
                if difference <= tolerance: 
                    print "%s:\tPASS" % wisdom.filename
                    successes += 1
                else:
                    print "%s\tFAIL\t(expected %d, actual %d, diff %d, image: %s, blank: %s" % (filepath, expected_angle, actual_angle, difference, answer.image, answer.blank)
                    #cv2.imwrite("failures/%s" % wisdom.filename, wisdom.prepared_rotated)

        print "Levelled %d out of %d textual wisdom" % (successes, texts)
        self.assertGreaterEqual(int(float(successes)/texts * 100), 94) # 94% success rate is the best so far

    def test_detect_blanks(self):
        """
        Check that blank wisdom is detected.
        """
        successes = 0
        pattern = os.path.join(TEST_DATA, "*.jpeg")
        filepaths = sorted(glob.glob(pattern))
        for filepath in filepaths:
            wisdom = Wisdom(filepath)
            answer = expected[wisdom.filename]
            if wisdom.blank == answer.blank:
                print "%s:\tPASS" % wisdom.filename
                successes += 1
            else:
                print "%s:\tFAIL\t(expected %s)" % (wisdom.filename, answer.blank)
        print "Blank detection in %d out of %d wisdom" % (successes, len(filepaths))
        self.assertGreaterEqual(int(float(successes)/len(filepaths) * 100), 100)

    def test_hough_transforms(self):
        """
        Check that transforms work and accumulator is correctly sized.
        """
        wisdom = Wisdom("test_hough_input.jpg")
        default_accumulator = wisdom._get_hough_transform()
        d_height, d_width = default_accumulator.shape[:2]
        self.assertEqual(d_height, 360)
        straight_accumulator = wisdom._get_hough_transform(straighten=True)
        s_height, s_width = straight_accumulator.shape[:2]
        self.assertEqual(s_height, 360)
        self.assertGreater(s_width, d_width)

    def test_detect_drawings(self):
        """
        Check that text and drawings can be distinguished with reasonable
        accuracy
        """
        successes = 0
        images = 0
        nonimages = 0
        image_successes = 0
        image_fails = 0
        nonimage_successes = 0
        nonimage_fails = 0
        pattern = os.path.join(TEST_DATA, "*.jpeg")
        filepaths = sorted(glob.glob(pattern))
        #for filepath in filepaths[70:]:
        #    wisdom = Wisdom(filepath)
        #    if not wisdom.blank:
        #        hough = wisdom._get_hough_transform(straighten=True)
        #        cv2.imwrite("full_hough/%s" % wisdom.filename, hough)
        #self.fail()

        for filepath in filepaths:
            wisdom = Wisdom(filepath)
            answer = expected[wisdom.filename]
            if answer:
                if wisdom.drawing == answer.image:
                    print "%s:\tPASS" % wisdom.filename
                    successes += 1
                    if answer.image:
                        images +=1
                        image_successes += 1
                    else:
                        nonimages += 1
                        nonimage_successes += 1
                else:
                    print "%s:\tFAIL\t(expected %s)" % (wisdom.filename, answer.image)
                    if answer.image:
                        images +=1
                    else:
                        nonimages += 1
        print "Image detection in %d out of %d wisdom" % (successes, len(filepaths))
        print "Image detection: %s out of %s" % (image_successes, images)
        print "Nonimage detection: %s out of %s" % (nonimage_successes, nonimages)
        self.assertGreaterEqual(int(float(successes)/len(filepaths) * 100), 77) #can get this with no code at all :(
        self.assertGreaterEqual(int(float(successes)/len(filepaths) * 100), 100)


if __name__ == '__main__':
    unittest.main()
