FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY edgeops/ ./edgeops/
COPY nginx/ ./nginx/

RUN useradd --create-home --shell /bin/bash edgeops && \
    chown -R edgeops:edgeops /app

USER edgeops

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)" || exit 1

CMD ["python", "-m", "edgeops.gateway"]
