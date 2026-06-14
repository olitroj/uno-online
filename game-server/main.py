import asyncio
import websockets
import threading
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from src.connection_handler import connection_handler
from src.db import init_db_conn
from src.event_handler import handle_turn_timeout
from src.globals import game_state
from src.objects import Stages

class TestClientRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="./test", **kwargs)
    def log_message(self, format, *args):
        pass

def run_http():
    httpd = HTTPServer(('', 8888), TestClientRequestHandler)
    httpd.serve_forever()

async def timeout_checker():
    """Background task that checks for turn timeouts every second."""
    from src.globals import state_lock
    while True:
        await asyncio.sleep(1)
        if game_state.stage == Stages.PLAY:
            await state_lock.acquire()
            try:
                await handle_turn_timeout()
            finally:
                state_lock.release()

async def main():
    await init_db_conn()
    await asyncio.gather(
        timeout_checker(),
        websockets.serve(connection_handler, "0.0.0.0", 8080)
    )

if os.environ.get("ENABLE_TEST_CLIENT", "false").lower() == "true":
    threading.Thread(target=run_http, daemon=True).start()

asyncio.run(main())