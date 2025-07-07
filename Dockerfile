# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy the dependency files to the working directory
COPY pyproject.toml poetry.lock ./

# Copy the rest of the application code to the working directory
COPY src/ /app/src/

# Install project dependencies
RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction --no-ansi

# Command to run the application
CMD ["poetry", "run", "python", "src/splunk_mcp/main.py"]
