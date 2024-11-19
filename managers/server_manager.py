import asyncio
from aiohttp import web


class ServerManager:
    def __init__(self):
        pass

    async def get_status(self, request) -> web.Response:
        return web.Response(text="Hello, World!")

    async def loop(self) -> None:
        app = web.Application()
        app.router.add_get('/', self.get_status)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()

        print("Web server started on http://localhost:8080")

        await asyncio.Event().wait()
