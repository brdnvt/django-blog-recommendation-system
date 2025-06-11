# Installation Guide

This guide will walk you through setting up the Django Blog Recommendation System on your local machine or server.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Manual Installation](#manual-installation)
- [Docker Installation](#docker-installation)
- [Production Deployment](#production-deployment)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System:** Windows 10+, macOS 10.14+, or Ubuntu 18.04+
- **Python:** 3.11 or higher
- **Node.js:** 16+ (optional, for frontend development)
- **Git:** Latest version

### Required Software

1. **Python 3.11+**
   ```bash
   # Check Python version
   python --version
   # or
   python3 --version
   ```

2. **pip (Python package installer)**
   ```bash
   # Usually comes with Python
   pip --version
   ```

3. **Git**
   ```bash
   git --version
   ```

4. **Docker & Docker Compose** (for containerized setup)
   ```bash
   docker --version
   docker-compose --version
   ```

## Quick Start

### Option 1: Using Start Script (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/django-blog-recommendation-system.git
   cd django-blog-recommendation-system
   ```

2. **Run the start script:**
   ```bash
   # Windows
   start-services.bat
   
   # Linux/macOS
   chmod +x start-services.sh
   ./start-services.sh
   ```

3. **Access the application:**
   - Blog: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs/
   - Admin: http://localhost:8000/admin/ (admin/admin123)

## Manual Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/django-blog-recommendation-system.git
cd django-blog-recommendation-system
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
cd wapp
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file in the `wapp` directory:

```bash
# Copy example environment file
cp .env.example .env

# Edit the file with your settings
nano .env  # or use your preferred editor
```

Example `.env` content:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
```

### Step 5: Generate JWT Keys

```bash
python generate_keys.py
```

This creates `private.key` and `public.key` files for JWT authentication.

### Step 6: Database Setup

```bash
# Apply database migrations
python manage.py migrate

# Create test data (optional)
python manage.py create_test_data

# Create superuser
python manage.py createsuperuser
```

### Step 7: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 8: Run Development Server

```bash
python manage.py runserver
```

The application will be available at http://localhost:8000

## Docker Installation

### Prerequisites for Docker Setup

- Docker Engine 20.10+
- Docker Compose 2.0+

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/django-blog-recommendation-system.git
cd django-blog-recommendation-system
```

### Step 2: Environment Configuration

Create `.env` file in the project root:

```bash
cp .env.docker.example .env
```

Edit the `.env` file with your configuration.

### Step 3: Build and Start Services

```bash
# Build and start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f django-app
```

### Step 4: Initialize Database

```bash
# Run migrations
docker-compose exec django-app python manage.py migrate

# Create test data
docker-compose exec django-app python manage.py create_test_data

# Create superuser
docker-compose exec django-app python manage.py createsuperuser
```

### Services Overview

After running `docker-compose up`, the following services will be available:

- **Django App:** http://localhost:8000
- **Recommendation Service:** http://localhost:8001
- **RabbitMQ Management:** http://localhost:15672 (admin/admin)
- **Nginx Proxy:** http://localhost:80
- **MongoDB:** localhost:27017
- **Redis:** localhost:6379

## Production Deployment

### Prerequisites

- VPS or cloud server (AWS, DigitalOcean, etc.)
- Domain name (optional)
- SSL certificate (recommended)

### Step 1: Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### Step 2: Application Setup

```bash
# Clone repository
git clone https://github.com/yourusername/django-blog-recommendation-system.git
cd django-blog-recommendation-system

# Create production environment
python3 -m venv venv
source venv/bin/activate
pip install -r wapp/requirements.txt
```

### Step 3: Production Configuration

Create production `.env` file:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/blogdb
REDIS_URL=redis://localhost:6379/0
STATIC_ROOT=/var/www/django-blog/static/
MEDIA_ROOT=/var/www/django-blog/media/
```

### Step 4: Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres createdb blogdb
sudo -u postgres createuser bloguser
sudo -u postgres psql -c "ALTER USER bloguser PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE blogdb TO bloguser;"

# Run migrations
cd wapp
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 5: Nginx Configuration

Create `/etc/nginx/sites-available/django-blog`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /static/ {
        alias /var/www/django-blog/static/;
    }

    location /media/ {
        alias /var/www/django-blog/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/django-blog /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Systemd Service

Create `/etc/systemd/system/django-blog.service`:

```ini
[Unit]
Description=Django Blog Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/django-blog-recommendation-system/wapp
Environment=PATH=/path/to/django-blog-recommendation-system/venv/bin
EnvironmentFile=/path/to/django-blog-recommendation-system/.env
ExecStart=/path/to/django-blog-recommendation-system/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wapp.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable django-blog
sudo systemctl start django-blog
```

### Step 7: SSL Certificate (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Django secret key | None | Yes |
| `DEBUG` | Debug mode | False | No |
| `ALLOWED_HOSTS` | Allowed hosts | localhost | Yes |
| `DATABASE_URL` | Database connection string | sqlite:///db.sqlite3 | No |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 | No |
| `RABBITMQ_URL` | RabbitMQ connection string | amqp://localhost:5672/ | No |
| `STATIC_ROOT` | Static files directory | static/ | No |
| `MEDIA_ROOT` | Media files directory | media/ | No |

### Database Configuration

#### SQLite (Development)
```env
DATABASE_URL=sqlite:///db.sqlite3
```

#### PostgreSQL (Production)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

#### MySQL
```env
DATABASE_URL=mysql://user:password@localhost:3306/dbname
```

### Cache Configuration

#### Redis
```env
REDIS_URL=redis://localhost:6379/0
```

#### Memcached
```env
CACHE_URL=memcached://localhost:11211
```

## Troubleshooting

### Common Issues

#### 1. Module Not Found Error

**Problem:** `ModuleNotFoundError: No module named 'webap'`

**Solution:**
```bash
# Make sure you're in the correct directory
cd wapp
python manage.py runserver
```

#### 2. Database Connection Error

**Problem:** `django.db.utils.OperationalError: could not connect to server`

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if not running
sudo systemctl start postgresql

# Check database configuration in .env file
```

#### 3. Permission Denied Error

**Problem:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER /path/to/project
chmod +x manage.py
```

#### 4. Port Already in Use

**Problem:** `Error: That port is already in use.`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
python manage.py runserver 8001
```

#### 5. Static Files Not Loading

**Problem:** CSS/JS files not loading in production

**Solution:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT and STATIC_URL settings
# Ensure Nginx is configured to serve static files
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs:**
   ```bash
   # Django logs
   tail -f /var/log/django-blog/django.log
   
   # Nginx logs
   sudo tail -f /var/log/nginx/error.log
   
   # Docker logs
   docker-compose logs -f django-app
   ```

2. **GitHub Issues:** [Report an issue](https://github.com/yourusername/django-blog-recommendation-system/issues)

3. **Documentation:** Check the [Wiki](https://github.com/yourusername/django-blog-recommendation-system/wiki)

4. **Community:** Join our [Discussions](https://github.com/yourusername/django-blog-recommendation-system/discussions)

## Next Steps

After successful installation:

1. **Explore the Admin Panel:** http://localhost:8000/admin/
2. **Read the API Documentation:** http://localhost:8000/api/docs/
3. **Check Performance Monitoring:** http://localhost:8000/silk/
4. **Configure Recommendations:** See [Configuration Guide](CONFIGURATION.md)
5. **Set up Monitoring:** See [Monitoring Guide](MONITORING.md)
