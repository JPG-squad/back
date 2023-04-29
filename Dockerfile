ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-buster as build-image

RUN apt-get update; apt-get dist-upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# poetry
WORKDIR /srv
RUN pip install poetry==1.3.2
COPY poetry.lock pyproject.toml /srv/
ARG POETRY_DEV=false
RUN poetry export -f requirements.txt -o requirements.txt --without-hashes $(test "$POETRY_DEV" = "true" && echo "--with dev") \
    && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
# end poetry

FROM python:${PYTHON_VERSION}-slim

COPY --from=build-image /srv/venv/ /srv/venv/

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/srv/venv/bin:$PATH"

WORKDIR /app
COPY app/ .
EXPOSE 80
