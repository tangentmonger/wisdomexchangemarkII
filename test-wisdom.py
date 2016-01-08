import unittest
import os
import glob
import cv2
import time

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

    def test_detect_drawings(self):
        """
        Check that text and drawings can be distinguished with reasonable
        accuracy
        """
        successes = 0
        pattern = os.path.join(TEST_DATA, "*.jpeg")
        filepaths = sorted(glob.glob(pattern))
        for filepath in filepaths:
            wisdom = Wisdom(filepath)
            #answer = expected[wisdom.filename]
            #if answer and wisdom.drawing == answer.image:
            #    print "%s:\tPASS" % wisdom.filename
            #    successes += 1
            #else:
            #    #print "%s:\tFAIL\t(expected %s)" % (wisdom.filename, answer.image)
            #    print "%s:\tFAIL\t(expected %s)" % (wisdom.filename)
            print wisdom.filename
            wisdom.drawing
        print "Image detection in %d out of %d wisdom" % (successes, len(filepaths))
        self.assertGreaterEqual(int(float(successes)/len(filepaths) * 100), 77) #can get this with no code at all :(
        self.assertGreaterEqual(int(float(successes)/len(filepaths) * 100), 100)

    def test_compare_hough(self):
        pattern = os.path.join(TEST_DATA, "*.jpeg")
        filepaths = sorted(glob.glob(pattern))
        for filepath in filepaths:
            wisdom = Wisdom(filepath)
            old_start_time = time.time()
            old_result = wisdom._get_histogram_at_angles()
            old_time = time.time() - old_start_time
            new_start_time = time.time()
            new_result = wisdom._get_hough_transform()
            new_time = time.time() - new_start_time
            self.assertLess(new_time, old_time)
            self.assertEqual(old_result, new_result)

if __name__ == '__main__':
    unittest.main()
