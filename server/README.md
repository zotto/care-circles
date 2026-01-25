# Care Circles Server

AI-assisted caregiving coordination system backend powered by CrewAI and FastAPI.

## Overview

This server implements a 5-agent AI pipeline that processes caregiving narratives and generates actionable care plans. The pipeline includes:

- **A1: Intake & Needs Analysis** - Interprets narratives and identifies needs
- **A2: Task Generation** - Creates actionable care tasks
- **A3: Guardian & Quality Pass** - Reviews tasks for safety and appropriateness
- **A4: Optimization** - Refines the care plan for clarity and completeness
- **A5: Review Packet Assembly** - Prepares the plan for human approval

## Architecture

```
┌─────────────┐
│   Frontend  │
│  (Vue.js)   │
└──────┬──────┘
       │ POST /api/care-requests
       ▼
┌─────────────────────────┐
│   FastAPI Server        │
│  ┌──────────────────┐   │
│  │   Job Runner     │   │
│  │   (Async Queue)  │   │
│  └────────┬─────────┘   │
│           │              │
│  ┌────────▼─────────┐   │
│  │ Agent Pipeline   │   │
│  │  A1 → A2 → A3   │   │
│  │  → A4 → A5      │   │
│  └──────────────────┘   │
└─────────────────────────┘
       │
       ▼
  Console Output
```

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- OpenAI API key

## Quick Start

### 1. Install UV (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# Required: OPENAI_API_KEY=sk-your-key-here
```

### 3. Install Dependencies

```bash
# UV automatically creates virtual environment and installs dependencies
uv sync
```

### 4. Run the Server

```bash
# Option 1: Using the run script
uv run python run.py

# Option 2: Using uvicorn directly
uv run uvicorn app.main:app --reload --port 8000

# The server will start on http://localhost:8000
```

## API Endpoints

### Core Endpoints

- **POST** `/api/care-requests` - Submit a new care request
- **GET** `/api/care-requests/{id}` - Get care request details
- **GET** `/api/jobs/{id}` - Get job status
- **GET** `/api/jobs` - List all jobs (debugging)
- **GET** `/health` - Health check
- **GET** `/docs` - Interactive API documentation (development only)

### Example: Create Care Request

```bash
curl -X POST http://localhost:8000/api/care-requests \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "My mom is recovering from hip surgery and needs help with meals and transportation to physical therapy appointments for the next 4 weeks.",
    "constraints": "Weekday afternoons are best for appointments",
    "boundaries": "Please respect that she values privacy and independence"
  }'
```

Response:
```json
{
  "care_request": {
    "id": "req_abc123",
    "narrative": "...",
    "status": "processing",
    "created_at": "2026-01-25T14:30:00Z"
  },
  "job_id": "job_xyz789"
}
```

### Example: Check Job Status

```bash
curl http://localhost:8000/api/jobs/job_xyz789
```

## Project Structure

```
server/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── config/
│   │   ├── settings.py            # Configuration & environment
│   │   └── constants.py           # Application constants
│   ├── api/
│   │   ├── routes/
│   │   │   ├── care_requests.py   # Care request endpoints
│   │   │   └── jobs.py            # Job status endpoints
│   │   └── dependencies.py        # Auth placeholder & deps
│   ├── models/
│   │   ├── domain.py              # Domain entities (Pydantic)
│   │   └── responses.py           # API response models
│   ├── services/
│   │   ├── job_runner.py          # Background job execution
│   │   └── agent_orchestrator.py  # CrewAI pipeline coordinator
│   ├── agents/
│   │   ├── config/
│   │   │   ├── agents.yaml        # Agent definitions
│   │   │   └── tasks.yaml         # Task definitions
│   │   ├── crew_factory.py        # CrewAI factory
│   │   └── output_handlers.py     # Console output formatting
│   └── middleware/
│       ├── cors.py                # CORS configuration
│       ├── error_handlers.py      # Global error handling
│       └── auth_placeholder.py    # Auth stub (for future)
├── pyproject.toml                 # UV project configuration
├── .env.example                   # Environment template
└── run.py                         # Development server launcher
```

## Configuration

All configuration is managed through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4` |
| `API_PORT` | Server port | `8000` |
| `ENVIRONMENT` | Environment name | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:5173,http://localhost:3000` |

## Console Output

The agent pipeline produces rich, colorized console output for each stage:

```
========================================
  AGENT PIPELINE: A1 - Intake & Needs
========================================
Agent: Care Needs Analyst
Started: 2026-01-25 14:30:15 UTC

Summary:
  Primary caregiver recovering from hip surgery...

Identified Needs:
  meals:
    • Dinner preparation for 2 people
    • Grocery shopping weekly
  transportation:
    • Physical therapy appointments 3x/week
    
Risks & Concerns:
  ⚠ mobility: Limited mobility during recovery
  
Assumptions:
  4-week recovery period based on typical hip surgery

✓ Stage Complete
========================================
```

This continues through all 5 stages (A1-A5), providing immediate visibility into the AI-generated care plan.

## Development

### Code Organization

The codebase follows enterprise patterns:

- **Separation of Concerns**: Clear boundaries between API, services, models, and agents
- **Constants Class**: All magic numbers and strings defined in `constants.py`
- **Type Safety**: Pydantic models with validation throughout
- **Dependency Injection**: Ready for testing and database integration
- **Auth Placeholder Pattern**: Authentication hooks in place for future Supabase integration

### Adding New Agents

1. Define agent in `app/agents/config/agents.yaml`
2. Define task in `app/agents/config/tasks.yaml`
3. Add agent name to `app/config/constants.py` → `AgentNames`
4. Add task name to `app/config/constants.py` → `TaskNames`
5. Add stage method in `app/services/agent_orchestrator.py`
6. Update pipeline execution in `run_pipeline()` method

## Future Enhancements

This implementation provides a solid foundation for:

1. **Database Persistence**: Models are ready for Supabase/PostgreSQL integration
2. **Authentication**: Replace `auth_placeholder` with Supabase JWT validation
3. **WebSocket Updates**: Add real-time job status updates
4. **Task Assignment**: Add endpoints for helpers to claim tasks
5. **Approval Workflow**: Implement organizer approval endpoints
6. **Distributed Queue**: Replace in-memory jobs with Celery/Redis if needed

## Troubleshooting

### "Module not found" errors

```bash
# Ensure dependencies are installed
uv sync

# Try cleaning and reinstalling
rm -rf .venv
uv sync
```

### "OpenAI API key not found"

Ensure your `.env` file has the correct API key:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### Port already in use

Change the port in `.env`:
```bash
API_PORT=8001
```

Or specify when running:
```bash
uv run uvicorn app.main:app --reload --port 8001
```

## Testing the Server

### Test with Frontend

If the Vue frontend is running on `http://localhost:5173`, it can make requests to the API:

1. Start the server: `uv run python run.py`
2. Start the frontend: `cd ../www-app && yarn dev`
3. Submit a care request through the UI
4. Monitor console output for agent pipeline execution

### Test with curl

```bash
# Health check
curl http://localhost:8000/health

# Create care request
curl -X POST http://localhost:8000/api/care-requests \
  -H "Content-Type: application/json" \
  -d '{"narrative": "Need help with meal prep and grocery shopping"}'

# Check job status (use job_id from previous response)
curl http://localhost:8000/api/jobs/{job_id}

# List all jobs
curl http://localhost:8000/api/jobs
```

## License

Part of the Care Circles hackathon project.

## Support

For issues or questions, check the console output for detailed error messages and agent pipeline logs.
