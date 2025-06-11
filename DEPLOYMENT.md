# Deployment Guide

This guide covers deploying the Django Blog Recommendation System to various production environments.

## Table of Contents

- [Overview](#overview)
- [AWS Deployment](#aws-deployment)
- [DigitalOcean Deployment](#digitalocean-deployment)
- [Google Cloud Platform](#google-cloud-platform)
- [Heroku Deployment](#heroku-deployment)
- [Docker Production](#docker-production)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Logging](#monitoring--logging)

## Overview

### Production Requirements

- **Compute:** 2+ CPU cores, 4GB+ RAM
- **Storage:** 20GB+ SSD storage
- **Database:** PostgreSQL 12+
- **Cache:** Redis 6+
- **Reverse Proxy:** Nginx or Apache
- **SSL Certificate:** Let's Encrypt or commercial

### Architecture Overview

```
Internet -> Load Balancer -> Nginx -> Gunicorn -> Django App
                                 |
                                 +-> Static Files
                                 |
                                 +-> Media Files
         
Database: PostgreSQL
Cache: Redis
Queue: RabbitMQ
Monitoring: Prometheus + Grafana
```

## AWS Deployment

### Prerequisites

- AWS Account
- AWS CLI configured
- Docker installed locally

### Step 1: Create AWS Resources

#### RDS PostgreSQL Database

```bash
# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier blog-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username blogadmin \
    --master-user-password YourSecurePassword123 \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --db-subnet-group-name default
```

#### ElastiCache Redis

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
    --cache-cluster-id blog-redis \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1
```

#### S3 Bucket for Static Files

```bash
# Create S3 bucket
aws s3 mb s3://your-blog-static-files
aws s3 website s3://your-blog-static-files
```

### Step 2: EC2 Instance Setup

```bash
# Launch EC2 instance (Ubuntu 20.04)
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx
```

#### Connect and Setup

```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 3: Application Deployment

```bash
# Clone repository
git clone https://github.com/yourusername/django-blog-recommendation-system.git
cd django-blog-recommendation-system

# Create production environment file
cat > .env.prod << EOF
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ec2-ip
DATABASE_URL=postgresql://blogadmin:YourSecurePassword123@your-rds-endpoint:5432/postgres
REDIS_URL=redis://your-redis-endpoint:6379/0
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-blog-static-files
AWS_S3_REGION_NAME=us-east-1
USE_S3=True
EOF

# Deploy with Docker
docker-compose -f docker-compose.prod.yml up -d
```

### Step 4: Load Balancer Setup

```yaml
# Application Load Balancer
Resources:
  BlogALB:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: blog-alb
      Scheme: internet-facing
      Type: application
      Subnets:
        - subnet-xxxxxxxxx
        - subnet-yyyyyyyyy
      SecurityGroups:
        - sg-xxxxxxxxx
```

## DigitalOcean Deployment

### Step 1: Create Droplet

```bash
# Using doctl CLI
doctl compute droplet create blog-production \
    --size s-2vcpu-4gb \
    --image ubuntu-20-04-x64 \
    --region nyc3 \
    --ssh-keys your-ssh-key-id
```

### Step 2: Managed Database

```bash
# Create managed PostgreSQL database
doctl databases create blog-db \
    --engine pg \
    --version 12 \
    --size db-s-1vcpu-1gb \
    --region nyc3
```

### Step 3: App Platform Deployment

Create `app.yaml`:

```yaml
name: django-blog
services:
- name: web
  source_dir: /
  github:
    repo: yourusername/django-blog-recommendation-system
    branch: main
  run_command: gunicorn wapp.wsgi:application --bind 0.0.0.0:8000
  environment_slug: python
  instance_count: 2
  instance_size_slug: basic-xxs
  envs:
  - key: SECRET_KEY
    value: your-secret-key
  - key: DATABASE_URL
    value: ${db.DATABASE_URL}
  - key: DEBUG
    value: "False"

databases:
- name: db
  engine: PG
  version: "12"
  size: db-s-1vcpu-1gb

static_sites:
- name: static
  source_dir: /static
  index_document: index.html
```

Deploy:
```bash
doctl apps create --spec app.yaml
```

## Google Cloud Platform

### Step 1: Setup GCP Project

```bash
# Create project
gcloud projects create blog-project-id

# Set project
gcloud config set project blog-project-id

# Enable APIs
gcloud services enable cloudsql.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
```

### Step 2: Cloud SQL Database

```bash
# Create Cloud SQL instance
gcloud sql instances create blog-db \
    --database-version=POSTGRES_12 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create blogdb --instance=blog-db

# Create user
gcloud sql users create bloguser \
    --instance=blog-db \
    --password=secure-password
```

### Step 3: App Engine Deployment

Create `app.yaml`:

```yaml
runtime: python39

env_variables:
  SECRET_KEY: "your-secret-key"
  DEBUG: "False"
  DATABASE_URL: "postgresql://bloguser:secure-password@/blogdb?host=/cloudsql/project-id:us-central1:blog-db"
  CLOUD_SQL_CONNECTION_NAME: "project-id:us-central1:blog-db"

beta_settings:
  cloud_sql_instances: "project-id:us-central1:blog-db"

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

Deploy:
```bash
gcloud app deploy
```

## Heroku Deployment

### Step 1: Prepare Application

Create `Procfile`:
```
web: gunicorn wapp.wsgi:application
worker: celery -A wapp worker -l info
```

Create `runtime.txt`:
```
python-3.11.6
```

Update `requirements.txt`:
```bash
# Add Heroku-specific packages
echo "gunicorn" >> wapp/requirements.txt
echo "django-heroku" >> wapp/requirements.txt
echo "psycopg2-binary" >> wapp/requirements.txt
```

### Step 2: Heroku Configuration

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-blog-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-blog-app.herokuapp.com

# Deploy
git push heroku main

# Run migrations
heroku run python wapp/manage.py migrate

# Create superuser
heroku run python wapp/manage.py createsuperuser
```

## Docker Production

### Docker Compose Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      - web

  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    env_file:
      - .env.prod
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: blogdb
      POSTGRES_USER: bloguser
      POSTGRES_PASSWORD: blogpass
    ports:
      - "5432:5432"

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin
    ports:
      - "5672:5672"
      - "15672:15672"

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Production Dockerfile

Create `Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY wapp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY wapp/ .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wapp.wsgi:application"]
```

## Kubernetes Deployment

### Step 1: Create Kubernetes Manifests

#### Namespace
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: blog-system
```

#### ConfigMap
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: blog-config
  namespace: blog-system
data:
  DEBUG: "False"
  ALLOWED_HOSTS: "blog.example.com"
```

#### Secret
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: blog-secrets
  namespace: blog-system
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  DATABASE_URL: <base64-encoded-db-url>
```

#### Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blog-app
  namespace: blog-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: blog-app
  template:
    metadata:
      labels:
        app: blog-app
    spec:
      containers:
      - name: blog-app
        image: your-registry/blog-app:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: blog-config
        - secretRef:
            name: blog-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

#### Service
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: blog-service
  namespace: blog-system
spec:
  selector:
    app: blog-app
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

#### Ingress
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: blog-ingress
  namespace: blog-system
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - blog.example.com
    secretName: blog-tls
  rules:
  - host: blog.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: blog-service
            port:
              number: 80
```

### Step 2: Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Check deployment
kubectl get pods -n blog-system
kubectl get services -n blog-system
kubectl get ingress -n blog-system
```

## CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        cd wapp
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd wapp
        python manage.py test
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/postgres

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: |
        docker build -t blog-app:${{ github.sha }} .
        docker tag blog-app:${{ github.sha }} blog-app:latest
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push blog-app:${{ github.sha }}
        docker push blog-app:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to production
      run: |
        # Deploy using your preferred method
        # SSH to server and update containers
        ssh -o StrictHostKeyChecking=no ${{ secrets.PRODUCTION_HOST }} "
          docker pull blog-app:latest &&
          docker-compose -f docker-compose.prod.yml up -d
        "
```

### GitLab CI/CD

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

variables:
  POSTGRES_DB: test_db
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres

test:
  stage: test
  image: python:3.11
  services:
    - postgres:13
  script:
    - cd wapp
    - pip install -r requirements.txt
    - python manage.py test
  only:
    - main

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main

deploy:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache openssh-client
    - ssh -o StrictHostKeyChecking=no $DEPLOY_USER@$DEPLOY_HOST "
        docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA &&
        docker-compose -f docker-compose.prod.yml up -d
      "
  only:
    - main
```

## Monitoring & Logging

### Prometheus & Grafana

Create `monitoring/docker-compose.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

  node-exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"

volumes:
  grafana-storage:
```

### ELK Stack

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"

  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

## SSL Certificate Setup

### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### SSL with Docker

Create `ssl/nginx.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/static/;
    }

    location /media/ {
        alias /app/media/;
    }
}
```

## Backup Strategy

### Database Backup

```bash
#!/bin/bash
# backup-db.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DATABASE_URL="postgresql://user:pass@host:5432/dbname"

# Create backup
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://your-backup-bucket/
```

### Media Files Backup

```bash
#!/bin/bash
# backup-media.sh

MEDIA_DIR="/app/media"
BACKUP_DIR="/backups/media"
DATE=$(date +%Y%m%d_%H%M%S)

# Create archive
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C $MEDIA_DIR .

# Upload to S3
aws s3 cp $BACKUP_DIR/media_$DATE.tar.gz s3://your-backup-bucket/media/

# Remove old backups
find $BACKUP_DIR -name "media_*.tar.gz" -mtime +7 -delete
```

## Performance Optimization

### Database Optimization

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'OPTIONS': '-c default_transaction_isolation=read_committed'
        },
        'CONN_MAX_AGE': 60,
    }
}

# Connection pooling
DATABASES['default']['OPTIONS']['MAX_CONNS'] = 20
```

### Caching Configuration

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50}
        }
    }
}

# Session engine
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## Security Hardening

### Django Security Settings

```python
# settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_MAX_AGE = 31536000
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
```

### Firewall Configuration

```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

This deployment guide covers the major cloud platforms and deployment strategies. Choose the one that best fits your needs and infrastructure requirements.
