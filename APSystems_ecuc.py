import pandas as pd
import re
url = r'http://192.168.1.220'
tables = pd.read_html(url)
pve_table = tables[0]
# to see all table just print it out :
print (pve_table)
ecu_id = pve_table[1][0]
ecu_firmware = pve_table[1][7]
ecu_tz = pve_table[1][8]
inv_qty = pve_table[1][6]
life_time_generation = float(re.search(r'\d+\.\d+', pve_table[1][1]).group())
current_day = float(re.search(r'\d+\.\d+', pve_table[1][3]).group())
current_power = int(re.search(r'\d+', pve_table[1][2]).group())
print (f"ECU ID: {ecu_id} FW: {ecu_firmware} TZ: {ecu_tz}")
print (f"Current power: {current_power} W. Today's production: {current_day} kWh.")
print (f"Lifetime generation: {life_time_generation} kWh")

url = r'http://192.168.1.220/index.php/realtimedata'
tables = pd.read_html(url)
pve_table = tables[0]
inverters = {}
for row in pve_table.values:
    inv_id = str(row[0].split('-')[0])
    panel_id = row[0].split('-')[1]
    panel_power = int(re.search(r'\d+', row[1]).group()) if row[1] != '-' else 0
    grid_freq = float(re.search(r'\d+\.\d+', row[2]).group()) if row[1] != '-' else 0
    grid_voltage = int(re.search(r'\d+', row[3]).group()) if row[1] != '-' else 0
    inv_temperature = int(re.search(r'\d+', row[4]).group()) if row[1] != '-' else 0
    report_time = str(row[5])
    if inv_id in inverters:
        curr_power = inverters[inv_id]['sum_of_power']
    else:
        inverters[inv_id] = {}
        curr_power = 0
    inverters[inv_id]['sum_of_power'] = curr_power + panel_power
    if not 'grid_freq' in inverters[inv_id]:
        inverters[inv_id]['grid_freq'] = grid_freq
        inverters[inv_id]['grid_voltage'] = grid_voltage
        inverters[inv_id]['inv_temperature'] = inv_temperature
        inverters[inv_id]['reporting_time'] = report_time
    inverters[inv_id]['ch_' + panel_id] = panel_power
print (f"Quantity of inverters: {inv_qty}")
for key, value in inverters.items():
    print (f"Inwerter ID - {key}: Data: {value}")