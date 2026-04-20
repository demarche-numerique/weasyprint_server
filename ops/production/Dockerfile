FROM debian:12-slim

ARG UV_VERSION=0.5.4
ARG GROUP_ID=1000
ARG USER_ID=1000

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV GUNICORN_WORKERS=4
ENV APP_PORT=5000
ENV BASE_URL=http://localhost:5000

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  ca-certificates \
  tini \
  weasyprint \
  curl && rm -rf /var/lib/apt/lists/*

RUN curl -sSL "https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-x86_64-unknown-linux-gnu.tar.gz" | tar -xz -C /usr/local/bin --strip-components=1

RUN groupadd -g "${GROUP_ID}" app && \
    useradd --create-home --no-log-init -u "${USER_ID}" -g "${GROUP_ID}" app

USER app

WORKDIR /home/app

COPY --chown=app:app src/ src/
COPY --chown=app:app pyproject.toml .

ENV PATH="/home/app/venv/bin:$PATH"
RUN uv venv /home/app/venv && \
    . /home/app/venv/bin/activate && \
    uv pip install -e . && \
    uv pip install gunicorn

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sh", "-c", "gunicorn --workers $GUNICORN_WORKERS --bind 0.0.0.0:$APP_PORT 'src.app:create_app()'"]
