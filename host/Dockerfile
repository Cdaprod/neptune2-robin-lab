FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      bash \
      ca-certificates \
      curl \
      iproute2 \
      iputils-ping \
      netcat-openbsd \
      nmap \
      socat \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY pyproject.toml README.md /workspace/
COPY src /workspace/src

RUN python -m pip install --no-cache-dir -e .

CMD ["sleep", "infinity"]
