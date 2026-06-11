import asyncio
import websockets
import threading
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from src.connection_handler import connection_handler
from src.db import init_db_conn

class TestClientRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="./test", **kwargs)
    def log_message(self, format, *args):
        pass

def run_http():
    httpd = HTTPServer(('', 8888), TestClientRequestHandler)
    httpd.serve_forever()

async def main():
    await init_db_conn()
    async with websockets.serve(connection_handler, "0.0.0.0", 8080):
        await asyncio.Future()

if os.environ.get("ENABLE_TEST_CLIENT", "false").lower() == "true":
    threading.Thread(target=run_http, daemon=True).start()

asyncio.run(main())