# Use the official Python 3.9 image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY . .

# Run the Flask application
CMD ["python", "main.py"]
