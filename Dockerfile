# 1. Use lightweight Python
FROM python:3.9-slim

# 2. Set working folder
WORKDIR /app

# 3. Copy files
COPY requirements.txt .

# 4. Install dependencies (Now much faster & smaller!)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy app code
COPY . .

# 6. Run
EXPOSE 5000
CMD ["python", "app.py"]