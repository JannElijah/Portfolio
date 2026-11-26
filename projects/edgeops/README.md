# EdgeOps — Dockerized Reverse Proxy & Service Health Stack

Multi-container reverse proxy, rate-limiting, and service health monitoring stack pairing production **Docker + Nginx (`1.27-alpine`)** manifests with an executable Python Reverse-Proxy Gateway and live SRE Web Console (`edgeops/gateway.py`).

## Architecture & Files
- `docker-compose.yml` & `Dockerfile` — Orchestrates `nginx-edge` (`8080:80`) forwarding to healthy `edgeops-gateway` containers with `HEALTHCHECK`.
- `nginx/edgeops.conf` — Production Nginx server block with `limit_req_zone` throttling, `X-Frame-Options` / `X-Content-Type-Options` / `Referrer-Policy` headers, `/healthz`, and upstream pooling.
- `edgeops/gateway.py` & `edgeops/monitor.py` — Executable reverse proxy (`/proxy/<service>`), Prometheus-format `/metrics`, upstream TCP/HTTP probes, sliding-window rate limiter (`429`), and live web dashboard.

## Running Locally or via Docker
```bash
# With Docker Compose (Linux / Docker Desktop)
cd projects/edgeops && docker compose up --build

# Or execute native Python gateway & SRE console directly
cd projects/edgeops
python -m edgeops.gateway
python -m pytest -v
```
