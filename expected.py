
class Expected():
    """
    Store expected analysis results for pieces of Wisdom.
    """

    def __init__(self, text_angle=0, image=False, lines=0):
        self.text_angle = text_angle # what angle is the wisdom written at?
        self.image = image # does it contain an image?
        self.lines = lines # how many lines of text are there?

    @property
    def blank(self):
        return (self.image==False and self.lines==0)

expected = {}
expected["wisdom-0000.jpeg"] = Expected(text_angle=0, image=False, lines=6)
expected["wisdom-0001.jpeg"] = Expected(text_angle=0, image=True, lines=2)
expected["wisdom-0002.jpeg"] = Expected(image=True)
expected["wisdom-0003.jpeg"] = Expected(image=True)
expected["wisdom-0004.jpeg"] = Expected(image=True)
expected["wisdom-0005.jpeg"] = Expected(text_angle=0, image=False, lines=1)
expected["wisdom-0006.jpeg"] = Expected(text_angle=12, image=False, lines=1)
expected["wisdom-0007.jpeg"] = Expected(text_angle=0, image=False, lines=4)
expected["wisdom-0008.jpeg"] = Expected(text_angle=0, image=False, lines=4)
expected["wisdom-0009.jpeg"] = Expected(text_angle=0, image=False, lines=2)
expected["wisdom-0010.jpeg"] = Expected(text_angle=-3, image=False, lines=3)
expected["wisdom-0011.jpeg"] = Expected(text_angle=0, image=False, lines=3)
expected["wisdom-0012.jpeg"] = Expected(text_angle=0, image=False, lines=6)
expected["wisdom-0013.jpeg"] = Expected(text_angle=12, image=False, lines=4)
expected["wisdom-0014.jpeg"] = Expected(text_angle=0, image=False, lines=3)
expected["wisdom-0015.jpeg"] = Expected(text_angle=10, image=False, lines=2)
expected["wisdom-0016.jpeg"] = Expected(text_angle=0, image=False, lines=5)
expected["wisdom-0017.jpeg"] = Expected(text_angle=5, image=False, lines=2)
expected["wisdom-0018.jpeg"] = Expected(text_angle=0, image=False, lines=6)
expected["wisdom-0019.jpeg"] = Expected(text_angle=5, image=False, lines=3)
expected["wisdom-0020.jpeg"] = Expected(text_angle=5, image=False, lines=3)
expected["wisdom-0021.jpeg"] = Expected(text_angle=0, image=False, lines=3)
expected["wisdom-0022.jpeg"] = Expected(text_angle=0, image=False, lines=5)
expected["wisdom-0023.jpeg"] = Expected(text_angle=0, image=False, lines=2)
expected["wisdom-0024.jpeg"] = Expected(text_angle=5, image=False, lines=4)
expected["wisdom-0025.jpeg"] = Expected(text_angle=90, image=False, lines=3)
expected["wisdom-0026.jpeg"] = Expected(text_angle=90, image=False, lines=10)
expected["wisdom-0027.jpeg"] = Expected(image=True)
expected["wisdom-0028.jpeg"] = Expected(text_angle=90, image=False, lines=5)
expected["wisdom-0029.jpeg"] = Expected(text_angle=0, image=False, lines=2)
expected["wisdom-0030.jpeg"] = Expected(text_angle=10, image=False, lines=2)
expected["wisdom-0031.jpeg"] = Expected(text_angle=5, image=False, lines=4)
expected["wisdom-0032.jpeg"] = Expected(text_angle=-85, image=True, lines=5)
expected["wisdom-0033.jpeg"] = Expected(text_angle=-90, image=True, lines=3)
expected["wisdom-0034.jpeg"] = Expected(text_angle=0, image=False, lines=2)
expected["wisdom-0035.jpeg"] = Expected()
expected["wisdom-0036.jpeg"] = Expected(text_angle=0, image=False, lines=3)
expected["wisdom-0037.jpeg"] = Expected(text_angle=5, image=False, lines=2)
expected["wisdom-0038.jpeg"] = Expected(text_angle=90, image=False, lines=14)
expected["wisdom-0039.jpeg"] = Expected(text_angle=5, image=False, lines=7)
expected["wisdom-0040.jpeg"] = Expected(text_angle=5, image=False, lines=3)
expected["wisdom-0041.jpeg"] = Expected(text_angle=90, image=False, lines=8)
expected["wisdom-0042.jpeg"] = Expected(text_angle=120, image=False, lines=9)
expected["wisdom-0043.jpeg"] = Expected(text_angle=90, image=False, lines=5)
expected["wisdom-0044.jpeg"] = Expected(text_angle=10, image=False, lines=5)
expected["wisdom-0045.jpeg"] = Expected(text_angle=-90, image=False, lines=5)
expected["wisdom-0046.jpeg"] = Expected(text_angle=0, image=True, lines=4)
expected["wisdom-0047.jpeg"] = Expected(text_angle=47, image=False, lines=3)
expected["wisdom-0048.jpeg"] = Expected(image=True)
expected["wisdom-0049.jpeg"] = Expected(text_angle=0, image=False, lines=4)
expected["wisdom-0050.jpeg"] = Expected(text_angle=0, image=False, lines=3)
expected["wisdom-0051.jpeg"] = Expected(text_angle=5, image=True, lines=2)
expected["wisdom-0052.jpeg"] = Expected(text_angle=-90, image=True, lines=3)
expected["wisdom-0053.jpeg"] = Expected(image=True)
expected["wisdom-0054.jpeg"] = Expected(image=True)
expected["wisdom-0055.jpeg"] = Expected(image=True)
expected["wisdom-0056.jpeg"] = Expected(image=True)
expected["wisdom-0057.jpeg"] = Expected(text_angle=5, image=True, lines=2)
expected["wisdom-0058.jpeg"] = Expected(text_angle=0, image=True, lines=1)
expected["wisdom-0059.jpeg"] = Expected(text_angle=0, image=False, lines=2)
expected["wisdom-0060.jpeg"] = Expected(text_angle=0, image=False, lines=5)
expected["wisdom-0061.jpeg"] = Expected(text_angle=-3, image=False, lines=2)
expected["wisdom-0062.jpeg"] = Expected(text_angle=0, image=False, lines=1)
expected["wisdom-0063.jpeg"] = Expected(text_angle=90, image=False, lines=1)
expected["wisdom-0064.jpeg"] = Expected(text_angle=5, image=False, lines=3)
expected["wisdom-0065.jpeg"] = Expected(text_angle=0, image=False, lines=2)
expected["wisdom-0066.jpeg"] = Expected(text_angle=0, image=False, lines=4)
expected["wisdom-0067.jpeg"] = Expected(text_angle=0, image=False, lines=2)
expected["wisdom-0068.jpeg"] = Expected(text_angle=5, image=False, lines=4)
expected["wisdom-0069.jpeg"] = Expected(text_angle=10, image=True, lines=3)
expected["wisdom-0070.jpeg"] = Expected(text_angle=-1, image=False, lines=2)
expected["wisdom-0071.jpeg"] = Expected(text_angle=16, image=False, lines=2)
expected["wisdom-0072.jpeg"] = Expected()
expected["wisdom-0073.jpeg"] = Expected(text_angle=0, image=True, lines=2)
expected["wisdom-0074.jpeg"] = Expected(text_angle=0, image=False, lines=3)
expected["wisdom-0075.jpeg"] = Expected(text_angle=0, image=False, lines=5)
expected["wisdom-0076.jpeg"] = Expected(text_angle=5, image=False, lines=5)
expected["wisdom-0077.jpeg"] = Expected()
expected["wisdom-0078.jpeg"] = Expected(text_angle=0, image=False, lines=3)
expected["wisdom-0079.jpeg"] = Expected(image=True)
expected["wisdom-0080.jpeg"] = Expected(text_angle=0, image=False, lines=3)
expected["wisdom-0081.jpeg"] = Expected(text_angle=0, image=False, lines=4)
expected["wisdom-0082.jpeg"] = Expected(text_angle=0, image=False, lines=3)
expected["wisdom-0083.jpeg"] = Expected(text_angle=0, image=True, lines=2)
expected["wisdom-0084.jpeg"] = Expected(text_angle=0, image=False, lines=1)
expected["wisdom-0085.jpeg"] = Expected(text_angle=0, image=False, lines=3)
expected["wisdom-0086.jpeg"] = Expected(text_angle=0, image=False, lines=4)
expected["wisdom-0087.jpeg"] = Expected(text_angle=0, image=False, lines=2)
expected["wisdom-0088.jpeg"] = Expected(text_angle=45, image=False, lines=2)
expected["wisdom-0089.jpeg"] = Expected(text_angle=0, image=False, lines=5)
expected["wisdom-0090.jpeg"] = Expected(text_angle=0, image=True, lines=3)
expected["wisdom-0090.jpeg"] = Expected(text_angle=0, image=True, lines=2)
expected["wisdom-0091.jpeg"] = Expected(text_angle=0, image=False, lines=1)
expected["wisdom-0092.jpeg"] = Expected(text_angle=30, image=False, lines=4)
expected["wisdom-0093.jpeg"] = Expected(text_angle=0, image=False, lines=3)
expected["wisdom-0094.jpeg"] = Expected(text_angle=0, image=False, lines=4)
expected["wisdom-0095.jpeg"] = Expected(text_angle=0, image=True, lines=3)
expected["wisdom-0096.jpeg"] = Expected(text_angle=15, image=False, lines=4)
expected["wisdom-0097.jpeg"] = Expected(text_angle=0, image=False, lines=5)
expected["wisdom-0098.jpeg"] = Expected(text_angle=30, image=False, lines=2)
expected["wisdom-0099.jpeg"] = Expected(text_angle=0, image=False, lines=2)

