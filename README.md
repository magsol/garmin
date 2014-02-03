Garmin
======

Let's face it: Garmin Connect doesn't have the most exquisite statistics to slice up your running data. This is an attempt to bridge that gap between the raw data and seeing the long (and possibly short) term trends.

Ultimately I'd like to make this into a web service, but it depends *entirely* on Garmin Connect's website: if they change how forms are submitted, the data-scraping portion of this service will break until I can refactor my scripts to emulate it again.

Packages
--------

If any of the following packages require dependencies, they will be listed. To install these dependencies, you can use either your favorite package manager, or install `pip` and run:

    pip install package

 - **monthly.py**: A script for updating one's Twitter account with monthly statistics. Currently, the statistics and format are identical to those seen on [DailyMile](http://www.dailymile.com) for their weekly statistics. I just thought it'd be neat to have monthly updates, too. *Dependencies: tweepy, mechanize*