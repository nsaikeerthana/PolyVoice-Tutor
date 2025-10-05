# Use a Python image that supports system packages (Debian-based)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for audio/media processing (ffmpeg for whisper)
# NOTE: ffmpeg is essential for openai-whisper
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit default port
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]