@echo off
echo 🚀 Starting Blog Recommendation Microservices...

REM 
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)

echo 📦 Building and starting all services...
cd blogrecommendation

REM 
docker-compose up --build -d

echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM 
echo 🔍 Checking service status...
docker-compose ps

echo.
echo 📋 Service URLs:
echo   🌐 Django App: http://localhost:8000
echo   🎯 Recommendation Service: http://localhost:8001
echo   🐰 RabbitMQ Management: http://localhost:15672 (admin/admin)
echo   🌐 Nginx Proxy: http://localhost:80
echo.
echo 📊 MongoDB Services:
echo   📂 Event Store: localhost:27017
echo   🎯 Recommendations: localhost:27018
echo   📢 Notifications: localhost:27019
echo   📦 Redis: localhost:6379
echo.
echo ✅ All services are starting up!
echo 💡 Use 'docker-compose logs -f [service_name]' to view logs
echo 💡 Use 'docker-compose down' to stop all services
pause
