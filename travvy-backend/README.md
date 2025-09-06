# Travvy Backend

An advanced AI-powered trip planning platform with real-time collaboration, built with FastAPI and Google Cloud services.

## 🚀 Features

- **AI-Powered Trip Generation**: Intelligent itinerary creation using Google Gemini AI
- **Real-time Collaboration**: Multi-user trip planning with WebSocket support
- **Voice & Image Input**: Process voice commands and analyze images for destinations
- **Smart Optimization**: Route and cost optimization algorithms
- **Scalable Architecture**: Microservices with Celery background processing
- **Google Cloud Integration**: Firestore, Vision API, Speech-to-Text, and more

## 🏗️ Architecture

Based on microservices architecture with:
- **FastAPI** for REST API endpoints
- **Celery** for background task processing
- **Redis** for caching and message brokering
- **Google Cloud Firestore** for database
- **WebSocket** for real-time features
- **Docker** for containerization

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Google Cloud Project with enabled APIs:
  - Firestore
  - Cloud AI Platform
  - Vision API
  - Speech-to-Text API
  - Google Maps API

## 🛠️ Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd travvy-backend
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Celery Monitoring: http://localhost:5555

## 📚 API Documentation

The API documentation is automatically generated and available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Main Endpoints

- `POST /api/v1/auth/google` - Google OAuth authentication
- `POST /api/v1/trips` - Create a new trip
- `GET /api/v1/trips/{trip_id}` - Get trip details
- `POST /api/v1/ai/conversation` - AI conversation for trip planning
- `POST /api/v1/ai/image-analysis` - Analyze images for destinations
- `WebSocket /ws/{trip_id}` - Real-time collaboration

## 🔧 Development

### Running without Docker

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Redis**
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. **Start the API server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start Celery workers**
   ```bash
   celery -A app.core.celery worker --loglevel=info
   ```

5. **Start Celery Beat**
   ```bash
   celery -A app.core.celery beat --loglevel=info
   ```

### Testing

Run tests using pytest:
```bash
pytest tests/ -v
```

### Code Quality

Format code with Black and isort:
```bash
black app/
isort app/
```

Check code quality with flake8:
```bash
flake8 app/
```

## 📁 Project Structure

```
travvy-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/     # API route handlers
│   ├── core/                  # Core functionality
│   │   ├── config.py         # Configuration management
│   │   ├── database.py       # Database connections
│   │   ├── security.py       # Authentication & authorization
│   │   ├── celery.py         # Celery configuration
│   │   └── monitoring.py     # Monitoring utilities
│   ├── services/             # Business logic services
│   ├── tasks/                # Celery background tasks
│   ├── models/               # Pydantic models & schemas
│   ├── websocket/            # WebSocket handlers
│   └── utils/                # Utility functions
├── tests/                    # Test files
├── scripts/                  # Deployment scripts
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile               # Docker image definition
├── requirements.txt         # Python dependencies
└── env.example             # Environment variables template
```

## 🚀 Deployment

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

### Google Cloud Run Deployment

1. **Build and push image**
   ```bash
   docker build -t gcr.io/your-project/travvy .
   docker push gcr.io/your-project/travvy
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy travvy-api \
     --image gcr.io/your-project/travvy \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## 🔒 Security

- JWT-based authentication with Google OAuth integration
- Request validation using Pydantic models
- Rate limiting on API endpoints
- CORS and trusted host middleware
- Input sanitization and SQL injection prevention

## 📊 Monitoring

The application includes comprehensive monitoring:
- Structured logging with JSON format
- Performance metrics tracking
- Health check endpoints
- Celery task monitoring with Flower
- Integration ready for Google Cloud Monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the application logs for debugging

## 🚧 Roadmap

- [ ] Advanced AI model fine-tuning
- [ ] Mobile app integration
- [ ] Offline functionality
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with more travel APIs
