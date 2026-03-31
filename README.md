# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

# Smarter Scheduling
The updated PawPal+ system introduces more advanced logic to handle the complexities of households with multiple pets. Improved features include:

Smarter priority scoring: The scheduler calculates a priority score based on task weight, deadline "slack," and even the pet's age to ensure critical needs are met first.

Intelligent Time-Blocking: It automatically assigns start and end times for tasks, incorporating a "cooldown" period after heavy activities to prevent owner burnout.

Conflict Detection: A new algorithm identifies overlapping windows by checking if a task's duration extends into the start time of the next scheduled item.

Relative Recurrence: When a recurring task like "Heartworm Meds" is marked complete, the system automatically schedules the next occurrence relative to the completion time.

Workload Monitoring: The system analyzes total daily minutes and provides visual warnings if the schedule becomes moderate or heavy.