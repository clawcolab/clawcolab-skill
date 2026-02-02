---
name: clawbrain
description: "Claw Brain - Personal AI Memory System. Migrated to new repo. Use clawcolab/clawbrain."
metadata: {"clawdbot":{"emoji":"🧠","requires":{"dirs":["clawbrain"]},"install":[{"id":"git","kind":"git","url":"https://github.com/clawcolab/clawbrain.git","label":"Install Claw Brain (git)"}]}}
---

# Claw Brain Skill (Migrated) 🧠

**This skill has migrated to its own repository.**

## New Repository

Use the standalone Claw Brain repository:
- **URL:** https://github.com/clawcolab/clawbrain
- **Install:** `pip install git+https://github.com/clawcolab/clawbrain.git`

## Features

- 🎭 Soul/Personality - Evolving traits
- 👤 User Profile - Learns preferences
- 💭 Conversation State - Mood/intent detection
- 📚 Learning Insights - Continuous improvement
- 🧠 get_full_context() - Everything for personalized responses

## Quick Start

```bash
pip install git+https://github.com/clawcolab/clawbrain.git
```

```python
from clawbrain import Brain

brain = Brain()
context = brain.get_full_context(
    session_key="chat_123",
    user_id="user",
    agent_id="agent",
    message="Hey!"
)
```

## Storage Options

### SQLite (Default)
```python
brain = Brain({"storage_backend": "sqlite"})
```

### PostgreSQL + Redis (Production)
```python
# Requires: psycopg2-binary, redis
brain = Brain()  # Auto-detects
```

## Legacy

This skill package previously pointed to CLAWCOLAB. It now redirects to the standalone clawbrain repository.
