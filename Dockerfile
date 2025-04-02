FROM debian:bookworm-slim

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE x
ENV LC_ALL=C.UTF-8
ENV UV_COMPILE_BYTECODE 0

RUN apt-get -y update && apt-get -y install \
      build-essential \
      gcc \
      git \
      python3-dev \
      libffi-dev \
      libpq-dev  \
      libssl-dev \
      gettext \
      pipx \
    && \
    apt-get clean

WORKDIR /app

RUN grep -q -w 1000 /etc/group || groupadd --gid 1000 app && \
    id -u app >/dev/null 2>&1 || useradd --gid 1000 --uid 1000 -m app && \
    chown app:app /app

USER app

COPY --chown=app requirements* /app/

ENV PATH /home/app/.local/bin:/home/app/venv/bin:${PATH}

RUN pipx install --force uv==0.6.11 && uv venv ~/venv && \
    uv pip install --no-cache --upgrade --requirements /app/requirements-test.txt && \
    uv cache clean

ENV DJANGO_SETTINGS_MODULE example.settings

EXPOSE 8000
