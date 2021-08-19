import asyncio
import aiohttp

from table_parser import HTMLTableParser

async def read_url(session, url):
    async with session.get(url) as resp:
        return await resp.read()

# 
async def main():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in ['http://192.168.1.220', 'http://192.168.1.220/index.php/realtimedata/']:
            tasks.append(asyncio.create_task(read_url(session, url)))
        html_list = await asyncio.gather(*tasks)
        p = HTMLTableParser()
        p.feed(html_list[0].decode('utf-8'))
        print(p.tables[0][0][1])
        
        p = HTMLTableParser()
        p.feed(html_list[1].decode('utf-8'))
        for index in range(1, len(p.tables[0])):
            print(p.tables[0][index])

if __name__ == '__main__':
    asyncio.run(main())
