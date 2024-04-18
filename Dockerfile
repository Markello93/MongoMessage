FROM python:3.11-slim-bullseye

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
        apt-transport-https \
        apt-transport-https \
        build-essential \
        ca-certificates \
        curl \
        git \
        gnupg \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives/* \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && truncate -s 0 /var/log/*log

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH $PATH:/root/.local/bin

RUN poetry config virtualenvs.create false

RUN mkdir -p /app
WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi


ADD . /app


EXPOSE 8000/tcp

CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]