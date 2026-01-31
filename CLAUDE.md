# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Movie Generator - an open-source AI-driven video generation system that automates the complete workflow from script creation to video production. Supports multiple video generation platforms (Kling, Hailuo, JiMeng, Tongyi).

## Common Commands

```bash
# Setup
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run Streamlit story generator UI
streamlit run src/story_generator/app.py --server.port 8502

# Run multi-agent workflow CLI
python scripts/run_workflow.py start "故事创意" --genre 科幻 --episodes 1
python scripts/run_workflow.py list
python scripts/run_workflow.py resume <session_id>
python scripts/run_workflow.py view <session_id>
python scripts/run_workflow.py videos <session_id> --wait --download

# Run tests
python scripts/test_agents.py      # Agent unit tests (7 tests)
python scripts/test_session.py     # Session management tests (5 tests)
python scripts/test_e2e.py         # End-to-end tests (4 tests)
python scripts/test_mcp_servers.py # MCP server tests

# Run MCP servers (for agent tool access)
python scripts/run_mcp_servers.py project
python scripts/run_mcp_servers.py storyboard
python scripts/run_mcp_servers.py video
```

## Architecture

### Multi-Agent Workflow System

The system uses LangGraph for multi-agent orchestration with human-in-the-loop checkpoints:

```
INIT → STORY_OUTLINE → CHARACTER_DESIGN → EPISODE_WRITING
    → STORYBOARD → VIDEO_PROMPTS → VIDEO_GENERATION → REVIEW → COMPLETED
```

**Agents** (`src/agents/`):
- `StoryWriterAgent`: Generates story outline, characters, episodes
- `DirectorAgent`: Creates storyboard with shot descriptions
- `VideoProducerAgent`: Generates video prompts and submits to platforms
- `SupervisorAgent`: Orchestrates workflow routing

**Shared State** (`src/agents/state.py`):
- `AgentState` dataclass holds all workflow data
- `WorkflowPhase` enum tracks current phase
- `InteractionMode`: INTERACTIVE (with approvals) or AUTONOMOUS

**Workflow Runners** (`src/agents/graph.py`):
- `WorkflowRunner`: Basic workflow execution
- `PersistentWorkflowRunner`: Adds session persistence and recovery

### Skills System

Skills are Markdown files in `src/skills/` that provide knowledge/prompts to agents:
- `writing/`: story_outline, random_idea, consistency_check
- `character/`: character_design, character_events
- `directing/`: storyboard, shot_description
- `video/`: prompt_generation, platforms/{kling,hailuo,jimeng,tongyi}

Load skills via `src/skills/loader.py`.

### Video Providers

Abstract `VideoProvider` base class in `src/providers/base.py` with implementations:
- `KlingProvider`: JWT auth, text-to-video, image-to-video, subject reference
- `HailuoProvider`: API key auth, camera movement control
- `JimengProvider`: Volcengine signature auth
- `TongyiProvider`: Bearer token auth

All return `VideoTask` objects with `task_id`, `status`, `video_url`.

### MCP Servers

Model Context Protocol servers provide tool interfaces for agents:
- `project_server.py`: Project/Character/Episode CRUD
- `storyboard_server.py`: Shot management
- `video_server.py`: Video generation API wrapper

### Data Models

Core models in `src/story_generator/models.py`:
- `Project`: Container with characters and episodes
- `Character`: Name, appearance, personality, visual_description
- `Episode`: Title, outline, shots list
- `Shot`: Visual description, dialogue, camera_movement, duration

Database operations in `src/story_generator/database.py` (SQLite).

### Session Management

`src/agents/session.py` provides:
- `SessionManager`: Create, save, load, resume sessions
- `Session`: Tracks workflow state, status (running/paused/completed/failed)
- `Checkpoint`: Records each workflow step for recovery

## Configuration

**API Keys**: Set `GEMINI_API_KEY` environment variable or create `src/providers/config.local.yaml`:
```yaml
providers:
  kling:
    access_key: "..."
    secret_key: "..."
  hailuo:
    api_key: "..."
```

## Key Patterns

**Language Detection**: Use `_is_chinese_input()` to detect Chinese input and generate Chinese output accordingly.

**Error Recovery**: `PersistentWorkflowRunner.resume()` can recover from failed sessions by clearing error and retrying from the failed phase.

**Video Task Handling**: Providers return `VideoTask` objects (not dicts). Access `task.task_id`, `task.status.value`, `task.video_url`.

## Visual Development & Testing

### Design System

The project follows S-Tier SaaS design standards inspired by Stripe, Airbnb, and Linear. All UI development must adhere to:

- **Design Principles**: `/context/design-principles.md` - Comprehensive checklist for world-class UI
- **Component Library**: NextUI with custom Tailwind configuration

### Quick Visual Check

**IMMEDIATELY after implementing any front-end change:**

1. **Identify what changed** - Review the modified components/pages
2. **Navigate to affected pages** - Use `mcp__playwright__browser_navigate` to visit each changed view
3. **Verify design compliance** - Compare against `/context/design-principles.md`
4. **Validate feature implementation** - Ensure the change fulfills the user's specific request
5. **Check acceptance criteria** - Review any provided context files or requirements
6. **Capture evidence** - Take full page screenshot at desktop viewport (1440px) of each changed view
7. **Check for errors** - Run `mcp__playwright__browser_console_messages` ⚠️

This verification ensures changes meet design standards and user requirements.

### Comprehensive Design Review

For significant UI changes or before merging PRs, use the design review agent:

```bash
# Option 1: Use the slash command
/design-review

# Option 2: Invoke the agent directly
@agent-design-review
```

The design review agent will:

- Test all interactive states and user flows
- Verify responsiveness (desktop/tablet/mobile)
- Check accessibility (WCAG 2.1 AA compliance)
- Validate visual polish and consistency
- Test edge cases and error states
- Provide categorized feedback (Blockers/High/Medium/Nitpicks)

### Playwright MCP Integration

#### Essential Commands for UI Testing

```javascript
// Navigation & Screenshots
mcp__playwright__browser_navigate(url); // Navigate to page
mcp__playwright__browser_take_screenshot(); // Capture visual evidence
mcp__playwright__browser_resize(
  width,
  height
); // Test responsiveness

// Interaction Testing
mcp__playwright__browser_click(element); // Test clicks
mcp__playwright__browser_type(
  element,
  text
); // Test input
mcp__playwright__browser_hover(element); // Test hover states

// Validation
mcp__playwright__browser_console_messages(); // Check for errors
mcp__playwright__browser_snapshot(); // Accessibility check
mcp__playwright__browser_wait_for(
  text / element
); // Ensure loading
```

### Design Compliance Checklist

When implementing UI features, verify:

- [ ] **Visual Hierarchy**: Clear focus flow, appropriate spacing
- [ ] **Consistency**: Uses design tokens, follows patterns
- [ ] **Responsiveness**: Works on mobile (375px), tablet (768px), desktop (1440px)
- [ ] **Accessibility**: Keyboard navigable, proper contrast, semantic HTML
- [ ] **Performance**: Fast load times, smooth animations (150-300ms)
- [ ] **Error Handling**: Clear error states, helpful messages
- [ ] **Polish**: Micro-interactions, loading states, empty states

## When to Use Automated Visual Testing

### Use Quick Visual Check for:

- Every front-end change, no matter how small
- After implementing new components or features
- When modifying existing UI elements
- After fixing visual bugs
- Before committing UI changes

### Use Comprehensive Design Review for:

- Major feature implementations
- Before creating pull requests with UI changes
- When refactoring component architecture
- After significant design system updates
- When accessibility compliance is critical

### Skip Visual Testing for:

- Backend-only changes (API, database)
- Configuration file updates
- Documentation changes
- Test file modifications
- Non-visual utility functions