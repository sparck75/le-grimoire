# MongoDB Authentication Error Fix

## Problem
Backend failing to start with error:
```
pymongo.errors.OperationFailure: Authentication failed.
{'ok': 0.0, 'errmsg': 'Authentication failed.', 'code': 18}
```

## Root Cause
MongoDB credentials in production `.env` file don't match the actual MongoDB container configuration.

## Solution

### Step 1: Check Current MongoDB Credentials on Production

```bash
# SSH into production server
ssh legrimoire@149.248.53.57
cd ~/apps/le-grimoire

# Check what MongoDB credentials are set in docker-compose.yml environment
docker compose config | grep -A 5 "MONGO_INITDB"
```

Expected output should show:
```yaml
environment:
  MONGO_INITDB_ROOT_USERNAME: legrimoire
  MONGO_INITDB_ROOT_PASSWORD: grimoire_mongo_password
```

### Step 2: Check Backend Environment Variables

```bash
# Check backend MongoDB connection string
docker compose config | grep MONGODB_URL
```

Should show:
```
MONGODB_URL: mongodb://legrimoire:grimoire_mongo_password@mongodb:27017/legrimoire?authSource=admin
```

### Step 3: Check Production .env File

```bash
# View current .env file
cat .env | grep -E "MONGO|DATABASE_URL"
```

**The `.env` file on the production server MUST have:**
```bash
MONGODB_URL=mongodb://legrimoire:grimoire_mongo_password@mongodb:27017/legrimoire?authSource=admin
MONGODB_DB_NAME=legrimoire
```

### Step 4: Fix the .env File (if needed)

```bash
# Edit production .env
nano .env
```

Add or update these lines:
```bash
# MongoDB Configuration
MONGODB_URL=mongodb://legrimoire:grimoire_mongo_password@mongodb:27017/legrimoire?authSource=admin
MONGODB_DB_NAME=legrimoire
```

**Important:** If your production MongoDB has DIFFERENT credentials, use those instead. The credentials must match what's in `docker-compose.yml` under the `mongodb` service.

### Step 5: Restart Backend

```bash
docker compose restart backend
docker compose logs -f backend
```

Wait for:
```
✅ MongoDB client created: True
✅ MongoDB initialized: legrimoire
INFO:     Application startup complete.
```

### Step 6: Verify Backend is Running

```bash
# Check container status
docker compose ps backend

# Should show "Up" status
# NAME                   IMAGE                  STATUS
# le-grimoire-backend    le-grimoire-backend    Up X seconds

# Test API endpoint
curl http://localhost:8000/api/ai/providers
```

Should return JSON (not 502 error):
```json
{
  "ai_enabled": true,
  "providers": { ... }
}
```

## Alternative: Reset MongoDB (If Password is Lost)

⚠️ **WARNING**: This will delete all data in MongoDB!

```bash
# Stop all containers
docker compose down

# Remove MongoDB volume (deletes all data)
docker volume rm le-grimoire_mongodb_data

# Restart - MongoDB will be recreated with default credentials
docker compose up -d

# Wait 30 seconds for services to start
sleep 30

# Re-import ingredients
docker compose exec backend python scripts/import_off_ingredients.py
```

## Common Mistakes

❌ **Wrong authSource**
```bash
# WRONG - missing authSource
MONGODB_URL=mongodb://legrimoire:password@mongodb:27017/legrimoire

# CORRECT - includes authSource=admin
MONGODB_URL=mongodb://legrimoire:password@mongodb:27017/legrimoire?authSource=admin
```

❌ **Credentials don't match docker-compose.yml**
- Check `docker-compose.yml` `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD`
- `.env` `MONGODB_URL` must use the SAME credentials

❌ **Using localhost instead of container name**
```bash
# WRONG - localhost doesn't work inside Docker
MONGODB_URL=mongodb://legrimoire:password@localhost:27017/legrimoire

# CORRECT - use container name
MONGODB_URL=mongodb://legrimoire:password@mongodb:27017/legrimoire?authSource=admin
```

## Verification Checklist

- [ ] MongoDB container is running: `docker compose ps mongodb` shows "Up"
- [ ] MongoDB health check passing: `docker compose ps mongodb` shows "healthy"
- [ ] Backend `.env` has `MONGODB_URL` with correct credentials
- [ ] Backend `.env` has `authSource=admin` in connection string
- [ ] Backend container restarts successfully
- [ ] Backend logs show "MongoDB initialized"
- [ ] No authentication errors in backend logs
- [ ] API endpoints return data (not 502)

## Quick Check Script

Run this on production to diagnose:

```bash
#!/bin/bash
echo "=== MongoDB Container Status ==="
docker compose ps mongodb

echo -e "\n=== MongoDB Environment (from docker-compose.yml) ==="
docker compose config | grep -A 3 "MONGO_INITDB"

echo -e "\n=== Backend MongoDB Config (from .env) ==="
docker compose config | grep MONGODB

echo -e "\n=== Backend Container Status ==="
docker compose ps backend

echo -e "\n=== Recent Backend Logs ==="
docker compose logs --tail=20 backend | grep -E "MongoDB|Authentication|ERROR"

echo -e "\n=== Test MongoDB Connection ==="
docker compose exec mongodb mongosh \
  -u legrimoire -p grimoire_mongo_password \
  --authenticationDatabase admin \
  --eval "db.adminCommand('ping')"
```

Save as `check-mongodb.sh`, make executable: `chmod +x check-mongodb.sh`, and run: `./check-mongodb.sh`

## Expected Healthy Output

```
✅ MongoDB container: Up (healthy)
✅ Backend logs: "MongoDB initialized: legrimoire"
✅ API responds: 200 OK (not 502)
✅ No authentication errors
```

## Still Not Working?

1. **Check MongoDB logs**:
   ```bash
   docker compose logs mongodb | tail -50
   ```

2. **Try manual MongoDB connection**:
   ```bash
   docker compose exec mongodb mongosh \
     -u legrimoire -p grimoire_mongo_password \
     --authenticationDatabase admin \
     --eval "db.adminCommand('listDatabases')"
   ```

3. **Check if MongoDB created user properly**:
   ```bash
   docker compose exec mongodb mongosh \
     -u legrimoire -p grimoire_mongo_password \
     --authenticationDatabase admin \
     --eval "db.getUsers()" legrimoire
   ```

4. **Recreate MongoDB** (if all else fails - DELETES DATA):
   ```bash
   docker compose stop mongodb backend
   docker volume rm le-grimoire_mongodb_data
   docker compose up -d mongodb
   sleep 20
   docker compose up -d backend
   ```

## Contact

If issue persists after trying all steps, provide:
- Output of `docker compose config | grep MONGODB`
- Output of `docker compose logs backend | tail -100`
- Output of `docker compose logs mongodb | tail -100`
- Contents of `.env` file (redact passwords but show format)
