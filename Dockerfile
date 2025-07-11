FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8333

# Run with 0.0.0.0 binding
CMD ["uvicorn", "src.splunk_mcp.main:app", "--host", "0.0.0.0", "--port", "8333", "--log-level", "info"]
