import sys
import threading
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import logging
from dotenv import load_dotenv

from algorithm import check_entry_condition, monitor_open_trades, TIMEZONE
from library.telegram import TelegramSender

load_dotenv()
Telegram = TelegramSender()

# Simple HTTP server
class SimpleServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"MetaTrader5 Python Server is running")

def run_server():
    httpd = HTTPServer(('0.0.0.0', int(os.environ.get('APP_FOREX_PORT'))), SimpleServer)
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
        fractal_thread = threading.Thread(target=check_entry_condition, daemon=True)
        monitor_thread = threading.Thread(target=monitor_open_trades, daemon=True)
        fractal_thread.start()
        monitor_thread.start()

        text = f"{datetime.now(tz=TIMEZONE)} - Threads started successfully."

        logger.info(text)
        Telegram.send_message(text)

        while True:
            time.sleep(1)

    except Exception as e:
        text = f"{datetime.now(tz=TIMEZONE)} - Unhandled exception: {e}"
        logger.error(text)
        Telegram.send_message(text)
