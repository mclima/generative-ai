# Task Maestro

A sophisticated AI-powered task management assistant built with LangGraph that helps users create, organize, and manage their ToDo lists with intelligent memory capabilities.

**Live Demo:** https://generative-ai-production.up.railway.app/docs

## Features

- **Intelligent Task Management**: Automatically extracts and organizes tasks from natural conversation
- **User Profile Memory**: Maintains context about the user (name, location, job, connections, interests)
- **Smart ToDo Lists**: Tracks tasks with:
  - Task descriptions
  - Estimated completion time
  - Deadlines
  - Actionable solutions
  - Status tracking (not started, in progress, done, archived)
- **Adaptive Learning**: Learns user preferences for how they like tasks to be managed
- **Multi-Category Support**: Organize tasks by different categories
- **Persistent Memory**: Uses LangGraph's store for long-term memory across sessions

## Architecture

Task Maestro uses a graph-based architecture with LangGraph:

1. **task_mAIstro**: Main chatbot node that loads memories and decides what to update
2. **update_profile**: Updates user profile information
3. **update_todos**: Manages the ToDo list using Trustcall for structured extraction
4. **update_instructions**: Learns and adapts to user preferences

The system uses three memory namespaces:
- `profile`: User information
- `todo`: Task list items
- `instructions`: User preferences for task management

## Tech Stack

- **LangGraph**: State graph orchestration
- **LangChain**: LLM integration and tooling
- **OpenAI GPT-4o**: Language model
- **Trustcall**: Structured information extraction
- **Pydantic**: Data validation and schemas

## Installation

### Prerequisites

- Python 3.11+
- OpenAI API key

### Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd task-maestro
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

4. Run the application:
```bash
python task_maistro.py
```

### Docker Setup

1. Build the Docker image:
```bash
docker build -t task-maestro .
```

2. Run with docker-compose:
```bash
docker-compose up
```

## Configuration

The application can be configured through the `Configuration` class in `configuration.py`:

- `user_id`: Unique identifier for the user (default: "default-user")
- `todo_category`: Category for organizing tasks (default: "general")
- `task_maistro_role`: System role/personality for the assistant

## Usage

Task Maestro works through natural conversation. Simply chat with it about your tasks:

```
User: "I need to finish the project report by Friday"
Task Maestro: [Automatically creates a task with deadline]

User: "I'm interested in learning Python and machine learning"
Task Maestro: [Updates user profile with interests]

User: "Always add at least 3 solutions when creating tasks"
Task Maestro: [Learns this preference for future task creation]
```

## API Endpoints

When deployed, the application exposes LangGraph API endpoints for:
- Streaming conversations
- Managing memory stores
- Accessing task history

See the [API documentation](https://generative-ai-production.up.railway.app/docs) for details.

## Project Structure

```
task-maestro/
├── task_maistro.py      # Main application logic and graph definition
├── configuration.py      # Configuration schema
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Docker compose setup
├── langgraph.json       # LangGraph configuration
└── README.md           # This file
```

## Development

The application uses:
- **Pydantic models** for schema validation (`Profile`, `ToDo`)
- **LangGraph StateGraph** for conversation flow
- **Trustcall extractors** for intelligent information extraction
- **InMemoryStore** for development (can be replaced with persistent storage)

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]