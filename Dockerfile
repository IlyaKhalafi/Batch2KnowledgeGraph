FROM docker:27.4.0-rc.2-dind

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    libmagic \
    poppler-utils \
    tesseract-ocr \
    libreoffice \
    && python3 -m pip install --upgrade pip

RUN apk add --no-cache docker-cli

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN docker pull falkordb/falkordb:latest
CMD ["sh", "-c", "docker run --rm -v ./data:/data -d --name falkordb -p 6379:6379 falkordb/falkordb:latest && python3 main.py"]
