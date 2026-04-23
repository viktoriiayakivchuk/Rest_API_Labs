FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/requirements.txt

RUN uv pip install --system --no-cache -r /code/requirements.txt

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py"]