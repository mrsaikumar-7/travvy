# Travvy - AI-Powered Trip Planning Platform

Welcome to Travvy, a comprehensive full-stack application for AI-powered trip planning with real-time collaboration features.

## 🏗️ Repository Structure

This is a **monorepo** containing both the backend and frontend applications:

```
travvy/
├── travvy-backend/          # FastAPI backend application
│   ├── app/                # Main application code
│   ├── Dockerfile         # Backend container configuration
│   ├── requirements.txt   # Python dependencies
│   └── README.md          # Backend-specific documentation
├── travvy-frontend/         # React frontend application
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   └── README.md          # Frontend-specific documentation
├── .gitignore             # Git ignore patterns for both projects
├── LLD_Travvy.md          # Low-level design document
├── PRD_Travvy.md          # Product requirements document
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Google Cloud Platform account (for Firebase/Firestore)

### Development Setup

#### Option 1: Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd travvy
   ```

2. **Start the development environment:**
   ```bash
   # Start both backend and frontend with Docker
   cd travvy-backend
   docker-compose up
   ```

3. **Access the applications:**
   - Backend API: http://localhost:8001
   - Frontend: http://localhost:3000

#### Option 2: Manual Setup

1. **Backend Setup:**
   ```bash
   cd travvy-backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Copy environment variables
   cp env.example .env
   # Edit .env with your configuration
   
   # Start the backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

2. **Frontend Setup:**
   ```bash
   cd travvy-frontend
   npm install
   npm start
   ```

## 🧪 Testing

### Backend Testing
```bash
cd travvy-backend
# Using Docker
docker exec -it dockerfiles-backend-1 bash
python -m pytest tests/

# Or locally
python -m pytest tests/
```

### Frontend Testing
```bash
cd travvy-frontend
npm test
```

## 🔧 Key Features

### Backend (FastAPI)
- **Authentication & Authorization:** JWT-based auth with secure password hashing
- **AI Integration:** Google Gemini Pro for intelligent trip planning
- **Real-time Features:** WebSocket support for live collaboration
- **Database:** Firestore integration for scalable data storage
- **Analytics:** Comprehensive trip and user analytics
- **API Documentation:** Auto-generated OpenAPI/Swagger docs

### Frontend (React)
- **Modern UI:** Responsive design with best UX practices
- **Authentication:** Complete auth flow with JWT token management
- **AI Chat Interface:** Interactive trip planning with AI assistance
- **Real-time Collaboration:** Live trip sharing and editing
- **Trip Management:** Complete CRUD operations for trips
- **Progressive Web App:** PWA capabilities for mobile experience

## 📚 Documentation

- **[Product Requirements Document](./PRD_Travvy.md)** - High-level product specifications
- **[Low-Level Design Document](./LLD_Travvy.md)** - Technical architecture and design
- **[Backend Documentation](./travvy-backend/README.md)** - Backend-specific setup and API docs
- **[Frontend Documentation](./travvy-frontend/README.md)** - Frontend-specific setup and components

## 🔒 Security

- Environment variables for sensitive data
- GCP credentials excluded from version control
- Password hashing with bcrypt
- JWT token-based authentication
- CORS configuration for cross-origin requests

## 🛠️ Development Guidelines

### Code Style
- **Python:** Follow PEP 8, use type hints
- **JavaScript:** Follow ESLint configuration, use modern ES6+ features
- **File Limits:** Max 200-300 lines per file, max 40 lines per function
- **Testing:** Test-driven development approach

### Git Workflow
- Feature branches for new development
- Descriptive commit messages
- Pull request reviews before merging

## 📦 Dependencies

### Backend
- FastAPI for API framework
- Firestore for database
- Google AI (Gemini Pro) for AI features
- JWT for authentication
- WebSocket for real-time features

### Frontend
- React 18+ for UI framework
- React Router for navigation
- Context API for state management
- Axios for API communication

## 🌟 Getting Started with Development

1. **Read the documentation:** Start with PRD and LLD documents
2. **Set up the environment:** Follow the Quick Start guide
3. **Explore the codebase:** Both backend and frontend have modular structures
4. **Run the tests:** Ensure everything works before making changes
5. **Start developing:** Follow the established patterns and conventions

## 📞 Support

For development questions or issues:
1. Check the documentation in each project directory
2. Review the existing issues and PRs
3. Create a new issue with detailed information

## 🚀 Deployment

The application is containerized and ready for deployment on various platforms:
- Google Cloud Platform
- AWS
- Azure
- Docker-based hosting platforms

---

**Happy Coding!** 🎉
