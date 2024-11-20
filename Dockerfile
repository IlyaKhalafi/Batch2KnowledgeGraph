FROM cruizba/ubuntu-dind:latest

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    libreoffice \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["bash", "-c", "dockerd & sleep 5 && docker run -d --name falkordb -p 6379:6379 falkordb/falkordb:latest && python3 main.py"]
