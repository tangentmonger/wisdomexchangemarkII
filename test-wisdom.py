import unittest
import os
import glob
import cv2

from wisdom import Wisdom
from expected import expected

TEST_DATA = "sample_wisdom" # contains 100 wisdom samples

#optimisations
#TODO: try otsu's binarisation instead of hardcoded thresholds
#TODO: try hough transform to get the levelling angle

class TestWisdom(unittest.TestCase):

    def test_checks_input(self):
        pattern = os.path.join(TEST_DATA, "*.jpeg")
        filepaths = glob.glob(pattern)
        wisdom_ok = Wisdom(filepaths[0])
        self.assertIsNotNone(wisdom_ok)

        with self.assertRaises(IOError):
            wisdom_bad = Wisdom("no_such.file.jpeg")

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

        print "Levelled %d out of %d textual wisdom" % (successes, texts)
        self.assertGreaterEqual(int(float(successes)/texts * 100), 94) # 94% success rate is the best so far

    def preload_prepared_rotated_image(self, wisdom):
        """
        Manage pre-generated levelled wisdom, for testing speed
        """
        prepared_filename = "prepared_rotated/%s" % wisdom.filename
        if os.path.isfile(prepared_filename):
            # load existing levelled wisdom
            image = cv2.imread("prepared_rotated/%s" % wisdom.filename)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            wisdom.prepared_rotated = image
        else:
            # generate and save for next time
            cv2.imwrite(prepared_filename, wisdom.prepared_rotated)

    def test_line_detection(self):
        """
        Check that line detection works with reasonable accuracy.
        """
        successes = 0
        near = 0
        tested =0
        import glob, os

        filelist = glob.glob("failures/*.jpeg")
        for f in filelist:
            os.remove(f)

        pattern = os.path.join(TEST_DATA, "*.jpeg")
        filepaths = sorted(glob.glob(pattern))
        for filepath in filepaths[0:10]:
            wisdom = Wisdom(filepath)
            self.preload_prepared_rotated_image(wisdom)
            tested +=1
            answer = expected[wisdom.filename]
            #print "Testing %s" % wisdom.filename
            if wisdom.lines == answer.lines:
                successes += 1
                print "%s: PASS\t%f%%\t%d" % (wisdom.filename, float(successes)/tested*100, answer.lines)
            elif answer.lines > 0 and abs(answer.lines - wisdom.lines) == 1:
                near += 1
                print "%s: NEAR\t%f%%\t%d" % (wisdom.filename, float(successes+near)/tested*100, wisdom.lines )
            else:
                print "%s: FAIL\t%f%%\t(expected %d, actual %d)" % (wisdom.filename, float(successes)/tested*100, answer.lines, wisdom.lines )
                cv2.imwrite("failures/%s" % wisdom.filename, wisdom.prepared_rotated)

        print "Detected lines in %d out of %d wisdom" % (successes, len(filepaths))
        print "Nearly detected lines in %d out of %d wisdom" % (near, len(filepaths))
        print "Failed: %d out of %d wisdom" % ((len(filepaths) - near - successes), len(filepaths))

        self.assertGreaterEqual(int(float(successes+near)/len(filepaths) * 100), 94) 



if __name__ == '__main__':
    unittest.main()
