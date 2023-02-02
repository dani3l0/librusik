import asyncio
import os
from librus import Librus


async def main():
    librus = Librus()

    if await librus.mktoken(os.environ["LIBRUS_LOGIN"], os.environ["LIBRUS_PASS"]):
        data = await librus.get_notifications()
        print(data)

asyncio.run(main())
