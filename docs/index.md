# pyawe

Python client library for the [AWE (Advanced Workflow Engine)](https://github.com/colinmanning/awe-server) API.

## Installation

```bash
pip install pyawe
```

Requires Python 3.9+.

## Quick start

```python
from pyawe import AweClient

client = AweClient(
    api_url="http://localhost:8080",
    auth_url="http://localhost:8081",  # omit if auth is behind the same proxy
)
client.login(email="you@example.com", password="secret")

# List workflows
workflows = client.workflows.list()

# Create a job and a workflow inside it
job = client.jobs.create("Q3 Onboarding")
wf  = client.workflows.create("Onboarding Steps", job_id=job.id)

# Add tasks
start = client.tasks.create("Kick-off",    workflow_id=wf.id, is_start=True)
review = client.tasks.create("Doc Review", workflow_id=wf.id)
end   = client.tasks.create("Complete",    workflow_id=wf.id, is_end=True)

# Link them
client.task_links.create(start.id, review.id)
client.task_links.create(review.id, end.id)

# Advance a task
client.tasks.update(start.id, status="In Progress")
```

## Authentication

pyawe authenticates against the `ullav-user-management` service, which may be the same host as the AWE API or a separate one.

```python
# Same host
client = AweClient("http://awe.example.com")

# Separate auth service
client = AweClient(
    api_url="http://awe.example.com",
    auth_url="http://auth.example.com",
)
```

Calling [`login()`][pyawe.AweClient.login] stores the JWT in the session. All subsequent calls attach it automatically as `Authorization: Bearer <token>`. Tokens expire according to the server configuration — call `login()` again to refresh.

## Error handling

All exceptions inherit from [`AweError`][pyawe.AweError]:

```python
from pyawe import AweClient, AweNotFoundError, AweAuthError, AweError

try:
    wf = client.workflows.get("non-existent-id")
except AweNotFoundError:
    print("Workflow not found")
except AweAuthError:
    print("Not authenticated or forbidden")
except AweError as e:
    print(f"Unexpected error: {e}")
```

See the [Exceptions reference](api/exceptions.md) for the full hierarchy.

## Sub-clients

`AweClient` exposes one sub-client per resource family:

| Attribute | Resource |
|---|---|
| `client.workflows` | Workflows — create, update, duplicate, merge |
| `client.tasks` | Tasks — CRUD, decide, rework |
| `client.task_links` | Links between tasks; data bindings |
| `client.task_ports` | Port specs and runtime values |
| `client.task_scripts` | Automated task scripts |
| `client.task_runs` | Execution run history |
| `client.task_team_roles` | Team-role assignments on tasks |
| `client.jobs` | Jobs — group workflows together |
| `client.projects` | Projects — group jobs together |
| `client.loop_blocks` | Loop block tasks |
| `client.execution_profiles` | Kubernetes execution environments |
| `client.task_history` | Task status transition history |
| `client.connections` | Reusable credential ("connection profile") management |
| `client.work_items` | Reusable task templates |
| `client.checkpoint_checks` | Checkpoint task check gating |
| `client.scheduled_scripts` | Cron-scheduled, task-independent scripts |
| `client.ai_chat_sessions` | The authenticated user's own AI chat history |
