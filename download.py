"""
This script was inspired from tmcw's Ruby script doing the same thing:

    https://gist.github.com/tmcw/1098861

The goal is to iteratively download all detailed information from Garmin Connect
and store it locally for further perusal and analysis. This is still very much
preliminary; future versions should include the ability to seamlessly merge
all the data into a single file, filter by workout type, and other features
to be determined.
"""

import argparse
from getpass import getpass
import json
import mechanize as me
import os

LOGIN = "https://sso.garmin.com/sso/login?service=http%%3A%%2F%%2Fconnect.garmin.com%%2Fpost-auth%%2Flogin&webhost=olaxpw-connect01.garmin.com&source=http%%3A%%2F%%2Fconnect.garmin.com%%2Fen-US%%2Fsignin&redirectAfterAccountLoginUrl=http%%3A%%2F%%2Fconnect.garmin.com%%2Fpost-auth%%2Flogin&redirectAfterAccountCreationUrl=http%%3A%%2F%%2Fconnect.garmin.com%%2Fpost-auth%%2Flogin&gauthHost=https%%3A%%2F%%2Fsso.garmin.com%%2Fsso&locale=en&id=gauth-widget&cssUrl=https%%3A%%2F%%2Fstatic.garmincdn.com%%2Fcom.garmin.connect%%2Fui%%2Fsrc-css%%2Fgauth-custom.css&clientId=GarminConnect&rememberMeShown=true&rememberMeChecked=false&createAccountShown=true&openCreateAccount=false&usernameShown=true&displayNameShown=false&consumeServiceTicket=false&initialFocus=true&embedWidget=false#"
REDIRECT = "http://connect.garmin.com/post-auth/login"
ACTIVITIES = "http://connect.garmin.com/proxy/activity-search-service-1.2/json/activities?start=%s&limit=%s"
TCX = "https://connect.garmin.com/proxy/activity-service-1.1/tcx/activity/%s?full=true"
GPX = "https://connect.garmin.com/proxy/activity-service-1.1/gpx/activity/%s?full=true"
KML = "https://connect.garmin.com/proxy/activity-service-1.0/kml/activity/%s?full=true"

def login(agent, username, password):
    global LOGIN, REDIRECT
    agent.open(LOGIN)
    agent.select_form(predicate = lambda f: 'id' in f.attrs and f.attrs['id'] == 'login-form')
    agent['username'] = username
    agent['password'] = password

    agent.submit()
    agent.open(REDIRECT)
    if agent.title().find('Sign In') > -1:
        quit('Login incorrect! Check your credentials.')

def activities(agent, outdir, increment = 100):
    global ACTIVITIES
    currentIndex = 0
    initUrl = ACTIVITIES % (currentIndex, increment) # 100 activities seems a nice round number
    response = agent.open(initUrl)
    search = json.loads(response.get_data())
    totalActivities = int(search['results']['totalFound'])
    while True:
        for item in search['results']['activities']:
            # Read this list of activities and save the files.
            print '.'
            activityId = item['activity']['activityId']
            url = TCX % activityId
            datafile = agent.open(url).get_data()
            f = open("%s%s.tcx" % (outdir, activityId), "w")
            f.write(datafile)
            f.close()

        if (currentIndex + increment) > totalActivities:
            # All done!
            break

        # We still have at least 1 activity.
        currentIndex += increment
        url = ACTIVITIES % (currentIndex, increment)
        response = agent.open(url)
        search = json.loads(response.get_data())

parser = argparse.ArgumentParser(description = 'Garmin Data Scraper',
    epilog = 'Because the hell with APIs!', add_help = 'How to use',
    prog = 'python download.py -u <username> -o <output dir>')
parser.add_argument('-u', '--user', required = True,
    help = 'Garmin username. This will NOT be saved!')
parser.add_argument('-o', '--output', required = True,
    help = 'Output directory.')

args = vars(parser.parse_args())
password = getpass('Garmin account password (NOT saved): ')
username = args['user']
output = args['output']

# Create the agent and log in.
agent = me.Browser()
login(agent, username, password)

# Create output directory (if it does not already exist).
if not os.path.exists(output):
    os.mkdir(output)

# Scrape all the activities.
activities(agent, output)