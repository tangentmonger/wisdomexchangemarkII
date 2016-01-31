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

Step 3: decide whether this wisdom comprises text, an image or both. On this branch, try it with a straightened Hough transform:

![Accumulator array](https://raw.githubusercontent.com/tangentmonger/wisdomexchangemarkII/cascade_classifier/full_hough/wisdom-0047.jpeg)

This transform reveals a lot of information. Peak blobs in a row are probably lines of text, the y component gives the most level angle, tiny peaks are probably lines, images create a mess of peaks (or no particular peaks). Then use Haar feature cascade classifier to identify those peak blobs. 

    python generate_positive.py -i full_hough/
    rm stage*
    opencv_createsamples  -info info.dat -vec positive_vector.dat -show
    opencv_traincascade -data ./ -vec positive_vector.dat -bg bg.txt -numPos 22 -numNeg 10 -numStages 12 -minHitRate 0.900

    match numPos and numNeg to info.dat and bg.txt respectively
    what do all the other parameters actually do?

    Image detection in 76 out of 100 wisdom
    Image detection: 14 out of 23
    Nonimage detection: 62 out of 77

generate_positive.py is a quick and dirty tool to assist with generating the positive example metadata (e.g. info.dat) for training OpenCV cascade classifiers. Go through images and drag or shift-drag to select areas of interest. (x to undo a selection, n and p for next/previous image). Hit Enter when complete. The resulting data file can be passed in to the opencv_traincascade utility.


Build
-----

Travis CI status: [![Travis CI status](https://travis-ci.org/tangentmonger/wisdomexchangemarkII.svg?branch=master)](https://travis-ci.org/tangentmonger/wisdomexchangemarkII)

Requires OpenCV v2.4, which is a bit of a faff to install. See [.travis.yml](https://github.com/tangentmonger/wisdomexchangemarkII/blob/master/.travis.yml) for one way of doing it. (So far I am not using any of OpenCV's specific features; it might be possible to convert to PIL which is easier to install.)
