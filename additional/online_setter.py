from config import token, group_id

from loguru import logger
import aiohttp
import asyncio


@logger.catch
async def set_group_status_online():
    while True:
        async with aiohttp.ClientSession() as session:
            await session.get(f'https://api.vk.com/method/groups.enableOnline?access_token={token}&v=5.130&group_id={group_id}') # noqa

        await asyncio.sleep(14400)


if __name__ == '__main__':
    asyncio.run(set_group_status_online())
