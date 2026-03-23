# Archie Deployment Guide

## Prerequisites

- Python 3.11 or higher
- Git repository access
- GitHub account with API token
- Anthropic API key (Claude)
- Server with public IP (for webhooks)

## Local Development Setup

### 1. Clone and Install

```bash
cd archie
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
GITHUB_TOKEN=ghp_your-token-here
GITHUB_REPO_OWNER=yourusername
GITHUB_REPO_NAME=yourrepo
REPO_PATH=/absolute/path/to/your/codebase
WEBHOOK_SECRET=generate-random-secret-here
EMBEDDINGS_MODEL=all-MiniLM-L6-v2
LANCEDB_PATH=./.lancedb
GRAPH_PERSIST_PATH=./.graph.pkl
LOG_LEVEL=INFO
```

### 3. Test Locally

```bash
# Run tests
pytest tests/ -v

# Run demo
python example_usage.py

# Start server
python -m archie.main
```

Server runs on `http://localhost:8000`

### 4. Index Your Codebase

```bash
curl -X POST http://localhost:8000/index/trigger
```

## Production Deployment

### Option 1: Docker Deployment

#### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install git (needed for GitPython)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "-m", "archie.main"]
```

#### Create docker-compose.yml

```yaml
version: '3.8'

services:
  archie:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - /path/to/your/repo:/repo:ro
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - GITHUB_REPO_OWNER=${GITHUB_REPO_OWNER}
      - GITHUB_REPO_NAME=${GITHUB_REPO_NAME}
      - REPO_PATH=/repo
      - WEBHOOK_SECRET=${WEBHOOK_SECRET}
      - LANCEDB_PATH=/app/data/.lancedb
      - GRAPH_PERSIST_PATH=/app/data/.graph.pkl
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

#### Deploy

```bash
docker-compose up -d
```

### Option 2: Systemd Service (Linux)

#### Create service file

```bash
sudo nano /etc/systemd/system/archie.service
```

```ini
[Unit]
Description=Archie AI Staff Engineer
After=network.target

[Service]
Type=simple
User=archie
WorkingDirectory=/opt/archie
Environment="PATH=/opt/archie/venv/bin"
ExecStart=/opt/archie/venv/bin/python -m archie.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable archie
sudo systemctl start archie
sudo systemctl status archie
```

### Option 3: Cloud Deployment (AWS/GCP/Azure)

#### AWS EC2

1. Launch EC2 instance (t3.medium or larger)
2. Install Python 3.11
3. Clone repository
4. Follow local setup steps
5. Configure security group (allow port 8000)
6. Set up Elastic IP
7. Use systemd or supervisor for process management

#### Google Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/archie

# Deploy
gcloud run deploy archie \
  --image gcr.io/PROJECT_ID/archie \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
```

#### Heroku

```bash
# Create Procfile
echo "web: python -m archie.main" > Procfile

# Deploy
heroku create your-archie-app
heroku config:set ANTHROPIC_API_KEY=your-key
git push heroku main
```

## Webhook Configuration

### Sentry

1. Go to **Settings → Integrations → Webhooks**
2. Add webhook URL: `https://your-server.com/webhook/incident`
3. Add custom header: `X-Signature: your_webhook_secret`
4. Select events: Error, Issue
5. Save

### PagerDuty

1. Go to **Services → Your Service → Integrations**
2. Add **Generic Webhook (v3)**
3. Webhook URL: `https://your-server.com/webhook/incident`
4. Custom headers: `X-Signature: your_webhook_secret`
5. Save

### Slack

1. Create Slack App at api.slack.com/apps
2. Enable **Event Subscriptions**
3. Request URL: `https://your-server.com/webhook/incident`
4. Subscribe to bot events: `message.channels`
5. Install app to workspace

## SSL/TLS Setup

### Using Nginx as Reverse Proxy

```nginx
server {
    listen 80;
    server_name archie.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name archie.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/archie.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/archie.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Get SSL Certificate

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d archie.yourdomain.com
```

## Monitoring

### Health Check

```bash
curl https://your-server.com/health
```

### Logs

```bash
# Systemd
sudo journalctl -u archie -f

# Docker
docker-compose logs -f archie

# File
tail -f /var/log/archie/archie.log
```

### Metrics to Monitor

- API response times
- Indexing duration
- Claude API latency
- GitHub API rate limits
- Disk space (for LanceDB)
- Memory usage
- Error rates

## Backup Strategy

### What to Backup

1. `.lancedb/` - Vector embeddings
2. `.graph.pkl` - Knowledge graph
3. `.env` - Configuration (encrypted)
4. Logs

### Backup Script

```bash
#!/bin/bash
BACKUP_DIR="/backups/archie/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup data
cp -r /opt/archie/.lancedb $BACKUP_DIR/
cp /opt/archie/.graph.pkl $BACKUP_DIR/
cp /opt/archie/.env $BACKUP_DIR/

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Keep only last 7 days
find /backups/archie -name "*.tar.gz" -mtime +7 -delete
```

### Restore

```bash
tar -xzf backup.tar.gz
cp -r backup/.lancedb /opt/archie/
cp backup/.graph.pkl /opt/archie/
```

## Scaling Considerations

### Horizontal Scaling

Archie is currently single-instance. For multiple instances:

1. Use shared storage for LanceDB and graph
2. Implement distributed locking
3. Use message queue for incident processing

### Vertical Scaling

Recommended specs by repo size:

- Small (<1000 files): 2 CPU, 4GB RAM
- Medium (1000-5000 files): 4 CPU, 8GB RAM
- Large (>5000 files): 8 CPU, 16GB RAM

### Database Optimization

For large codebases:
- Increase LanceDB cache size
- Use SSD for storage
- Consider graph partitioning

## Security Checklist

- [ ] Use strong webhook secret (32+ characters)
- [ ] Enable HTTPS/TLS
- [ ] Restrict GitHub token permissions (repo scope only)
- [ ] Keep API keys in environment variables
- [ ] Use firewall to restrict access
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Monitor for suspicious activity
- [ ] Backup encryption keys
- [ ] Use secrets management (AWS Secrets Manager, etc.)

## Maintenance

### Regular Tasks

**Daily:**
- Check logs for errors
- Monitor API rate limits

**Weekly:**
- Review generated PRs
- Check disk space
- Verify backups

**Monthly:**
- Update dependencies
- Review security advisories
- Optimize graph/embeddings

### Updates

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart archie
```

## Troubleshooting Production Issues

### High Memory Usage

```bash
# Check memory
free -h

# Restart service
sudo systemctl restart archie
```

### Slow Indexing

- Check disk I/O
- Increase worker threads
- Use faster storage (SSD)

### Webhook Failures

- Verify signature
- Check network connectivity
- Review logs for errors

### GitHub Rate Limits

- Use GitHub App instead of personal token
- Implement request caching
- Add retry logic with backoff

## Cost Estimation

### Monthly Costs (approximate)

**Infrastructure:**
- AWS t3.medium: ~$30/month
- Storage (100GB): ~$10/month
- Bandwidth: ~$5/month

**APIs:**
- Anthropic Claude: ~$50-200/month (depends on usage)
- GitHub API: Free (within rate limits)

**Total: ~$95-245/month**

## Support

For production issues:
1. Check logs first
2. Review TROUBLESHOOTING.md
3. Check GitHub issues
4. Contact support

## Rollback Plan

If deployment fails:

```bash
# Stop service
sudo systemctl stop archie

# Restore backup
tar -xzf backup.tar.gz
cp -r backup/* /opt/archie/

# Restart
sudo systemctl start archie
```

## Success Criteria

Deployment is successful when:
- [ ] Server starts without errors
- [ ] Health check returns 200
- [ ] Indexing completes successfully
- [ ] Webhooks are received
- [ ] PRs are created automatically
- [ ] Logs show no errors
- [ ] Monitoring is active

---

**Ready for production deployment!**
