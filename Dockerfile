ARG PYTHON_VERSION=3.9.10
FROM python:${PYTHON_VERSION}-buster as build-image

RUN apt-get update; apt-get dist-upgrade -y \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -m 700 /root/.ssh; \
    touch -m 600 /root/.ssh/known_hosts; \
    ssh-keyscan github.com > /root/.ssh/known_hosts

# poetry
WORKDIR /srv
RUN pip install poetry==1.3.2
COPY poetry.lock pyproject.toml /srv/
ARG POETRY_DEV=false
RUN --mount=type=ssh,id=default --mount=type=cache,mode=0777,target=/root/.cache/pip \
    poetry export -f requirements.txt -o requirements.txt --without-hashes $(test "$POETRY_DEV" = "true" && echo "--with dev") \
    && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
# end poetry

FROM python:${PYTHON_VERSION}-slim

RUN apt-get update; apt-get dist-upgrade -y \
    && apt-get install -qq ffmpeg -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build-image /srv/venv/ /srv/venv/

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/srv/venv/bin:$PATH"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app
COPY app/ .
EXPOSE 80

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["prod"]