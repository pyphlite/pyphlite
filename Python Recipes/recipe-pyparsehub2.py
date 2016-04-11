from ph2 import ParseHub

# Parsehub Sample Recipe
# - Requires Py-Parsehub 2 (ph2.py) from:
#      - https://github.com/hronecviktor/py-parsehub
# - Tested on Python 3.4.4
# - Notes:
#      - not compatible with Python 2
#      - cannot download CSV

#1. Download basic information for all projects

API_KEY = '<SECRET API KEY>' #redacted

print('1. Downloading data for Account(api_key="%s")' % API_KEY)

ph = ParseHub(API_KEY)
project_list = ph.projects

print('\tFound the following projects:')
for p in project_list:
    print('\t\tProject(token="%s", title="%s")' %
        (p.token, p.title))
print('')

#2a. Find a project by its token

target_token = 'tqql73HM3EBX8Bxa3knM10n5'

print('2a. Finding project with token="%s"...' % target_token)

token2project = {}
for p in project_list:
    token2project[p.token] = p

target_project = token2project[target_token]

print('\tIdentified by token: Project(token="%s", title="%s")"' %
    (target_project.token, target_project.title))
print('')

#2b. OR: Find a project by its token

target_title = 'TLP - Part 1'

print('2b. Finding project with title="%s"...' % target_title)

title2project = {}
for p in project_list:
    title2project[p.title] = p

target_project = title2project[target_title]

print('\tIdentified by title: Project(token="%s", title="%s")"' %
    (target_project.token, target_project.title))
print('')

#3. Download the latest ready data for that project

print('3. Downloading latest ready data for target project...', end=' ')

last_ready_run = target_project.last_ready_run
latest_data = last_ready_run.get_data_sync()
print('Done.')

print('\tFirst 500 characters of acquired data:', end=' ')
print(str(latest_data)[:500].replace('\n', '\\n'))

fn = 'latest_data.json'
print('\tWriting data to "%s"...' % fn, end='')
with open(fn, 'w+') as f:
    f.write(str(latest_data))
print('Done.')
print('')

#4. Start a run

print('4. Starting a new run of the data...', end=' ')

current_run = target_project.run()
run_token = current_run.run_token

print ('Done.')
print('\tNew run token is "%s".' % run_token)
print('')

#5,6. Wait for run to complete + download the data

wait_increment = 5     #check for updates every 5 seconds
wait_timeout   = 10*60 #timeout after 10 minutes

print('5. Waiting for run to complete (timeout=%ss)' % wait_timeout, end='')
print(' AND (one step)')
print('6. Downloading the new data...', end=' ')

current_data = current_run.get_data_sync(
    chk_interval=wait_increment,
    max_chks=wait_timeout/wait_increment)

print('Done.')

print('\tFirst 500 characters of acquired data:', end='')
print(str(current_data)[:500].replace('\n', '\\n'))

fn = 'current_data.json'
print('\tWriting data to "%s"...' % fn, end='')
with open(fn, 'w+') as f:
    f.write(str(current_data))
print(' Done.')
print('')

