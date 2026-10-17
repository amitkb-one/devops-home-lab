# Docker & Docker Compose — Hands-on Learning Handbook

**DevOps Home Lab | Labs 06A–06D | 17 October 2026**

This document records lessons and commands before Lab 06E. Lab 06D deployment is not yet confirmed as completed.

## 1. Learning journey and scope

### What we completed

Lab 06A: Docker installation, image/container fundamentals, hello-world and Nginx. Lab 06B: Dockerfile and FastAPI image. Lab 06C: custom networking, PostgreSQL persistence, application connectivity and authentication troubleshooting. Lab 06D: three-service Docker Compose with PostgreSQL, Redis and FastAPI. Compose validation was still being debugged in the latest exchange; successful deployment has not yet been confirmed.

### Environment

Apple Silicon Mac mini Pro (48 GB RAM), macOS, Docker Desktop, VS Code, Git/GitHub. Repository: devops-home-lab; local project path used most recently: ~/dev/devops-lab/04-docker/compose-lab. Confirm the actual path on your machine.

## 2. Core Docker concepts

### Image vs container

An image is an immutable, layered application package. A container is a running or stopped instance created from an image. One image can create multiple containers.

### Registry, repository, tag

A registry stores images; an image repository groups related images; a tag identifies a version reference (not necessarily immutable). Example: postgres:17. Image digests provide stronger reproducibility.

### Dockerfile

A Dockerfile specifies build steps such as FROM, WORKDIR, COPY, RUN, USER, EXPOSE and CMD. Build context limits what COPY can access; .dockerignore excludes unnecessary and sensitive files.

### Networking

Containers have their own network namespaces. localhost inside FastAPI means FastAPI's own container, not PostgreSQL. Containers on a user-defined bridge or Compose network can resolve each other by name.

### Ports

-p 127.0.0.1:8002:8000 publishes container port 8000 to local Mac port 8002. No published port is required for API-to-database communication on the same Docker network.

### Volumes

Named volumes persist data independently of a container. Bind mounts map host paths to container paths. docker compose down retains named volumes; down -v removes project volumes.

## 3. Lab 06A: First containers

### Commands

```bash
docker version
docker run --rm hello-world
docker run -d --name devops-nginx -p 8080:80 nginx:alpine
docker ps
docker logs devops-nginx
docker stop devops-nginx
docker rm devops-nginx
```

### Learning

docker run creates and starts a container; -d detaches; --name names it; -p publishes a port; --rm deletes an exited container. docker ps shows running containers; docker ps -a includes stopped containers.

## 4. Lab 06B: Containerizing FastAPI

### Workflow

Write main.py, requirements.txt, Dockerfile and .dockerignore; build with docker build -t devops-fastapi:1.0 .; run with docker run -d --name <name> -p 8000:8000 devops-fastapi:1.0; test curl http://localhost:8000/health.

### Dockerfile example

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build lesson

Copy dependency manifests before source files to improve layer-cache reuse. Run as a non-root user where practical. EXPOSE documents a port; it does not publish it.

## 5. Lab 06C: PostgreSQL, network and persistence

### Infrastructure commands

```bash
docker network create devops-net
docker volume create devops-postgres-data
docker run -d --name devops-postgres --network devops-net --mount type=volume,source=devops-postgres-data,target=/var/lib/postgresql/data -e POSTGRES_USER=devops -e POSTGRES_DB=devopsdb -e POSTGRES_PASSWORD="$(cat ~/devops-lab-secrets/postgres-password)" postgres:17
```

### Schema

```sql
CREATE TABLE IF NOT EXISTS tasks (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'OPEN',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### API connection

Use DB_HOST=devops-postgres, DB_NAME=devopsdb, DB_USER=devops and DB_PASSWORD from the password file; never use localhost for cross-container database connections.

### Troubleshooting case

The /health endpoint returned HTTP 503 with Database unavailable. A direct psycopg connection showed FATAL: password authentication failed for user devops. This proved container DNS and TCP connectivity worked; credentials were mismatched.

### Resolution pattern

Check container readiness, network membership, DNS and direct DB authentication. PostgreSQL's POSTGRES_PASSWORD only initializes a fresh data directory; changing it later does not reset the stored database password. ALTER ROLE can change the existing password. Recreate the API container to refresh environment variables; docker restart does not refresh them. Preserve database volumes.

## 6. Lab 06D: Docker Compose architecture

### Purpose

Compose declares an application consisting of api, db and redis services, a default internal network and two named volumes. API is published to 127.0.0.1:8002, while db and redis remain internal.

### Project and services

name: devops-compose-lab gives the project a resource namespace. services: holds db, redis and api, all indented at the same level. Top-level volumes: declares postgres_data and redis_data.

### PostgreSQL

postgres:17; POSTGRES_USER, POSTGRES_DB, POSTGRES_PASSWORD; persistent mount postgres_data:/var/lib/postgresql/data; read-only bind mount ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro. Initialization scripts execute only for a fresh database directory.

### Redis

redis:7-alpine; command [redis-server, --appendonly, yes]; redis_data:/data; redis-cli ping health check. In this lab Redis holds an API request counter.

### API

Build from local Dockerfile; image devops-compose-api:1.0; publish 127.0.0.1:${APP_PORT:-8002}:8000; DB_HOST=db and REDIS_HOST=redis. Compose DNS resolves service names.

### Health and startup

pg_isready and redis-cli ping are container health checks. depends_on with condition: service_healthy delays initial API startup until dependencies report healthy; it does not guarantee continued health or automatic restart on dependency failure.

### Restart policy

restart: unless-stopped restarts exited containers according to Docker policy, but an unhealthy status alone does not restart a container.

### Variable syntax

${POSTGRES_USER} is resolved by Compose from its environment or .env. $$POSTGRES_USER passes a literal $ to a command running in the container. ${APP_PORT:-8002} uses 8002 if APP_PORT is unset or empty.

## 7. Reference Compose file

### compose.yaml

```yaml
name: devops-compose-lab

services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \"$$POSTGRES_USER\" -d \"$$POSTGRES_DB\""]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  api:
    build:
      context: .
      dockerfile: Dockerfile
    image: devops-compose-api:1.0
    ports:
      - "127.0.0.1:${APP_PORT:-8002}:8000"
    environment:
      DB_HOST: db
      DB_NAME: ${POSTGRES_DB}
      DB_USER: ${POSTGRES_USER}
      DB_PASSWORD: ${POSTGRES_PASSWORD}
      REDIS_HOST: redis
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### .env.example

```bash
POSTGRES_USER=devops
POSTGRES_DB=devopsdb
POSTGRES_PASSWORD=replace-with-local-secret
APP_PORT=8002
```

### Security

Keep .env out of Git. The environment method is for local labs; environment values can be exposed through container inspection. Do not paste docker compose config output publicly because it may include secrets. Redis is unauthenticated in this isolated lab.

## 8. Compose validation errors and fixes

### Missing environment variables

Warnings that POSTGRES_USER, POSTGRES_DB or POSTGRES_PASSWORD are unset mean Compose could not resolve them. Ensure .env exists alongside compose.yaml or pass --env-file explicitly. Confirm filename and current directory.

### Typo

POSTRES_USER is a misspelling of POSTGRES_USER; correct the variable name everywhere.

### Additional properties api not allowed

Usually api: was indented at the top level instead of under services:. YAML indentation defines hierarchy; db, redis and api must be siblings under services.

### Undefined volume postgres data

A service mount referred to postgres data (with a space), but the declared named volume was postgres_data (underscore). Use exactly the same name in the service mount and top-level volumes declaration.

### Validate safely

```bash
docker compose config --quiet
docker compose config --services
docker compose config --volumes
Avoid sharing unredacted docker compose config because it can reveal secrets.
```

## 9. Operational command reference

### Lifecycle

```bash
docker compose up -d --build
docker compose ps
docker compose logs --tail=30 api
docker compose logs -f
docker compose stop
docker compose start
docker compose down
```

### Inspect and test

```bash
docker compose exec redis redis-cli ping
docker compose exec db psql -U devops -d devopsdb -c '\dt'
curl -i http://localhost:8002/health
curl http://localhost:8002/tasks
curl http://localhost:8002/metrics
```

### Persistence exercise

Create a task; run docker compose down; then docker compose up -d and verify the task remains. Do not run docker compose down -v unless intentionally deleting the project's persistent data.

### Failure drill

docker compose stop db; verify /health returns 503; docker compose start db; wait until healthy; verify /health returns 200. This demonstrates the difference between process running, dependency health and application health.

## 10. Readiness checklist before Lab 06E

### Validation

[ ] compose.yaml validates without warnings
[ ] docker compose config --services lists db, redis and api
[ ] docker compose config --volumes lists postgres_data and redis_data

### Deployment

[ ] docker compose up -d --build succeeds
[ ] docker compose ps shows all three services running
[ ] GET /health returns HTTP 200 with database connected
[ ] POST /tasks and GET /tasks work
[ ] GET /metrics returns a Redis-backed count

### Operational safety

[ ] Database data survives docker compose down / up
[ ] .env is ignored by Git and not committed
[ ] Project changes committed to a feature branch and reviewed

### Next topic

Lab 06E: container registries, image tagging and pushing, GitHub Container Registry, vulnerability scanning, multi-platform builds (Apple Silicon arm64 vs Linux amd64), digests, and supply-chain security.
