# FROM python:3.12.4-alpine
FROM python:3.12.6-slim-bullseye

WORKDIR /app/

COPY ./requirements.txt /app/requirements.txt

RUN \
  apt-get update && \
  apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    python3-dev && \
  python -m pip install --no-cache-dir --upgrade pip && \
  python -m pip install --no-cache-dir --ignore-requires-python -r /app/requirements.txt && \
  python -m pip install torch==2.2.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html && \
  python -m pip install torchvision==0.18.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html && \
  apt-get purge -y --auto-remove build-essential python3-dev gcc && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

COPY ./app /app/
COPY ./detectron2 ./detectron2

CMD ["fastapi", "run", "main.py", "--port", "8000"]