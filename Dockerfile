# 1. Use a lightweight Python base
FROM python:3.9-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy requirements first
COPY requirements.txt .

# 4. Install dependencies efficiently (The FIX is here!)
# --no-cache-dir prevents storing 1GB+ of cache files in RAM
# We install torch CPU-only specifically before other packages
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the app
COPY . .

# 6. Expose port 5000
EXPOSE 5000

# 7. Start the app (Single worker to save RAM)
CMD ["python", "app.py"]