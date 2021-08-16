import pandas as pd
import re
url = r'http://192.168.1.220'
tables = pd.read_html(url)
pve_table = tables[0]
# to see all table just print it out :
#print (pve_table)
life_time_generation = float(re.search(r'\d+\.\d+', pve_table[1][1]).group())
current_day = float(re.search(r'\d+\.\d+', pve_table[1][3]).group())
current_power = int(re.search(r'\d+', pve_table[1][2]).group())
print (f"Current power {current_power} W. Today's production {current_day} kWh.")
print (f"Lifetime generation : {life_time_generation} kWh")

url = r'http://192.168.1.220/index.php/realtimedata'
tables = pd.read_html(url)
pve_table = tables[0]
#String(pve_table).split('\n')
# print (pve_table)
for row in pve_table.values:
    print (f"Inverter ID {row[0]} power = {row[1]}")