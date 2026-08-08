# VoxPilot AI — Deployment Guide

## 1. Docker Compose Deployment
Launch the full VoxPilot AI platform stack (Backend, Frontend, PostgreSQL, Redis) locally or on cloud instance:

```bash
docker-compose up --build -d
```

Services:
- **Backend API & Voice Engine**: `http://localhost:8000`
- **Web Frontend Studio UI**: `http://localhost` (or `http://localhost:8000/app/`)
- **PostgreSQL Database**: `localhost:5432`
- **Redis Cache**: `localhost:6379`

## 2. Cloud & AWS Deployment
- **ECS / Kubernetes**: Deploy `Dockerfile.backend` container to AWS ECS / Fargate with ALB WebSocket support.
- **S3 / CloudFront**: Serve `frontend/` static assets via CloudFront distribution.
- **RDS PostgreSQL & ElastiCache Redis**: Provision managed PostgreSQL with `pgvector` extension and Redis cluster.
