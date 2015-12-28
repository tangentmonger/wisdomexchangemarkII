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

Step 2: level it. The approach here is to stretch out each pixel horizontally and record the resulting area, then rotate the image a few degrees and try again, and so on. When the lines of text are level, the area is smallest. This approach correctly levels about 95% of textual wisdom. It fails on images (which is fine), and on text where the lines are closer together than the letters. It is slower than I would like because image rotation is costly. Levelled wisdom is sometimes upside down because this algorithm has no way to distinguish text orientation, but for my purposes that's ok.

![Levelling in action](https://raw.githubusercontent.com/tangentmonger/wisdomexchangemarkII/master/levelling.gif "Levelling in action")

Step 3: count the number of lines. Summing the amount of ink on each line produces a characteristic peak for each line. Identifying these peaks is in progress. 

Build
-----

Travis CI status: [![Travis CI status](https://travis-ci.org/tangentmonger/wisdomexchangemarkII.svg?branch=master)](https://travis-ci.org/tangentmonger/wisdomexchangemarkII))

Requires OpenCV v2.4, which is a bit of a faff to install. See [.travis.yml](https://github.com/tangentmonger/wisdomexchangemarkII/blob/master/.travis.yml) for one way of doing it.
