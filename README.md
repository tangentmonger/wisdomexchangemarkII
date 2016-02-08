The Wisdom Exchange Mark II
===========================

The problem with the [Mark I Wisdom Exchange](https://github.com/tangentmonger/wisdomexchange) was that sometimes someone would put a lot of thought into their contribution, write something personal and meaningful, and receive a blank page or a crappy doodle. The Mark II aims to provide a better exchange experience.

In this version, the machine will scan new wisdom as it's pulled in, and analyse it for "wisdom content". Then it can select and print a matching piece of wisdom. 

If it were possible, I would love to run text recognition on the wisdom, figure out the topic and offer a related piece of wisdom. However, current text recognition libraries only work on printed text, not wildly different handwriting that even humans struggle to read sometimes. (If you know differently, please get in touch!) So instead, I want this machine to offer wisdom of a similar level of effort. If you wrote six lines, you get a different six-line wisdom back. Write one line, get one line. Draw a doodle, get a doodle. (Write nothing, receive mockery.)

Complications: people write in different styles, at different angles, mix text and images, go off the edge of the page, use different pens...

Analysis
--------

![Original wisdom](https://raw.githubusercontent.com/tangentmonger/wisdomexchangemarkII/master/levelling-before.jpeg)

Step 1: prepare the image for analysis. Convert it to a smaller, inverted, B&W image, with extra padding.

Step 2: check whether the image is blank, by summing the ink area. If it's less than the threshold (to allow for noise) the image contains no wisdom and analysis stops.

Step 3: level it. When the lines are level, and you stretch out each pixel horizontally and record the resulting ink area, the total is much smaller than when the lines are not level. So, search through different angles of rotation to find the minimum. This approach correctly levels about 95% of textual wisdom. It fails on images (which is fine), and on text where the lines are closer together than the letters. Levelled wisdom is sometimes upside down because this algorithm has no way to distinguish text orientation, but for my purposes that's ok.

![Levelling in action](https://raw.githubusercontent.com/tangentmonger/wisdomexchangemarkII/master/levelling.gif "Levelling in action")

Step 4: decide whether this wisdom comprises text, an image or both. Tried a few approaches on different branches:

* Sum the ink on each row and detect peaks. This works quite well for textual wisdom (and gives a count of the lines), but is poor for detecting images because they also generate peaks.

* Sum the ink on each row and column, and multiply together to give a spectrograph representation. Looks cool, and creates different areas for images and lines of text, but there's no clear way to analyse it from that point.

* Sum the ink on each row and differentiate it, and detect peaks in that. Works about as well as the first approach. Tried to detect images by the quality of the peaks, but this just misdetected textual wisdom.

* Sum the ink on each row and compare it to templates for 1-n lines. Not great because any noise in the image throws off the start/end points. Wouldn't work well for messy textual wisdom.

* Go back to the rotation stage and look for the sudden occurrence of clear peaks in the rotation data. If it doesn't show, this is probably an image. Not much use for differentiating single-line wisdom and compact images.

* Machine learning: no idea what I'm doing here. What features would distinguish text from images? Average line lengths, maybe? Enclosed areas? I probably don't have enough samples to train a neural network.

* ???

It doesn't matter too much if the line count is off by one (write one line, get two lines?) but I really want to distinguish images and text reliably.



Build
-----

Travis CI status: [![Travis CI status](https://travis-ci.org/tangentmonger/wisdomexchangemarkII.svg?branch=master)](https://travis-ci.org/tangentmonger/wisdomexchangemarkII)

Requires OpenCV v2.4, which is a bit of a faff to install. See [.travis.yml](https://github.com/tangentmonger/wisdomexchangemarkII/blob/master/.travis.yml) for one way of doing it. (So far I am not using any of OpenCV's specific features; it might be possible to convert to PIL which is easier to install.)
