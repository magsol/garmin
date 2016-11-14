Garmin
======

Let's face it: Garmin Connect doesn't have the most exquisite statistics to slice up your running data. This is an attempt to bridge that gap between the raw data and seeing the long (and possibly short) term trends.

Ultimately I'd like to make this into a web service, but it depends *entirely* on Garmin Connect's website: if they change how forms are submitted, the data-scraping portion of this service will break until I can refactor my scripts to emulate it again.

Quickstart
----------

To download all your Garmin workouts in TCX format (basically XML), perform the following steps:

(**This should work in either Python 2 or Python 3.**)

 1. Download the `download.py` file, either by checking out the repository, downloading the ZIP archive, or by literally copy/pasting the text into a file.
 2. Make sure you have the `mechanize` Python package installed; instructions to do so are below (though this will hopefully be replaced very soon).
 3. Run the command:

    python download.py -u your_garmin_username

 When prompted for your password, type it in (it won't be saved), and within a few seconds you should see your activities being downloaded!

 Alternatively, you can also set up a CSV file with only 1 line that looks like this:

    your_garmin_username,your_garmin_password

 Let's say you saved that file with the name `garmin_login.csv`. Then run the following command:

    python download.py -c garmin_login.csv

 Again, you should see activities downloading in a few seconds.

If you run into any problems, please create a ticket!

Packages
--------

If any of the following packages require dependencies, they will be listed. To install these dependencies, you can use either your favorite package manager, or install `pip` and run:

    pip install package

 - **download.py**: A script for downloading all Garmin Connect data as TCX files for offline parsing. *Dependencies: mechanize*

 - **monthly.py**: A script for updating one's Twitter account with monthly statistics. Currently, the statistics and format are identical to those seen on [DailyMile](http://www.dailymile.com) for their weekly statistics. I just thought it'd be neat to have monthly updates, too. *Dependencies: tweepy, mechanize*