# 🚂 Railway Database Setup Guide

## Why Railway for AI Budget Tracker?

✅ **Perfect fit for this project:**
- PostgreSQL hosting optimized for Python/FastAPI
- Easy GitHub integration for deployment
- Affordable pricing ($5/month for development)
- Automatic backups and monitoring
- Environment variable management
- One-click deployments

## 🚀 Railway Setup Steps

### 1. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub account
3. Connect your GitHub repository

### 2. Create PostgreSQL Database
```bash
# In Railway dashboard:
1. Click "New Project"
2. Choose "Provision PostgreSQL"
3. Database will be created automatically
```

### 3. Get Connection String
```bash
# Railway provides connection string in format:
postgresql://postgres:[password]@[host]:[port]/railway

# Example:
postgresql://postgres:abc123@containers-us-west-123.railway.app:5432/railway
```

### 4. Update Environment Variables
```bash
# Update your .env file:
DATABASE_URL=postgresql://postgres:[your-password]@[your-host]:5432/railway

# Railway also provides individual variables:
PGHOST=[host]
PGPORT=5432
PGDATABASE=railway
PGUSER=postgres
PGPASSWORD=[password]
```

### 5. Deploy Database Schema
```bash
# Option 1: Use Railway's built-in tools
# Upload init.sql through Railway dashboard

# Option 2: Connect locally and run migrations
psql $DATABASE_URL < database/init.sql

# Option 3: Use Alembic migrations (recommended)
cd backend
alembic upgrade head
```

## 🔄 Alternative: Supabase Setup

### Why Supabase?
- Built-in authentication (perfect for user management)
- Real-time subscriptions (for live expense updates)
- Generous free tier
- Built-in APIs

### Supabase Setup:
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Get connection string from Settings > Database
4. Use their SQL editor to run init.sql

## 💰 Cost Comparison

| Service | Free Tier | Paid Tier | Best For |
|---------|-----------|-----------|----------|
| **Railway** | Limited | $5/month | Simple deployment |
| **Supabase** | 500MB, 2 projects | $25/month | Full-stack features |
| **Neon** | 3GB | $19/month | Pure PostgreSQL |
| **AWS RDS** | None | $15-30/month | Enterprise apps |

## 🎯 Recommendation for This Project

**Use Railway because:**
1. **Cost-effective**: $5/month for development
2. **FastAPI-friendly**: Optimized for Python deployments
3. **Simple setup**: Minimal configuration needed
4. **GitHub integration**: Deploy backend + database together
5. **PostgreSQL**: Matches our existing schema

## 🔧 Updated Docker Compose (Development Only)

```yaml
# For local development without database
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}  # Points to Railway
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "19006:19006"
    environment:
      - API_BASE_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
```

## ✅ Next Steps

1. **Choose your service** (Railway recommended)
2. **Set up cloud database**
3. **Update .env with connection string**
4. **Remove local PostgreSQL from docker-compose.yml**
5. **Deploy schema to cloud database**
6. **Test connection from local backend**

This approach gives you:
- 📊 **Production-ready database**
- 🚀 **Easy deployment**
- 💰 **Cost-effective**
- 🔒 **Automatic backups**
- 📈 **Scalability**
