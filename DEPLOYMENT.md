# ResumeFit Production Deployment Guide

This guide details deployment options for Railway, Render, Fly.io, AWS ECS, and Docker Compose.

---

## 1. Production Pre-Flight Checklist

Before deploying to public infrastructure, ensure:
- [ ] **Generate Strong JWT Secret**: `openssl rand -hex 32`
- [ ] **Configure Environment Mode**: Set `ENVIRONMENT=production`
- [ ] **Allowed Origins**: Restrict `ALLOWED_CORS_ORIGINS` to your production domain (e.g. `https://resumefit.io`)
- [ ] **Database Connection Pooling**: Ensure `DATABASE_URL` connects over SSL (`sslmode=require`)
- [ ] **Run Database Migrations**: Execute `alembic upgrade head`
- [ ] **Set OpenAI API Key**: Provide a valid `OPENAI_API_KEY` for GPT-4o-mini parsing and embeddings
- [ ] **File Storage Backend**: For distributed containers, set `STORAGE_BACKEND=s3` and configure AWS S3 credentials
- [ ] **SMTP Email**: Configure `EMAIL_PROVIDER=smtp` with production credentials for password reset delivery
- [ ] **Rate Limiting**: Configure Redis backend URL (`REDIS_URL`)

---

## 2. Option A: Docker Compose (Single Host / VPS)

For a DigitalOcean Droplet, AWS EC2, or Linode server:

```bash
# 1. Clone repository
git clone https://github.com/your-username/resume-fit.git
cd resume-fit

# 2. Copy and populate environment variables
cp .env.example .env
nano .env

# 3. Build and launch all services in detached mode
docker compose up -d --build

# 4. Run database migrations
docker compose exec backend alembic upgrade head

# 5. Verify service health
curl -f http://localhost:8000/health
curl -f http://localhost:3000
```

---

## 3. Option B: Railway Deployment

Railway supports multi-service repositories with automatic PostgreSQL and Redis provisioning.

1. **Create Project**: In Railway, click **New Project** &rarr; **Deploy from GitHub repo**.
2. **Add PostgreSQL**: Click **Add Service** &rarr; **Database** &rarr; **PostgreSQL**.
3. **Add Redis**: Click **Add Service** &rarr; **Database** &rarr; **Redis**.
4. **Configure Backend Service**:
   - Root directory: `/backend`
   - Build command: Automatic (Dockerfile)
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Link variables: `DATABASE_URL=${Postgres.DATABASE_URL}`, `REDIS_URL=${Redis.REDIS_URL}`
5. **Configure Frontend Service**:
   - Root directory: `/frontend`
   - Build command: `npm run build`
   - Start command: `npm run start`
   - Variable: `NEXT_PUBLIC_API_URL=https://<your-backend-railway-url>/api/v1`

---

## 4. Option C: Render Deployment

1. **Web Service (Backend)**:
   - Environment: Docker
   - Context: `backend`
   - Health Check Path: `/health`
2. **PostgreSQL Database**: Add managed PostgreSQL instance.
3. **Redis Instance**: Add managed Redis instance.
4. **Web Service (Frontend)**:
   - Environment: Node
   - Build Command: `cd frontend && npm install && npm run build`
   - Start Command: `cd frontend && npm run start`
   - Environment variable: `NEXT_PUBLIC_API_URL=https://<render-backend-url>/api/v1`

---

## 5. Option D: Fly.io Deployment

Deploy backend and frontend independently using `fly launch`:

```bash
# Backend deploy
cd backend
fly launch --name resumefit-backend
fly postgres create
fly redis create
fly deploy

# Frontend deploy
cd ../frontend
fly launch --name resumefit-frontend
fly deploy
```
