# 🚀 Golett Gateway Demo

Welcome to the Golett Gateway demo! This demonstrates a complete end-to-end conversational AI system with persistent memory, CrewAI integration, and business intelligence capabilities.

## 🎯 What This Demo Shows

- **🧠 Persistent Memory**: Dual storage with PostgreSQL + Qdrant for structured and semantic data
- **🤖 Crew-Based AI**: Multi-agent collaboration using CrewAI framework
- **💬 Session Management**: Long-term conversation tracking across sessions
- **📚 Knowledge Integration**: File-based knowledge sources with contextual retrieval
- **🔍 Semantic Search**: Vector-based similarity search for relevant information
- **⚡ Real-time Chat**: Interactive conversation with intelligent agents

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_key_here
```

### 2. Start Services
```bash
# Setup and start all services
./docker-setup.sh setup
./docker-setup.sh start
```

### 3. Install & Test
```bash
# Install the package
pip install -e .

# Quick connectivity test
python test_setup.py

# Run the full demo
python demo_crew_chat.py
```

## 🎮 Demo Features

### System Tests
The demo automatically tests:
- ✅ Memory system (PostgreSQL + Qdrant)
- ✅ Knowledge sources (file-based)
- ✅ Session management
- ✅ Crew chat flow
- ✅ Context storage and retrieval

### Interactive Chat
After tests pass, you can:
- 💬 Chat with the AI system
- 📜 View conversation history
- 📊 Check session information
- 🔍 Ask about Golett Gateway features
- 🤖 Experience multi-agent responses

### Sample Conversations
Try asking:
- "What is Golett Gateway?"
- "How does the memory system work?"
- "Explain the business intelligence features"
- "What are the key architectural components?"

## 🛠 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chat Layer    │    │  Agent Layer    │    │  Memory Layer   │
│                 │    │                 │    │                 │
│ • Session Mgmt  │◄──►│ • CrewAI Agents │◄──►│ • PostgreSQL    │
│ • Flow Control  │    │ • Specialized   │    │ • Qdrant        │
│ • User Interface│    │   Roles         │    │ • Context Mgmt  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Knowledge Layer │
                    │                 │
                    │ • File Sources  │
                    │ • Retrieval     │
                    │ • Integration   │
                    └─────────────────┘
```

## 📁 Key Files

- **`demo_crew_chat.py`** - Main demo script with full system test
- **`test_setup.py`** - Quick connectivity verification
- **`golett/api/main.py`** - FastAPI REST API server
- **`docker-setup.sh`** - Service management script
- **`DEMO_SETUP.md`** - Detailed setup instructions

## 🔧 Troubleshooting

### Common Issues

1. **Services not running**
   ```bash
   ./docker-setup.sh status
   ./docker-setup.sh start
   ```

2. **Import errors**
   ```bash
   pip install -e .
   ```

3. **API key issues**
   ```bash
   # Check .env file
   cat .env | grep OPENAI_API_KEY
   ```

4. **Database connection**
   ```bash
   # Test PostgreSQL
   docker exec -it golett-postgres psql -U golett_user -d golett_db -c "SELECT 1;"
   ```

### Getting Help

- 📋 Check logs: `./docker-setup.sh logs`
- 🔍 Run tests: `python test_setup.py`
- 📖 Read setup guide: `DEMO_SETUP.md`
- 🐛 Check service status: `./docker-setup.sh status`

## 🎯 Next Steps

After running the demo:

1. **🌐 Try the API**: Start the FastAPI server and visit http://localhost:8000/docs
2. **📚 Add Knowledge**: Place your documents in the `knowledge/` directory
3. **🤖 Customize Agents**: Modify agents in `golett/agents/`
4. **🔧 Extend Features**: Add new tools and capabilities
5. **🚀 Production Setup**: Configure for your specific use case

## 📊 Demo Results

The demo will show you:
- System component health checks
- Memory storage and retrieval
- Knowledge source integration
- Session-based conversation tracking
- Multi-agent collaboration
- Real-time interactive chat

Enjoy exploring Golett Gateway! 🎉