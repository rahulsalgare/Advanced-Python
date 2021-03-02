import asyncio
import aiofiles
import aiohttp
import logging
import re
import sys
import urllib.error
import urllib.parse
from aiohttp import ClientSession


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("areq")
logging.getLogger("chardet.charsetprober").disabled = True


HREF_RE = re.compile(r'href="(.*?)"')

async def fetch_html(url: str, session: ClientSession, **kwargs) -> str:
    """GET request wrapper to fetch page HTML.

    kwargs are passed to `session.request()`.
    """

    resp = await session.request(method="GET", url=url, **kwargs)
    resp.raise_for_status()
    logger.info("Got response [%s] for URL: %s", resp.status, url)
    html = await resp.text()
    return html


async def parse(url, session, **kwargs):
    found = set()
    try:
        html = await fetch_html(url=url, session=session, **kwargs)

    except( aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError) as e:
        logger.error(
            "aiohttp exception for %s [%s]: %s",
            url,
            getattr(e, "status", None),
            getattr(e, "message", None),
        )
        return found
        
    except Exception as e:
        logger.exception(
            "Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {})
        )
        return found

    else:
        for link in HREF_RE.findall(html):
            try:
                abslink = urllib.parse.urljoin(url, link)
            except (urllib.error.URLError, ValueError):
                logger.exception("Error parsing URL: %s", link)
                pass
            else:
                found.add(abslink)
        logger.info("Found %d links for %s", len(found), url)
        return found

async def write_one(file, url, **kwargs):
    res = await parse(url=url, **kwargs)
    if not res:
        return None
    async with aiofiles.open(file, 'a') as f:
        for p in res:
            await f.write(f"{url}\t{p}\n")
        logger.info("Wrote results for source URL: %s", url)

async def bulk_crawl_and_write(file, urls):
    async with ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(
                write_one(file=file, url=url, session=session)
            )
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    import pathlib
    import sys

    with open('async/urls.txt') as infile:
        urls = set(map(str.strip, infile))
    
    outfile = open('async/foundurls.txt', 'w')

    asyncio.run(bulk_crawl_and_write(file=outfile, urls=urls))