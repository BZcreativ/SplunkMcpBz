import os
import socket
import splunklib.client as client
from dotenv import load_dotenv

load_dotenv()

class SplunkConnector:
    def __init__(self):
        self.host = os.getenv("SPLUNK_HOST")
        self.port = int(os.getenv("SPLUNK_PORT", 8089))
        self.username = os.getenv("SPLUNK_USERNAME")
        self.password = os.getenv("SPLUNK_PASSWORD")
        self.scheme = os.getenv("SPLUNK_SCHEME", "https")
        self.verify = os.getenv("VERIFY_SSL", "true").lower() == "true"
        self.service = None

    def check_splunk_availability(self):
        try:
            with socket.create_connection((self.host, self.port), timeout=5):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            print(f"Splunk availability check failed: {e}")
            return False

    def connect(self):
        if not self.check_splunk_availability():
            print(f"Splunk server at {self.host}:{self.port} is not reachable.")
            return None
        try:
            self.service = client.connect(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                scheme=self.scheme,
                verify=self.verify,
            )
            return self.service
        except Exception as e:
            print(f"Error connecting to Splunk: {e}")
            return None
