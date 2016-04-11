from ph2 import ParseHub

#Requires Py-Parsehub 2 (ph2.py) from:
#  https://github.com/hronecviktor/py-parsehub

ph = ParseHub('<SECRET API KEY>') #redacted
target_project = ph.project_from_token('tqql73HM3EBX8Bxa3knM10n5')

latest_data = target_project.last_ready_run.get_data_sync()
with open('latest_data.json', 'w+') as f:
    f.write(str(latest_data))

current_data = target_project.run().get_data_sync()
with open('current_data.json', 'w+') as f:
    f.write(str(current_data))
