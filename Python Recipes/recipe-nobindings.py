from __future__ import print_function

import json
import requests
import time

# Parsehub Sample Recipe
# - No Bindings (uses Requests)
# - Tested on Python 2.7.11 and Python 3.4.4

#1. Download basic information for all projects

API_KEY = '<SECRET API KEY>' #Redacted

print('1. Downloading data for Account(api_key="%s")' % API_KEY)

project_data_req = requests.get(
    'https://www.parsehub.com/api/v2/projects', #list all projects
    params={'api_key': API_KEY}
)

project_data_json = json.loads(project_data_req.text)
project_list = project_data_json['projects']

print('\tFound the following projects:')
for p in project_list:
    print('\t\tProject(token="%s", title="%s")' %
        (p['token'], p['title']))
print('')

#2a. Find a project by its token

target_token = 'tqql73HM3EBX8Bxa3knM10n5'

print('2a. Finding project with token="%s"...' % target_token)

token2project = {}
for p in project_list:
    token2project[p['token']] = p

target_project = token2project[target_token]

print('\tIdentified by token: Project(token="%s", title="%s")"' %
    (target_project['token'], target_project['title']))
print('')

#2b. OR: Find a project by its token

target_title = 'TLP - Part 1'

print('2b. Finding project with title="%s"...' % target_title)

title2project = {}
for p in project_list:
    title2project[p['title']] = p

target_project = title2project[target_title]

print('\tIdentified by title: Project(token="%s", title="%s")"' %
    (target_project['token'], target_project['title']))
print('')

#3. Download the latest ready data for that project

print('3. Downloading latest ready data for target project...', end=' ')

download_req_latest = requests.get(
    'https://www.parsehub.com/api/v2/projects/%s/last_ready_run/data' %
    target_project['token'],
    params={
        'api_key': API_KEY,
        'format': 'csv' #json/csv
    }
)

latest_data = download_req_latest.text
print('Done.')

print('\tFirst 500 characters of acquired data:', end=' ')
print(str(latest_data)[:500].replace('\n', '\\n'))

fn = 'latest_data.csv'
print('\tWriting data to "%s"...' % fn, end='')
with open(fn, 'w+') as f:
    f.write(latest_data)
print('Done.')
print('')

#4. Start a run

print('4. Starting a new run of the data...', end=' ')

run_req = requests.post(
    'https://www.parsehub.com/api/v2/projects/%s/run' % #run the project
    target_project['token'], #project token
    params={'api_key': API_KEY}
)

run_json = json.loads(run_req.text)
run_token = run_json['run_token']

print ('Done.')
print('\tNew run token is "%s".' % run_token)
print('')

#5. Wait for run to complete

wait_increment = 5     #check for updates every 5 seconds
wait_timeout   = 10*60 #timeout after 10 minutes
curr_wait_time = 0     #total time waited so far

print('5. Waiting for run to complete (timeout=%ss)' % wait_timeout, end='')

data_ready = False
while not data_ready:

    run_info_req = requests.get(
        'https://www.parsehub.com/api/v2/runs/%s' % run_token, #get the run
        params={'api_key': API_KEY} 
    )

    run_info = json.loads(run_info_req.text)

    status = run_info['status']
    data_ready = run_info['data_ready']

    if status not in ['initialized', 'running', 'complete']:
        raise Exception('Error: status="%s".' % status)

    if not data_ready:
        print('.', sep='', end='')
        time.sleep(wait_increment)
        curr_wait_time += wait_increment

        if curr_wait_time >= wait_timeout:
            raise Exception('Data download time out after %s seconds.' % curr_wait_time)

print(' Done.')
print('')

#6. Download data for that run

print('6. Downloading the new data...', end=' ')

download_req_current = requests.get(
    'https://www.parsehub.com/api/v2/runs/%s/data' % run_token,
    params={
        'api_key': API_KEY,
        'format': 'csv' #json/csv
    }
)

current_data = download_req_current.text
print('Done.')

print('\tFirst 500 characters of acquired data:', end='')
print(str(latest_data)[:500].replace('\n', '\\n'))

fn = 'current_data.csv'
print('\tWriting data to "%s"...' % fn, end='')
with open(fn, 'w+') as f:
    f.write(current_data)
print(' Done.')
print('')

