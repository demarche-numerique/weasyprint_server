FROM ubuntu:jammy

RUN apt-get update \
    && apt-get install -yqq curl git \
    && curl -sSL "https://github.com/astral-sh/uv/releases/download/0.11.22/uv-x86_64-unknown-linux-gnu.tar.gz" | tar -xz -C /usr/local/bin --strip-components=1 \
    # simulate gitlab runner builds directory
    && mkdir -p /builds

WORKDIR /builds
