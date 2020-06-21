Download Podcasts
=================

Script for my personal usage to download the newest podcast from the URLs specified
in `settings.PODCASTS` and store them to `settings.BASEPATH/YYYY-MM-DD` where `YYYY-MM-DD`
is the current date.

Used for my Aftershokz Xtrainerz bone conduction Swimming MP3 player for my long swim practices.

Each podcast is prepended by a spoken audio label which tells about the date and the title 
of the podcast.   

If the `-b` is set, Audio compression is applied to the Podcasts.

[FFMPEG](https://ffmpeg.org/) must be available in the path. 


