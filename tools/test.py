import asyncio

loop=asyncio.get_event_loop()

async def pt():
    await asyncio.sleep(1)
    return 'hello'

a=pt()
res=loop.run_until_complete(a)
print(res)
loop.close()