# Playwright Docker Configuration

This document describes how to run Playwright tests in Docker environments.

## Running Tests with Docker

### Option 1: Using the existing Docker Compose setup

The simplest way is to use the existing docker-compose setup which already has all services running:

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready
sleep 30

# Run tests from the host (requires Playwright installed locally)
cd frontend
npm test
```

### Option 2: Adding a test service to docker-compose

You can add a dedicated test service to `docker-compose.yml`:

```yaml
  playwright-tests:
    build:
      context: ./frontend
      dockerfile: Dockerfile.playwright
    container_name: le-grimoire-playwright
    depends_on:
      - frontend
      - backend
    environment:
      PLAYWRIGHT_BASE_URL: http://frontend:3000
    volumes:
      - ./frontend/tests:/app/tests
      - ./frontend/playwright-report:/app/playwright-report
      - ./frontend/test-results:/app/test-results
    command: npm test
```

### Option 3: Using Playwright Docker image

You can use the official Playwright Docker image:

```bash
# Pull the Playwright image
docker pull mcr.microsoft.com/playwright:v1.56.1-jammy

# Run tests
docker run --rm \
  --network le-grimoire_default \
  -v $(pwd)/frontend:/app \
  -w /app \
  -e PLAYWRIGHT_BASE_URL=http://frontend:3000 \
  mcr.microsoft.com/playwright:v1.56.1-jammy \
  npm test
```

## CI/CD with Docker

The GitHub Actions workflow uses Docker Compose to orchestrate all services:

1. Starts the entire stack with `docker-compose up -d`
2. Waits for services to be healthy
3. Runs Playwright tests against the running services
4. Collects artifacts (reports, screenshots, videos)
5. Cleans up with `docker-compose down -v`

## Environment Variables for Docker

When running in Docker, make sure to set:

```bash
PLAYWRIGHT_BASE_URL=http://frontend:3000  # Or appropriate service name
```

## Debugging in Docker

To see logs from services during test runs:

```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f frontend
docker-compose logs -f backend
```

## Network Configuration

Tests need to access services on the Docker network. Make sure:

1. All services are on the same Docker network
2. Service names are used as hostnames (e.g., `http://frontend:3000`)
3. Ports are exposed if running tests from the host

## Troubleshooting

### Tests can't connect to services

- Check that all services are running: `docker-compose ps`
- Check that services are on the same network: `docker network ls`
- Verify service URLs are correct for Docker environment

### Browser not found in container

Make sure to install Playwright browsers:

```bash
npx playwright install --with-deps chromium
```

Or use the official Playwright Docker image which has browsers pre-installed.

### Permission issues with volumes

If you encounter permission issues with mounted volumes:

```bash
# Fix ownership
sudo chown -R $(id -u):$(id -g) frontend/test-results frontend/playwright-report
```
