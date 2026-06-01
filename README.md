# CompanyCloud ShopLab

ARM-compatible microservices testbed for **From Gut Feeling to Evidence / CompanyCloud ChangeAudit**.

This is a controlled demo shop built for analytics experiments, not a random demo. It provides a realistic enough service chain while staying simple, reliable, and fully under our control.

## Services

- `frontend` — public entry point
- `catalog` — product list
- `cart` — cart action simulation
- `checkout` — orchestrates catalog/payment/inventory
- `payment` — payment simulation
- `inventory` — stock reservation simulation
- `recommendation` — recommendation simulation
- `worker` — background service

## Experiment endpoints

- `GET /` — app info
- `GET /products?limit=20&delay_ms=50`
- `POST /cart/add`
- `GET /checkout?delay_ms=80`
- `GET /work?delay_ms=100` — controlled latency endpoint
- `GET /cpu?level=low|medium|high` — controlled CPU endpoint
- `GET /health`

## Run

```bash
chmod +x scripts/*.sh
./scripts/deploy.sh
./scripts/port_forward.sh
```

Open `http://SERVER_TAILSCALE_IP:8080`.
