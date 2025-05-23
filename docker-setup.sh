#!/bin/bash

# Golett Gateway Docker Setup Script
# This script helps you set up and run all required services for Golett Gateway

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    if ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are available"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p knowledge
    mkdir -p data
    mkdir -p notebooks
    
    print_success "Directories created"
}

# Function to check and create .env file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            print_warning "Created .env file from env.example"
            print_warning "Please edit .env file and add your OpenAI API key and other configurations"
        else
            print_error "env.example file not found. Cannot create .env file."
            exit 1
        fi
    else
        print_success ".env file already exists"
    fi
    
    # Check if OpenAI API key is set
    if grep -q "your_openai_api_key_here" .env; then
        print_warning "Please update your OpenAI API key in the .env file"
        read -p "Do you want to edit the .env file now? (y/n): " edit_env
        if [ "$edit_env" = "y" ] || [ "$edit_env" = "Y" ]; then
            ${EDITOR:-nano} .env
        fi
    fi
}

# Function to create sample knowledge files
create_sample_knowledge() {
    print_status "Creating sample knowledge files..."
    
    if [ ! -f knowledge/sample.txt ]; then
        cat > knowledge/sample.txt << EOF
# Golett Gateway Knowledge Base

## Overview
Golett Gateway is a modular, long-term conversational agent framework built on CrewAI with enhanced memory and BI capabilities.

## Key Features
- Persistent context across multiple chat sessions
- Dual storage backend (PostgreSQL + Qdrant) for different data types
- Semantic search capabilities for contextual retrieval
- Decision tracking and reasoning storage
- Modular agent architecture with specialized roles

## Architecture
The system uses a multi-layered architecture:
1. Memory Layer: PostgreSQL for structured data, Qdrant for vector storage
2. Agent Layer: CrewAI-based agents for different specialized tasks
3. Chat Layer: Session management and conversation flow
4. Knowledge Layer: Document processing and retrieval

## Usage
Golett Gateway can be used for various applications including:
- Business Intelligence query processing
- Long-term conversational AI
- Knowledge management systems
- Multi-agent collaboration scenarios
EOF
        print_success "Created sample knowledge file"
    else
        print_status "Sample knowledge file already exists"
    fi
}

# Function to start services
start_services() {
    local profile="$1"
    
    print_status "Starting Golett Gateway services..."
    
    if [ -n "$profile" ]; then
        print_status "Using profile: $profile"
        docker compose --profile "$profile" up -d
    else
        docker compose up -d postgres qdrant redis
    fi
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    check_service_health
}

# Function to check service health
check_service_health() {
    print_status "Checking service health..."
    
    # Check PostgreSQL
    if docker compose exec -T postgres pg_isready -U golett_user -d golett_db &> /dev/null; then
        print_success "PostgreSQL is ready"
    else
        print_warning "PostgreSQL is not ready yet"
    fi
    
    # Check Qdrant
    if curl -s http://localhost:6333/health &> /dev/null; then
        print_success "Qdrant is ready"
    else
        print_warning "Qdrant is not ready yet"
    fi
    
    # Check Redis
    if docker compose exec -T redis redis-cli ping &> /dev/null; then
        print_success "Redis is ready"
    else
        print_warning "Redis is not ready yet"
    fi
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    docker compose ps
    
    echo ""
    print_status "Service URLs:"
    echo "  PostgreSQL: localhost:5432"
    echo "  Qdrant: http://localhost:6333"
    echo "  Redis: localhost:6379"
    echo "  pgAdmin (if enabled): http://localhost:5050"
    echo "  Jupyter (if enabled): http://localhost:8888"
    echo "  Golett API (if enabled): http://localhost:8000"
}

# Function to stop services
stop_services() {
    print_status "Stopping Golett Gateway services..."
    docker compose down
    print_success "Services stopped"
}

# Function to clean up (remove volumes)
cleanup() {
    print_warning "This will remove all data including databases!"
    read -p "Are you sure you want to continue? (y/N): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        print_status "Cleaning up services and volumes..."
        docker compose down -v
        docker system prune -f
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Function to show logs
show_logs() {
    local service="$1"
    if [ -n "$service" ]; then
        docker compose logs -f "$service"
    else
        docker compose logs -f
    fi
}

# Function to show help
show_help() {
    echo "Golett Gateway Docker Setup Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start [profile]    Start services (optional profile: admin, dev)"
    echo "  stop              Stop services"
    echo "  restart           Restart services"
    echo "  status            Show service status"
    echo "  logs [service]    Show logs (optional: specific service)"
    echo "  cleanup           Remove all data and volumes"
    echo "  setup             Initial setup (create dirs, env file)"
    echo "  help              Show this help message"
    echo ""
    echo "Profiles:"
    echo "  admin             Include pgAdmin for database management"
    echo "  dev               Include Jupyter for development"
    echo ""
    echo "Examples:"
    echo "  $0 setup          # Initial setup"
    echo "  $0 start          # Start core services"
    echo "  $0 start admin    # Start with pgAdmin"
    echo "  $0 start dev      # Start with Jupyter"
    echo "  $0 logs postgres  # Show PostgreSQL logs"
}

# Main script logic
case "$1" in
    "setup")
        check_docker
        create_directories
        setup_environment
        create_sample_knowledge
        print_success "Setup completed! Run '$0 start' to start services."
        ;;
    "start")
        check_docker
        start_services "$2"
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 2
        start_services "$2"
        show_status
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$2"
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        print_error "No command specified"
        show_help
        exit 1
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 