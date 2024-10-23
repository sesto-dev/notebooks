import sys
import threading
import time
from datetime import datetime, timedelta
import MetaTrader5 as mt5
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import logging
# Import your algorithm
from algorithm import check_entry_condition, monitor_open_trades, TIMEZONE

# Import database operations
from database import store_trade, update_trade

# Simple HTTP server
class SimpleServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"MetaTrader5 Python Server is running")

def run_server():
    httpd = HTTPServer(('0.0.0.0', 1111), SimpleServer)
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
        # Initialize MT5 connection
        if not mt5.initialize():
            print("initialize() failed")
            mt5.shutdown()
            sys.exit(1)

        # Start the HTTP server in a separate thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Start MetaTrader5 threads
        fractal_thread = threading.Thread(target=check_entry_condition, daemon=True)
        monitor_thread = threading.Thread(target=monitor_open_trades, daemon=True)
        fractal_thread.start()
        monitor_thread.start()

        print(f"{datetime.now(tz=TIMEZONE)} - Threads started successfully.")

        logger.info(f"Threads started successfully.")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"{datetime.now(tz=TIMEZONE)} - Program terminated by user.")
    except Exception as e:
        print(f"{datetime.now(tz=TIMEZONE)} - Unhandled exception: {e}")
    finally:
        mt5.shutdown()