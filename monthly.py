"""
This script was inspired from tmcw's Ruby script:

    https://gist.github.com/tmcw/1098861

The goal is to pretty much scrape the Garmin Connect data and post it to Twitter.
It's a little ad-hoc, considering Garmin Connect doesn't have a well-publicized
(or well-documented) API, so it requires a bit of trial-and-error to get
this to work properly. Furthermore, *it can break at any time*. Don't come crying
to me when Garmin Connect suddenly changes the API and this script doesn't work.
"""

import argparse
import json
import datetime
import base64
import mechanize as me
import tweepy

LOGIN = "https://sso.garmin.com/sso/login?service=http%%3A%%2F%%2Fconnect.garmin.com%%2Fpost-auth%%2Flogin&webhost=olaxpw-connect01.garmin.com&source=http%%3A%%2F%%2Fconnect.garmin.com%%2Fen-US%%2Fsignin&redirectAfterAccountLoginUrl=http%%3A%%2F%%2Fconnect.garmin.com%%2Fpost-auth%%2Flogin&redirectAfterAccountCreationUrl=http%%3A%%2F%%2Fconnect.garmin.com%%2Fpost-auth%%2Flogin&gauthHost=https%%3A%%2F%%2Fsso.garmin.com%%2Fsso&locale=en&id=gauth-widget&cssUrl=https%%3A%%2F%%2Fstatic.garmincdn.com%%2Fcom.garmin.connect%%2Fui%%2Fsrc-css%%2Fgauth-custom.css&clientId=GarminConnect&rememberMeShown=true&rememberMeChecked=false&createAccountShown=true&openCreateAccount=false&usernameShown=true&displayNameShown=false&consumeServiceTicket=false&initialFocus=true&embedWidget=false#"
REDIRECT = "http://connect.garmin.com/post-auth/login"
ACTIVITIES = 'http://connect.garmin.com/proxy/activity-search-service-1.2/json/activities?activityType=running&beginTimestamp>%s&beginTimestamp<%s&limit=%s'

#####################################################
# MODIFY THE FOLLOWING FIELDS WITH YOUR INFORMATION #
#####################################################

# Authentication with Garmin Connect.
# If you don't really care about your GC username/password sitting in plaintext,
# then just wipe out the calls to 'base64' and stick in the plain strings.
# Otherwise, fire up a Python console and do:
#   import base64
#   base64.b64encode("your_username")
# and so forth to get the base64 username and password.
USERNAME = base64.b64decode('')
PASSWORD = base64.b64decode('')

# Authentication with Twitter.
# Get these by signing into dev.twitter.com and creating an app for yourself.
CONSUMER_KEY = 'your_consumer_key'
CONSUMER_SECRET = 'your_consumer_secret'
ACCESS_KEY = 'your_access_token'
ACCESS_SECRET = 'your_access_token_secret'

################################################
# THAT'S IT DON'T MODIFY ANYTHING ELSE PLZ THX #
################################################

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

def activities(agent, increment = 100):
    global ACTIVITIES

    # Set up the datetime stuff. If there's a bug along the lines of not
    # tabulating the results correctly (e.g. recorded 30 workouts and you only
    # did 29, or vice versa), it's probably in the next three lines.
    currentDate = datetime.datetime.now()
    endDate = currentDate - datetime.timedelta(days = currentDate.day)
    startDate = endDate - datetime.timedelta(days = endDate.day - 1)
    
    # Create the URL.
    initUrl = ACTIVITIES % (startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d"), increment)
    response = agent.open(initUrl)
    search = json.loads(response.get_data())
    totalActivities = int(search['results']['totalFound'])
    if totalActivities > increment:
        # Get everything on one page.
        initUrl = ACTIVITIES % (startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d"), totalActivities)
        response = agent.open(initUrl)
        search = json.loads(response.get_data())
        totalActivities = int(search['results']['totalFound'])

    # Loop through all the activities, capturing the summary data.
    # If you want to collect more statistics (elevation, max speed, avg pace, etc),
    # capture them here.
    calories = 0.0
    distance = 0.0
    activitiesWithoutCalories = 0
    missingMiles = 0.0
    for item in search['results']['activities']:
        value = float(item['activity']['activitySummary']['SumDistance']['value'])
        distance += value

        if 'SumEnergy' not in item['activity']['activitySummary']:
            activitiesWithoutCalories += 1
            missingMiles += value
        else:
            calories += float(item['activity']['activitySummary']['SumEnergy']['value'])

    # Are there any calorie counts we need to estimate?
    if activitiesWithoutCalories > 0:
        # Use the average calorie count, times the number of activities we have to estimate.
        # It's crude, but it gets the job done. If you want something more accurate,
        # FILL IN YOUR CALORIE COUNTS.
        m = calories / (distance - missingMiles)
        calories += (m * missingMiles)

    # All done! Return the information we want.
    return [totalActivities, distance, calories]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Garmin Monthly Statistics',
        epilog = 'Because DailyMile apparently can\'t handle the awesome!',
        add_help = 'How to use', prog = 'python monthly.py')

    # Create the agent and log in.
    agent = me.Browser()
    login(agent, USERNAME, PASSWORD)

    # Scrape all the activities.
    workouts, miles, calories = activities(agent)

    # Authenticate with Twitter.
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    status = "My training last month: %s workout%s for %.2f mi and %d calories burned." % (workouts, 's' if workouts != 1 else '', miles, int(calories))
    api.update_status(status = status)
