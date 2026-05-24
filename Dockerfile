FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-dev \
    libasound2-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables for headless mode
ENV KIVY_NO_FILELOG=1
ENV KIVY_NO_CONSOLELOG=1

CMD ["python", "main.py"]
