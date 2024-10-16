import sys
import threading
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import logging

from nobitex.trailing import run_strategy_for_clients  # Import the function that sets up the ThreadPoolExecutor

from database import store_trade, update_trade

from sesto.telegram import TelegramSender

Telegram = TelegramSender()

# Simple HTTP server
class SimpleServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Crypto Python Server is running")

def run_server():
    httpd = HTTPServer(('0.0.0.0', 3000), SimpleServer)
    httpd.serve_forever()

    # Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Start the HTTP server in a separate thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Start MetaTrader5 threads
        trailing_stop_thread = threading.Thread(target=run_strategy_for_clients, daemon=True)
        trailing_stop_thread.start()

        logger.info(f"Threads started successfully.")
        Telegram.send_message("Threads started successfully.")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"{datetime.now()} - Program terminated by user.")
    except Exception as e:
        print(f"{datetime.now()} - Unhandled exception: {e}")