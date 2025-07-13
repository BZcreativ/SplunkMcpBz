from splunklib.client import connect

def list_splunk_indexes():
    try:
        # Get connection details from environment
        host = "192.168.1.15"
        port = 8089
        token = "eyJraWQiOiJzcGx1bmsuc2VjcmV0IiwiYWxnIjoiSFM1MTIiLCJ2ZXIiOiJ2MiIsInR0eXAiOiJzdGF0aWMifQ.eyJpc3MiOiJhZG1pbiBmcm9tIHNwbHVua3Rlc3QiLCJzdWIiOiJhZG1pbiIsImF1ZCI6IndlYiIsImlkcCI6IlNwbHVuayIsImp0aSI6IjZlZWY5MzMzOGM1NzdlNDFmZDIyOTc0MzA1NjkwOWM2ZDExOGQyODlkMTMxZmMzNjExOTk3NmZhNWMxZWRjYmYiLCJpYXQiOjE3NTIzNDI3MTQsImV4cCI6MTc4Mzg3ODcxNCwibmJyIjoxNzUyMzQyNzE0fQ.rVNMaOd7EUf9ls6QPulzvvI2TmLwZ8GBNoZnAnwt1K0EU1YcR1aM1GqZLAELlFux0PKbb0CPrvPKqW75z35stg"
        
        print(f"Connecting to Splunk at {host}:{port}")
        service = connect(
            host=host,
            port=port,
            splunkToken=token,
            scheme="https",
            verify=False
        )
        
        print("Successfully connected to Splunk")
        indexes = service.indexes
        print(f"Found {len(indexes)} indexes:")
        
        for idx in indexes:
            print(f"- {idx.name}")
            
        return True
        
    except Exception as e:
        print(f"Error connecting to Splunk: {str(e)}")
        return False

if __name__ == "__main__":
    list_splunk_indexes()
