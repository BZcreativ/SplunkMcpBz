import os
import splunklib.client as client
from dotenv import load_dotenv

load_dotenv()

class ITSIConnector:
    def __init__(self):
        self.host = os.getenv("SPLUNK_HOST")
        self.port = int(os.getenv("SPLUNK_PORT", 8089))
        self.username = os.getenv("SPLUNK_USERNAME")
        self.password = os.getenv("SPLUNK_PASSWORD")
        self.scheme = os.getenv("SPLUNK_SCHEME", "https")
        self.verify = os.getenv("VERIFY_SSL", "true").lower() == "true"
        self.service = None

    def connect(self):
        try:
            self.service = client.connect(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                scheme=self.scheme,
                verify=self.verify,
                app="SA-ITOA"
            )
            return self.service
        except Exception as e:
            print(f"Error connecting to ITSI: {e}")
            return None
