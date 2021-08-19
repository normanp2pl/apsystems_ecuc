import asyncio
import aiohttp
from table_parser import HTMLTableParser
import re
import logging

_LOGGER = logging.getLogger(__name__)

class APSystemsECUC:

    def __init__(self, ipaddr, port=8899, raw_ecu=None, raw_inverter=None):
        self.ipaddr = ipaddr
        self.port = port
        self.summary_url = f"http://{self.ipaddr}"
        self.details_url = f"http://{self.ipaddr}/index.php/realtimedata"

        self.qs1_ids = [ "802", "801", "804", "806" ]
        self.yc600_ids = [ "406", "407", "408", "409" ]
        self.yc1000_ids = [ "501", "502", "503", "504" ]

        self.ecu_id = None
        self.qty_of_inverters = 0
        self.lifetime_energy = 0
        self.current_power = 0
        self.today_energy = 0
        self.inverters = []
        self.firmware = None
        self.timezone = None
        self.last_update = None

        self.ecu_raw_data = raw_ecu
        self.inverter_raw_data = raw_inverter
        self.inverter_raw_signal = None

    def dump(self):
        print(f"ECU : {self.ecu_id}")
        print(f"Firmware : {self.firmware}")
        print(f"TZ : {self.timezone}")
        print(f"Qty of inverters : {self.qty_of_inverters}")

    async def read_url(self, session, url):
        async with session.get(url) as resp:
            return await resp.read()

    async def async_query_ecu(self):
        tasks = []
        async with aiohttp.ClientSession() as session:
            _LOGGER.info(f"Asking page {self.summary_url} for a ECU data")
            for url in [self.summary_url, self.details_url]:
                tasks.append(asyncio.create_task(self.read_url(session, url)))
            html_pages = await asyncio.gather(*tasks)
            summary_table = HTMLTableParser()
            summary_table.feed(html_pages[0].decode('utf-8'))
            self.process_ecu_data(summary_table.tables[0])

            details_table = HTMLTableParser()
            details_table.feed(html_pages[1].decode('utf-8'))
            data = self.process_inverter_data(details_table.tables[0])

            data["ecu_id"] = self.ecu_id
            data["today_energy"] = self.today_energy
            data["lifetime_energy"] = self.lifetime_energy
            data["current_power"] = self.current_power

            return(data)

    def process_ecu_data(self, data=None):
        # if not data:
        #     data = self.ecu_raw_data
        self.ecu_id = data[0][1]
        self.qty_of_inverters = data[5][1]
        self.firmware = data[7][1]
        self.timezone = data[8][1]
        self.lifetime_energy = float(re.search(r'\d+\.\d+', data[1][1]).group())
        self.today_energy = float(re.search(r'\d+\.\d+', data[3][1]).group())
        self.current_power = int(re.search(r'\d+', data[2][1]).group())

    def process_inverter_data(self, data=None):
        # if not data:
        #     data = self.inverter_raw_data
        output = {}
        output["inverter_qty"] = self.qty_of_inverters
        output["inverters"] = {}
        inverters = {}
        for index in range(1, len(data)):
            row = data[index]
            inverter_uid = str(row[0].split('-')[0])
            if not inverter_uid in inverters:
                inverters[inverter_uid] = {}
                inverters[inverter_uid]["uid"] = inverter_uid
                inverters[inverter_uid]["online"] = True
                inverters[inverter_uid]["frequency"] = float(re.search(r'\d+\.\d+', row[2]).group()) if row[1] != '-' else 0
                inverters[inverter_uid]["temperature"] = int(re.search(r'\d+', row[4]).group()) if row[1] != '-' else 0
                inverters[inverter_uid]["signal"] = 100
                inv_model_id = inverter_uid[0:3]
                if inv_model_id in self.qs1_ids:
                    inv_model = "QS1"
                elif inv_model_id in self.yc600_ids:
                    inv_model = "YC600"
                elif inv_model_id in self.yc1000_ids:
                    inv_model = "YC1000"
                else:
                    inv_model = "Uknkown"
                inverters[inverter_uid]["model"] = inv_model
                inverters[inverter_uid]["channel_qty"] = 0
                inverters[inverter_uid]["power"] = []
                inverters[inverter_uid]["voltage"] = []
                output["timestamp"] = str(row[5])
                self.last_update = output["timestamp"]
            panel_id = int(row[0].split('-')[1])
            inverters[inverter_uid]["channel_qty"] += 1
            inverters[inverter_uid]["power"].append(int(re.search(r'\d+', row[1]).group()) if row[1] != '-' else 0)
            if panel_id == 1:
                inverters[inverter_uid]["voltage"].append(int(re.search(r'\d+', row[3]).group()) if row[1] != '-' else 0)
            else:
                inverters[inverter_uid]["voltage"].append(int(re.search(r'\d+', row[2]).group()) if row[1] != '-' else 0)
        output["inverters"] = inverters
        return (output)
# async def main():
ecu = APSystemsECUC("192.168.1.220")
data = asyncio.run(ecu.async_query_ecu())
print(data)

# asyncio.run(main())

# print(data["ecu_id"])