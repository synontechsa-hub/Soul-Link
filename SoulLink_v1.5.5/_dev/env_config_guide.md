# SoulLink v1.5.5 - Environment Configuration Guide

## 📋 Required Environment Variables

### Backend (.env in root)

#### Essential

- `GROQ_API_KEY` - Your Groq API key for LLM
- `SUPABASE_DB_URL` - PostgreSQL connection string (pooler)
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_JWT_SECRET` - JWT verification secret
- `ARCHITECT_UUID` - Your admin user UUID

#### Configuration

- `SOULLINK_DEBUG` - Set to `1` for debug mode, `0` for production
- `VERSION` - Current version (1.5.5)
- `ENVIRONMENT` - `development` or `production`
- `PRODUCTION_FRONTEND_URL` - Frontend URL for CORS (production only)

#### Optional

- `SENTRY_DSN` - Sentry error tracking DSN
- `ENABLE_REDIS_CACHE` - Enable Redis caching (default: False)
- `REDIS_URL` - Redis connection string (if enabled)

### Frontend (frontend/.env)

#### Essential

- `SUPABASE_URL` - Same as backend
- `SUPABASE_ANON_KEY` - Same as backend
- `API_BASE_URL` - Backend API URL

#### Development

```bash
API_BASE_URL=http://127.0.0.1:8000
```

#### Production

```bash
API_BASE_URL=https://your-production-api.com
```

## ✅ Current Status

Both .env files have been updated with:

- ✅ API_BASE_URL added to frontend (required for AppConfig)
- ✅ ENVIRONMENT variable added to backend
- ✅ PRODUCTION_FRONTEND_URL placeholder added
- ✅ SENTRY_DSN format fixed
- ✅ VERSION updated to 1.5.5

## 🚀 Deployment Checklist

### Before Production Deployment

1. **Backend .env**:
   - [ ] Set `ENVIRONMENT=production`
   - [ ] Set `SOULLINK_DEBUG=0`
   - [ ] Set `PRODUCTION_FRONTEND_URL` to your frontend domain
   - [ ] Verify `SENTRY_DSN` is correct

2. **Frontend .env**:
   - [ ] Update `API_BASE_URL` to production backend URL
   - [ ] Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct

3. **Security**:
   - [ ] Never commit .env files to git
   - [ ] Use environment variables in CI/CD
   - [ ] Rotate keys if accidentally exposed

## 📝 Notes

- The frontend AppConfig will use `API_BASE_URL` from .env
- Backend CORS will allow `PRODUCTION_FRONTEND_URL` in production mode
- All hardcoded localhost URLs have been replaced with AppConfig
