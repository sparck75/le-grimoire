# 502 Bad Gateway Troubleshooting

## Quick Diagnosis

Run these commands on production to identify the issue:

```bash
# 1. Check container status
docker compose ps

# Look for:
# - Which containers are "Up" vs "Restarting" or "Exited"
# - Health status (healthy vs unhealthy)

# 2. Check backend health
curl -I http://localhost:8000/health

# Should return: HTTP/1.1 200 OK
# If not, backend is down

# 3. Check frontend health  
curl -I http://localhost:3000

# Should return: HTTP/1.1 200 OK
# If not, frontend is down

# 4. Check nginx configuration
docker compose exec nginx nginx -t

# Should say: "syntax is ok"
```

## Common 502 Causes

### Cause 1: Backend Not Running (MongoDB Auth Error)

**Symptoms:**
- Backend container status: "Restarting" or "Exited"
- Backend logs show: "Authentication failed"

**Check:**
```bash
docker compose logs backend | grep -E "Authentication|MongoDB|ERROR"
```

**Fix:**
```bash
# If MongoDB authentication is failing:
docker compose down
docker volume rm le-grimoire_mongodb_data
docker compose up -d
```

### Cause 2: Frontend Not Running

**Symptoms:**
- Frontend container status: "Exited" or "Restarting"
- Nginx logs show: "upstream not found" or "connect() failed"

**Check:**
```bash
docker compose logs frontend | tail -50
```

**Fix:**
```bash
docker compose restart frontend
docker compose logs -f frontend
```

### Cause 3: Nginx Can't Connect to Services

**Symptoms:**
- Backend and Frontend are "Up"
- Nginx logs show: "connect() failed (111: Connection refused)"

**Check:**
```bash
docker compose logs nginx | grep -E "error|failed|refused"
```

**Fix:**
```bash
# Check if services are on the same network
docker compose ps
docker network ls
docker network inspect le-grimoire_grimoire-network

# Restart nginx
docker compose restart nginx
```

### Cause 4: Nginx Configuration Error

**Symptoms:**
- Nginx container "Up" but not working
- nginx -t shows syntax errors

**Check:**
```bash
docker compose exec nginx nginx -t
docker compose exec nginx cat /etc/nginx/nginx.conf | head -50
```

**Fix:**
```bash
# Check nginx config file exists
ls -la nginx/nginx.conf

# Restart with fresh config
docker compose restart nginx
```

## Step-by-Step Debugging

### Step 1: Identify What's Down

```bash
docker compose ps

# Expected output:
# backend    Up       (healthy)
# frontend   Up
# mongodb    Up       (healthy)
# nginx      Up
# db         Up       (healthy)
# redis      Up
```

### Step 2: Check Logs of Down Services

If backend is down:
```bash
docker compose logs backend | tail -100
```

If frontend is down:
```bash
docker compose logs frontend | tail -100
```

### Step 3: Test Direct Access

```bash
# Test backend directly (bypassing nginx)
curl http://localhost:8000/health
curl http://localhost:8000/api/ai/providers

# Test frontend directly (bypassing nginx)
curl http://localhost:3000
```

### Step 4: Check Network Connectivity

```bash
# Check if nginx can resolve service names
docker compose exec nginx ping -c 3 backend
docker compose exec nginx ping -c 3 frontend

# If ping fails, network issue
docker network inspect le-grimoire_grimoire-network
```

## Most Likely Issue (Based on Previous Logs)

Your backend is probably still failing due to MongoDB authentication. Here's the complete fix:

```bash
# 1. Pull latest code with env_file fixes
git pull origin copilot/add-ai-agent-integration

# 2. Verify .env has MongoDB credentials
cat .env | grep MONGODB
# Should show:
# MONGODB_USER=legrimoire
# MONGODB_PASSWORD=9pHOBy6G1_PWF__hYI4QpIe3_TJ8szT4
# MONGODB_URL=mongodb://legrimoire:9pHOBy6G1_PWF__hYI4QpIe3_TJ8szT4@mongodb:27017/legrimoire?authSource=admin
# MONGODB_DB_NAME=legrimoire

# 3. Stop everything
docker compose down

# 4. Remove MongoDB volume (recreate with correct password)
docker volume rm le-grimoire_mongodb_data

# 5. Start everything
docker compose up -d

# 6. Wait 60 seconds for MongoDB to initialize
sleep 60

# 7. Check backend logs
docker compose logs backend | tail -50

# Should see:
# ✅ MongoDB initialized: legrimoire
# INFO:     Application startup complete.

# 8. Test backend
curl http://localhost:8000/health

# Should return: {"status":"ok"}

# 9. Test frontend
curl -I http://localhost:3000

# Should return: HTTP/1.1 200 OK

# 10. Test through nginx
curl -I https://legrimoireonline.ca

# Should return: HTTP/1.1 200 OK (not 502)
```

## Quick Health Check Script

Save as `check-health.sh`:

```bash
#!/bin/bash
echo "=== Container Status ==="
docker compose ps

echo -e "\n=== Backend Health ==="
curl -s http://localhost:8000/health || echo "❌ Backend DOWN"

echo -e "\n=== Frontend Health ==="
curl -I -s http://localhost:3000 | head -1 || echo "❌ Frontend DOWN"

echo -e "\n=== Backend Errors ==="
docker compose logs backend | grep -i error | tail -5

echo -e "\n=== Frontend Errors ==="
docker compose logs frontend | grep -i error | tail -5

echo -e "\n=== Nginx Errors ==="
docker compose logs nginx | grep -i error | tail -5
```

Run: `chmod +x check-health.sh && ./check-health.sh`

## Expected Healthy Output

```
=== Container Status ===
NAME                   STATUS
le-grimoire-backend    Up 5 minutes (healthy)
le-grimoire-frontend   Up 5 minutes
le-grimoire-mongodb    Up 5 minutes (healthy)
le-grimoire-nginx      Up 5 minutes
le-grimoire-db         Up 5 minutes (healthy)
le-grimoire-redis      Up 5 minutes

=== Backend Health ===
{"status":"ok","mongodb":"connected"}

=== Frontend Health ===
HTTP/1.1 200 OK

No errors in logs ✅
```

## If Still 502 After All Steps

1. **Check if using correct compose file:**
   ```bash
   # Are you using docker-compose.yml or docker-compose.prod.yml?
   docker compose ps | head -1
   
   # Container names should match:
   # docker-compose.yml = le-grimoire-backend
   # docker-compose.prod.yml = le-grimoire-backend-prod
   ```

2. **Check nginx.conf points to correct container names:**
   ```bash
   docker compose exec nginx cat /etc/nginx/nginx.conf | grep proxy_pass
   
   # Should show:
   # proxy_pass http://backend:8000;  (or backend-prod for prod compose)
   # proxy_pass http://frontend:3000; (or frontend-prod for prod compose)
   ```

3. **Nuclear option - complete rebuild:**
   ```bash
   docker compose down -v  # Removes all volumes
   docker compose up -d --build --force-recreate
   ```

## Contact

If 502 persists after all steps, provide:
1. Output of: `docker compose ps`
2. Output of: `docker compose logs backend | tail -100`
3. Output of: `docker compose logs frontend | tail -100`
4. Output of: `docker compose logs nginx | tail -50`
5. Output of: `curl -v http://localhost:8000/health`
