FROM python:3.11-slim

# Install only the necessary dependencies for Playwright Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libnss3 \
    libgbm1 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libx11-xcb1 \
    libxrandr2 \
    libgtk-3-0 \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy app code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir flask playwright beautifulsoup4

# Install only Chromium (not Firefox or WebKit)
RUN playwright install chromium

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
