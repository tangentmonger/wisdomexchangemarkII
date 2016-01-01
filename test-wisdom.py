import unittest
import os
import glob
import cv2

from wisdom import Wisdom
from expected import expected

TEST_DATA = "sample_wisdom" # contains 100 wisdom samples

class TestWisdom(unittest.TestCase):

    sample_wisdom = []

    @classmethod
    def setUpClass(cls):
        """
        Load sample wisdom.
        """
        pattern = os.path.join(TEST_DATA, "*.jpeg")
        filepaths = sorted(glob.glob(pattern))
        for filepath in filepaths:
            cls.sample_wisdom.append(Wisdom(filepath))
        cls.sample_wisdom.sort(key=lambda x: expected[x.filename].lines)

    def test_best_angle(self):
        """
        Check that sample wisdom can be levelled reasonably accurately.
        """
        self.fail()
        tolerance = 5 # degrees
        texts = 0
        successes = 0
        for wisdom in self.sample_wisdom:
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
                    successes += 1
                else:
                    print "Failed to level wisdom %s (expected %d, actual %d, diff %d, image: %s, blank: %s" % (wisdom.filename, expected_angle, actual_angle, difference, answer.image, answer.blank)
                    #cv2.imwrite("failures/%s" % wisdom.filename, wisdom.prepared_rotated)

        print "Levelled %d out of %d textual wisdom" % (successes, texts)
        self.assertGreaterEqual(int(float(successes)/texts * 100), 94) # 94% success rate is the best so far

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

        for wisdom in self.sample_wisdom:
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

        print "Detected lines in %d out of %d textual wisdom" % (successes, len(self.sample_wisdom))
        print "Nearly detected lines in %d out of %d textual wisdom" % (near, len(self.sample_wisdom))
        print "Failed: %d out of %d textual wisdom" % ((len(self.sample_wisdom) - near - successes), len(self.sample_wisdom))

        self.assertGreaterEqual(int(float(successes+near)/len(self.sample_wisdom) * 100), 94) 


if __name__ == '__main__':
    unittest.main()
