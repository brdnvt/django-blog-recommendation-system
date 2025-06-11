# 🚀 Django Blog Recommendation System

A comprehensive, feature-rich blog platform with intelligent recommendation engine, real-time notifications, and advanced analytics. Built with Django, Docker, and microservices architecture.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://djangoproject.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)


## 📋 Table of Contents

- [🌟 Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [🐳 Docker Setup](#-docker-setup)
- [🔧 Configuration](#-configuration)
- [📚 API Documentation](#-api-documentation)
- [🧪 Testing](#-testing)
- [📊 Monitoring](#-monitoring)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🌟 Features

### Core Blog Functionality
- 📝 **Rich Post Creation** - Create and manage blog posts with categories and tags
- 👥 **User Management** - Complete user authentication and profile system
- 💬 **Interactive Comments** - Nested comments with like/dislike functionality
- 🏷️ **Categorization** - Organize posts with categories and tags
- 🔍 **Advanced Search** - Full-text search across posts and comments
- 📱 **Responsive Design** - Mobile-friendly interface

### Advanced Features
- 🎯 **Smart Recommendations** - AI-powered content recommendation engine
- 📊 **Analytics Dashboard** - Real-time analytics and insights
- 🔔 **Real-time Notifications** - Live updates using WebSockets
- 👤 **User Profiles** - Detailed user profiles with follower system
- ❤️ **Social Features** - Like, save, and share functionality
- 📈 **Performance Monitoring** - Built-in profiling with Django Silk

### Technical Features
- 🔐 **JWT Authentication** - Secure API authentication
- 📡 **RESTful API** - Complete REST API with OpenAPI documentation
- 🚀 **Caching System** - Redis-based caching for performance
- 🐰 **Message Queue** - RabbitMQ for asynchronous processing
- 📊 **Database** - PostgreSQL with SQLite fallback
- 🐳 **Containerization** - Docker and Docker Compose ready

## 🏗️ Architecture

The system follows a microservices architecture with the following components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Django App    │    │ Recommendation   │    │   Notification  │
│   (Port 8000)   │────│    Service       │────│    Service      │
│                 │    │   (Port 8001)    │    │   (WebSocket)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────────────┐              │
         │              │   RabbitMQ     │              │
         └──────────────│  (Port 5672)   │──────────────┘
                        └────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────┐
         │                                                     │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     MongoDB      │    │     Redis       │
│   (Main DB)     │    │   (Analytics)    │    │    (Cache)      │
│   (Port 5432)   │    │   (Port 27017)   │    │   (Port 6379)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Service Components

1. **Django Application** - Main web application and API
2. **Recommendation Service** - AI-powered content recommendations
3. **Notification Service** - Real-time notifications
4. **Analytics Service** - Data processing and insights
5. **Moderation Service** - Content moderation and filtering

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/django-blog-recommendation-system.git
cd django-blog-recommendation-system
```

### 2. Start All Services

```bash
# Windows
start-services.bat

# Linux/Mac
./start-services.sh
```

### 3. Access the Application

- **Blog Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/
- **RabbitMQ Management**: http://localhost:15672 (admin/admin)

## 📦 Installation

### Manual Setup

1. **Clone and Setup Virtual Environment**
```bash
git clone https://github.com/yourusername/django-blog-recommendation-system.git
cd django-blog-recommendation-system
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
cd wapp
pip install -r requirements.txt
```

3. **Database Setup**
```bash
python manage.py migrate
python manage.py create_test_data  # Optional: Create sample data
python manage.py createsuperuser
```

4. **Generate JWT Keys**
```bash
python generate_keys.py
```

5. **Run Development Server**
```bash
python manage.py runserver
```

## 🐳 Docker Setup

### Full Microservices Stack

```bash
# Start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f django-app

# Stop all services
docker-compose down
```

### Django Only

```bash
cd wapp
docker build -t django-blog .
docker run -p 8000:8000 django-blog
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/blogdb

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://admin:admin@localhost:5672/

# JWT Settings
JWT_PRIVATE_KEY_PATH=private.key
JWT_PUBLIC_KEY_PATH=public.key

# External APIs
OPENAI_API_KEY=your-openai-key  # Optional: For AI features
```

### Database Configuration

The system supports multiple database backends:

- **SQLite** (Development) - Default
- **PostgreSQL** (Production) - Recommended
- **MySQL** (Alternative)

## 📚 API Documentation

### Authentication

The API uses JWT authentication. Obtain a token:

```bash
POST /api/auth/login/
{
    "username": "your_username",
    "password": "your_password"
}
```

### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/posts/` | GET, POST | Blog posts |
| `/api/posts/{id}/` | GET, PUT, DELETE | Individual post |
| `/api/posts/{id}/like/` | POST | Like/unlike post |
| `/api/posts/{id}/save/` | POST | Save/unsave post |
| `/api/comments/` | GET, POST | Comments |
| `/api/users/` | GET | User list |
| `/api/users/profile/` | GET, PUT | User profile |
| `/api/categories/` | GET | Categories |
| `/api/tags/` | GET | Tags |
| `/api/search/` | GET | Search posts |
| `/api/recommendations/` | GET | Get recommendations |
| `/api/analytics/` | GET | Analytics data |

### Interactive Documentation

Visit http://localhost:8000/api/docs/ for interactive API documentation with Swagger UI.

## 🧪 Testing

### Run Tests

```bash
# Django tests
cd wapp
python manage.py test

# With coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### API Testing

```bash
# Install HTTPie
pip install httpie

# Test API endpoints
http GET localhost:8000/api/posts/
http POST localhost:8000/api/auth/login/ username=admin password=admin
```

## 📊 Monitoring

### Performance Monitoring

- **Django Silk** - http://localhost:8000/silk/
- **System Metrics** - Built-in analytics dashboard
- **Database Profiling** - Query optimization insights

### Health Checks

```bash
# Check service health
curl http://localhost:8000/health/
curl http://localhost:8001/health/

# Database connection
python manage.py check --database default
```

## 🔒 Security Features

- **JWT Authentication** - Secure token-based authentication
- **CSRF Protection** - Cross-site request forgery protection
- **SQL Injection Prevention** - Django ORM protection
- **XSS Protection** - Content sanitization
- **Rate Limiting** - API rate limiting
- **Content Moderation** - Automated content filtering

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
```bash
export DEBUG=False
export ALLOWED_HOSTS=yourdomain.com
export DATABASE_URL=postgresql://...
```

2. **Static Files**
```bash
python manage.py collectstatic
```

3. **Database Migration**
```bash
python manage.py migrate --run-syncdb
```

4. **Web Server**
```bash
# Using Gunicorn
pip install gunicorn
gunicorn wapp.wsgi:application --bind 0.0.0.0:8000
```

### Docker Production

```bash
# Build production image
docker build -f Dockerfile.prod -t django-blog-prod .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Performance Optimization

- **Database Indexing** - Optimized database queries
- **Redis Caching** - Full-page and fragment caching
- **Image Optimization** - Automatic image compression
- **CDN Integration** - Static file delivery
- **Query Optimization** - Django ORM optimization

## 🛠️ Development

### Code Style

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Code formatting
black .
isort .

# Linting
flake8 .
pylint webap/
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## 📱 Frontend Integration

The system provides a complete REST API that can be consumed by:

- **React** - Single Page Application
- **Vue.js** - Progressive Web App
- **Mobile Apps** - iOS/Android applications
- **Third-party Services** - API integrations

## 🔄 CI/CD

### GitHub Actions

```yaml
# .github/workflows/django.yml
name: Django CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python manage.py test
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django Team for the amazing framework
- Django REST Framework for API capabilities
- Docker for containerization
- All contributors and the open-source community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/django-blog-recommendation-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/django-blog-recommendation-system/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/django-blog-recommendation-system/wiki)

---

⭐ **Star this repository if you find it useful!**

