import asyncio
import websockets
from src.connection_handler import connection_handler

async def main():
    async with websockets.serve(connection_handler, "0.0.0.0", 8080):
        await asyncio.Future()

asyncio.run(main())