from __future__ import print_function
from pyphlite import *

#Requires PyPhLite (pyphlite.py) from:
#  https://github.com/pyphlite/pyphlite

proj = PhProject('<SECRET API KEY>', 'tqql73HM3EBX8Bxa3knM10n5') #API key redacted

latest_data = proj.get_last_ready_data(format='json')
with open('latest_data.json', 'w+') as f:
    f.write(str(latest_data))

current_data = proj.run().get_data(format='csv')
with open('current_data.csv', 'w+') as f:
    f.write(str(current_data))

