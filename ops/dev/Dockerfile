FROM debian:12-slim

ARG UV_VERSION=0.5.4
ARG GROUP_ID=1000
ARG USER_ID=1000

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  ca-certificates \
  weasyprint \
  curl && rm -rf /var/lib/apt/lists/*

RUN curl -sSL "https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-x86_64-unknown-linux-gnu.tar.gz" | tar -xz -C /usr/local/bin --strip-components=1

RUN groupadd -g "${GROUP_ID}" app && \
    useradd --create-home --no-log-init -u "${USER_ID}" -g "${GROUP_ID}" app

USER app

WORKDIR /home/app

RUN uv venv /home/app/venv
ENV PATH="/home/app/venv/bin:$PATH"

RUN uv pip install -e .

CMD ["python3", "-m", "flask", "--app", "src.app:create_app()", "run", "--host=0.0.0.0"]
