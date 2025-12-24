# Use lightweight Python
FROM python:3.9-slim

# Set working folder
WORKDIR /app

# Copy requirements first to speed up builds
COPY requirements.txt .

# Install dependencies (CPU Torch to save space)
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Open the port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]