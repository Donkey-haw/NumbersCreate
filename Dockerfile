# Use official Python image
FROM python:3.11-slim

# Install system dependencies for PyMuPDF and snappy
RUN apt-get update && apt-get install -y \
    build-essential \
    libmupdf-dev \
    libsnappy-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure frontend directory exists
RUN mkdir -p frontend

# Expose port (Render uses environment variable, but 7000 is our default)
EXPOSE 7000

# Run the application
CMD ["python", "main.py"]
