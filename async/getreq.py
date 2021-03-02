import asyncio
import aiohttp
from aiohttp import ClientSession


async def get_req(url, writefile, session):
    print(f'making request to {url}')
    response = await session.request(method='GET', url=url)

    html = f'{url}'+ ' '+ str(response.status)
    
    print(f'writing {url} msg to file')
    writefile.write(html)

    return html

async def main(urls, writefile):
    async with ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(get_req(url, writefile, session))
        
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    with open('async/urls.txt') as f:
        urls = list(map(str.strip, f))
    
    writefile = open('msg.txt','a')

    asyncio.run(main(urls, writefile))