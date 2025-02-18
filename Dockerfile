FROM debian:bookworm-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE x
ENV LC_ALL=C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get -y install \
      build-essential \
      gcc \
      git \
      python3-venv \
      python3-dev \
      libffi-dev \
      libpq-dev  \
      libssl-dev \
      gettext \
    && \
    apt-get clean

WORKDIR /app

RUN grep -q -w 1000 /etc/group || groupadd --gid 1000 app && \
    id -u app >/dev/null 2>&1 || useradd --gid 1000 --uid 1000 -m app && \
    chown app:app /app

USER app

COPY --chown=app requirements* /app/

ENV PATH /home/app/venv/bin:${PATH}

RUN python3 -m venv ~/venv && \
    pip install --no-cache-dir --no-compile --upgrade pip && \
    pip install wheel && \
    pip install --no-cache-dir --no-compile --upgrade --requirement  /app/requirements-test.txt

ENV DJANGO_SETTINGS_MODULE example.settings

EXPOSE 8000
