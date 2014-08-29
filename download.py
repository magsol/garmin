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
import shutil
import sys

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

def file_exists_in_folder(filename, folder):
    "Check if the file exists in folder of any subfolder"
    for _, _, files in os.walk(folder):
        if filename in files:
            return True
    return False

def activities(agent, outdir, increment = 100):
    global ACTIVITIES
    currentIndex = 0
    initUrl = ACTIVITIES % (currentIndex, increment) # 100 activities seems a nice round number
    try:
        response = agent.open(initUrl)
    except:
        print('Wrong credentials for user {}. Skipping.'.format(username))
        return
    search = json.loads(response.get_data())
    totalActivities = int(search['results']['totalFound'])
    while True:
        for item in search['results']['activities']:
            # Read this list of activities and save the files.
            # print '.'
            activityId = item['activity']['activityId']
            url = TCX % activityId
            file_name = '{}_{}.txt'.format(username, activityId)
            if file_exists_in_folder(file_name, output):
                print('{} already exists in {}. Skipping.'.format(file_name, output))
                continue
            print('{} is downloading...'.format(file_name))
            datafile = agent.open(url).get_data()
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
        response = agent.open(url)
        search = json.loads(response.get_data())

def download_files_for_user(username, password, output):
    # Create the agent and log in.
    agent = me.Browser()
    login(agent, username, password)

    user_output = os.path.join(output, username)
    download_folder = os.path.join(user_output, 'Historical')

    # Create output directory (if it does not already exist).
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Scrape all the activities.
    activities(agent, download_folder)


folder_execute = os.path.dirname(sys.executable)
if folder_execute.endswith('/Contents/MacOS'):
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(folder_execute))))


parser = argparse.ArgumentParser(description = 'Garmin Data Scraper',
    epilog = 'Because the hell with APIs!', add_help = 'How to use',
    prog = 'python download.py -u <user> -c <csv fife with credentials> -o <output dir>')
parser.add_argument('-u', '--user', required = False,
    help = 'Garmin username. This will NOT be saved!')
parser.add_argument('-c', '--csv', required=False,
                    help='CSV file with username and password (comma separated).',
                    default=os.path.join(os.getcwd(),'credentials.csv'))
parser.add_argument('-o', '--output', required = False,
    help = 'Output directory.', default=os.path.join(os.getcwd(), 'Results/'))

args = vars(parser.parse_args())
# Try to use the user argument from command line
output = args['output']

if args['user'] is not None:
    password = getpass('Garmin account password (NOT saved): ')
    username = args['user']
    download_files_for_user(username, password, output)

# Try to use csv argument from command line

if args['csv'] is not None:
    csv_file_path = args['csv']
    if not os.path.exists(csv_file_path):
        print("CSV file doesn't exist")
        sys.exit()
    else:
        with open(csv_file_path, 'r') as f:
            for line in f:
                try:
                    if ',' in line:
                        username, password = (line.strip().split(','))
                        print 'Downloading files for user {}'.format(username)
                        download_files_for_user(username, password, output)
                except IndexError:
                    raise Exception('Wrong line in CSV file. Please check the line {}'.format(line))

