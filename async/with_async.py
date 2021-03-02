import asyncio

async def fun():
    print('one')
    await asyncio.sleep(1)
    print('two')

async def main():
    await asyncio.gather(fun(), fun(), fun())

if __name__ == '__main__':
    import time

    s = time.perf_counter()
    asyncio.run(main())
    e = time.perf_counter() - s

    print('executed in :', e)