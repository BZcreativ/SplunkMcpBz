FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl net-tools git && \
    rm -rf /var/lib/apt/lists/*

# Clone repository
RUN git clone https://github.com/BZcreativ/SplunkMcpBz.git .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8334

# Run with 0.0.0.0 binding
CMD ["uvicorn", "src.splunk_mcp.main:root_app", "--host", "0.0.0.0", "--port", "8334"]
