# Multi-Agent Video Generation System

A multi-agent system for automated AI video generation, built with LangGraph.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ CLI Tool    │  │ Streamlit   │  │ Python API  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    Agent Layer (LangGraph)                   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SupervisorAgent                         │    │
│  │         (Orchestrates workflow)                      │    │
│  └──────────┬──────────┬──────────┬─────────────────────┘    │
│             │          │          │                          │
│  ┌──────────▼───┐ ┌────▼─────┐ ┌──▼──────────┐              │
│  │ StoryWriter  │ │ Director │ │ VideoProducer│              │
│  │ Agent        │ │ Agent    │ │ Agent        │              │
│  │              │ │          │ │              │              │
│  │ - Outline    │ │ - Story- │ │ - Video      │              │
│  │ - Characters │ │   board  │ │   prompts    │              │
│  │ - Episodes   │ │ - Shots  │ │ - Generation │              │
│  └──────────────┘ └──────────┘ └──────────────┘              │
└────────────────────────────┬────────────────────────────────┘
                             │ Loads Skills
┌────────────────────────────▼────────────────────────────────┐
│                      Skills (Knowledge)                      │
│  writing/*.md  |  directing/*.md  |  video/platforms/*.md   │
└────────────────────────────┬────────────────────────────────┘
                             │ Uses MCP Tools
┌────────────────────────────▼────────────────────────────────┐
│                     MCP Servers (Tools)                      │
│  ProjectServer  |  StoryboardServer  |  VideoServer         │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Using the CLI

```bash
# Activate virtual environment
source venv/bin/activate

# Start a new workflow
python scripts/run_workflow.py start "一个机器人学会了爱" --genre 科幻

# List sessions
python scripts/run_workflow.py list

# Resume a session
python scripts/run_workflow.py resume <session_id>

# Interactive mode
python scripts/run_workflow.py interactive
```

### Using Python API

```python
from agents import PersistentWorkflowRunner, InteractionMode

# Create runner
runner = PersistentWorkflowRunner()

# Start workflow
result = runner.start(
    idea="一个机器人学会了爱",
    genre="科幻",
    num_episodes=1,
    episode_duration=60,
    mode=InteractionMode.INTERACTIVE,
)

# Get session ID for later
session_id = result['session_id']
print(f"Phase: {result['summary']['phase']}")

# Approve and continue
if result['summary']['pending_approval']:
    result = runner.approve_and_continue(approved=True)

# Resume later
runner = PersistentWorkflowRunner()
result = runner.resume(session_id)
```

## Modules

### state.py
Defines the shared state used across all agents:
- `AgentState` - Main state object
- `WorkflowPhase` - Workflow phases (INIT, STORY_OUTLINE, etc.)
- `InteractionMode` - INTERACTIVE or AUTONOMOUS
- `UserRequest` - User's story request

### base.py
Base class for all agents:
- LLM client (Gemini)
- Skill loading
- JSON parsing utilities
- Database access

### story_writer.py
Story Writer Agent handles:
- Story outline generation
- Character design
- Episode writing

### director.py
Director Agent handles:
- Storyboard creation
- Shot descriptions
- Visual planning

### video_producer.py
Video Producer Agent handles:
- Platform-specific prompt generation
- Video task submission
- Status tracking

### supervisor.py
Supervisor Agent orchestrates:
- Task routing
- Phase transitions
- Human-in-the-loop checkpoints

### graph.py
LangGraph workflow definition:
- `WorkflowRunner` - Simple runner
- `PersistentWorkflowRunner` - With session persistence

### session.py
Session management:
- `SessionManager` - Database operations
- `Session` - Session data
- `Checkpoint` - Recovery points

## Workflow Phases

1. **INIT** → Story Writer generates outline
2. **STORY_OUTLINE** → Story Writer designs characters
3. **CHARACTER_DESIGN** → Story Writer writes episodes
4. **STORYBOARD** → Director creates storyboard
5. **VIDEO_PROMPTS** → Video Producer generates prompts
6. **VIDEO_GENERATION** → Video Producer submits tasks
7. **REVIEW** → Final review
8. **COMPLETED** → Done

## Human-in-the-Loop

In interactive mode, the workflow pauses at checkpoints:
- Story outline approval
- Character design approval
- Episode approval
- Storyboard approval
- Video prompt approval

Users can:
- **Approve** - Continue to next phase
- **Reject** - Stop workflow with feedback
- **Pause** - Save session for later

## Session Persistence

Sessions are saved to SQLite database:
- Full state serialization
- Checkpoint history
- Resume from any point

```python
# List paused sessions
sessions = runner.list_sessions(status="paused")

# Get session details
info = runner.get_session_info(session_id)

# Delete session
runner.delete_session(session_id)
```

## Testing

```bash
# Run agent tests
python scripts/test_agents.py

# Run session tests
python scripts/test_session.py

# Run end-to-end tests
python scripts/test_e2e.py
```

## Dependencies

- `langgraph` - Agent orchestration
- `google-genai` - Gemini LLM
- `fastmcp` - MCP tools (optional)
