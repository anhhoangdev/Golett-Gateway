# Golett Gateway Demo Setup Guide

This guide will help you set up and run the complete Golett Gateway demo, including all required services and the crew chat functionality.

## Quick Start (Recommended)

### 1. Environment Setup

First, copy the environment template and configure your settings:

```bash
cp env.example .env
```

Edit the `.env` file and set your OpenAI API key:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - these have defaults
POSTGRES_CONNECTION=postgresql://golett_user:golett_password@localhost:5432/golett_db
QDRANT_URL=http://localhost:6333
LLM_MODEL=gpt-4o
USER_ID=demo_user
```

### 2. Start Services with Docker

Use the provided setup script to start all required services:

```bash
# Initial setup (creates directories, environment files)
./docker-setup.sh setup

# Start core services (PostgreSQL, Qdrant, Redis)
./docker-setup.sh start

# Or start with admin tools (includes pgAdmin)
./docker-setup.sh start admin

# Or start with development tools (includes Jupyter)
./docker-setup.sh start dev
```

### 3. Install Python Package

Install Golett Gateway in editable mode:

```bash
pip install -e .
```

### 4. Run the Demo

Run the comprehensive demo script:

```bash
python demo_crew_chat.py
```

The demo will:
- ✅ Test all system components
- 🧠 Verify memory system functionality
- 📚 Set up knowledge sources
- 💬 Test session management
- 🤖 Test crew chat flow
- 🎮 Offer an interactive chat demo

## Manual Setup (Alternative)

If you prefer to set up services manually:

### 1. PostgreSQL Setup

```bash
# Using Docker
docker run -d \
  --name golett-postgres \
  -e POSTGRES_DB=golett_db \
  -e POSTGRES_USER=golett_user \
  -e POSTGRES_PASSWORD=golett_password \
  -p 5432:5432 \
  postgres:15-alpine

# Initialize the database
docker exec -i golett-postgres psql -U golett_user -d golett_db < docker/postgres/init.sql
```

### 2. Qdrant Setup

```bash
# Using Docker
docker run -d \
  --name golett-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  qdrant/qdrant:latest
```

### 3. Redis Setup (Optional)

```bash
# Using Docker
docker run -d \
  --name golett-redis \
  -p 6379:6379 \
  redis:7-alpine
```

## API Server (Optional)

To run the FastAPI server:

```bash
# Start the API server
python -m uvicorn golett.api.main:app --host 0.0.0.0 --port 8000 --reload

# Or using Docker
docker-compose up golett-app
```

The API will be available at:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

## Testing the System

### 1. Basic Functionality Test

```bash
python demo_crew_chat.py
```

### 2. API Testing

```bash
# Health check
curl http://localhost:8000/health

# Create a session
curl -X POST "http://localhost:8000/sessions?user_id=test_user" \
  -H "Content-Type: application/json"

# Send a chat message
curl -X POST "http://localhost:8000/sessions/{session_id}/chat" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, what is Golett Gateway?"}'
```

### 3. Individual Component Testing

```bash
# Test simple chat (without crews)
python examples/simple_chat.py

# Test crew-based chat
python examples/crew_chat.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure the package is installed
   pip install -e .
   
   # Check if all dependencies are installed
   pip install -r requirements.txt
   ```

2. **Database Connection Issues**
   ```bash
   # Check if PostgreSQL is running
   docker ps | grep postgres
   
   # Check connection string in .env file
   echo $POSTGRES_CONNECTION
   ```

3. **Qdrant Connection Issues**
   ```bash
   # Check if Qdrant is running
   curl http://localhost:6333/health
   
   # Check Qdrant URL in .env file
   echo $QDRANT_URL
   ```

4. **OpenAI API Issues**
   ```bash
   # Verify API key is set
   echo $OPENAI_API_KEY
   
   # Test API key
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

### Service Management

```bash
# Check service status
./docker-setup.sh status

# View logs
./docker-setup.sh logs
./docker-setup.sh logs postgres  # specific service

# Restart services
./docker-setup.sh restart

# Stop services
./docker-setup.sh stop

# Clean up (removes all data)
./docker-setup.sh cleanup
```

### Database Management

```bash
# Access PostgreSQL directly
docker exec -it golett-postgres psql -U golett_user -d golett_db

# Access pgAdmin (if started with admin profile)
# http://localhost:5050
# Email: admin@golett.local
# Password: admin123
```

## Demo Features

The demo showcases:

### 🧠 Memory Management
- Dual storage (PostgreSQL + Qdrant)
- Session-based conversation tracking
- Context storage and retrieval
- Semantic search capabilities

### 🤖 Crew-Based Chat
- CrewAI integration
- Multi-agent collaboration
- Specialized agent roles
- Decision tracking

### 📚 Knowledge Integration
- File-based knowledge sources
- Contextual information retrieval
- Memory-knowledge fusion

### 💬 Interactive Chat
- Real-time conversation
- Session management
- Message history
- Command interface

## Next Steps

After running the demo successfully:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Customize Agents**: Modify agents in `golett/agents/`
3. **Add Knowledge**: Place documents in the `knowledge/` directory
4. **Extend Functionality**: Add new tools and capabilities
5. **Production Setup**: Configure for your specific use case

## Support

For issues and questions:
- Check the logs: `./docker-setup.sh logs`
- Review the documentation in `docs/`
- Examine the example scripts in `examples/`

Happy chatting with Golett Gateway! 🚀 