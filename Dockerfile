FROM python:3.12

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    poppler-utils \
    curl \
    wget \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libmagic1 \
    libpoppler-cpp-dev \
    libpoppler-glib8 \
    libx11-6 \
    libxcb1 \
    libxau6 \
    libxdmcp6 \
    libjpeg-dev \
    libpng-dev \
    libtiff5-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --timeout=1000 -r requirements.txt

COPY . .
RUN mkdir -p uploads data logs

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV OPENCV_LOG_LEVEL=ERROR
ENV DISPLAY=:99
ENV QT_X11_NO_MITSHM=1

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
