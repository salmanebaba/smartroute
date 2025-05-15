# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Installer make
RUN apt-get update && apt-get install -y make && rm -rf /var/lib/apt/lists/*

# Copy application code and data
COPY app/ ./app/
COPY log/ ./log/
COPY maps/ ./maps/
COPY start.sh ./

# Make start.sh executable
RUN chmod +x start.sh

# Expose any ports if needed (uncomment if your app uses a port)
# EXPOSE 8000

# Default command
CMD ["make", "first-run"]
