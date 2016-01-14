import cProfile
import pstats
from wisdom import Wisdom

w = Wisdom("sample_wisdom/wisdom-0000.jpeg")

cProfile.run("w._get_hough_transform()", "profile.dat")

p = pstats.Stats("profile.dat")
p.sort_stats('time').print_stats()
#p.print_callees(Wisdom._get_hough_transform)


