# pyawe

Python client library for the [AWE (Advanced Workflow Engine)](https://github.com/colinmanning/awe-server) API.

**[Documentation](https://ullav-dev.github.io/pyawe/)**

## Installation

```bash
pip install pyawe
```

## Quick start

```python
from pyawe import AweClient

client = AweClient(
    api_url="http://localhost:8080",
    auth_url="http://localhost:8081",   # ullav-user-management service
)
client.login(email="user@example.com", password="secret")

# Workflows
workflows = client.workflows.list()
wf = client.workflows.create("Q1 Onboarding", is_template=False)
detail = client.workflows.get(wf.id)          # WorkflowWithTasks

# Tasks
task = client.tasks.create("Review docs", workflow_id=wf.id, is_start=True)
client.tasks.update(task.id, status="In Progress")
mine = client.tasks.list_mine()               # tasks assigned to me / my roles

# Jobs
job = client.jobs.create("Q1 Campaign")
client.jobs.clone_workflow(job.id, workflow_template_id)

# Notes
note = client.notes.create("task", task.id, "Looks good", is_shared=True)
client.notes.create_reply(note.id, "Agreed")

# Automated tasks
client.task_scripts.upsert(
    task.id,
    script_type="python",
    script_body="print('hello')",
    timeout_secs=60,
)
runs = client.task_runs.list(task.id)
```

## Example: list your tasks

Print every task assigned to the authenticated user, along with its status and
the workflow (and job, if any) it belongs to:

```python
import os
from pyawe import AweClient

client = AweClient(
    api_url=os.environ["AWE_API_URL"],
    auth_url=os.environ.get("AWE_AUTH_URL", os.environ["AWE_API_URL"]),
)
client.login(email=os.environ["AWE_EMAIL"], password=os.environ["AWE_PASSWORD"])

for twc in client.tasks.list_mine():
    context = twc.workflow_name
    if twc.job_name:
        context = f"{twc.job_name} / {twc.workflow_name}"
    print(f"[{twc.task.status}]  {twc.task.name}  ({context})")
```

A runnable version of this script is at `examples/list_my_tasks.py`.

## Authentication

`AweClient` authenticates against the `ullav-user-management` service, which
issues the JWT accepted by the AWE server.

- `api_url` — AWE server base URL (e.g. `http://awe-server:8080`)
- `auth_url` — auth service base URL (e.g. `http://ullav-user-management:8081`);
  omit if both services are behind the same proxy

Call `client.login(email, password)` before any other method. Tokens expire
according to the server's configuration; call `login()` again to refresh.

## Resource clients

| Attribute | Resource |
|---|---|
| `client.workflows` | Workflow CRUD, merge, duplicate, team |
| `client.tasks` | Task CRUD, mine, decide, rework |
| `client.task_links` | Link create/delete, next/previous tasks, data bindings |
| `client.task_ports` | Port spec CRUD, input/output values |
| `client.task_scripts` | Automated task script upsert/delete |
| `client.task_runs` | Execution run history |
| `client.task_team_roles` | Team-role assignment |
| `client.jobs` | Job CRUD, clone workflow, team |
| `client.execution_profiles` | Kubernetes execution profile CRUD |
| `client.loop_blocks` | Loop block CRUD |
| `client.notes` | Note CRUD, replies, folder move |
| `client.note_folders` | Note folder CRUD |

## Error handling

```python
from pyawe import AweAuthError, AweNotFoundError, AweValidationError

try:
    wf = client.workflows.get("non-existent-id")
except AweNotFoundError:
    print("not found")
except AweAuthError:
    client.login(email, password)  # token expired — re-authenticate
except AweValidationError as e:
    print("bad request:", e)
```

| Exception | HTTP status |
|---|---|
| `AweAuthError` | 401 / 403, or `login()` not called |
| `AweNotFoundError` | 404 |
| `AweValidationError` | 400 |
| `AweServerError` | 5xx |
| `AweError` | base class |

## Status values

Use the `Status` and `ScheduleStatus` enumerations or plain strings:

```python
from pyawe import Status, ScheduleStatus

client.tasks.update(task_id, status=Status.IN_PROGRESS)
client.tasks.update(task_id, status="In Progress")  # equivalent
```

## Licence

MIT
