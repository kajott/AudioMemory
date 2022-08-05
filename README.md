Audio Memory
============

A simple HTML5-based memory game with a twist: instead of images, the players
need to match short audio samples.
Supports various board sizes (3x3 to 10x10) and 1 to 8 players.

The source code release uses a "bring your own samples" principle;
see [the README file in the _rawsamples subdirectory](_rawsamples/README.md)
for details. Python 3.5 (or later) and somewhat recent [FFmpeg](https://ffmpeg.org) binaries somewhere in the `PATH` are required to run the [process_samples.py](process_samples.py) tool, which converts the raw samples into their final format (MP3). [ReplayGain](https://wiki.hydrogenaud.io/index.php/ReplayGain) Volume normalization is also performed during this process, in order to minimize perceived volume differences between samples.

Written using [Vanilla JS](http://vanilla-js.com). <br>
Tested on Chromium-based browsers, Firefox, and various Android browsers. <br>
Doesn't need any "allow file access from files"-like shenanigans when run from disk. <br>
MIT-licensed.
