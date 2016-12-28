"""
This script was inspired from tmcw's Ruby script doing the same thing:

    https://gist.github.com/tmcw/1098861

And recent fixes implemented thanks to the login structure by wederbrand:

    https://github.com/wederbrand/workout-exchange/blob/master/garmin_connect/download_all.rb

The goal is to iteratively download all detailed information from Garmin Connect
and store it locally for further perusal and analysis. This is still very much
preliminary; future versions should include the ability to seamlessly merge
all the data into a single file, filter by workout type, and other features
to be determined.
"""

import argparse
from getpass import getpass
import json
import os
import re
import shutil
import sys
import urllib

import mechanicalsoup as me

BASE_URL = "http://connect.garmin.com/en-US/signin"
GAUTH = "https://connect.garmin.com/gauth/hostname"
SSO = "https://sso.garmin.com/sso"
CSS = "https://static.garmincdn.com/com.garmin.connect/ui/css/gauth-custom-v1.2-min.css"
REDIRECT = "https://connect.garmin.com/post-auth/login"
ACTIVITIES = "http://connect.garmin.com/proxy/activity-search-service-1.2/json/activities?start=%s&limit=%s"

TCX = "https://connect.garmin.com/modern/proxy/download-service/export/tcx/activity/%s"
GPX = "https://connect.garmin.com/modern/proxy/download-service/export/gpx/activity/%s"

def login(agent, username, password):
    global BASE_URL, GAUTH, REDIRECT, SSO, CSS

    # First establish contact with Garmin and decipher the local host.
    page = agent.get(BASE_URL)
    pattern = "\"\S+sso\.garmin\.com\S+\""
    script_url = re.search(pattern, page.text).group()[1:-1]
    agent.get(script_url)
    hostname_url = agent.get(GAUTH)
    hostname = json.loads(hostname_url.text)['host']

    # Package the full login GET request...
    data = {'service': REDIRECT,
        'webhost': hostname,
        'source': BASE_URL,
        'redirectAfterAccountLoginUrl': REDIRECT,
        'redirectAfterAccountCreationUrl': REDIRECT,
        'gauthHost': SSO,
        'locale': 'en_US',
        'id': 'gauth-widget',
        'cssUrl': CSS,
        'clientId': 'GarminConnect',
        'rememberMeShown': 'true',
        'rememberMeChecked': 'false',
        'createAccountShown': 'true',
        'openCreateAccount': 'false',
        'usernameShown': 'false',
        'displayNameShown': 'false',
        'consumeServiceTicket': 'false',
        'initialFocus': 'true',
        'embedWidget': 'false',
        'generateExtraServiceTicket': 'false'}

    # ...and officially say "hello" to Garmin Connect.
    login_url = 'https://sso.garmin.com/sso/login?%s' % urllib.parse.urlencode(data)
    login_page = agent.get(login_url)

    # Set up the login form.
    f = login_page.soup.select("#login-form")[0]
    f.input({"username": username, "password": password})

    # Submit the login!
    submission = agent.submit(f, login_page.url)
    if submission.text.find("Invalid") >= 0:
        quit("Login failed! Check your credentials, or submit a bug report.")
    elif submission.text.find("SUCCESS") >= 0:
        print('Login successful! Proceeding...')
    else:
        quit('UNKNOWN STATE. This script may need to be updated. Submit a bug report.')

    # Now we need a very specific URL from the respose.
    response_url = re.search("response_url\s*=\s*'(.*)';", submission.text).groups()[0]
    agent.get(response_url.replace("\/", "/"))

    # In theory, we're in.

def file_exists_in_folder(filename, folder):
    "Check if the file exists in folder of any subfolder"
    for _, _, files in os.walk(folder):
        if filename in files:
            return True
    return False

def activities(agent, outdir, increment = 100):
    global ACTIVITIES
    currentIndex = 0
    initUrl = ACTIVITIES % (currentIndex, increment)  # 100 activities seems a nice round number
    try:
        response = agent.get(initUrl)
    except:
        print('Wrong credentials for user {}. Skipping.'.format(username))
        return
    search = json.loads(response.text)
    totalActivities = int(search['results']['totalFound'])
    while True:
        for item in search['results']['activities']:
            # Read this list of activities and save the files.

            activityId = item['activity']['activityId']
            activityDate = item['activity']['activitySummary']['BeginTimestamp']['value'][:10]
            url = TCX % activityId
            file_name = '{}_{}.txt'.format(activityDate, activityId)
            if file_exists_in_folder(file_name, output):
                print('{} already exists in {}. Skipping.'.format(file_name, output))
                continue
            print('{} is downloading...'.format(file_name))
            datafile = agent.get(url).text
            file_path = os.path.join(outdir, file_name)
            f = open(file_path, "w")
            f.write(datafile)
            f.close()
            shutil.copy(file_path, os.path.join(os.path.dirname(os.path.dirname(file_path)), file_name))

        if (currentIndex + increment) > totalActivities:
            # All done!
            break

        # We still have at least 1 activity.
        currentIndex += increment
        url = ACTIVITIES % (currentIndex, increment)
        response = agent.get(url)
        search = json.loads(response.text)

def download_files_for_user(username, password, output):
    # Create the agent and log in.
    agent = me.Browser()
    print("Attempting to login to Garmin Connect...")
    login(agent, username, password)

    user_output = os.path.join(output, username)
    download_folder = os.path.join(user_output, 'Historical')

    # Create output directory (if it does not already exist).
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Scrape all the activities.
    activities(agent, download_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Garmin Data Scraper',
        epilog = 'Because the hell with APIs!', add_help = 'How to use',
        prog = 'python download.py [-u <user> | -c <csv fife with credentials>] -o <output dir>')
    parser.add_argument('-u', '--user', required = False,
        help = 'Garmin username. This will NOT be saved!',
        default = None)
    parser.add_argument('-c', '--csv', required = False,
        help = 'CSV file with username and password in "username,password" format.',
        default = None)
    parser.add_argument('-o', '--output', required = False,
        help = 'Output directory.', default = os.path.join(os.getcwd(), 'Results/'))
    args = vars(parser.parse_args())

    # Sanity check, before we do anything:
    if args['user'] is None and args['csv'] is None:
        print("Must either specify a username (-u) or a CSV credentials file (-c).")
        sys.exit()

    # Try to use the user argument from command line
    output = args['output']

    if args['user'] is not None:
        password = getpass('Garmin account password (NOT saved): ')
        username = args['user']
    else:
        csv_file_path = args['csv']
        if not os.path.exists(csv_file_path):
            print("Could not find specified credentials file \"{}\"".format(csv_file_path))
            sys.exit()
        try:
            with open(csv_file_path, 'r') as f:
                contents = f.read()
        except IOError as e:
            print(e)
            sys.exit()
        try:
            username, password = contents.strip().split(",")
        except IndexError:
            print("CSV file must only have 1 line, in \"username,password\" format.")
            sys.exit()

    # Perform the download.
    download_files_for_user(username, password, output)
